# Poker Vision Bot (Computer Vision + Automation)

A real-time poker assistant that **reads the game directly from the screen**, understands the current hand using computer vision, asks a custom decision engine what to do, and **automatically performs the action** (fold / check / raise).

This project does **not** hook into the game.  
Everything is done via **screen capture + image processing + mouse automation**.

---

## What This Does

- Captures the poker table from a specific monitor
- Detects:
  - Your **hole cards** (rank + suit, tilted)
  - **Community cards** (straight layout)
  - Whether it is **your turn**
- Builds a structured game state
- Sends the state to a custom engine (`OwnEngine.analyze_game_state`)
- Executes the recommended move by clicking the UI
- Displays a live debug overlay

---

## How It Works (High Level)

1. **Screen Capture**
   - Uses `mss` to grab frames from a chosen monitor
   - All detection is done on raw screenshots

2. **Card Detection**
   - Template matching via OpenCV
   - Separate logic for:
     - Tilted hole cards
     - Straight community cards
   - Handles edge cases like the `"10"` rank (two digits)

3. **Turn Detection**
   - Checks for a visual indicator (`palo.png`)
   - Prevents actions when it’s not your turn

4. **Decision Engine**
   - Game state is passed to:
     ```python
     OwnEngine.analyze_game_state(game_state)
     ```
   - Engine returns:
     - `("FOLD",)`
     - `("CHECK",)` / `("CALL",)`
     - `("RAISE", amount)` where `amount ∈ [0, 1]`

5. **Automation**
   - Uses `pyautogui` to click Fold / Check / Raise
   - Raise size is mapped linearly to the raise slider

## Usage

### Pre-Flop
<img width="3840" height="1080" alt="Screenshot (17)" src="https://github.com/user-attachments/assets/2369ed61-2126-4962-b5a5-20e2c5c95e5a" />

### Flop
<img width="3840" height="1080" alt="Screenshot (19)" src="https://github.com/user-attachments/assets/d61dfff5-d84b-4ef3-94ec-9e5ca62efe17" />

### River
<img width="3840" height="1080" alt="Screenshot (20)" src="https://github.com/user-attachments/assets/d188fea4-10d8-435f-9433-c05cb4a58bcc" />

### Shell
<img width="1934" height="1080" alt="Screenshot (21)" src="https://github.com/user-attachments/assets/00c3acf4-2c8c-4403-a2de-80f8ed24eec0" />



## Requirements

- Python 3.9+
- Windows (mouse automation + screen capture assumptions)
- Stable screen resolution & UI layout

Python dependencies:
- opencv-python
- numpy
- mss
- pyautogui
- screeninfo
- Pillow

---

## Configuration Notes

- **All coordinates are hard-coded**
  - Card positions
  - Action buttons
  - Turn indicator
- Changing resolution, scaling, or table theme **will break detection**
- `SAMPLE_INTERVAL` controls how often decisions are made

---

## Controls

- `q` → Quit
- `d` → Force next detection cycle (debug)

A live OpenCV window shows:
- Detection regions
- Identified cards
- Engine recommendation

---

## Safety Notes

- This project **automates mouse input**
- Do **NOT** run while interacting manually
- Always test with:
  - Fake money
  - Paused engine
  - Logging only (no clicks)

---

## Disclaimer

This project is for **educational and technical experimentation only**.  
Using automation tools on real money platforms may violate terms of service.

You are fully responsible for how and where this is used.

---

## Author Notes

- No ML
- No OCR
- Pure CV + geometry + templates
