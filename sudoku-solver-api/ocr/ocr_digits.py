import cv2
import pytesseract
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def remove_grid_lines(img):
    h, w = img.shape

    edges = cv2.Canny(img, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=120,
        minLineLength=w // 3,
        maxLineGap=20
    )

    cleaned = img.copy()

    if lines is None:
        return cleaned

    for line in lines:
        x1, y1, x2, y2 = line[0]

        # Vertical line
        if abs(x1 - x2) < 10:
            cv2.line(cleaned, (x1, 0), (x1, h), 255, thickness=5)

        # Horizontal line
        elif abs(y1 - y2) < 10:
            cv2.line(cleaned, (0, y1), (w, y1), 255, thickness=5)

    return cleaned

def enhance_contrast(img):
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    return clahe.apply(img)

def otsu(img):
    ret, image = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return image


def preprocess_cell_for_ocr(cell):
    if len(cell.shape) == 3:
        cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    cell = cv2.resize(cell, (64, 64), interpolation=cv2.INTER_CUBIC)
    return cell

def is_cell_empty(cell, std_thresh=8):
    return np.count_nonzero(cell < 200) < 20

def ocr_cell(cell):
    for psm in [13, 10]:
        config = f"--oem 3 --psm {psm} -c tessedit_char_whitelist=123456789"
        text = pytesseract.image_to_string(cell, config=config).strip()
        digits = [ch for ch in text if ch in "123456789"]
        if len(digits) == 1:
            return digits[0]
    return ""


def extract_cells(grid_img):
    h, w = grid_img.shape
    cell_h = h // 9
    cell_w = w // 9

    cells = []
    for r in range(9):
        for c in range(9):
            y1 = r * cell_h
            y2 = (r + 1) * cell_h
            x1 = c * cell_w
            x2 = (c + 1) * cell_w
            cells.append(grid_img[y1:y2, x1:x2])

    return cells


if __name__ == "__main__":
    grid = cv2.imread("debug/6_warped_clean.png", cv2.IMREAD_GRAYSCALE)
    grid = enhance_contrast(grid)
    cv2.imwrite("debug/7_contrast.png", grid)
    grid = otsu(grid)
    cv2.imwrite("debug/8_otsu.png",grid)
    grid_no_lines = remove_grid_lines(grid)

    cv2.imwrite("debug/9_warped_no_lines.png", grid_no_lines)

    if grid is None:
        raise ValueError("Warped grid image not found")

    cells = extract_cells(grid_no_lines)

    os.makedirs("debug/ocr_cells", exist_ok=True)

    board = [[0] * 9 for _ in range(9)]

    for i, cell in enumerate(cells):
        r, c = divmod(i, 9)

        cell_proc = preprocess_cell_for_ocr(cell)

        cv2.imwrite(f"debug/ocr_cells/cell_{r}_{c}.png", cell_proc)

        if is_cell_empty(cell_proc):
            continue

        digit = ocr_cell(cell_proc)
        if digit:
            board[r][c] = int(digit)

    print("Recognized board:")
    for row in board:
        print(row)
