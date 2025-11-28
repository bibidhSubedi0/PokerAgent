import cv2
import os
import numpy as np

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

SELF_CARD1_RANK_START = np.array([1040,765])
SELF_CARD1_RANK_END = np.array([1100,807])

SELF_CARD2_RANK_START = np.array([1132,735])
SELF_CARD2_RANK_END = np.array([1200,790])

src = cv2.imread("test_img_2.png", cv2.IMREAD_GRAYSCALE)

# Correct region
x1, y1 = SELF_CARD2_RANK_START
x2, y2 = SELF_CARD2_RANK_END

roi = src[y1:y2, x1:x2]
w = x2 - x1
h = y2 - y1

print(f"ROI shape: {roi.shape} ({w}x{h})")

# Test ALL ranks
rank_names = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

best_rank = None
best_score = -1.0

for rank in rank_names:
    template_path = f"ranks/{rank}r.png"
    
    if not os.path.exists(template_path):
        print(f"{rank}: template not found")
        continue
    

    # Load template with alpha channel handling, 
    # Had to manually fucking remove every single background from every single image -  Gadha ko kam
    # print("SHAPE: ", template_img.shape) SHAPE:  (49, 47, 4) (x,y,no_of_channels)
    template_img = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if len(template_img.shape) == 3 and template_img.shape[2] == 4:
        alpha = template_img[:, :, 3]
        bgr = template_img[:, :, :3]
        template = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        template[alpha == 0] = 255
    else:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    # Try multiple scales and pick best for this rank
    rank_best_score = -1.0
    
    # So when taking screenshots, i did not do it uniformly so all template images are not of same size
    # tei vara check different scaling factors
    for scale in [0.80, 0.85, 0.90, 0.95, 1.0, 1.05, 1.1]:
        template_h, template_w = template.shape
        
        new_h = int(h * scale)
        new_w = int((template_w / template_h) * new_h)
        
        if new_w > w or new_h > h or new_w < 5 or new_h < 5:
            # template must be smaller then ROI or else place nai garna midlena
            continue
        
        try:
            resized_template = cv2.resize(template, (new_w, new_h))

            # Ini haru apply gare, better result audo raixa
            tpl_blur = cv2.GaussianBlur(resized_template, (3,3), 0)
            roi_blur = cv2.GaussianBlur(roi, (3,3), 0)
            
            # Template matching
            res = cv2.matchTemplate(roi_blur, tpl_blur, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            
            if max_val > rank_best_score:
                rank_best_score = max_val
        except:
            continue
    
    print(f"{rank:3s}: {rank_best_score:.3f}")
    
    if rank_best_score > best_score:
        best_score = rank_best_score
        best_rank = rank

print(f"\n{'-'*30}")
print(f"Best match: {best_rank} with score {best_score:.3f}")
print(f"{'-'*30}")