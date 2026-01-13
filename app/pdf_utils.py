import fitz  # PyMuPDF
import random
import os


def process_pdf(input_path: str, output_path: str) -> None:
    """
    Processes a PDF by blacking out ~45% of pages at random,
    excluding the first three pages.

    Args:
        input_path (str): Path to uploaded PDF
        output_path (str): Path to save processed PDF
    """

    # Open the PDF
    doc = fitz.open(input_path)

    # 🔐 Handle encrypted / permission-restricted PDFs
    if doc.is_encrypted:
        try:
            # Many academic PDFs require this even with no password
            doc.authenticate("")
        except Exception:
            doc.close()
            raise RuntimeError("Encrypted PDF cannot be processed")

    total_pages = doc.page_count

    # If PDF is too short, just save as-is
    if total_pages <= 3:
        doc.save(output_path)
        doc.close()
        if os.path.exists(input_path):
            os.remove(input_path)
        return

    # Pages are 0-indexed:
    # Pages 0,1,2 -> keep unchanged
    # Pages 3 onward -> eligible for blackout
    processable_pages = list(range(3, total_pages))

    # Calculate number of pages to black out (~45%)
    pages_to_blackout = int(0.45 * len(processable_pages))

    # Guard against zero
    if pages_to_blackout == 0:
        doc.save(output_path)
        doc.close()
        if os.path.exists(input_path):
            os.remove(input_path)
        return

    # Randomly select unique pages (no duplicates)
    blackout_pages = random.sample(
        processable_pages,
        pages_to_blackout
    )

    # Black out selected pages
    for page_number in blackout_pages:
        page = doc.load_page(page_number)
        rect = page.rect

        # Draw solid black rectangle over entire page
        page.draw_rect(
            rect,
            color=(0, 0, 0),
            fill=(0, 0, 0),
        )

    # Save processed PDF
    doc.save(output_path)
    doc.close()

    # Clean up uploaded file
    if os.path.exists(input_path):
        os.remove(input_path)
