import numpy as np
import cv2
import mss

PALO_POS_START = np.array([752, 929])
PALO_POS_END   = np.array([1742, 1014])
Moinitor = 2

def determin_turn(src_gray, start_pos, end_pos, template):
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    roi = src_gray[y1:y2, x1:x2]
    w, h = x2 - x1, y2 - y1 
    
    if w <= 0 or h <= 0:
        return -1.0

    tpl_h, tpl_w = template.shape

    scale_w = (w - 1) / tpl_w
    scale_h = (h - 1) / tpl_h
    scale = min(scale_w, scale_h)

    if scale <= 0:
        return -1.0

    new_w = max(5, int(tpl_w * scale))
    new_h = max(5, int(tpl_h * scale))

    resized_template = cv2.resize(template, (new_w, new_h))

    tpl_blur = cv2.GaussianBlur(resized_template, (3, 3), 0)
    roi_blur = cv2.GaussianBlur(roi, (3, 3), 0)

    res = cv2.matchTemplate(roi_blur, tpl_blur, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    return max_val


# ---------------- MAIN (LIVE MONITOR 2) ------------------

palo = cv2.imread("palo.png")
if palo is None:
    raise Exception("palo.png not found")

palo_gray = cv2.cvtColor(palo, cv2.COLOR_BGR2GRAY)

sct = mss.mss()
monitor = sct.monitors[Moinitor]       

while True:
    frame = np.array(sct.grab(monitor))
    src = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    score = determin_turn(src_gray, PALO_POS_START, PALO_POS_END, palo_gray)
    print("Match score:", score)

    # show ROI and template
    x1, y1 = PALO_POS_START
    x2, y2 = PALO_POS_END

    roi = src[y1:y2, x1:x2]
    cv2.imshow("ROI", roi)
    cv2.imshow("Template", palo)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
