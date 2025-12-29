import cv2
import numpy as np
import os
import sys

def extract_cells(grid_img):
    h, w = grid_img.shape
    cell_h = h // 9
    cell_w = w // 9

    cells = []

    for row in range(9):
        for col in range(9):
            y1 = row * cell_h
            y2 = (row + 1) * cell_h
            x1 = col * cell_w
            x2 = (col + 1) * cell_w

            cell = grid_img[y1:y2, x1:x2]
            cells.append(cell)

    return cells

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cell_extract.py <warped_clean_grid>")
        sys.exit(1)

    grid_path = sys.argv[1]
    grid = cv2.imread(grid_path, cv2.IMREAD_GRAYSCALE)

    if grid is None:
        raise ValueError("Could not read grid image")

    cells = extract_cells(grid)

    os.makedirs("debug/cells_raw", exist_ok=True)
    os.makedirs("debug/cells_light", exist_ok=True)

    for i, cell in enumerate(cells):
        row = i // 9
        col = i % 9

        cv2.imwrite(f"debug/cells_raw/cell_{row}_{col}.png", cell)

    print("Cell extraction complete.")
    print("Check:")
    print("  debug/cells_raw/")
