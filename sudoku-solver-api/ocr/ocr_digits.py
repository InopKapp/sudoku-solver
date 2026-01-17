import cv2
import pytesseract
import numpy as np

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
            cv2.line(cleaned, (x1, 0), (x1, h), 255, thickness=20)

        # Horizontal line
        elif abs(y1 - y2) < 10:
            cv2.line(cleaned, (0, y1), (w, y1), 255, thickness=20)

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

def recognize_digits(warped_grid, dbg=None):
    grid = warped_grid
    grid = enhance_contrast(warped_grid)
    if dbg:
        dbg.save(grid, "07_contrast.png")
    grid = otsu(grid)
    if dbg:
        dbg.save(grid, "08_otsu.png")
    grid = remove_grid_lines(grid)
    if dbg:
        dbg.save(grid, "09_remove_lines.png")
    cells = extract_cells(grid)

    board = [[0] * 9 for _ in range(9)]

    for i, cell in enumerate(cells):
        r, c = divmod(i, 9)
        if dbg:
            dbg.save(cell, f"cells/raw_{r}_{c}.png")
        cell = preprocess_cell_for_ocr(cell)
        if dbg:
            dbg.save(cell, f"cells_processed/raw_{r}_{c}.png")
        if is_cell_empty(cell):
            continue
        digit = ocr_cell(cell)
        if digit:
            board[r][c] = int(digit)
    return board