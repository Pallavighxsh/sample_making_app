import fitz  # PyMuPDF
import random
import os
import time


BLACKOUT_RATIO = 0.40

# ⏱️ Soft execution budget (seconds)
# Render free tier usually dies ~30s; stay WELL below
TIME_BUDGET = 12.0


def process_pdf(input_path: str, output_path: str) -> None:
    """
    Time-aware PDF processing.

    - Targets ~40% blackout
    - Stops early if time budget is reached
    - Always saves whatever work is done
    - Lowest quality / fastest possible save
    """

    start_time = time.monotonic()

    doc = fitz.open(input_path)
    total_pages = doc.page_count

    if total_pages <= 3:
        doc.save(output_path)
        doc.close()
        os.remove(input_path)
        return

    processable_pages = list(range(3, total_pages))
    random.shuffle(processable_pages)

    target_blackouts = int(BLACKOUT_RATIO * len(processable_pages))
    blacked_out = 0

    for page_number in processable_pages:
        elapsed = time.monotonic() - start_time

        # ⛔ Stop before Render can kill us
        if elapsed >= TIME_BUDGET:
            break

        if blacked_out >= target_blackouts:
            break

        page = doc.load_page(page_number)
        rect = page.rect

        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(fill=(0, 0, 0))
        shape.commit()

        blacked_out += 1

    # 🚀 FASTEST + LOWEST QUALITY SAVE
    doc.save(
        output_path,
        garbage=0,        # no cleanup
        deflate=False,    # no compression (fastest)
        clean=False,
    )

    doc.close()
    os.remove(input_path)
