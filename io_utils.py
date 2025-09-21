from docx import Document
import pdfplumber


def extract_txt(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_docx(file_path: str):
    doc = Document(file_path)
    paras = [p.text for p in doc.paragraphs]
    return "\n".join(paras), paras


def save_docx(paragraphs, output_path: str):
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc.save(output_path)


def extract_pdf(file_path: str):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.split("\n")  # إرجاع النص كقائمة من الفقرات
