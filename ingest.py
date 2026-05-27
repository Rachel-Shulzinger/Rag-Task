import os
from pathlib import Path
from dotenv import load_dotenv

# טעינת משתני הסביבה מקובץ ה-.env
load_dotenv()

# ==========================================
# 🔌 שלב 1: Loading & Metadata Extraction
# ==========================================
from llama_index.core import SimpleDirectoryReader

def extract_title_from_md(file_path):
    """פונקציית עזר לחילוץ הכותרת הראשית (H1) מתוך קובץ ה-Markdown"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('# '):
                    return line.strip().replace('# ', '')
    except Exception:
        pass
    return "Untitled Document"

def file_metadata_func(file_path):
    """
    פונקציה לחילוץ Metadata מלא לפי דרישות המטלה:
    סוג הכלי, שם הקובץ, הנתיב וכותרת המסמך.
    """
    path = Path(file_path)
    tool_name = "Unknown"
    
    # זיהוי הכלי לפי שם התיקייה בנתיב
    if ".claudecode" in path.parts:
        tool_name = "Claude Code"
    elif ".cursor" in path.parts:
        tool_name = "Cursor"
    elif ".kiro" in path.parts:
        tool_name = "Kiro"
        
    # חילוץ הכותרת מתוך הקובץ
    title = extract_title_from_md(file_path)
        
    return {
        "file_name": path.name,
        "tool": tool_name,
        "file_path": str(file_path),
        "title": title
    }

print("⏳ שלב 1: מתחיל בסריקה וטעינה של קבצי ה-md...")

# שימוש בנתיבים מוחלטים כדי למנוע קריסה בווינדוס
current_dir = Path(__file__).parent.resolve()
input_dirs = [
    current_dir / ".claudecode",
    current_dir / ".cursor",
    current_dir / ".kiro"
]

documents = []

for data_dir in input_dirs:
    if data_dir.exists() and data_dir.is_dir():
        # מציאת כל קבצי ה-md בתיקייה (תומך בכל סוגי אותיות הסיומת)
        all_files = []
        for ext in ["*.md", "*.MD", "*.markdown"]:
            all_files.extend(list(data_dir.glob(ext)))
            
        if all_files:
            print(f"📂 נמצאו {len(all_files)} קבצים בתיקיית: {data_dir.name}")
            
            # העברת רשימת הקבצים המפורשת לקורא כדי למנוע בעיות סריקה פנימיות
            reader = SimpleDirectoryReader(
                input_files=[str(f) for f in all_files],
                file_metadata=file_metadata_func
            )
            documents.extend(reader.load_data())
        else:
            print(f"⚠️ אזהרה: לא נמצאו קבצי Markdown בתיקיית {data_dir.name}")
    else:
        print(f"❌ שגיאה: התיקייה {data_dir.name} לא קיימת פיזית בנתיב.")

if not documents:
    print("🚨 שגיאה קריטית: לא נטענו מסמכים בכלל! ודאי שהקבצים קיימים בתיקיות.")
    exit(1)

print(f"✅ שלב 1 הושלם: נטענו בהצלחה {len(documents)} מסמכים.")


# ==========================================
# ✂️ שלב 2: Chunking (חיתוך המידע)
# ==========================================
from llama_index.core.node_parser import SentenceSplitter

print("⏳ שלב 2: מחלק את המסמכים ל-Chunks באמצעות Node Parser...")

# הגדרת ה-Node Parser עם גודל Chunk של 512 טוקנים וחפיפה של 50
node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

# חיתוך המסמכים לאובייקטים מסוג Nodes
nodes = node_parser.get_nodes_from_documents(documents)

print(f"✅ שלב 2 הושלם: המידע חולק ל-{len(nodes)} Chunks (Nodes).")


# ==========================================
# 🧬 שלב 3: Embedding (התממשקות ל-Cohere)
# ==========================================
from llama_index.embeddings.cohere import CohereEmbedding

print("⏳ שלב 3: מגדיר את מודל ה-Embedding של Cohere...")

embed_model = CohereEmbedding(
    cohere_api_key=os.environ.get("COHERE_API_KEY"),
    model_name="embed-multilingual-v3.0" # תומך מצוין בעברית ובאנגלית משולבת
)
print("✅ שלב 3 הושלם: מודל Cohere מוכן.")


# ==========================================
# 🌲 שלב 4: Pinecone & VectorStoreIndex (גרסה מוגנת Rate-Limit)
# ==========================================
import time
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext, VectorStoreIndex

print("⏳ שלב 4: מתחבר ל-Pinecone ומעלה את הוקטורים...")

# התחברות ל-Pinecone API
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
# pinecone_index = pc.Index("PINECONE_INDEX_NAME")
pinecone_index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))

# הגדרת ה-Vector Store
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# יצירת אינדקס ריק בהתחלה
print("🧱 מייצר את בסיס האינדקס הריק ב-Pinecone...")
index = VectorStoreIndex(
    nodes=[],
    storage_context=storage_context,
    embed_model=embed_model
)

# העלאת ה-Nodes במנות קטנות (Batches) עם השהיה
BATCH_SIZE = 15  # נעלה 15 חתיכות בכל פעם
DELAY_SECONDS = 8  # נחכה 8 שניות בין מנה למנה כדי ש-Cohere לא יחסום אותנו

print(f"🚀 מתחיל להעלות {len(nodes)} Chunks במנות של {BATCH_SIZE} עם השהיה של {DELAY_SECONDS} שניות...")

for i in range(0, len(nodes), BATCH_SIZE):
    batch_nodes = nodes[i:i + BATCH_SIZE]
    print(f"📦 מעלה מנה {i // BATCH_SIZE + 1} מתוך {(len(nodes) - 1) // BATCH_SIZE + 1} (Chunks {i} עד {min(i + BATCH_SIZE, len(nodes))})...")
    
    # הוספת המנה הנוכחית לאינדקס (מבצע embedding ומעלה ל-Pinecone)
    index.insert_nodes(batch_nodes)
    
    # השהיה לפני המנה הבאה - חוץ מאשר במנה האחרונה
    if i + BATCH_SIZE < len(nodes):
        print(f"😴 ממתין {DELAY_SECONDS} שניות כדי למנוע חסימה מ-Cohere...")
        time.sleep(DELAY_SECONDS)

print("✨ חלק ראשון הושלם פרפקט! כל 462 ה-Chunks, המטא-דאטה והכותרות שמורים ומאונדקסים ב-Pinecone.")