import cv2
import pytesseract
import numpy as np

def enhance_contrast(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img)

def otsu(img):
    # THRESH_BINARY_INV so text/digits are white and background is black for contour finding
    ret, image = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return image

def recognize_digits(warped_grid, dbg=None):
    if len(warped_grid.shape) == 3:
        gray = cv2.cvtColor(warped_grid, cv2.COLOR_BGR2GRAY)
    else:
        gray = warped_grid

    grid = enhance_contrast(gray)
    binary = otsu(grid)
    
    # GUARANTEE white text on black background for contour extraction
    if np.mean(binary) > 127:
        binary = cv2.bitwise_not(binary)
        
    if dbg:
        dbg.save(binary, "08_otsu_inv.png")
        
    h, w = binary.shape
    cell_h = h // 9
    cell_w = w // 9
    
    board = [[0] * 9 for _ in range(9)]
    processed_cells = []
    cell_positions = []
    
    for r in range(9):
        for c in range(9):
            y1 = r * cell_h
            y2 = (r + 1) * cell_h
            x1 = c * cell_w
            x2 = (c + 1) * cell_w
            
            cell = binary[y1:y2, x1:x2]
            
            def get_best_contour(img, offset_x=0, offset_y=0):
                conts, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                best = None
                m_dist = float('inf')
                cx_img, cy_img = img.shape[1] / 2.0, img.shape[0] / 2.0
                
                for cnt in conts:
                    cx, cy, cw, ch = cv2.boundingRect(cnt)
                    
                    # 1. reject dust and tiny artifacts (digit must be at least 25% of cell height)
                    if cw * ch < 50 or ch < img.shape[0] * 0.25:
                        continue
                        
                    # 2. reject massive shapes (grid lines engulfing the cell)
                    if cw > img.shape[1] * 0.8 or ch > img.shape[0] * 0.8:
                        continue
                        
                    # 3. reject weird aspect ratios (broken lines, horizontal bars)
                    if cw / ch > 2.0 or ch / cw > 8.0:
                        continue
                        
                    # 4. find the one closest to the center
                    cnt_cx = cx + cw / 2.0
                    cnt_cy = cy + ch / 2.0
                    dist = (cnt_cx - cx_img)**2 + (cnt_cy - cy_img)**2
                    
                    if dist < m_dist:
                        m_dist = dist
                        best = (cx + offset_x, cy + offset_y, cw, ch)
                        
                if best is None:
                    return None
                    
                # reject if sitting in the extreme corner
                max_allowed_dist = (img.shape[1] * 0.4)**2 + (img.shape[0] * 0.4)**2
                if m_dist > max_allowed_dist:
                    return None
                    
                return best
                
            bbox = get_best_contour(cell)
            
            if bbox is None:
                # fallback: Shave 15% off the edges to detach grid lines and try again
                my, mx = int(cell_h * 0.15), int(cell_w * 0.15)
                shaved = cell[my:cell_h-my, mx:cell_w-mx]
                bbox = get_best_contour(shaved, offset_x=mx, offset_y=my)
                
            if bbox is None:
                continue
                
            cx, cy, cw, ch = bbox
            digit_roi = cell[cy:cy+ch, cx:cx+cw]
            
            # resize digit to standard height 32
            scale = 32.0 / ch
            target_w = int(cw * scale)
            if target_w == 0:
                continue
                
            # place in the center of a 48x48 black canvas
            start_y = 8
            start_x = (48 - target_w) // 2
            
            # if it's wider than 48 after scaling height to 32 then it's definitely not a digit
            if start_x < 0:
                continue
                
            resized = cv2.resize(digit_roi, (target_w, 32), interpolation=cv2.INTER_AREA)
            canvas = np.zeros((48, 48), dtype=np.uint8)
            canvas[start_y:start_y+32, start_x:start_x+target_w] = resized
            
            # invert so Tesseract gets black text on white background
            final_digit = cv2.bitwise_not(canvas)
            
            if dbg:
                dbg.save(final_digit, f"cells_processed/cleaned_{r}_{c}.png")
                
            processed_cells.append(final_digit)
            cell_positions.append((r, c))
            
    if not processed_cells:
        return board
        
    separator = np.ones((10, processed_cells[0].shape[1]), dtype=np.uint8) * 255
    stacked = processed_cells[0]
    for cell_img in processed_cells[1:]:
        stacked = np.vstack((stacked, separator, cell_img))
        
    if dbg:
        dbg.save(stacked, "09_stacked_digits.png")
        
    config = "--oem 3 --psm 6 -c tessedit_char_whitelist=123456789"
    try:
        data = pytesseract.image_to_data(stacked, config=config, output_type=pytesseract.Output.DICT)
    except Exception as e:
        data = {'text': [], 'top': []}
        
    found_indices = set()
    
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        # keep only the first valid digit if it grouped them
        digit = [d for d in text if d in "123456789"]
        if digit:
            y = data['top'][i]
            # 48px + 10px separator = 58px.
            idx = y // 58
            if idx < len(processed_cells):
                r, c = cell_positions[idx]
                board[r][c] = int(digit[0])
                found_indices.add(idx)
                
    # fallback for any cells that were missed by the stacked OCR
    if len(found_indices) < len(processed_cells):
        print(f"Stacked OCR found {len(found_indices)}/{len(processed_cells)} digits. Running individual fallback...")
        for idx, cell_img in enumerate(processed_cells):
            if idx not in found_indices:
                r, c = cell_positions[idx]
                # try PSM 10 (Single Char) and then PSM 6 (Single Block)
                for psm in [10, 6, 13]:
                    ch = pytesseract.image_to_string(cell_img, config=f"--oem 3 --psm {psm} -c tessedit_char_whitelist=123456789").strip()
                    digit = [d for d in ch if d in "123456789"]
                    if digit:
                        board[r][c] = int(digit[0])
                        print(f"Fallback caught digit {digit[0]} at ({r},{c}) with PSM {psm}")
                        break
                        
    return board
