

# import os
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

# # מודל ה-Embedding של Cohere (חייב להתאים למה שהגדרנו ב-ingest.py)
# embed_model = CohereEmbedding(
#     cohere_api_key=os.environ.get("COHERE_API_KEY"),
#     model_name="embed-multilingual-v3.0"
# )

# # התחברות ל-Pinecone
# pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
# pinecone_index = pc.Index("cohere-index") 

# vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
# index = VectorStoreIndex.from_vector_store(
#     vector_store=vector_store,
#     embed_model=embed_model
# )
# print("✅ החיבור לבסיס הנתונים ב-Pinecone הצליח!")


# # ==========================================
# # ⚡ שלב 2: הגדרת מודל ה-LLM של Groq
# # ==========================================
# from llama_index.llms.groq import Groq

# # הגדרת Llama 3 דרך Groq למהירות ומענה חכם
# llm = Groq(
#     model="llama3-70b-8192",
#     api_key=os.environ.get("GROQ_API_KEY")
# )


# # ==========================================
# # 🔍 שלב 3: הגדרת רכיבי ה-RAG (לפי דרישות המטלה)
# # ==========================================
# from llama_index.core.postprocessor import SimilarityPostprocessor
# from llama_index.core.query_engine import RetrieverQueryEngine
# from llama_index.core.response_synthesizers import get_response_synthesizer

# # 1. דרישה: Retrieve - שליפת 5 ה-Chunks הכי רלוונטיים לשאלת המשתמש
# retriever = index.as_retriever(similarity_top_k=5)

# # 2. דרישה: Postprocessing - סינון אובייקטים לפי רמת ביטחון (Confidence)
# node_postprocessor = SimilarityPostprocessor(similarity_cutoff=0.60)

# # 3. דרישה: Synthesizing - הגדרת מנסח התשובות (Response Synthesizer)
# response_synthesizer = get_response_synthesizer(
#     llm=llm,
#     response_mode="compact"
# )

# # חיבור הכל למנוע שאילתות אחד (Query Engine)
# query_engine = RetrieverQueryEngine(
#     retriever=retriever,
#     node_postprocessors=[node_postprocessor],
#     response_synthesizer=response_synthesizer
# )


# # ==========================================
# # 🎨 שלב 4: הגדרת ה-CSS לעיצוב החדשני והנקי
# # ==========================================
# custom_css = """
# /* עיצוב כללי של עמוד הרקע */
# body, .gradio-container {
#     background: radial-gradient(circle at top right, #111827, #030712) !important;
#     font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
#     direction: rtl !important; /* תמיכה מלאה בכיוון עברית */
# }

# /* כותרת המערכת */
# h1 {
#     font-weight: 800 !important;
#     background: linear-gradient(90deg, #10B981, #3B82F6);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
#     text-align: center;
#     margin-bottom: 5px !important;
# }

# /* תיאור קטן מתחת לכותרת */
# .gradio-container p {
#     text-align: center;
#     color: #9CA3AF !important;
#     font-size: 15px;
# }

# /* תיבת הצ'אט עצמה */
# .chatbot {
#     border: 1px solid rgba(255, 255, 255, 0.08) !important;
#     border-radius: 20px !important;
#     background: rgba(17, 24, 39, 0.7) !important;
#     backdrop-filter: blur(12px) !important;
#     box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
#     padding: 10px !important;
# }

# /* בועות הודעה של הצ'אט */
# .message {
#     border-radius: 16px !important;
#     padding: 12px 16px !important;
#     font-size: 15px !important;
#     line-height: 1.6 !important;
# }

# /* בועת הודעה של המשתמש */
# .user-message {
#     background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
#     color: white !important;
#     border-top-left-radius: 4px !important;
# }

# /* בועת הודעה של הבוט/מערכת */
# .bot-message {
#     background: rgba(31, 41, 55, 0.8) !important;
#     color: #F3F4F6 !important;
#     border: 1px solid rgba(255, 255, 255, 0.05) !important;
#     border-top-right-radius: 4px !important;
# }

# /* שורת קלט הטקסט של המשתמש */
# input[type="text"] {
#     background: #1F2937 !important;
#     border: 1px solid rgba(255, 255, 255, 0.1) !important;
#     border-radius: 14px !important;
#     color: white !important;
#     padding: 14px !important;
#     font-size: 15px !important;
# }

# input[type="text"]:focus {
#     border-color: #10B981 !important;
#     box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
# }

# /* כפתורי הדוגמאות (Examples) */
# .examples-container button {
#     background: rgba(31, 41, 55, 0.6) !important;
#     border: 1px solid rgba(255, 255, 255, 0.05) !important;
#     color: #9CA3AF !important;
#     border-radius: 10px !important;
#     transition: all 0.2s ease !important;
#     text-align: right !important;
# }

# .examples-container button:hover {
#     background: rgba(55, 65, 81, 0.8) !important;
#     color: white !important;
#     border-color: #3B82F6 !important;
# }

# /* כפתור ה-Submit וה-Clear */
# button.primary-btn {
#     background: #10B981 !important;
#     color: white !important;
#     border-radius: 12px !important;
#     font-weight: 600 !important;
# }
# """

# # ==========================================
# # 💬 שלב 5: ממשק ה-Chat עם Gradio (גרסת Blocks יציבה)
# # ==========================================
# import gradio as gr

# def ask_rag(message, history):
#     try:
#         print(f"🙋 שאלה שהתקבלה: {message}")
#         response = query_engine.query(message)
#         return str(response)
#     except Exception as e:
#         return f"❌ שגיאה בהפקת התשובה: {str(e)}"

# # בניית הממשק במבנה Blocks המודרני שמפריד את העיצוב מהלוגיקה
# with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
#     # יצירת ממשק הצ'אט בתוך הבלוק המעוצב
#     gr.ChatInterface(
#         fn=ask_rag,
#         title="📊 Agentic Tools Knowledge RAG",
#         description="מאגר ידע סמנטי מאוחד. שאל שאלות על החלטות ארכיטקטורה, מפרטי מערכת ושינויי קוד מהתיעוד שלך.",
#         examples=[
#             "מה הצבע העיקרי שנבחר לדיזיין של המערכת?",
#             "לאילו שפות הוחלט לתרגם את הכיתובים בממשק?",
#             "האם נעשה שינוי במבנה ה-DB בחודש האחרון?"
#         ]
#     )

# if __name__ == "__main__":
#     print("🌍 מפעיל את שרת Gradio המקומי בעיצוב החדש...")
#     demo.launch(share=False)


import os
from dotenv import load_dotenv

# טעינת משתני הסביבה (מפתחות ה-API)
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
# ⚡ שלב 2: הגדרת מודל ה-LLM של Groq
# ==========================================
from llama_index.llms.groq import Groq

llm = Groq(
    model="llama3-70b-8192",
    api_key=os.environ.get("GROQ_API_KEY")
)


# ==========================================
# 🔍 שלב 3: הגדרת רכיבי ה-RAG
# ==========================================
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer

retriever = index.as_retriever(similarity_top_k=5)
node_postprocessor = SimilarityPostprocessor(similarity_cutoff=0.60)
response_synthesizer = get_response_synthesizer(llm=llm, response_mode="compact")

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=[node_postprocessor],
    response_synthesizer=response_synthesizer
)


# ==========================================
# 🎨 שלב 4: CSS משופר - Modern SaaS UI
# ==========================================
executive_css = """
body, .gradio-container { 
    background-color: #F3F4F6 !important; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; 
    direction: rtl !important; 
}

/* סרגל עליון צף ומעוגל */
.top-bar { 
    background-color: #FFFFFF !important; 
    padding: 16px 32px !important; 
    border-radius: 16px !important;
    margin-bottom: 24px !important; 
    margin-top: 10px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    align-items: center !important;
}

/* כרטיסיות הסיידבר */
.sidebar-panel { 
    background-color: transparent !important; 
    border: none !important; 
    padding: 0 0 0 20px !important; 
}
.status-item { 
    background-color: #FFFFFF !important; 
    border: 1px solid #F3F4F6 !important; 
    padding: 14px 16px !important; 
    border-radius: 12px !important; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
    margin-bottom: 12px !important;
    transition: transform 0.2s, box-shadow 0.2s; 
}
.status-item:hover { 
    transform: translateY(-2px); 
    box-shadow: 0 4px 6px rgba(0,0,0,0.08); 
}

/* חלון הצ'אט - גובה קבוע ומסגרת רכה */
.chatbot-container { 
    background-color: #FFFFFF !important; 
    border: none !important; 
    border-radius: 16px !important; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; 
    padding: 10px !important; 
}

/* עיצוב הבועות */
.message { 
    border-radius: 16px !important; 
    padding: 14px 20px !important; 
    font-size: 15px !important; 
    line-height: 1.6 !important; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important; 
}
.user-message { 
    background: linear-gradient(135deg, #2563EB, #1D4ED8) !important; /* כחול הייטק */
    color: white !important; 
    border-bottom-left-radius: 4px !important; 
}
.bot-message { 
    background-color: #F8FAFC !important; 
    color: #1E293B !important; 
    border: 1px solid #E2E8F0 !important; 
    border-bottom-right-radius: 4px !important; 
}

/* --- התיקון המרכזי: שורת הקלט (Prompt Bar) --- */
.unified-input { 
    background: #FFFFFF !important; 
    border-radius: 30px !important; 
    padding: 6px 6px 6px 20px !important; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important; 
    border: 1px solid #E5E7EB !important; 
    margin-top: 15px !important;
    align-items: center !important;
}
.unified-input input { 
    border: none !important; 
    box-shadow: none !important; 
    background: transparent !important; 
    font-size: 15px !important; 
}
.unified-input input:focus { border: none !important; box-shadow: none !important; }

/* כפתור שליחה עגול בפנים */
.submit-btn { 
    background-color: #2563EB !important; 
    color: white !important; 
    border-radius: 24px !important; 
    height: 100% !important; 
    padding: 10px 24px !important; 
    font-weight: 600 !important; 
    border: none !important; 
    transition: background-color 0.2s !important;
}
.submit-btn:hover { background-color: #1D4ED8 !important; }

/* כפתורי הדוגמאות - סידור חכם שמונע גלילה */
.example-btn {
    display: flex !important;
    flex-wrap: wrap !important; /* מאפשר לכפתורים לרדת שורה אם אין מקום במסך */
    gap: 10px !important; /* מרווח אחיד ויפה בין הכפתורים */
    justify-content: flex-start !important; /* יישור לימין (RTL) */
    width: 100% !important;
    margin-bottom: 20px !important;
}

.example-btn button { 
    background: #FFFFFF !important; 
    border: 1px solid #E5E7EB !important; 
    border-radius: 20px !important; 
    padding: 8px 16px !important; /* טיפה יותר קומפקטי */
    color: #4B5563 !important; 
    font-size: 13.5px !important; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important; 
    transition: all 0.2s ease !important;
    flex: 0 1 auto !important; /* הכפתור יתפוס בדיוק את הרוחב של הטקסט שלו */
    white-space: normal !important; /* מאפשר לטקסט להישבר בפנים אם המסך ממש קטן */
}

.example-btn button:hover { 
    border-color: #2563EB !important; 
    color: #2563EB !important; 
    background: #EFF6FF !important; 
    transform: translateY(-1px) !important; /* אנימציית ריחוף קטנה */
    box-shadow: 0 3px 6px rgba(37, 99, 235, 0.1) !important;
}
"""

# ==========================================
# 💬 שלב 5: בניית הממשק במבנה קונסולה (Blocks)
# ==========================================
import gradio as gr

def predict(message, history):
    if not message.strip():
        return "", history
    try:
        response = query_engine.query(message)
        history.append((message, str(response)))
        return "", history
    except Exception as e:
        history.append((message, f"❌ שגיאה: {str(e)}"))
        return "", history

# השתמשנו ב-Base Theme כדי שהעיצוב שלנו ישלוט לגמרי
with gr.Blocks(theme=gr.themes.Base()) as demo:
    
    # 1. סרגל עליון (Top Header) - מיושר וברור
    with gr.Row(elem_classes=["top-bar"]):
        gr.Markdown("<h2 style='margin:0; font-weight:700; color:#1F2937;'><span style='font-size:22px; margin-left:10px;'>📚</span>Agentic Coding Knowledge Core</h2>")
        gr.Markdown("<div style='text-align:left;'><span style='background-color:#DEF7EC; color:#03543F; padding:6px 16px; border-radius:20px; font-size:13px; font-weight:600; box-shadow:0 1px 2px rgba(0,0,0,0.05);'>🟢 Connected to Pinecone</span></div>")

    # 2. גוף העמוד
    with gr.Row():
        
        # סיידבר ימני (מקורות)
        with gr.Column(scale=1, min_width=280, elem_classes=["sidebar-panel"]):
            gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-bottom:15px; font-weight:600;'>מקורות מידע פעילים</h3>")
            gr.Markdown("<div class='status-item'>🛠️ <b style='color:#1F2937'>Cursor Agent</b><br><span style='font-size:12px; color:#059669;'>● 20 קבצים מאונדקסים</span></div>")
            gr.Markdown("<div class='status-item'>🤖 <b style='color:#1F2937'>Claude Code</b><br><span style='font-size:12px; color:#059669;'>● 16 קבצים מאונדקסים</span></div>")
            gr.Markdown("<div class='status-item'>⚡ <b style='color:#1F2937'>Kiro Engine</b><br><span style='font-size:12px; color:#059669;'>● 12 קבצים מאונדקסים</span></div>")
            
            gr.Markdown("<h3 style='color:#6B7280; font-size:14px; margin-top:30px; margin-bottom:10px; font-weight:600;'>הגדרות מנוע (RAG)</h3>")
            gr.Markdown("<div style='background:#FFFFFF; padding:15px; border-radius:12px; border:1px solid #E5E7EB; font-size:13px; color:#4B5563; line-height:1.7; box-shadow:0 1px 3px rgba(0,0,0,0.03);'><b>Vector DB:</b> Pinecone<br><b>Embed:</b> Cohere Multilingual v3<br><b>LLM:</b> Llama 3 70B (Groq)<br><b>Top-K:</b> 5 Nodes</div>")

        # חלון הצ'אט המרכזי
        with gr.Column(scale=3):
            # הוספנו גובה קבוע (height=500) וסמל חמוד לבוט (avatar)
            chatbot = gr.Chatbot(
                elem_classes=["chatbot-container"],
                show_label=False,
                height=500,
                avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/6062/6062646.png")
            )
            
            # שורת קלט מאוחדת (Unified Prompt Bar)
            with gr.Row(elem_classes=["unified-input"]):
                txt = gr.Textbox(
                    show_label=False,
                    placeholder="שאל שאלה על החלטות ארכיטקטורה, מפרטי מערכת וכו'...",
                    container=False, # מעיף את המסגרת המכוערת של גראדיו
                    scale=8
                )
                submit_btn = gr.Button("שלח", elem_classes=["submit-btn"], scale=1, min_width=100)
            
            # קיצורי דרך משופרים
            gr.Markdown("<div style='font-size:13px; color:#6B7280; margin-top:20px; font-weight:500;'>💡 שאלות מומלצות לבדיקה:</div>")
            with gr.Row(elem_classes=["example-btn"]):
                ex1 = gr.Button("מה הצבע העיקרי שנבחר לדיזיין?")
                ex2 = gr.Button("האם נעשה שינוי ב-DB לאחרונה?")
                ex3 = gr.Button("מה ההנחיה לגבי שימוש ב-RTL?")

            def set_example(text):
                return text

            ex1.click(fn=set_example, inputs=[gr.State("מה הצבע העיקרי שנבחר לדיזיין של המערכת?")], outputs=[txt])
            ex2.click(fn=set_example, inputs=[gr.State("האם נעשה שינוי במבנה ה-DB בחודש האחרון?")], outputs=[txt])
            ex3.click(fn=set_example, inputs=[gr.State("האם קיימת הנחיה עקבית לגבי שימוש ב-RTL בממשק?")], outputs=[txt])

            submit_btn.click(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])
            txt.submit(fn=predict, inputs=[txt, chatbot], outputs=[txt, chatbot])

if __name__ == "__main__":
    print("🏢 מפעיל את הממשק הארגוני המחודש...")
    demo.launch(share=False, css=executive_css)