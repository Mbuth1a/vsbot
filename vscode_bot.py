import time
import random
import threading
import pyautogui
from pynput import mouse, keyboard

# Built-in Windows sound module (no extra pip install needed)
try:
    import winsound
    def play_sound(action):
        if action == "resume":
            winsound.Beep(1000, 150)  # High beep
        elif action == "pause":
            winsound.Beep(500, 200)   # Low beep
except ImportError:
    def play_sound(action):
        pass

# --- Configuration Settings ---
CONFIG = {
    "file_read_time_seconds": 12,    # Time spent per file before switching tabs
    "scroll_speed": 1,               # Base scroll speed (1 = smooth tick)
    "reading_pause_chance": 0.25,    # Chance to simulate reading a function
    "slight_backscroll_chance": 0.10,# Chance to scroll back up slightly
    "pause_on_user_scroll": True,    # If True: touching your scroll wheel pauses the bot indefinitely
}

# State flags
is_running = True
is_paused = False

pyautogui.FAILSAFE = True

# --- Natural Scrolling Mechanics ---
def smooth_scroll_step(direction=-1, steps=3, step_delay=0.08):
    for _ in range(steps):
        if not is_running or is_paused:
            break
        pyautogui.scroll(direction * CONFIG["scroll_speed"])
        time.sleep(step_delay + random.uniform(-0.015, 0.02))

def humanized_reading_pattern():
    # 1. Normal downward scroll
    smooth_scroll_step(direction=-1, steps=random.randint(2, 5))

    # 2. Reading pause simulation
    if random.random() < CONFIG["reading_pause_chance"]:
        time.sleep(random.uniform(1.2, 3.0))

    # 3. Occasional back-scroll simulation
    if random.random() < CONFIG["slight_backscroll_chance"]:
        smooth_scroll_step(direction=1, steps=random.randint(1, 2))
        time.sleep(random.uniform(0.5, 1.0))

# --- File Switching ---
def switch_to_next_file():
    print("[Action] Switching to next open tab...")
    pyautogui.hotkey('ctrl', 'pagedown')
    time.sleep(1.0)

# --- Infinite Automation Loop ---
def bot_loop():
    global is_running, is_paused

    print("\n" + "=" * 50)
    print(" [BOT READY] Click into VS Code now!")
    print(" -> Runs continuously until you pause it.")
    print(" -> Press F8 or manually scroll to PAUSE.")
    print(" -> Press F8 again to RESUME.")
    print(" -> Press Esc to EXIT.")
    print("=" * 50 + "\n")
    
    time.sleep(4)  # 4 seconds to focus VS Code

    while is_running:
        if is_paused:
            time.sleep(0.1)
            continue

        file_start = time.time()
        print("[Action] Reading current file...")

        # Keep scrolling through current file
        while (time.time() - file_start < CONFIG["file_read_time_seconds"]) and is_running:
            if is_paused:
                break
            humanized_reading_pattern()
            time.sleep(random.uniform(0.3, 0.7))

        # Switch to next file tab (loops infinitely across all open tabs)
        if is_running and not is_paused:
            switch_to_next_file()

# --- Pause / Resume Controller ---
def toggle_pause(force_state=None, trigger_source="User"):
    global is_paused
    if force_state is not None:
        if is_paused == force_state:
            return  # Already in desired state
        is_paused = force_state
    else:
        is_paused = not is_paused

    if is_paused:
        print(f"\n[PAUSED] ({trigger_source}) Bot is stopped. Press F8 to resume.")
        play_sound("pause")
    else:
        print(f"\n[RESUMED] ({trigger_source}) Bot is running again.")
        play_sound("resume")

# --- Event Triggers (Mouse Scroll & Hotkeys) ---
def on_mouse_scroll(x, y, dx, dy):
    """
    Trigger: If you manually scroll your trackpad or mouse wheel,
    the bot immediately pauses until you explicitly hit F8 to resume.
    """
    if CONFIG["pause_on_user_scroll"] and not is_paused:
        toggle_pause(force_state=True, trigger_source="Manual Scroll Detected")

def on_key_press(key):
    global is_running
    try:
        if key == keyboard.Key.f8:
            toggle_pause(trigger_source="F8 Key")
        elif key == keyboard.Key.esc:
            print("\n[STOPPED] Esc pressed. Exiting...")
            is_running = False
            return False
    except Exception:
        pass

# --- Main Entry Point ---
if __name__ == "__main__":
    # Mouse scroll listener
    mouse_listener = mouse.Listener(on_scroll=on_mouse_scroll)
    mouse_listener.daemon = True
    mouse_listener.start()

    # Keyboard hotkey listener
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.daemon = True
    keyboard_listener.start()

    # Main bot thread
    bot_thread = threading.Thread(target=bot_loop)
    bot_thread.start()
    bot_thread.join()

    print("[Finished] Bot closed cleanly.")