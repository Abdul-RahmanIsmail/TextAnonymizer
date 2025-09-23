# 🛡️ Text Anonymizer

A **web-based Text Anonymizer** built with **FastAPI** for anonymizing sensitive information in `.txt` or `.docx` files. Supports **NER**, **Regex**, and optional **Faker** replacements.

---

## ✨ Features

- **Upload Files**: `.txt` or `.docx`
- **Entity Detection**:
  - NER-based / Zero-shot: `PER`, `ORG`, `LOC`
  - Regex-based: `EMAIL`, `PHONE`
- **Customizable Replacement**:
  - Fixed string (e.g., `[REDACTED]`) or realistic **Faker** data
- **Interactive Frontend**:
  - Tag-based entity selection
  - Editable replacement style (`datalist`) with suggestions
  - File upload progress bar
  - Download anonymized `.docx` file
- **Responsive UI**: Works on desktop and mobile

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Frontend**: HTML, CSS, Vanilla JS
- **Libraries**:
  - `transformers` / any NER model
  - `python-docx` for DOCX handling
  - `Faker` for generating realistic data
- **Utilities**: `shutil`, `uuid`, `os` for file management


---


## 🗂️ Project Structure
- text-anonymizer/
- │
- │── `main.py`                 FastAPI backend
- │── `io_utils.py`             Read/write TXT & DOCX
- │── `ner.py`                  Named Entity Recognition
- │── `anonymizer.py`           Anonymization logic
- │── `uploads/`                Temporary uploads
- │── `outputs/`                Anonymized files
- │── `static/`
- │   └── `index.html`          Frontend
- │── `requirements.txt`        Python dependencies
- │── `Examples`        Examples For Test
- │   └── `Example_1.txt`          Text File
- │   └── `Example_1.docx`         Word File
- │   └── `Example_1.pdf`          PDF File
- │── `README.md`


---

## ⚡ Installation

  **Clone repository**
  ```bash  
  git clone https://github.com/yourusername/text-anonymizer.git
  
  cd text-anonymizer
  ```

  **Install dependencies**
  ```bash
    pip install -r requirements.txt
  ```

 **Start FastAPI server**
  ```bash
    uvicorn main:app --reload
  ```

---

## 🚀 Usage

- **Upload File**: Select `.txt` or `.docx.`
- **Select Entities**: Click tags (`PER, ORG, LOC, EMAIL, PHONE`).:
- **Replacement Style**: Choose from suggestions or type custom.:
- **Use Faker**: Optional realistic replacements.:
- **Submit**: Click Execute.:
- **Download**: Get anonymized .docx file.:


---

## 📝 Example

- **Input**:
   - **File Contnet:** John Doe works at OpenAI in San Francisco.
    Contact: john.doe@example.com, +1 555-123-4567.

  - **Entities**: `PER`, `ORG`, `LOC`, `EMAIL`, `PHONE`.
  - **Style**: `[REDACTED]`.

- **Output**:
  - `[REDACTED]` works at `[REDACTED]` in  `[REDACTED]`.
    Contact:  `[REDACTED]`,  `[REDACTED]`.

- **Output (With Faker)**:
  - `Michael Smith` works at `Acme Corp` in `New York`. Contact: `jane.smith@example.com`, `+1 555-987-6543`.


