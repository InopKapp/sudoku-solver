import cv2
import numpy as np

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

        if child_count > best_child_count or area > best_area:
            best_child_count = child_count
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


def warp_sudoku(gray_img, contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

    if len(approx) > 4:
        approx = cv2.convexHull(approx)

    ordered = order_points(approx)

    (tl, tr, br, bl) = ordered
    maxWidth = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    maxHeight = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(ordered, dst)
    warped = cv2.warpPerspective(gray_img, M, (maxWidth, maxHeight))

    return warped


def detect_and_warp(gray_img, binary_img, dbg=None):
    square = find_largest_square(binary_img)
    
    if dbg:
        debug_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(debug_img, [square], -1, (0,255,0), 3)
        dbg.save(debug_img, "05_detected_grid.png")

    warped = warp_sudoku(gray_img, square)

    if dbg:
        dbg.save(warped, "06_warped.png")

    return warped
