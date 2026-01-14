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

from .pdf_utils import process_pdf
from .auth import verify_password

app = FastAPI()

# Render-friendly temp directory
TMP_DIR = "/tmp"

# 200 MB upload limit (safe for 200–400 page textbooks)
MAX_FILE_SIZE = 200 * 1024 * 1024  # bytes


@app.post("/process-pdf")
async def process_pdf_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    password: str = Form(...),          # 🔐 app-level password
    pdf_password: str = Form(""),       # 🔐 PDF password (may be empty)
):
    # 🔐 Validate app access password FIRST
    verify_password(password)

    # Basic file validation
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    # Read file into memory
    contents = await file.read()

    # Enforce upload size limit
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum allowed size is 200 MB.",
        )

    # Unique filenames to avoid collisions
    file_id = str(uuid.uuid4())
    input_path = os.path.join(TMP_DIR, f"{file_id}_input.pdf")
    output_path = os.path.join(TMP_DIR, f"{file_id}_output.pdf")

    # Save uploaded PDF
    with open(input_path, "wb") as f:
        f.write(contents)

    # Process PDF (catch intentional failures)
    try:
        process_pdf(input_path, output_path, pdf_password)
    except RuntimeError as e:
        # Clean up input file on failure
        if os.path.exists(input_path):
            os.remove(input_path)

        # Map known error to frontend-friendly message
        if str(e) == "INCORRECT_PASSWORD":
            raise HTTPException(
                status_code=400,
                detail="Incorrect PDF password",
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    # Ensure output file is deleted after response is sent
    background_tasks.add_task(os.remove, output_path)

    # Return processed PDF
    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="processed.pdf",
    )
