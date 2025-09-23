import os  # لإجراء عمليات على نظام الملفات
import shutil  # لنسخ الكائنات التي تشبه الملفات
import uuid  # لتوليد معرفات فريدة للملفات
from fastapi import FastAPI, UploadFile, Form  # API لاستيراد المكونات الرئيسية لبناء
from fastapi.responses import FileResponse, JSONResponse

from fastapi.middleware.cors import CORSMiddleware  # للتعامل مع سياسات CORS الأمنية
from io_utils import extract_txt, extract_docx, extract_pdf, save_docx

print("loading.......")

from ner import get_entities  # استيراد الدالة المسؤولة عن اكتشاف الكيانات
from anonymizer import anonymize_text  # استيراد الدالة المسؤولة عن تعمية النص
from fastapi.staticfiles import StaticFiles  # HTML لتوفير الملفات الثابتة


# FastAPI تهيئة
app = FastAPI()

# السماح بالوصول من أي مصدر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#  المجلدات التي سيتم استخدامها لتخزين الملفات
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

# إنشاء لم تكن موجودة
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ليعمل كخادم للملفات الثابتة static تركيب مجلد
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


print("\nGO To http://127.0.0.1:8000\n")


@app.get("/")
async def root():
    # تعريف المسار الأساسي '/ الذي يوجه الى صفحة الويب الخاصة بالتطبيق
    return FileResponse("static/index.html")


@app.post("/api/anonymize")
async def anonymize_file(
    # تعريف المسار الخاص بالتعمية - هذا المسار يستقبل الملفات المرفوعة
    file: UploadFile,  # الملف المرفوع من قبل المستخدم
    labels: str = Form(...),  # الفئات التي سيتم تعميتها
    model_name: str = Form("bert-base"),  # اسم النموذج الذي سيتم استخدامه
    style: str = Form("*****"),  # نمط التعمية
    use_faker: bool = Form(False),  # Fake خيار استخدام بيانات وهمية
):
    # (list) إلى قائمة (string) تحويل سلاسل الفئات
    selected_labels = [label.strip() for label in labels.split(",")]

    # توليد معرف فريد لتسمية الملف
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    # حفظ الملف المرفوع
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # التحقق من لاحقة الملف ومعالجته حسب النوع
    if file.filename.endswith(".txt"):
        paras = extract_txt(file_path).split("\n")
        text = "\n".join(paras)
    elif file.filename.endswith(".docx"):
        text, paras = extract_docx(file_path)
    elif file.filename.endswith(".pdf"):
        paras = extract_pdf(file_path)
        text = "\n".join(paras)
    else:
        # ارجاع خطأ إذا كان نوع الملف غير مدعوم
        return JSONResponse(
            {"error": "Only .txt, .docx, or .pdf supported"}, status_code=400
        )

    # استخراج الكيانات من النص باستخدام النموذج المختار
    entities = get_entities(text, model_name, selected_labels)

    # تنفيذ عملية التعمية للنص
    anonymized = anonymize_text(
        text, entities, selected_labels, model_name, style, use_faker
    )

    # بناء المسار للملف المعمّى
    out_path = os.path.join(OUTPUT_DIR, file_id + ".docx")
    # جديد .docx حفظ النص المعمّى في ملف
    save_docx(anonymized.split("\n"), out_path)

    # إرسال الملف المعمّى كاستجابة ليتمكن المستخدم من تنزيله
    return FileResponse(out_path, filename="anonymized.docx")
