import os
import ssl
import json
import traceback
import asyncio
import base64
from typing import List

# ==========================================
# 🛡️ מעקף חסימות SSL רשמי של נטפרי
# ==========================================
try:
    from netfree_unstrict_ssl import unstrict_ssl
    unstrict_ssl()
except ImportError:
    ssl._create_default_https_context = ssl._create_unverified_context
    os.environ["CURL_CA_BUNDLE"] = ""

from dotenv import load_dotenv
load_dotenv()

# ==========================================
# 🌲 שלב 1: חיבור לאינדקס הקיים ב-Pinecone
# ==========================================
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore

print("⏳ מתחבר ל-Pinecone וטוען את בסיס הידע הוקטורי...")

embed_model = CohereEmbedding(
    cohere_api_key=os.environ.get("COHERE_API_KEY"),
    model_name="embed-multilingual-v3.0"
)

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
pinecone_index = pc.Index("cohere-index") 

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)
print("✅ החיבור לבסיס הנתונים ב-Pinecone הצליח!")

# ==========================================
# ⚡ שלב 2: הגדרת מודל ה-LLM של Gemini
# ==========================================
from llama_index.llms.google_genai import GoogleGenAI

llm = GoogleGenAI(
    model="gemini-2.5-flash",
    api_key=os.environ.get("GEMINI_API_KEY")
)
print("✅ מודל Gemini הוגדר בהצלחה!")

# ==========================================
# 🔍 שלב 3: הגדרת רכיבי ה-RAG הבסיסיים
# ==========================================
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.schema import NodeWithScore, TextNode

retriever = index.as_retriever(similarity_top_k=5)
response_synthesizer = get_response_synthesizer(llm=llm, response_mode="compact")

# טעינת בסיס הנתונים המובנה שחולץ בשלב ג' חלק 1
EXTRACTED_JSON_PATH = "extracted_knowledge.json"

# ==========================================
# 🔄 שלב 3.5: בניית ארכיטקטורת Event-Driven Workflow היברידית
# ==========================================
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step

# הגדרת האירועים בצינור הזרימה
class RouteEvent(Event):
    query_str: str

class RetrieveEvent(Event):
    query_str: str

class StructuredSearchEvent(Event):
    query_str: str
    routing_decision: dict

class GenerationEvent(Event):
    nodes: List[NodeWithScore]
    query_str: str

class RAGHybridWorkflow(Workflow):
    
    @step
    async def validate_input_step(self, ev: StartEvent) -> RouteEvent | StopEvent:
        """שלב 1: הלבנה ואימות ראשוני של הקלט"""
        query_str = ev.query_str
        if not query_str or len(query_str.strip()) < 3:
            print("🛑 [Workflow] קלט ריק או קצר מדי.")
            return StopEvent(result="נראה ששכחת להקליד שאלה...")
        print(f"📥 [Workflow] קלט מאומת -> משגר RouteEvent")
        return RouteEvent(query_str=query_str)

    @step
    async def routing_step(self, ev: RouteEvent) -> RetrieveEvent | StructuredSearchEvent:
        """שלב 2 (חדש): נתב חכם (Router) המזהה את כוונת השאלה של המשתמש"""
        print(f"🔀 [Workflow] מנתח כוונת שאלה לצורך ניתוב אופטימלי...")
        
        router_prompt = (
            "You are a routing agent for a project documentation system.\n"
            "Your job is to decide if the user query should be routed to a 'VECTOR' search or a 'STRUCTURED' search.\n\n"
            "Guidelines:\n"
            "- Route to 'STRUCTURED' if the query asks for lists, aggregations, total counts, strict time frames "
            "(e.g., 'this week', 'last month'), updates, or overview of choices across files (e.g., 'give me all rules', 'list technical decisions', 'what warnings exist').\n"
            "- Route to 'VECTOR' if the query is a semantic question asking for 'how to', explanations, definitions, or code guides.\n\n"
            "If the choice is 'STRUCTURED', you must also identify which target category is needed ('decisions', 'rules', or 'warnings') and a short string filter keyword if applicable (otherwise empty string).\n\n"
            "Respond ONLY with a valid JSON in this exact schema:\n"
            "{{\n"
            "  \"route\": \"VECTOR\" or \"STRUCTURED\",\n"
            "  \"category\": \"decisions\" or \"rules\" or \"warnings\" or \"none\",\n"
            "  \"keyword\": \"filter keyword or empty string\"\n"
            "}}\n\n"
            f"User Query: \"{ev.query_str}\"\n"
            "JSON Response:"
        )
        
        try:
            # פנייה מהירה ל-LLM לצורך קבלת החלטת הניתוב במבנה קשיח
            response = await llm.acomplete(router_prompt)
            clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            decision = json.loads(clean_text)
            
            if decision.get("route") == "STRUCTURED" and decision.get("category") in ["decisions", "rules", "warnings"]:
                print(f"📊 [Router Match] נותב למסלול מובנה (JSON) -> קטגוריה: {decision.get('category')}")
                return StructuredSearchEvent(query_str=ev.query_str, routing_decision=decision)
        except Exception as e:
            print(f"⚠️ שגיאה בלוגיקת הנתב האוטומטי, חוזר למסלול וקטורי כגיבוי: {e}")
            
        print(f"🌲 [Router Match] נותב למסלול סמנטי (Pinecone Vector DB)")
        return RetrieveEvent(query_str=ev.query_str)

    @step
    async def retrieve_and_score_step(self, ev: RetrieveEvent) -> GenerationEvent | StopEvent:
        """שלב 3א: אחזור סמנטי וקטורי מתוך Pinecone (הלוגיקה המקורית שלך)"""
        print(f"🔍 [Workflow] שולף חתיכות מידע מ-Pinecone...")
        nodes = await retriever.aretrieve(ev.query_str)
        if not nodes:
            return StopEvent(result="מצטער, לא נמצא שום מידע רלוונטי בבסיס הוקטורי.")
            
        highest_score = nodes[0].score if nodes[0].score is not None else 0
        print(f"📊 [Workflow] Vector Confidence Score: {highest_score}")
        
        if highest_score < 0.30:
            print("🛑 [Workflow] Confidence וקטורי נמוך מדי!")
            return StopEvent(result="מצטער, לא מצאתי מידע מוסמך מספיק בקבצים הסמנטיים.")
            
        return GenerationEvent(nodes=nodes, query_str=ev.query_str)

    @step
    async def structured_retrieval_step(self, ev: StructuredSearchEvent) -> GenerationEvent | StopEvent:
        """שלב 3ב (חדש): שליפה וסינון לוגי מובנה בשיטת המתקדמים מתוך קובץ ה-JSON"""
        print(f"📁 [Workflow] פותח בסיס נתונים מובנה לשליפת רשימה מלאה...")
        
        if not os.path.exists(EXTRACTED_JSON_PATH):
            return StopEvent(result="❌ שגיאה: קובץ בסיס הנתונים המובנה (extracted_knowledge.json) חסר. אנא הריצי את extract.py תחילה.")
            
        with open(EXTRACTED_JSON_PATH, "r", encoding="utf-8") as f:
            db_data = json.load(f)
            
        decision = ev.routing_decision
        category = decision.get("category")
        keyword = str(decision.get("keyword", "")).lower()
        
        # שליפת המערך המבוקש מתוך ה-JSON
        raw_items = db_data.get("items", {}).get(category, [])
        filtered_items = []
        
        # סינון פייתון מהיר וקשיח על פני הפריטים (Text-to-Query Logic)
        for item in raw_items:
            item_str = json.dumps(item, ensure_ascii=False).lower()
            if keyword in item_str:
                filtered_items.append(item)
                
        if not filtered_items:
            print(f"⚠️ לא נמצאו פריטים מובנים תחת הקטגוריה '{category}' עם מילת הסינון '{keyword}'")
            return StopEvent(result=f"חיפשתי במאגר המובנה תחת רשימת {category}, אך לא נמצאו פריטים מתאימים העונים לשאילתה.")
            
        print(f"🎯 [Structured Match] שלפתי בהצלחה {len(filtered_items)} פריטים מובנים מתוך ה-JSON!")
        
        # 👑 קסם ארכיטקטוני: הפיכת ה-JSON המסונן ל-TextNodes כדי ששלב הניסוח הבא לא ישתנה!
        wrapped_nodes = []
        for item in filtered_items:
            serialized_text = json.dumps(item, ensure_ascii=False, indent=2)
            node_obj = NodeWithScore(node=TextNode(text=serialized_text), score=1.0)
            wrapped_nodes.append(node_obj)
            
        return GenerationEvent(nodes=wrapped_nodes, query_str=ev.query_str)

    @step
    async def generate_response_step(self, ev: GenerationEvent) -> StopEvent:
        """שלב 4: ניסוח תשובה סופית באמצעות Gemini (הלוגיקה המקורית שלך)"""
        print("🤖 [Workflow] Gemini מנסח תשובה מבוססת עובדות...")
        response = await response_synthesizer.asynthesize(query=ev.query_str, nodes=ev.nodes)
        return StopEvent(result=str(response))

# אתחול ה-Workflow ההיברידי החדש
rag_workflow = RAGHybridWorkflow(timeout=60, verbose=True)

# ==========================================
# 🗺️ בניית הגרף החזותי המעודכן באמצעות PyVis
# ==========================================
def build_stable_graph():
    try:
        from pyvis.network import Network
        net = Network(height="450px", width="100%", directed=True, bgcolor="#ffffff", font_color="#111827")
        
        # הגדרת הצמתים החדשים של שלב ג'
        net.add_node(1, label="Validate Input\n(Step 1)", shape="box", color="#3B82F6", font={'size': 13, 'color': 'white'})
        net.add_node(2, label="Intent Router\n(Step 2)", shape="diamond", color="#F59E0B", font={'size': 13, 'color': 'white'})
        net.add_node(3, label="Vector Search\n(Step 3a)", shape="box", color="#10B981", font={'size': 13, 'color': 'white'})
        net.add_node(4, label="Structured JSON\n(Step 3b)", shape="box", color="#EC4899", font={'size': 13, 'color': 'white'})
        net.add_node(5, label="Gemini Generator\n(Step 4)", shape="box", color="#8B5CF6", font={'size': 13, 'color': 'white'})
        
        # הגדרת החיבורים מבוססי האירועים (Events)
        net.add_edge(1, 2, label="RouteEvent", color="#2563EB", arrows="to")
        net.add_edge(2, 3, label="RetrieveEvent", color="#059669", arrows="to")
        net.add_edge(2, 4, label="StructuredSearchEvent", color="#DB2777", arrows="to")
        net.add_edge(3, 5, label="GenerationEvent", color="#059669", arrows="to")
        net.add_edge(4, 5, label="GenerationEvent", color="#8B5CF6", arrows="to")
        
        net.write_html("workflow_graph.html")
        print("✅ מפת ה-Workflow ההיברידית (workflow_graph.html) עודכנה בהצלחה!")
    except Exception as e:
        print(f"⚠️ שגיאה ביצירת הגרף: {e}")

build_stable_graph()

# ==========================================
# 🎨 שלב 4: CSS משופר - Modern SaaS UI (העיצוב המקורי שלך ללא שינוי)
# ==========================================
executive_css = """
body, .gradio-container { background-color: #F3F4F6 !important; direction: rtl !important; }
.top-bar { background-color: #FFFFFF !important; padding: 16px 32px !important; border-radius: 16px !important; margin-bottom: 24px !important; margin-top: 10px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important; align-items: center !important; }
.sidebar-panel { background-color: transparent !important; border: none !important; padding: 0 0 0 20px !important; }
.status-item { background-color: #FFFFFF !important; border: 1px solid #F3F4F6 !important; padding: 14px 16px !important; border-radius: 12px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 12px !important; }
.chatbot-container { background-color: #FFFFFF !important; border: none !important; border-radius: 16px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; padding: 10px !important; }
.unified-input { background: #FFFFFF !important; border-radius: 30px !important; padding: 6px 6px 6px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important; border: 1px solid #E5E7EB !important; margin-top: 15px !important; align-items: center !important; }
.unified-input input { border: none !important; box-shadow: none !important; background: transparent !important; font-size: 15px !important; }
.submit-btn { background-color: #2563EB !important; color: white !important; border-radius: 24px !important; height: 100% !important; padding: 10px 24px !important; font-weight: 600 !important; border: none !important; }
.example-btn button { background: #FFFFFF !important; border: 1px solid #E5E7EB !important; border-radius: 20px !important; padding: 8px 16px !important; color: #4B5563 !important; font-size: 13.5px !important; margin: 5px; }
"""

# ==========================================
# 💬 שלב 5: בניית הממשק והפעלת ה-Workflow (ה-UI המקורי שלך)
# ==========================================
import gradio as gr

def get_graph_iframe_content():
    try:
        graph_path = "workflow_graph.html"
        if os.path.exists(graph_path):
            with open(graph_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            return f'data:text/html;base64,{b64_html}'
    except Exception as e:
        print(f"⚠️ שגיאה בטעינת הגרף החזותי: {e}")
    return ""

def get_wrapped_iframe():
    iframe_src = get_graph_iframe_content()
    return f'<iframe src="{iframe_src}" width="100%" height="450px" style="border:none; background:white; border-radius:12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);"></iframe>'

async def predict(message, history):
    if not history: 
        history = []
    if not message.strip(): 
        return "", history
        
    try:
        print(f"📥 [Gradio] משגר שאילתה אסינכרונית ל-Workflow...")
        response = await rag_workflow.run(query_str=message)
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": str(response)})
        return "", history
        
    except Exception as e:
        print("\n🛑 שגיאה בריצת ה-Workflow:")
        traceback.print_exc()
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"❌ שגיאה: {str(e)}"})
        return "", history

with gr.Blocks() as demo:
    with gr.Row(elem_classes=["top-bar"]):
        gr.Markdown("<h2 style='margin:0; font-weight:700; color:#1F2937;'><span style='font-size:22px; margin-left:10px;'>📚</span>Agentic Coding Knowledge Core</h2>")
        gr.Markdown("<div style='text-align:left;'><span style='background-color:#DEF7EC; color:#03543F; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600;'>🟢 Hybrid Router Active</span></div>")

    with gr.Row():
        with gr.Column(scale=1, min_width=280, elem_classes=["sidebar-panel"]):
            gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-bottom:15px; font-weight:600;'>מקורות מידע פעילים</h3>")
            gr.Markdown("<div class='status-item'>🛠️ <b>Cursor Agent</b><br><span style='font-size:12px; color:#059669;'>● 20 קבצים מאונדקסים</span></div>")
            gr.Markdown("<div class='status-item'>🤖 <b>Claude Code</b><br><span style='font-size:12px; color:#059669;'>● 16 קבצים מאונדקסים</span></div>")
            gr.Markdown("<div class='status-item'>⚡ <b>Kiro Engine</b><br><span style='font-size:12px; color:#059669;'>● 12 קבצים מאונדקסים</span></div>")
            
            gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-top:30px; margin-bottom:10px; font-weight:600;'>הגדרות מנוע (RAG)</h3>")
            gr.Markdown("<div style='background:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #E5E7EB; font-size:13px; color:#4B5563; line-height:1.7;'><b>Architecture:</b> Event-Driven Hybrid<br><b>Vector DB:</b> Pinecone<br><b>Structured DB:</b> local JSON<br><b>LLM:</b> Gemini 2.5 Flash<br><b>Router Mode:</b> Auto Intent Selection</div>")

        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.TabItem("💬 מרכז תשאול ידע"):
                    chatbot = gr.Chatbot(
                        elem_classes=["chatbot-container"], show_label=False, height=450,
                        avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/6062/6062646.png")
                    )
                    
                    with gr.Row(elem_classes=["unified-input"]):
                        txt = gr.Textbox(show_label=False, placeholder="שאל שאלה על החלטות ארכיטקטורה, חוקים או אזהרות...", container=False, scale=8)
                        submit_btn = gr.Button("שלח", elem_classes=["submit-btn"], scale=1, min_width=100)
                    
                    gr.Markdown("<div style='font-size:13px; color:#6B7280; margin-top:20px; font-weight:500;'>💡 שאלות מומלצות לבדיקה:</div>")
                    with gr.Row(elem_classes=["example-btn"]):
                        ex1 = gr.Button("מהם יעדי ה-RTO וה-RPO של המערכת?")
                        ex2 = gr.Button("איך מתבצע הגיבוי של מסד הנתונים?")
                        ex3 = gr.Button("מהו נוהל ההתאוששות במקרה של מתקפת כופרה?")

                    def set_example(text): return text

                    ex1.click(fn=set_example, inputs=[gr.State("מהם יעדי ה-RTO וה-RPO של המערכת, והאם אנחנו עומדים בהם?")], outputs=[txt])
                    ex2.click(fn=set_example, inputs=[gr.State("באילו אזורים גיאוגרפיים (Regions) המערכת שלנו מגובה כרגע?")], outputs=[txt])
                    ex3.click(fn=set_example, inputs=[gr.State("מהו נוהל ההתאוששות והשלבים במקרה של קריסת אזור שלם ב-AWS?")], outputs=[txt])

                with gr.TabItem("🗺️ מפת מבנה ה-Workflow (שלב ג')"):
                    gr.Markdown("<p style='color:#4B5563; margin-top:10px;'>תרשים אינטראקטיבי רשמי המציג את ארכיטקטורת ה-Event-Driven Hybrid החדשה של הפרויקט:</p>")
                    gr.HTML(value=get_wrapped_iframe())

            submit_btn.click(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])
            txt.submit(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])

if __name__ == "__main__":
    print("🏢 מפעיל את הממשק הארגוני מבוסס האירועים והניתוב ההיברידי...")
    demo.launch(share=False, allowed_paths=["workflow_graph.html"], css=executive_css)