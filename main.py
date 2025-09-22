import os
import shutil
import uuid  # لتوليد اسماء ملفات فريدة
from fastapi import (
    FastAPI,
    UploadFile,
    Form,
)  # FastAPI لاستيراد المكونات الرئيسية لبناء

from fastapi.responses import (
    FileResponse,
    JSONResponse,
)  # JSON لإرسال الملفات واستجابات

from fastapi.middleware.cors import CORSMiddleware  # CORS للتعامل
from fastapi.staticfiles import StaticFiles  # HTML لتوفير ملف

from io_utils import (
    extract_txt,
    extract_docx,
    extract_pdf,
    save_docx,
)  # استيراد التوابع المساعدة للتعامل مع الملفات

print("loading.......")

from ner import get_entities  # استيراد التابع المسؤول عن اكتشاف الكيانات.
from anonymizer import anonymize_text  # استيراد التابع المسؤول عن تعمية النص.


# FastAPI انشاء
app = FastAPI()

# السماح بالوصول من أي مصدر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# تعريف مسار المجلدات التي سيتم استخدامها للدخل والخرج
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
# إنشاء هذه المجلدات إذا لم تكن موجودة بالفعل
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# html الذي يحوي صغحة  static تعريف مجلد
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


print("\n GO To http://127.0.0.1:8000 \n")


@app.get("/")
async def root():
    # تعريف المسار الأساسي '/'، والذي يعيد الصفحة الرئيسية للتطبيق
    return FileResponse("static/index.html")


@app.post("/api/anonymize")
async def anonymize_file(
    file: UploadFile,  # الملف المرفوع من قبل المستخدم
    labels: str = Form(...),  # الفئات التي سيتم تعميتها
    model_name: str = Form("bert-base"),  # اسم النموذج الذي سيتم استخدامه
    style: str = Form("[REDACTED]"),  # النمط المستخدم للتعمية
    use_faker: bool = Form(False),  # faker خيار استخدام بيانات وهمية باستخدام
):
    # توليد معرف فريد للملف لتجنب تضارب الأسماء
    file_id = str(uuid.uuid4())
    #  المسار الكامل لحفظ الملف المرفوع
    file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    # حفظ الملف المرفوع
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # التحقق من لاحقة الملف ومعالجته بناءً على النوع
    if file.filename.endswith(".txt"):
        paras = extract_txt(file_path).split("\n")
        text = "\n".join(paras)
    elif file.filename.endswith(".docx"):
        text, paras = extract_docx(file_path)
    elif file.filename.endswith(".pdf"):
        paras = extract_pdf(file_path)
        text = "\n".join(paras)
    else:
        # إرجاع خطأ إذا كان نوع الملف غير مدعوم
        return JSONResponse(
            {"error": "Only .txt, .docx, or .pdf supported"}, status_code=400
        )

    # استخراج الكيانات من النص باستخدام النموذج المختار
    entities = get_entities(text, model_name)
    # (string) تحويل نص الفئات
    # (list) إلى قائمة
    selected_labels = [label.strip() for label in labels.split(",")]

    # تنفيذ عملية التعمية للنص
    anonymized = anonymize_text(
        text, entities, selected_labels, model_name, style, use_faker
    )

    # بناء المسار للملف الذي تمت تعميته
    out_path = os.path.join(OUTPUT_DIR, file_id + ".docx")
    # جديد .docx حفظ النص الذي تمت تعميته في ملف
    save_docx(anonymized.split("\n"), out_path)

    # إرجاع الملف الذي تمت تعميته ليتمكن المستخدم من تنزيله
    return FileResponse(out_path, filename="anonymized.docx")
