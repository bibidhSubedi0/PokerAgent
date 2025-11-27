import cv2
import os
import numpy as np

# Hardcode the values for now, all of these are in my second monitor
SELF_CARD_START_POSITION = np.array([1025,728])
SELF_CARD_END_POSITION = np.array([1245,855])

N_SELF = 2
x1,y1 = SELF_CARD_START_POSITION
x2,y2 = SELF_CARD_END_POSITION
midx = int((x1+x2)/2)
midy = y2

SELF_CARD_1_START_POS = SELF_CARD_START_POSITION
SELF_CARD_1_END_POS = np.array([midx, y2])
SELF_CARD_2_START_POS = np.array([midx, y1])
SELF_CARD_2_END_POS = SELF_CARD_END_POSITION


SELF_CARD1_SUIT_START = np.array([1056,816])
SELF_CARD1_SUIT_END = np.array([1111,852])

SELF_CARD2_SUIT_START = np.array([1126,789])
SELF_CARD2_SUIT_END = np.array([1169,836])


src = cv2.imread("dd.png", cv2.IMREAD_GRAYSCALE)
lclubs = cv2.imread("suits/ClubLeft.png", cv2.IMREAD_GRAYSCALE)



x1, y1 = SELF_CARD1_SUIT_START
x2, y2 = SELF_CARD1_SUIT_END

roi = src[y1:y2, x1:x2]


# Resize template to roi size
w = x2 - x1
h = y2 - y1
lclubs = cv2.resize(lclubs, (w, h))

roi_blur = cv2.GaussianBlur(roi, (3,3), 0)
tpl_blur = cv2.GaussianBlur(lclubs, (3,3), 0)


# Template matching
res = cv2.matchTemplate(roi_blur, tpl_blur, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(res)

print("Found:", max_val >= 0.8)
print("Match score:", max_val)

cv2.imshow("ROI", roi)
cv2.imshow("Club", lclubs)
cv2.waitKey(0)
cv2.destroyAllWindows()
