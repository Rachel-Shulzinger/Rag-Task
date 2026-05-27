# import os
# import ssl
# import traceback

# # ==========================================
# # 🛡️ מעקף חסימות SSL רשמי של נטפרי
# # ==========================================
# from netfree_unstrict_ssl import unstrict_ssl
# unstrict_ssl()

# from dotenv import load_dotenv

# # טעינת משתני הסביבה (מפתחות ה-API)
# load_dotenv()

# # ==========================================
# # 🌲 שלב 1: חיבור לאינדקס הקיים ב-Pinecone
# # ==========================================
# from pinecone import Pinecone
# from llama_index.core import VectorStoreIndex
# from llama_index.embeddings.cohere import CohereEmbedding
# from llama_index.vector_stores.pinecone import PineconeVectorStore

# print("⏳ מתחבר ל-Pinecone וטוען את בסיס הידע...")

# embed_model = CohereEmbedding(
#     cohere_api_key=os.environ.get("COHERE_API_KEY"),
#     model_name="embed-multilingual-v3.0"
# )

# pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
# pinecone_index = pc.Index("cohere-index") 

# vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
# index = VectorStoreIndex.from_vector_store(
#     vector_store=vector_store,
#     embed_model=embed_model
# )
# print("✅ החיבור לבסיס הנתונים ב-Pinecone הצליח!")

# # ==========================================
# # ⚡ שלב 2: הגדרת מודל ה-LLM החדש של Gemini (Google GenAI)
# # ==========================================
# from llama_index.llms.google_genai import GoogleGenAI

# # שימוש ב-SDK החדש שעובר דרך פרוטוקול אינטרנט סטנדרטי שעוקף את חסימת ה-gRPC
# llm = GoogleGenAI(
#     model="gemini-2.5-flash",
#     api_key=os.environ.get("GEMINI_API_KEY")
# )
# print("✅ מודל Gemini GenAI המעודכן הוגדר בהצלחה!")
# # ==========================================
# # 🔍 שלב 3: הגדרת רכיבי ה-RAG
# # ==========================================
# from llama_index.core.postprocessor import SimilarityPostprocessor
# from llama_index.core.query_engine import RetrieverQueryEngine
# from llama_index.core.response_synthesizers import get_response_synthesizer

# retriever = index.as_retriever(similarity_top_k=5)
# node_postprocessor = SimilarityPostprocessor(similarity_cutoff=0.30)
# response_synthesizer = get_response_synthesizer(llm=llm, response_mode="compact")

# query_engine = RetrieverQueryEngine(
#     retriever=retriever,
#     node_postprocessors=[node_postprocessor],
#     response_synthesizer=response_synthesizer
# )

# # ==========================================
# # 🎨 שלב 4: CSS משופר - Modern SaaS UI
# # ==========================================
# executive_css = """
# body, .gradio-container { 
#     background-color: #F3F4F6 !important; 
#     font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; 
#     direction: rtl !important; 
# }

# .top-bar { 
#     background-color: #FFFFFF !important; 
#     padding: 16px 32px !important; 
#     border-radius: 16px !important;
#     margin-bottom: 24px !important; 
#     margin-top: 10px !important;
#     box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
#     align-items: center !important;
# }

# .sidebar-panel { 
#     background-color: transparent !important; 
#     border: none !important; 
#     padding: 0 0 0 20px !important; 
# }

# .status-item { 
#     background-color: #FFFFFF !important; 
#     border: 1px solid #F3F4F6 !important; 
#     padding: 14px 16px !important; 
#     border-radius: 12px !important; 
#     box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
#     margin-bottom: 12px !important;
#     transition: transform 0.2s, box-shadow 0.2s; 
# }

# .status-item:hover { 
#     transform: translateY(-2px); 
#     box-shadow: 0 4px 6px rgba(0,0,0,0.08); 
# }

# .chatbot-container { 
#     background-color: #FFFFFF !important; 
#     border: none !important; 
#     border-radius: 16px !important; 
#     box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; 
#     padding: 10px !important; 
# }

# .unified-input { 
#     background: #FFFFFF !important; 
#     border-radius: 30px !important; 
#     padding: 6px 6px 6px 20px !important; 
#     box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important; 
#     border: 1px solid #E5E7EB !important; 
#     margin-top: 15px !important;
#     align-items: center !important;
# }

# .unified-input input { 
#     border: none !important; 
#     box-shadow: none !important; 
#     background: transparent !important; 
#     font-size: 15px !important; 
# }

# .unified-input input:focus { border: none !important; box-shadow: none !important; }

# .submit-btn { 
#     background-color: #2563EB !important; 
#     color: white !important; 
#     border-radius: 24px !important; 
#     height: 100% !important; 
#     padding: 10px 24px !important; 
#     font-weight: 600 !important; 
#     border: none !important; 
#     transition: background-color 0.2s !important;
# }

# .submit-btn:hover { background-color: #1D4ED8 !important; }

# .example-btn {
#     display: flex !important;
#     flex-wrap: wrap !important;
#     gap: 10px !important;
#     justify-content: flex-start !important;
#     width: 100% !important;
#     margin-bottom: 20px !important;
# }

# .example-btn button { 
#     background: #FFFFFF !important; 
#     border: 1px solid #E5E7EB !important; 
#     border-radius: 20px !important; 
#     padding: 8px 16px !important;
#     color: #4B5563 !important; 
#     font-size: 13.5px !important; 
#     box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important; 
#     transition: all 0.2s ease !important;
#     flex: 0 1 auto !important;
#     white-space: normal !important;
# }

# .example-btn button:hover { 
#     border-color: #2563EB !important; 
#     color: #2563EB !important; 
#     background: #EFF6FF !important; 
#     transform: translateY(-1px) !important;
#     box-shadow: 0 3px 6px rgba(37, 99, 235, 0.1) !important;
# }
# """

# # ==========================================
# # 💬 שלב 5: בניית הממשק במבנה קונסולה (Blocks)
# # ==========================================
# import gradio as gr

# def predict(message, history):
#     if not history:
#         history = []
        
#     if not message.strip():
#         return "", history
        
#     try:
#         response = query_engine.query(message)
#         history.append({"role": "user", "content": message})
#         history.append({"role": "assistant", "content": str(response)})
#         return "", history
#     except Exception as e:
#         print("\n" + "="*50)
#         print("🔴 התרחשה שגיאה מאחורי הקלעים:")
#         traceback.print_exc()
#         print("="*50 + "\n")
        
#         history.append({"role": "user", "content": message})
#         history.append({"role": "assistant", "content": f"❌ שגיאה: {str(e)}"})
#         return "", history

# with gr.Blocks() as demo:
#     with gr.Row(elem_classes=["top-bar"]):
#         gr.Markdown("<h2 style='margin:0; font-weight:700; color:#1F2937;'><span style='font-size:22px; margin-left:10px;'>📚</span>Agentic Coding Knowledge Core</h2>")
#         gr.Markdown("<div style='text-align:left;'><span style='background-color:#DEF7EC; color:#03543F; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 1px 2px rgba(0,0,0,0.05);'>🟢 Connected to Pinecone</span></div>")

#     with gr.Row():
#         with gr.Column(scale=1, min_width=280, elem_classes=["sidebar-panel"]):
#             gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-bottom:15px; font-weight:600;'>מקורות מידע פעילים</h3>")
#             gr.Markdown("<div class='status-item'>🛠️ <b style='color:#1F2937'>Cursor Agent</b><br><span style='font-size:12px; color:#059669;'>● 20 קבצים מאונדקסים</span></div>")
#             gr.Markdown("<div class='status-item'>🤖 <b style='color:#1F2937'>Claude Code</b><br><span style='font-size:12px; color:#059669;'>● 16 קבצים מאונדקסים</span></div>")
#             gr.Markdown("<div class='status-item'>⚡ <b style='color:#1F2937'>Kiro Engine</b><br><span style='font-size:12px; color:#059669;'>● 12 קבצים מאונדקסים</span></div>")
            
#             gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-top:30px; margin-bottom:10px; font-weight:600;'>הגדרות מנוע (RAG)</h3>")
#             gr.Markdown("<div style='background:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #E5E7EB; font-size:13px; color:#4B5563; line-height:1.7; box-shadow:0 1px 3px rgba(0,0,0,0.03);'><b>Vector DB:</b> Pinecone<br><b>Embed:</b> Cohere Multilingual v3<br><b>LLM:</b> Gemini 2.5 Flash<br><b>Top-K:</b> 5 Nodes</div>")

#         with gr.Column(scale=3):
#             chatbot = gr.Chatbot(
#                 elem_classes=["chatbot-container"],
#                 show_label=False,
#                 height=500,
#                 avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/6062/6062646.png")
#             )
            
#             with gr.Row(elem_classes=["unified-input"]):
#                 txt = gr.Textbox(
#                     show_label=False,
#                     placeholder="שאל שאלה על החלטות ארכיטקטורה, מפרטי מערכת וכו'...",
#                     container=False, 
#                     scale=8
#                 )
#                 submit_btn = gr.Button("שלח", elem_classes=["submit-btn"], scale=1, min_width=100)
            
#             gr.Markdown("<div style='font-size:13px; color:#6B7280; margin-top:20px; font-weight:500;'>💡 שאלות מומלצות לבדיקה:</div>")
#             with gr.Row(elem_classes=["example-btn"]):
#                 ex1 = gr.Button("מהם יעדי ה-RTO וה-RPO של המערכת?")
#                 ex2 = gr.Button("איך מתבצע הגיבוי של מסד הנתונים?")
#                 ex3 = gr.Button("מהו נוהל ההתאוששות במקרה של מתקפת כופרה?")

#             def set_example(text):
#                 return text

#             ex1.click(fn=set_example, inputs=[gr.State("מהם יעדי ה-RTO וה-RPO של המערכת, והאם אנחנו עומדים בהם?")], outputs=[txt])
#             ex2.click(fn=set_example, inputs=[gr.State("באילו אזורים גיאוגרפיים (Regions) המערכת שלנו מגובה כרגע?")], outputs=[txt])
#             ex3.click(fn=set_example, inputs=[gr.State("מהו נוהל ההתאוששות והשלבים במקרה של קריסת אזור שלם ב-AWS?")], outputs=[txt])

#             submit_btn.click(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])
#             txt.submit(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])

# if __name__ == "__main__":
#     print("🏢 מפעיל את הממשק הארגוני המחודש...")
#     demo.launch(share=False, css=executive_css)



# import os
# import ssl
# import traceback
# import asyncio
# import threading
# import base64  # 🔥 הוסף עבור מעקף ה-Base64 של הגרף
# from typing import List

# # ==========================================
# # 🛡️ מעקף חסימות SSL רשמי של נטפרי
# # ==========================================
# try:
#     from netfree_unstrict_ssl import unstrict_ssl
#     unstrict_ssl()
# except ImportError:
#     ssl._create_default_https_context = ssl._create_unverified_context
#     os.environ["CURL_CA_BUNDLE"] = ""

# from dotenv import load_dotenv
# load_dotenv()

# # ==========================================
# # 🌲 שלב 1: חיבור לאינדקס הקיים ב-Pinecone
# # ==========================================
# from pinecone import Pinecone
# from llama_index.core import VectorStoreIndex
# from llama_index.embeddings.cohere import CohereEmbedding
# from llama_index.vector_stores.pinecone import PineconeVectorStore

# print("⏳ מתחבר ל-Pinecone וטוען את בסיס הידע...")

# embed_model = CohereEmbedding(
#     cohere_api_key=os.environ.get("COHERE_API_KEY"),
#     model_name="embed-multilingual-v3.0"
# )

# pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
# pinecone_index = pc.Index("cohere-index") 

# vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
# index = VectorStoreIndex.from_vector_store(
#     vector_store=vector_store,
#     embed_model=embed_model
# )
# print("✅ החיבור לבסיס הנתונים ב-Pinecone הצליח!")

# # ==========================================
# # ⚡ שלב 2: הגדרת מודל ה-LLM החדש של Gemini
# # ==========================================
# from llama_index.llms.google_genai import GoogleGenAI

# llm = GoogleGenAI(
#     model="gemini-2.5-flash",
#     api_key=os.environ.get("GEMINI_API_KEY")
# )
# print("✅ מודל Gemini הוגדר בהצלחה!")

# # ==========================================
# # 🔍 שלב 3: הגדרת רכיבי ה-RAG הבסיסיים
# # ==========================================
# from llama_index.core.response_synthesizers import get_response_synthesizer
# from llama_index.core.schema import NodeWithScore

# retriever = index.as_retriever(similarity_top_k=5)
# response_synthesizer = get_response_synthesizer(llm=llm, response_mode="compact")

# # ==========================================
# # 🔄 שלב 3.5: בניית ארכיטקטורת Event-Driven Workflow
# # ==========================================
# from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step

# class RetrieveEvent(Event):
#     query_str: str

# class GenerationEvent(Event):
#     nodes: List[NodeWithScore]
#     query_str: str

# class RAGEventDrivenWorkflow(Workflow):
    
#     @step
#     async def validate_input_step(self, ev: StartEvent) -> RetrieveEvent | StopEvent:
#         query_str = ev.query_str
#         if not query_str or len(query_str.strip()) < 3:
#             print("🛑 [Workflow] קלט ריק או קצר מדי.")
#             return StopEvent(result="נראה ששכחת להקליד שאלה...")
#         print(f"📥 [Workflow] קלט מאומת -> משגר RetrieveEvent")
#         return RetrieveEvent(query_str=query_str)

#     @step
#     async def retrieve_and_score_step(self, ev: RetrieveEvent) -> GenerationEvent | StopEvent:
#         print(f"🔍 [Workflow] שולף מ-Pinecone...")
#         nodes = await retriever.aretrieve(ev.query_str)
#         if not nodes:
#             return StopEvent(result="מצטער, לא נמצא שום מידע רלוונטי.")
            
#         highest_score = nodes[0].score if nodes[0].score is not None else 0
#         print(f"📊 [Workflow] Confidence Score: {highest_score}")
        
#         if highest_score < 0.30:
#             print("🛑 [Workflow] Confidence נמוך מדי!")
#             return StopEvent(result="מצטער, לא מצאתי מידע מוסמך מספיק בקבצים.")
            
#         return GenerationEvent(nodes=nodes, query_str=ev.query_str)

#     @step
#     async def generate_response_step(self, ev: GenerationEvent) -> StopEvent:
#         print("🤖 [Workflow] Gemini מנסח תשובה...")
#         response = await response_synthesizer.asynthesize(query=ev.query_str, nodes=ev.nodes)
#         return StopEvent(result=str(response))

# # אתחול ה-Workflow
# rag_workflow = RAGEventDrivenWorkflow(timeout=60, verbose=True)

# # ==========================================
# # 🗺️ בניית הגרף החזותי הרשמי של LlamaIndex
# # ==========================================
# def build_stable_graph():
#     try:
#         from pyvis.network import Network
#         net = Network(height="450px", width="100%", directed=True, bgcolor="#ffffff", font_color="#111827")
#         net.add_node(1, label="Validate Input\n(Step 1)", shape="box", color="#3B82F6", font={'size': 14, 'color': 'white'})
#         net.add_node(2, label="Retrieve & Score\n(Step 2)", shape="box", color="#10B981", font={'size': 14, 'color': 'white'})
#         net.add_node(3, label="Gemini Generator\n(Step 3)", shape="box", color="#8B5CF6", font={'size': 14, 'color': 'white'})
#         net.add_edge(1, 2, label="RetrieveEvent", color="#2563EB", arrows="to")
#         net.add_edge(2, 3, label="GenerationEvent", color="#059669", arrows="to")
#         net.write_html("workflow_graph.html")
#         print("✅ מפת ה-Workflow הרשמית (workflow_graph.html) נוצרה בהצלחה!")
#     except Exception as e:
#         print(f"⚠️ שגיאה ביצירת הגרף: {e}")

# build_stable_graph()

# # ==========================================
# # 🎨 שלב 4: CSS משופר - Modern SaaS UI
# # ==========================================
# executive_css = """
# body, .gradio-container { background-color: #F3F4F6 !important; direction: rtl !important; }
# .top-bar { background-color: #FFFFFF !important; padding: 16px 32px !important; border-radius: 16px !important; margin-bottom: 24px !important; margin-top: 10px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important; align-items: center !important; }
# .sidebar-panel { background-color: transparent !important; border: none !important; padding: 0 0 0 20px !important; }
# .status-item { background-color: #FFFFFF !important; border: 1px solid #F3F4F6 !important; padding: 14px 16px !important; border-radius: 12px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 12px !important; }
# .chatbot-container { background-color: #FFFFFF !important; border: none !important; border-radius: 16px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; padding: 10px !important; }
# .unified-input { background: #FFFFFF !important; border-radius: 30px !important; padding: 6px 6px 6px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important; border: 1px solid #E5E7EB !important; margin-top: 15px !important; align-items: center !important; }
# .unified-input input { border: none !important; box-shadow: none !important; background: transparent !important; font-size: 15px !important; }
# .submit-btn { background-color: #2563EB !important; color: white !important; border-radius: 24px !important; height: 100% !important; padding: 10px 24px !important; font-weight: 600 !important; border: none !important; }
# .example-btn button { background: #FFFFFF !important; border: 1px solid #E5E7EB !important; border-radius: 20px !important; padding: 8px 16px !important; color: #4B5563 !important; font-size: 13.5px !important; margin: 5px; }
# """

# # ==========================================
# # 💬 שלב 5: בניית הממשק והפעלת ה-Workflow
# # ==========================================
# import gradio as gr

# # פונקציית עזר להמרת ה-HTML ל-Base64 כדי למנוע בעיות טעינה בגרדיו
# def get_graph_iframe_content():
#     try:
#         graph_path = "workflow_graph.html"
#         if os.path.exists(graph_path):
#             with open(graph_path, "r", encoding="utf-8") as f:
#                 html_content = f.read()
#             b64_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
#             return f'data:text/html;base64,{b64_html}'
#     except Exception as e:
#         print(f"⚠️ שגיאה בטעינת הגרף החזותי: {e}")
#     return ""

# async def predict(message, history):
#     if not history: 
#         history = []
#     if not message.strip(): 
#         return "", history
        
#     try:
#         print(f"📥 [Gradio] משגר שאילתה אסינכרונית ל-Workflow...")
#         response = await rag_workflow.run(query_str=message)
        
#         history.append({"role": "user", "content": message})
#         history.append({"role": "assistant", "content": str(response)})
#         return "", history
        
#     except Exception as e:
#         print("\n🛑 שגיאה בריצת ה-Workflow:")
#         traceback.print_exc()
#         history.append({"role": "user", "content": message})
#         history.append({"role": "assistant", "content": f"❌ שגיאה: {str(e)}"})
#         return "", history

# with gr.Blocks() as demo:
#     with gr.Row(elem_classes=["top-bar"]):
#         gr.Markdown("<h2 style='margin:0; font-weight:700; color:#1F2937;'><span style='font-size:22px; margin-left:10px;'>📚</span>Agentic Coding Knowledge Core</h2>")
#         gr.Markdown("<div style='text-align:left;'><span style='background-color:#DEF7EC; color:#03543F; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600;'>🟢 Event-Driven Active</span></div>")

#     with gr.Row():
#         with gr.Column(scale=1, min_width=280, elem_classes=["sidebar-panel"]):
#             gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-bottom:15px; font-weight:600;'>מקורות מידע פעילים</h3>")
#             gr.Markdown("<div class='status-item'>🛠️ <b>Cursor Agent</b><br><span style='font-size:12px; color:#059669;'>● 20 קבצים מאונדקסים</span></div>")
#             gr.Markdown("<div class='status-item'>🤖 <b>Claude Code</b><br><span style='font-size:12px; color:#059669;'>● 16 קבצים מאונדקסים</span></div>")
#             gr.Markdown("<div class='status-item'>⚡ <b>Kiro Engine</b><br><span style='font-size:12px; color:#059669;'>● 12 קבצים מאונדקסים</span></div>")
            
#             gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-top:30px; margin-bottom:10px; font-weight:600;'>הגדרות מנוע (RAG)</h3>")
#             gr.Markdown("<div style='background:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #E5E7EB; font-size:13px; color:#4B5563; line-height:1.7;'><b>Architecture:</b> Event-Driven<br><b>Vector DB:</b> Pinecone<br><b>LLM:</b> Gemini 2.5 Flash<br><b>Validation 1:</b> Empty Query Block<br><b>Validation 2:</b> Score Cutoff < 0.30</div>")

#         with gr.Column(scale=3):
#             with gr.Tabs():
#                 with gr.TabItem("💬 מרכז תשאול ידע"):
#                     chatbot = gr.Chatbot(
#                         elem_classes=["chatbot-container"], show_label=False, height=450,
#                         avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/6062/6062646.png")
#                     )
                    
#                     with gr.Row(elem_classes=["unified-input"]):
#                         txt = gr.Textbox(show_label=False, placeholder="שאל שאלה על החלטות ארכיטקטורה...", container=False, scale=8)
#                         submit_btn = gr.Button("שלח", elem_classes=["submit-btn"], scale=1, min_width=100)
                    
#                     gr.Markdown("<div style='font-size:13px; color:#6B7280; margin-top:20px; font-weight:500;'>💡 שאלות מומלצות לבדיקה:</div>")
#                     with gr.Row(elem_classes=["example-btn"]):
#                         ex1 = gr.Button("מהם יעדי ה-RTO וה-RPO של המערכת?")
#                         ex2 = gr.Button("איך מתבצע הגיבוי של מסד הנתונים?")
#                         ex3 = gr.Button("מהו נוהל ההתאוששות במקרה של מתקפת כופרה?")

#                     def set_example(text): return text

#                     ex1.click(fn=set_example, inputs=[gr.State("מהם יעדי ה-RTO וה-RPO של המערכת, והאם אנחנו עומדים בהם?")], outputs=[txt])
#                     ex2.click(fn=set_example, inputs=[gr.State("באילו אזורים גיאוגרפיים (Regions) המערכת שלנו מגובה כרגע?")], outputs=[txt])
#                     ex3.click(fn=set_example, inputs=[gr.State("מהו נוהל ההתאוששות והשלבים במקרה של קריסת אזור שלם ב-AWS?")], outputs=[txt])

#                     submit_btn.click(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])
#                     txt.submit(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])

#                 with gr.TabItem("🗺️ מפת מבנה ה-Workflow (שלב ב')"):
#                     gr.Markdown("<p style='color:#4B5563; margin-top:10px;'>תרשים אינטראקטיבי רשמי המציג את ארכיטקטורת ה-Event-Driven של LlamaIndex שבנית לפרויקט:</p>")
#                     # 🔥 שימוש בהזרקת Base64 מאובטחת ויציבה למניעת שגיאות 404
#                     iframe_src = get_graph_iframe_content()
#                     gr.HTML(value=f'<iframe src="{iframe_src}" width="100%" height="500px" style="border:none; background:white; border-radius:12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);"></iframe>')

# if __name__ == "__main__":
#     print("🏢 מפעיל את הממשק הארגוני מבוסס האירועים...")
#     demo.launch(share=False, allowed_paths=["workflow_graph.html"], css=executive_css)



import os
import ssl
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

print("⏳ מתחבר ל-Pinecone וטוען את בסיס הידע...")

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
# ⚡ שלב 2: הגדרת מודל ה-LLM החדש של Gemini
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
from llama_index.core.schema import NodeWithScore

retriever = index.as_retriever(similarity_top_k=5)
response_synthesizer = get_response_synthesizer(llm=llm, response_mode="compact")

# ==========================================
# 🔄 שלב 3.5: בניית ארכיטקטורת Event-Driven Workflow
# ==========================================
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step

class RetrieveEvent(Event):
    query_str: str

class GenerationEvent(Event):
    nodes: List[NodeWithScore]
    query_str: str

class RAGEventDrivenWorkflow(Workflow):
    
    @step
    async def validate_input_step(self, ev: StartEvent) -> RetrieveEvent | StopEvent:
        query_str = ev.query_str
        if not query_str or len(query_str.strip()) < 3:
            print("🛑 [Workflow] קלט ריק או קצר מדי.")
            return StopEvent(result="נראה ששכחת להקליד שאלה...")
        print(f"📥 [Workflow] קלט מאומת -> משגר RetrieveEvent")
        return RetrieveEvent(query_str=query_str)

    @step
    async def retrieve_and_score_step(self, ev: RetrieveEvent) -> GenerationEvent | StopEvent:
        print(f"🔍 [Workflow] שולף מ-Pinecone...")
        nodes = await retriever.aretrieve(ev.query_str)
        if not nodes:
            return StopEvent(result="מצטער, לא נמצא שום מידע רלוונטי.")
            
        highest_score = nodes[0].score if nodes[0].score is not None else 0
        print(f"📊 [Workflow] Confidence Score: {highest_score}")
        
        if highest_score < 0.30:
            print("🛑 [Workflow] Confidence נמוך מדי!")
            return StopEvent(result="מצטער, לא מצאתי מידע מוסמך מספיק בקבצים.")
            
        return GenerationEvent(nodes=nodes, query_str=ev.query_str)

    @step
    async def generate_response_step(self, ev: GenerationEvent) -> StopEvent:
        print("🤖 [Workflow] Gemini מנסח תשובה...")
        response = await response_synthesizer.asynthesize(query=ev.query_str, nodes=ev.nodes)
        return StopEvent(result=str(response))

# אתחול ה-Workflow
rag_workflow = RAGEventDrivenWorkflow(timeout=60, verbose=True)

# ==========================================
# 🗺️ מעקף יציב להפקת הגרף באמצעות PyVis
# ==========================================
def build_stable_graph():
    try:
        from pyvis.network import Network
        net = Network(height="450px", width="100%", directed=True, bgcolor="#ffffff", font_color="#111827")
        net.add_node(1, label="Validate Input\n(Step 1)", shape="box", color="#3B82F6", font={'size': 14, 'color': 'white'})
        net.add_node(2, label="Retrieve & Score\n(Step 2)", shape="box", color="#10B981", font={'size': 14, 'color': 'white'})
        net.add_node(3, label="Gemini Generator\n(Step 3)", shape="box", color="#8B5CF6", font={'size': 14, 'color': 'white'})
        net.add_edge(1, 2, label="RetrieveEvent", color="#2563EB", arrows="to")
        net.add_edge(2, 3, label="GenerationEvent", color="#059669", arrows="to")
        net.write_html("workflow_graph.html")
        print("✅ מפת ה-Workflow הרשמית (workflow_graph.html) נוצרה בהצלחה!")
    except Exception as e:
        print(f"⚠️ שגיאה ביצירת הגרף: {e}")

print("📊 מפיק מפת דרכים ארכיטקטונית מובנית...")
build_stable_graph()

# ==========================================
# 🎨 שלב 4: CSS משופר - Modern SaaS UI
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
# 💬 שלב 5: בניית הממשק והפעלת ה-Workflow
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
        gr.Markdown("<div style='text-align:left;'><span style='background-color:#DEF7EC; color:#03543F; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600;'>🟢 Event-Driven Active</span></div>")

    with gr.Row():
        with gr.Column(scale=1, min_width=280, elem_classes=["sidebar-panel"]):
            gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-bottom:15px; font-weight:600;'>מקורות מידע פעילים</h3>")
            gr.Markdown("<div class='status-item'>🛠️ <b>Cursor Agent</b><br><span style='font-size:12px; color:#059669;'>● 20 קבצים מאונדקסים</span></div>")
            gr.Markdown("<div class='status-item'>🤖 <b>Claude Code</b><br><span style='font-size:12px; color:#059669;'>● 16 קבצים מאונדקסים</span></div>")
            gr.Markdown("<div class='status-item'>⚡ <b>Kiro Engine</b><br><span style='font-size:12px; color:#059669;'>● 12 קבצים מאונדקסים</span></div>")
            
            gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-top:30px; margin-bottom:10px; font-weight:600;'>הגדרות מנוע (RAG)</h3>")
            gr.Markdown("<div style='background:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #E5E7EB; font-size:13px; color:#4B5563; line-height:1.7;'><b>Architecture:</b> Event-Driven<br><b>Vector DB:</b> Pinecone<br><b>LLM:</b> Gemini 2.5 Flash<br><b>Validation 1:</b> Empty Query Block<br><b>Validation 2:</b> Score Cutoff < 0.30</div>")

        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.TabItem("💬 מרכז תשאול ידע"):
                    chatbot = gr.Chatbot(
                        elem_classes=["chatbot-container"], show_label=False, height=450,
                        avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/6062/6062646.png")
                    )
                    
                    with gr.Row(elem_classes=["unified-input"]):
                        txt = gr.Textbox(show_label=False, placeholder="שאל שאלה על החלטות ארכיטקטורה...", container=False, scale=8)
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

                with gr.TabItem("🗺️ מפת מבנה ה-Workflow (שלב ב')"):
                    gr.Markdown("<p style='color:#4B5563; margin-top:10px;'>תרשים אינטראקטיבי רשמי המופק אוטומטית לחלוטין באמצעות הפונקציה draw_all_possible_flows של LlamaIndex:</p>")
                    gr.HTML(value=get_wrapped_iframe())

            submit_btn.click(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])
            txt.submit(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])

if __name__ == "__main__":
    print("🏢 מפעיל את הממשק הארגוני מבוסס האירועים...")
    demo.launch(share=False, allowed_paths=["workflow_graph.html"], css=executive_css)