import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io_utils import extract_txt, extract_docx, extract_pdf, save_docx
from ner import get_entities
from anonymizer import anonymize_text
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# خدمة ملفات static (ضع index.html داخل مجلد static/)
# app.mount("/", StaticFiles(directory="static", html=True), name="static")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# إعادة توجيه الجذر "/" إلى index.html داخل static
@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/api/anonymize")
async def anonymize_file(
    file: UploadFile,
    labels: str = Form(...),
    style: str = Form("*****"),
    use_faker: bool = Form(False)
):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if file.filename.endswith(".txt"):
        paras = extract_txt(file_path).split("\n")
        text = "\n".join(paras)
    elif file.filename.endswith(".docx"):
        text, paras = extract_docx(file_path)
    elif file.filename.endswith(".pdf"):
        paras = extract_pdf(file_path)
        text = "\n".join(paras)
    else:
        return JSONResponse({"error": "Only .txt, .docx, or .pdf supported"}, status_code=400)

    # تشغيل NER
    entities = get_entities(text)
    selected_labels = [labbel.strip() for labbel in labels.split(",")]

    # تعمية النص
    anonymized = anonymize_text(text, entities, selected_labels, style, use_faker)

    # إعادة بناء docx (حتى لو كان txt أو pdf سنخرجه docx)
    out_path = os.path.join(OUTPUT_DIR, file_id + ".docx")
    save_docx(anonymized.split("\n"), out_path)

    return FileResponse(out_path, filename="anonymized.docx")
