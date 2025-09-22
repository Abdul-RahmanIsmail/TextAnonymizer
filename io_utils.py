from docx import Document  # Word للتعامل مع ملفات
import pdfplumber  # PDF التي تستخرج النص من ملفات pdfplumber استيراد مكتبة


def extract_txt(file_path: str):
    # (.txt) تابع لاستخراج النص من ملف نصي بسيط
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_docx(file_path: str):
    # (.docx) Word تابع لاستخراج النص من ملف
    doc = Document(file_path)
    # الموجودة في المستند (paragraphs) الحصول على قائمة بجميع الفقرات
    paras = [p.text for p in doc.paragraphs]
    # واحد وقائمة الفقرات بشكل منفصل string إرجاع النص المدمج في
    return "\n".join(paras), paras


def save_docx(paragraphs, output_path: str):
    # جديد وحفظه Word تابع لإنشاء ملف
    doc = Document()
    # إضافة كل فقرة من القائمة إلى المستند الجديد
    for p in paragraphs:
        doc.add_paragraph(p)
    # حفظ المستند الجديد في المسار المحدد
    doc.save(output_path)


def extract_pdf(file_path: str):
    # PDF تابع لاستخراج النص من ملف
    text = ""
    with pdfplumber.open(file_path) as pdf:
        # PDF المرور على كل صفحة في ملف
        for page in pdf.pages:
            # text استخراج النص من كل صفحة وإضافته إلى
            text += page.extract_text() or ""
    # تقسيم النص الكامل إلى فقرات وإرجاعه كقائمة.
    return text.split("\n")
