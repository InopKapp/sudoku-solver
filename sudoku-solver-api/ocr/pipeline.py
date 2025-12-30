from ocr.preprocess import preprocess_image
from ocr.grid_detect import detect_and_warp
from ocr.ocr_digits import recognize_digits
from ocr.debug_utils import OCRDebug

def run_ocr_pipeline(image_path: str,debug: bool = False):
    dbg = OCRDebug(debug)
    dbg.log("Starting OCR pipeline")
    gray, binary = preprocess_image(image_path, dbg)
    warped = detect_and_warp(gray, binary, dbg)
    board = recognize_digits(warped, dbg)
    dbg.log("OCR pipeline finished")
    return board
