import fitz  # PyMuPDF
import random
import os


BLACKOUT_RATIO = 0.40  # 🔥 40% blackout


def process_pdf(input_path: str, output_path: str, password: str | None = None) -> None:
    """
    Optimized PDF processing:
    - Blacks out 40% of pages (excluding first 3)
    - Minimizes save and compression cost
    - Safe for large PDFs on low-memory instances
    """

    doc = fitz.open(input_path)

    # 🔐 Handle encrypted PDFs
    if doc.is_encrypted:
        if not doc.authenticate(password or ""):
            doc.close()
            raise RuntimeError("INCORRECT_PASSWORD")

    total_pages = doc.page_count

    # If nothing to process, save directly
    if total_pages <= 3:
        doc.save(output_path)
        doc.close()
        os.remove(input_path)
        return

    # Pages eligible for blackout (0-indexed)
    processable_pages = range(3, total_pages)

    pages_to_blackout = int(BLACKOUT_RATIO * len(processable_pages))

    if pages_to_blackout <= 0:
        doc.save(output_path)
        doc.close()
        os.remove(input_path)
        return

    # Randomly select pages
    blackout_pages = sorted(
        random.sample(processable_pages, pages_to_blackout)
    )

    # 🔥 Draw blackout rectangles
    for page_number in blackout_pages:
        page = doc.load_page(page_number)
        rect = page.rect

        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(fill=(0, 0, 0))
        shape.commit()

    # 🚀 FAST SAVE (key optimization)
    doc.save(
        output_path,
        incremental=False,   # explicit full save
        deflate=True,        # keep size reasonable
        garbage=2            # avoid expensive cleanup passes
    )

    doc.close()
    os.remove(input_path)
