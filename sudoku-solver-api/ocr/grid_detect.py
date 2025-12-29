import cv2
import numpy as np
import sys
import os


def find_largest_square(binary_img):
    contours, hierarchy = cv2.findContours(
        binary_img,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    img_area = binary_img.shape[0] * binary_img.shape[1]

    best_cnt = None
    best_child_count = 0
    best_area = 0

    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < img_area * 0.15:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        ratio = w / float(h)
        if ratio < 0.75 or ratio > 1.25:
            continue

        child_count = 0
        if hierarchy is not None:
            child = hierarchy[0][i][2]
            while child != -1:
                child_count += 1
                child = hierarchy[0][child][0]

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        hull = cv2.convexHull(approx)

        if child_count > best_child_count:
            best_child_count = child_count
            best_area = area
            best_cnt = hull

        elif child_count == 0 and area > best_area:
            best_area = area
            best_cnt = hull

    if best_cnt is None:
        raise ValueError("Sudoku grid not found")

    return best_cnt


def order_points(pts):
    pts = pts.reshape(-1, 2)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    return np.array([tl, tr, br, bl], dtype="float32")


def warp_sudoku(image, contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

    if len(approx) < 4:
        raise ValueError("Could not approximate grid to 4 corners")

    if len(approx) > 4:
        hull = cv2.convexHull(approx)
        peri = cv2.arcLength(hull, True)
        approx = cv2.approxPolyDP(hull, 0.02 * peri, True)

    if len(approx) != 4:
        raise ValueError("Grid does not have 4 corners after approximation")

    ordered = order_points(approx)

    (tl, tr, br, bl) = ordered

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(ordered, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python grid_detect.py <original_image> <preprocessed_image>")
        sys.exit(1)

    orig_path = sys.argv[1]
    prep_path = sys.argv[2]

    gray_original = cv2.imread(orig_path, cv2.IMREAD_GRAYSCALE)
    if gray_original is None:
        raise ValueError("Could not read original image")

    binary = cv2.imread(prep_path, cv2.IMREAD_GRAYSCALE)
    if binary is None:
        raise ValueError("Could not read preprocessed image")

    square = find_largest_square(binary)

    warped_clean = warp_sudoku(gray_original, square)

    os.makedirs("debug", exist_ok=True)

    debug_contours = cv2.cvtColor(gray_original, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(debug_contours, [square], -1, (0, 255, 0), 3)

    cv2.imwrite("debug/5_detected_grid.png", debug_contours)
    cv2.imwrite("debug/6_warped_clean.png", warped_clean)

    print("Grid detection complete.")
    print("Check:")
    print("  debug/5_detected_grid.png")
    print("  debug/6_warped_clean.png")
