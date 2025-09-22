import os # لإجراء عمليات على نظام الملفات.
import shutil # لنسخ الكائنات التي تشبه الملفات.
import uuid # لتوليد معرفات فريدة للملفات.
from fastapi import FastAPI, UploadFile, Form # لاستيراد المكونات الرئيسية لبناء واجهة برمجة تطبيقات ويب.
from fastapi.responses import FileResponse, JSONResponse # لإرسال الملفات واستجابات JSON.
from fastapi.middleware.cors import CORSMiddleware # للتعامل مع سياسات CORS الأمنية.
from io_utils import extract_txt, extract_docx, extract_pdf, save_docx # استيراد الدوال المساعدة للتعامل مع الملفات.

print("loading.......")

from ner import get_entities # استيراد الدالة المسؤولة عن اكتشاف الكيانات.
from anonymizer import anonymize_text # استيراد الدالة المسؤولة عن تعمية النص.
from fastapi.staticfiles import StaticFiles # لتوفير الملفات الثابتة مثل HTML و CSS.


# تهيئة تطبيق FastAPI.
app = FastAPI()

# إضافة وسيط CORS. هذا يسمح للواجهة الأمامية بالاتصال بالخادم.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # السماح بالوصول من أي مصدر.
    allow_credentials=True, # السماح بملفات تعريف الارتباط (cookies).
    allow_methods=["*"], # السماح بجميع أنواع طلبات HTTP (GET, POST, etc).
    allow_headers=["*"], # السماح بجميع أنواع الرؤوس (headers).
)


# تعريف مسارات المجلدات التي سيتم استخدامها لتخزين الملفات.
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
# إنشاء هذه المجلدات إذا لم تكن موجودة بالفعل.
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# تركيب مجلد 'static' ليعمل كخادم للملفات الثابتة.
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


print("\nGO To http://127.0.0.1:8000\n")

@app.get("/")
async def root():
    # تعريف المسار الأساسي '/'، والذي يعيد الصفحة الرئيسية للواجهة الأمامية.
    return FileResponse("static/index.html")


@app.post("/api/anonymize")
async def anonymize_file(
    # تعريف المسار الخاص بالتعمية. هذا المسار يستقبل الملفات المرفوعة.
    file: UploadFile, # الملف المرفوع من قبل المستخدم.
    labels: str = Form(...), # الفئات التي سيتم تعميتها.
    model_name: str = Form("bert-base"), # اسم النموذج الذي سيتم استخدامه.
    style: str = Form("*****"), # النمط المستخدم للتعمية.
    use_faker: bool = Form(False), # خيار استخدام بيانات وهمية.
):
    # تحويل سلاسل الفئات (string) إلى قائمة (list).
    # يجب أن يتم هذا في بداية الدالة ليكون المتغير متاحًا دائمًا.
    selected_labels = [label.strip() for label in labels.split(",")]
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    # حفظ الملف المرفوع على القرص.
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # التحقق من امتداد الملف ومعالجته بناءً على النوع.
    if file.filename.endswith(".txt"):
        paras = extract_txt(file_path).split("\n")
        text = "\n".join(paras)
    elif file.filename.endswith(".docx"):
        text, paras = extract_docx(file_path)
    elif file.filename.endswith(".pdf"):
        paras = extract_pdf(file_path)
        text = "\n".join(paras)
    else:
        # إرجاع خطأ إذا كان نوع الملف غير مدعوم.
        return JSONResponse(
            {"error": "Only .txt, .docx, or .pdf supported"}, status_code=400
        )

    # استخراج الكيانات من النص باستخدام النموذج المختار.
    entities = get_entities(text, model_name, selected_labels)
    
    # تنفيذ عملية التعمية الفعلية للنص.
    anonymized = anonymize_text(text, entities, selected_labels, model_name, style, use_faker)

    # بناء المسار للملف المعمّى.
    out_path = os.path.join(OUTPUT_DIR, file_id + ".docx")
    # حفظ النص المعمّى في ملف .docx جديد.
    save_docx(anonymized.split("\n"), out_path)

    # إرسال الملف المعمّى كاستجابة ليتمكن المستخدم من تنزيله.
    return FileResponse(out_path, filename="anonymized.docx")
