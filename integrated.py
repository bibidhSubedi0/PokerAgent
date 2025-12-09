import cv2
import numpy as np
import mss
import os
import time
from OwnEngine import analyze_game_state
import pyautogui
from screeninfo import get_monitors

sct = mss.mss()
monitor = sct.monitors[2]
monitors = get_monitors()
second_monitor = monitors[1]

# ============================================================================
# CONFIGURATION
# ============================================================================

SAMPLE_INTERVAL = 2.0  # Sample once per second


# ============================================================================
# REGION DEFINITIONS
# ============================================================================

# Self card positions (tilted cards)
SELF_CARD1_RANK_START = np.array([1045, 758])
SELF_CARD1_RANK_END = np.array([1098, 805])
SELF_CARD1_SUIT_START = np.array([1065, 810])
SELF_CARD1_SUIT_END = np.array([1105, 854])

SELF_CARD2_RANK_START = np.array([1132, 735])
SELF_CARD2_RANK_END = np.array([1200, 790])
SELF_CARD2_SUIT_START = np.array([1126, 789])
SELF_CARD2_SUIT_END = np.array([1169, 836])

# Community card region (straight cards)
COMM_CARD_START_POSITION = np.array([737, 433])
COMM_CARD_END_POSITION = np.array([1253, 560])

# Determine turn
PALO_POS_START = np.array([752, 929])
PALO_POS_END   = np.array([1742, 1014])

# Actions
FOLD = np.array([913,970])
CHECK = np.array([1257,970])
RAISE = np.array([1580,970])

# ============================================================================
# TEMPLATE LOADING
# ============================================================================

def load_tilted_templates():
    """Load tilted templates for self cards"""
    ranks_left = {}
    ranks_right = {}
    suits_left = {}
    suits_right = {}
    
    rank_names = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suit_names = ['Club', 'Diamond', 'Heart', 'Spade']
    
    for rank in rank_names:
        left_path = f'ranks/{rank}l.png'
        right_path = f'ranks/{rank}r.png'
        
        if os.path.exists(left_path):
            img = cv2.imread(left_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    bgr = img[:, :, :3]
                    ranks_left[rank] = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                    ranks_left[rank][alpha == 0] = 255
                else:
                    ranks_left[rank] = cv2.imread(left_path, cv2.IMREAD_GRAYSCALE)
        
        if os.path.exists(right_path):
            img = cv2.imread(right_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    bgr = img[:, :, :3]
                    ranks_right[rank] = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                    ranks_right[rank][alpha == 0] = 255
                else:
                    ranks_right[rank] = cv2.imread(right_path, cv2.IMREAD_GRAYSCALE)
    
    for suit in suit_names:
        left_path = f'suits/{suit}Left.png'
        right_path = f'suits/{suit}Right.png'
        
        if os.path.exists(left_path):
            img = cv2.imread(left_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    bgr = img[:, :, :3]
                    suits_left[suit] = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                    suits_left[suit][alpha == 0] = 255
                else:
                    suits_left[suit] = cv2.imread(left_path, cv2.IMREAD_GRAYSCALE)
        
        if os.path.exists(right_path):
            img = cv2.imread(right_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    bgr = img[:, :, :3]
                    suits_right[suit] = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                    suits_right[suit][alpha == 0] = 255
                else:
                    suits_right[suit] = cv2.imread(right_path, cv2.IMREAD_GRAYSCALE)
    
    return ranks_left, ranks_right, suits_left, suits_right

def load_straight_templates():
    """Load straight templates for community cards"""
    ranks = {}
    suits = {}
    
    rank_names = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suit_names = ['Club', 'Diamond', 'Heart', 'Spade']
    
    for rank in rank_names:
        path = f's_ranks/{rank}.png'
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    bgr = img[:, :, :3]
                    ranks[rank] = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                    ranks[rank][alpha == 0] = 255
                else:
                    ranks[rank] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    
    for suit in suit_names:
        path = f's_suits/{suit}.png'
        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                if len(img.shape) == 3 and img.shape[2] == 4:
                    alpha = img[:, :, 3]
                    bgr = img[:, :, :3]
                    suits[suit] = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                    suits[suit][alpha == 0] = 255
                else:
                    suits[suit] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    
    return ranks, suits

# ============================================================================
# CARD DETECTION
# ============================================================================

def match_template_tilted(src_gray, start_pos, end_pos, template):
    """Match template for tilted cards"""
    x1, y1 = start_pos
    x2, y2 = end_pos
    roi = src_gray[y1:y2, x1:x2]
    w, h = x2 - x1, y2 - y1
    
    if w <= 0 or h <= 0:
        return -1.0
    
    best_score = -1.0
    for scale in [0.80, 0.85, 0.90, 0.95, 1.0, 1.05, 1.1]:
        template_h, template_w = template.shape
        new_h = int(h * scale)
        new_w = int((template_w / template_h) * new_h)
        
        if new_w > w or new_h > h or new_w < 5 or new_h < 5:
            continue
        
        try:
            resized_template = cv2.resize(template, (new_w, new_h))
            tpl_blur = cv2.GaussianBlur(resized_template, (3, 3), 0)
            roi_blur = cv2.GaussianBlur(roi, (3, 3), 0)
            res = cv2.matchTemplate(roi_blur, tpl_blur, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > best_score:
                best_score = max_val
        except:
            continue
    
    return best_score

def detect_self_cards(img_gray, ranks_left, ranks_right, suits_left, suits_right):
    """Detect both self cards"""
    # Card 1 (LEFT)
    best_rank1, best_rank1_score = None, -1.0
    for rank_name, template in ranks_left.items():
        if template is None:
            continue
        score = match_template_tilted(img_gray, SELF_CARD1_RANK_START, SELF_CARD1_RANK_END, template)
        if score > best_rank1_score:
            best_rank1_score = score
            best_rank1 = rank_name
    
    best_suit1, best_suit1_score = None, -1.0
    for suit_name, template in suits_left.items():
        if template is None:
            continue
        score = match_template_tilted(img_gray, SELF_CARD1_SUIT_START, SELF_CARD1_SUIT_END, template)
        if score > best_suit1_score:
            best_suit1_score = score
            best_suit1 = suit_name
    
    card1 = f"{best_rank1}{best_suit1[0]}" if best_rank1 and best_suit1 else None
    
    # Card 2 (RIGHT)
    best_rank2, best_rank2_score = None, -1.0
    for rank_name, template in ranks_right.items():
        if template is None:
            continue
        score = match_template_tilted(img_gray, SELF_CARD2_RANK_START, SELF_CARD2_RANK_END, template)
        if score > best_rank2_score:
            best_rank2_score = score
            best_rank2 = rank_name
    
    best_suit2, best_suit2_score = None, -1.0
    for suit_name, template in suits_right.items():
        if template is None:
            continue
        score = match_template_tilted(img_gray, SELF_CARD2_SUIT_START, SELF_CARD2_SUIT_END, template)
        if score > best_suit2_score:
            best_suit2_score = score
            best_suit2 = suit_name
    
    card2 = f"{best_rank2}{best_suit2[0]}" if best_rank2 and best_suit2 else None
    
    return card1, card2

def detect_card_rectangles(img_gray, comm_region_start, comm_region_end):
    """Detect white card rectangles in the community card area"""
    x1, y1 = comm_region_start
    x2, y2 = comm_region_end
    roi = img_gray[y1:y2, x1:x2]
    _, thresh = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    card_boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = h / w if w > 0 else 0
        area = w * h
        
        if (w > 60 and h > 80 and area > 5000 and area < 20000 and
            aspect_ratio > 1.2 and aspect_ratio < 2.0):
            card_boxes.append({'x': x1 + x, 'y': y1 + y, 'w': w, 'h': h})
    
    card_boxes.sort(key=lambda box: box['x'])
    return card_boxes

def extract_rank_and_suit_regions(card_box, img_gray):
    """Extract rank and suit regions from detected card - handles 10 card with 2 digits"""
    x, y, w, h = card_box['x'], card_box['y'], card_box['w'], card_box['h']
    card_img = img_gray[y:y+h, x:x+w]
    _, card_thresh = cv2.threshold(card_img, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(card_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_contours = []
    for cnt in contours:
        cx, cy, cw, ch = cv2.boundingRect(cnt)
        if cw * ch > 50:
            valid_contours.append({'x': cx, 'y': cy, 'w': cw, 'h': ch, 'center_y': cy + ch/2})
    
    valid_contours.sort(key=lambda c: c['center_y'])
    
    if len(valid_contours) < 2:
        return (np.array([x + 5, y + 5]), np.array([x + int(w * 0.40), y + int(h * 0.35)]),
                np.array([x + 5, y + int(h * 0.35)]), np.array([x + int(w * 0.40), y + int(h * 0.65)]))
    
    # Group contours that are close together vertically (for "10" rank which has 2 digits)
    grouped_contours = []
    current_group = [valid_contours[0]]
    
    for i in range(1, len(valid_contours)):
        prev_y = current_group[-1]['center_y']
        curr_y = valid_contours[i]['center_y']
        
        # If contours are within 20 pixels vertically, they're part of same symbol (e.g., "10")
        if abs(curr_y - prev_y) < 20:
            current_group.append(valid_contours[i])
        else:
            grouped_contours.append(current_group)
            current_group = [valid_contours[i]]
    
    grouped_contours.append(current_group)
    
    # If we still don't have at least 2 groups, fallback
    if len(grouped_contours) < 2:
        return (np.array([x + 5, y + 5]), np.array([x + int(w * 0.40), y + int(h * 0.35)]),
                np.array([x + 5, y + int(h * 0.35)]), np.array([x + int(w * 0.40), y + int(h * 0.65)]))
    
    # Merge each group into a single bounding box
    def merge_group(group):
        min_x = min(c['x'] for c in group)
        min_y = min(c['y'] for c in group)
        max_x = max(c['x'] + c['w'] for c in group)
        max_y = max(c['y'] + c['h'] for c in group)
        return {'x': min_x, 'y': min_y, 'w': max_x - min_x, 'h': max_y - min_y}
    
    rank_c = merge_group(grouped_contours[0])
    suit_c = merge_group(grouped_contours[1])
    
    padding = 3
    
    rank_start = np.array([x + max(0, rank_c['x'] - padding), y + max(0, rank_c['y'] - padding)])
    rank_end = np.array([x + min(w, rank_c['x'] + rank_c['w'] + padding), y + min(h, rank_c['y'] + rank_c['h'] + padding)])
    suit_start = np.array([x + max(0, suit_c['x'] - padding), y + max(0, suit_c['y'] - padding)])
    suit_end = np.array([x + min(w, suit_c['x'] + suit_c['w'] + padding), y + min(h, suit_c['y'] + suit_c['h'] + padding)])
    
    return rank_start, rank_end, suit_start, suit_end

def match_template_straight(src_gray, start_pos, end_pos, template):
    """Match template for straight community cards"""
    x1, y1 = start_pos
    x2, y2 = end_pos
    roi = src_gray[y1:y2, x1:x2]
    w, h = x2 - x1, y2 - y1
    
    if w <= 0 or h <= 0:
        return -1.0
    
    _, roi_thresh = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY_INV)
    best_score = -1.0
    
    for scale in [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
        template_h, template_w = template.shape
        new_h = int(h * scale)
        new_w = int((template_w / template_h) * new_h)
        
        if new_w > w or new_h > h or new_w < 5 or new_h < 5:
            continue
        
        try:
            resized_template = cv2.resize(template, (new_w, new_h))
            _, template_thresh = cv2.threshold(resized_template, 150, 255, cv2.THRESH_BINARY_INV)
            
            res1 = cv2.matchTemplate(roi, resized_template, cv2.TM_CCOEFF_NORMED)
            res2 = cv2.matchTemplate(roi_thresh, template_thresh, cv2.TM_CCOEFF_NORMED)
            
            _, max_val1, _, _ = cv2.minMaxLoc(res1)
            _, max_val2, _, _ = cv2.minMaxLoc(res2)
            
            if max(max_val1, max_val2) > best_score:
                best_score = max(max_val1, max_val2)
        except:
            continue
    
    return best_score

def detect_community_cards(img_gray, rank_templates, suit_templates):
    """Detect all community cards"""
    card_boxes = detect_card_rectangles(img_gray, COMM_CARD_START_POSITION, COMM_CARD_END_POSITION)
    results = []
    
    for card_box in card_boxes:
        rank_start, rank_end, suit_start, suit_end = extract_rank_and_suit_regions(card_box, img_gray)
        
        best_rank, best_rank_score = None, -1.0
        for rank_name, template in rank_templates.items():
            if template is None:
                continue
            score = match_template_straight(img_gray, rank_start, rank_end, template)
            if score > best_rank_score:
                best_rank_score = score
                best_rank = rank_name
        
        best_suit, best_suit_score = None, -1.0
        for suit_name, template in suit_templates.items():
            if template is None:
                continue
            score = match_template_straight(img_gray, suit_start, suit_end, template)
            if score > best_suit_score:
                best_suit_score = score
                best_suit = suit_name
        
        card_name = f"{best_rank}{best_suit[0]}" if best_rank and best_suit else None
        results.append(card_name)
    
    return [c for c in results if c is not None]
