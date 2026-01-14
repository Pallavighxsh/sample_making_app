import os
import uuid

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    BackgroundTasks,
)
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .pdf_utils import process_pdf
from .auth import verify_password

app = FastAPI()

# ✅ CORS for GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pallavighxsh.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMP_DIR = "/tmp"
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/process-pdf")
async def process_pdf_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    password: str = Form(...),
):
    verify_password(password)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large.")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(TMP_DIR, f"{file_id}_input.pdf")
    output_path = os.path.join(TMP_DIR, f"{file_id}_output.pdf")

    with open(input_path, "wb") as f:
        f.write(contents)

    try:
        process_pdf(input_path, output_path)
    except RuntimeError as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=400, detail=str(e))

    background_tasks.add_task(os.remove, output_path)

    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="processed.pdf",
        headers={"Content-Disposition": "attachment; filename=processed.pdf"},
    )
