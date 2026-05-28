import os
import ssl
import json
import time
import hashlib
import datetime
import traceback
from pathlib import Path
from dotenv import load_dotenv

# מעקף חסימות SSL עבור נטפרי
try:
    from netfree_unstrict_ssl import unstrict_ssl
    unstrict_ssl()
except ImportError:
    ssl._create_default_https_context = ssl._create_unverified_context
    os.environ["CURL_CA_BUNDLE"] = ""

load_dotenv()

# ייבוא הסכמות הרשמיות מתוך models.py
from models import (
    ProjectKnowledgeSchema, 
    ItemsContainer, 
    SourceMeta, 
    FileMeta, 
    SourceLocation
)
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.output_parsers import PydanticOutputParser

print("⏳ [Extraction] מאתחל את מודל Gemini ומנגנון הפלט המובנה לפי תיקיות...")

# 🔄 מנגנון חסין גורף לאתחול המודל - מעתיק את המבנה המקורי שעבד בהצלחה ב-app.py
llm = None
for init_attempt in range(4):
    try:
        print(f"  📡 מנסה ליצור חיבור ראשוני מול שרתי Gemini (ניסיון {init_attempt + 1}/4)...")
        
        # שימוש באתחול הנקי והפשוט ללא פקודות timeout מורכבות שמבלבלות את הפרוטוקול
        llm = GoogleGenAI(
            model="gemini-2.5-flash",
            api_key=os.environ.get("GEMINI_API_KEY")
        )
        
        # נבצע בדיקת דופק מהירה לוודא שהצינור באמת פתוח לעבודה
        print("  ✅ האתחול הצליח. מריץ בדיקת סנכרון מהירה...")
        llm.complete("ping")
        
        print("  🚀 [Connected] החיבור הראשוני והאימות מול גוגל עברו בהצלחה מלאה!")
        break
    except Exception as init_error:
        print(f"  ⚠️ ניסיון החיבור נכשל או התעכב ברשת (שגיאה: {type(init_error).__name__}).")
        if init_attempt < 3:
            print("  ⏳ נטפרי או הרשת זקוקים לרגע נוסף ללחיצת היד. ממתין 10 שניות ומנסה שוב...")
            time.sleep(10)
        else:
            print("  🚨 כל ניסיונות האתחול נכשלו.")
            raise init_error

if llm is None:
    print("🚨 [Critical Error] לא ניתן היה להשלים את לחיצת היד מול גוגל עקב איטיות ברשת.")
    exit(1)

# אנו מבקשים מהפארסר לחלץ את קונטיינר הפריטים עבור תיקייה שלמה בכל פעם
output_parser = PydanticOutputParser(ItemsContainer)

def calculate_sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_file_iso_timestamp(file_path: Path) -> str:
    mtime = os.path.getmtime(file_path)
    return datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).isoformat()

def run_structured_extraction():
    current_dir = Path(__file__).parent.resolve()
    tools_config = {
        "cursor": current_dir / ".cursor",
        "claude_code": current_dir / ".claudecode",
        "kiro": current_dir / ".kiro"
    }
    
    all_decisions = []
    all_rules = []
    all_warnings = []
    sources_metadata = []
    
    base_prompt = (
        "You are an expert systems architect monitoring a coding project.\n"
        "Analyze the following combined documentation files extracted from the tool '{tool_name}'.\n"
        "Your task is to scan ALL files in the provided text and extract EVERY single architectural decision, "
        "development rule, and warning/sensitivity mentioned across these files.\n\n"
        "Important Guidelines:\n"
        "- Under the 'source' object for each extracted item, make sure to accurately preserve the specific file name "
        "where it came from (indicated by the START OF FILE markers in the text), the line range, and nearest header anchor.\n"
        "- Leave the 'id' fields as placeholders, they will be handled by Python code.\n"
        "- If a category has no findings, return an empty list for it.\n\n"
        "Combined Folder Documentation:\n"
        "\"\"\"\n{combined_content}\n\"\"\"\n\n"
        "{format_instructions}"
    )

    print("\n📂 מתחיל בסריקת תיקיות התיעוד ואיחוד המידע...")

    for tool_name, folder_path in tools_config.items():
        if not folder_path.exists() or not folder_path.is_dir():
            continue
            
        all_files = list(folder_path.glob("*.md")) + list(folder_path.glob("*.markdown"))
        if not all_files:
            continue
            
        print(f"\n📦 [Folder Batch] אוסף מידע מתיקיית {tool_name} ({len(all_files)} קבצים)...")
        
        folder_combined_text = ""
        file_meta_list = []
        
        for file_path in all_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                folder_combined_text += f"\n\n--- START OF FILE: {file_path.name} ---\n{content}\n--- END OF FILE ---\n"
                
                file_meta_list.append(
                    FileMeta(
                        path=str(file_path),
                        last_modified=get_file_iso_timestamp(file_path),
                        hash=calculate_sha256(content)
                    )
                )
            except Exception as fe:
                print(f"  ⚠️ שגיאה בקריאת הקובץ {file_path.name}: {fe}")

        if not folder_combined_text:
            continue

        print(f"  🤖 שולח את כל תיקיית {tool_name} לניתוח מרוכז ב-Gemini...")
        
        full_prompt = base_prompt.format(
            tool_name=tool_name,
            combined_content=folder_combined_text,
            format_instructions=output_parser.format("")
        )
        
        extracted_container = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = llm.complete(full_prompt)
                extracted_container = output_parser.parse(response.text)
                print(f"  📥 החילוץ המובנה עבור תיקיית {tool_name} הושלם בהצלחה!")
                break
            except Exception as api_error:
                print(f"  ⚠️ ניסיון {attempt + 1} נכשל עקב עומס/מכסה. ממתין 65 שניות לאיפוס קשיח...")
                time.sleep(65)
                
        if extracted_container is None:
            print(f"🚨 [Error] לא ניתן היה לעבד את תיקיית {tool_name}. המידע מהתיקייה הזו יושמט.")
            continue

        current_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        for item in extracted_container.decisions:
            item.observed_at = current_time_iso
            all_decisions.append(item)
            
        for item in extracted_container.rules:
            item.observed_at = current_time_iso
            all_rules.append(item)
            
        for item in extracted_container.warnings:
            item.observed_at = current_time_iso
            all_warnings.append(item)
            
        if file_meta_list:
            sources_metadata.append(
                SourceMeta(tool=tool_name, root_path=str(folder_path), files=file_meta_list)
            )
            
        print("  😴 ממתין 15 שניות בין תיקיות לביטחון מקסימלי...")
        time.sleep(15)

    print("\n🔢 מבצע מירג' ומספור מחדש של ה-IDs בצורה סדרתית...")
    for idx, item in enumerate(all_decisions, start=1): item.id = f"dec-{idx:03d}"
    for idx, item in enumerate(all_rules, start=1): item.id = f"rule-{idx:03d}"
    for idx, item in enumerate(all_warnings, start=1): item.id = f"warn-{idx:03d}"

    final_schema = ProjectKnowledgeSchema(
        sources=sources_metadata,
        items=ItemsContainer(
            decisions=all_decisions,
            rules=all_rules,
            warnings=all_warnings
        )
    )

    output_json_path = "extracted_knowledge.json"
    try:
        with open(output_json_path, "w", encoding="utf-8") as json_file:
            json.dump(final_schema.model_dump(), json_file, ensure_ascii=False, indent=2)
            
        print(f"\n✨ [Success] תהליך ה-Structured Data Extraction הסתיים ב-100% הצלחה!")
        print(f"📁 בסיס הידע המובנה והמלא נשמר ב: {output_json_path}")
        print(f"📊 סיכום: חולצו {len(all_decisions)} החלטות, {len(all_rules)} חוקים, ו-{len(all_warnings)} אזהרות.")
    except Exception as e:
        print(f"❌ שגיאה בכתיבת קובץ ה-JSON: {e}")

if __name__ == "__main__":
    try:
        run_structured_extraction()
    except Exception as e:
        traceback.print_exc()