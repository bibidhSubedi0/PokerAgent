import pyautogui
from screeninfo import get_monitors

# Get all connected monitors
monitors = get_monitors()

# Assuming the second monitor is the second in the list (index 1)
second_monitor = monitors[1]

# Specify the pixel coordinates you want to click on the second monitor
x, y = 1257, 970

# Calculate the absolute position on the screen by adding the second monitors offset
absolute_x = second_monitor.x + x
absolute_y = second_monitor.y + y

# Move the mouse to the specified position on the second monitor and click
pyautogui.click(absolute_x, absolute_y)

print(f"Mouse clicked at position: ({absolute_x}, {absolute_y}) on the second monitor.")
