from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import subprocess
from uuid import uuid4

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    file_id = str(uuid4())
    input_path = f"{UPLOAD_DIR}/{file_id}_input.pdf"
    output_path = f"{RESULT_DIR}/{file_id}_output.pdf"

    # Lưu file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Chạy OCR bằng ocrmypdf
    try:
        subprocess.run([
            "ocrmypdf", "--language", "eng+vie",
            input_path, output_path
        ], check=True)
    except subprocess.CalledProcessError:
        return {"error": "OCR failed"}

    return templates.TemplateResponse("index.html", {
        "request": request,
        "download_link": f"/download/{file_id}"
    })

@app.get("/download/{file_id}")
async def download_pdf(file_id: str):
    return FileResponse(path=f"{RESULT_DIR}/{file_id}_output.pdf", filename="ocr_result.pdf", media_type='application/pdf')
