# DVSA Auto-Booking & Session Keep-Alive Bot 🚗💨

A lightweight, background-friendly macOS automation script designed to work alongside manual booking or notification apps (like Testi). The bot supports two modes: keeping your Safari session active to prevent logouts/bans, or actively searching and auto-booking cancellation slots on the UK Driver and Vehicle Standards Agency (DVSA) portal.

---

## 🌟 Key Features

* **Dual Operation Modes:**
  * **`keep_alive` (Pivot Mode):** Relaxed refreshing to keep your active booking session logged in without getting banned. Alerts you immediately if the session expires, gets blocked, or requires a CAPTCHA.
  * **`auto_book`:** Aggressively monitors the calendar for whitelisted slots and books them automatically.
* **Intelligent Alarm Loop:** Continues sounding system alarms and sends a WhatsApp notification when a block or login redirect is detected. The alarm automatically stops once the user logs back in or solves the CAPTCHA.
* **Twilio WhatsApp Alerts:** Instantly sends real-time status alerts to your phone.
* **Anti-Detection Measures:** Implements random human-like delay times (e.g. 3–5 minutes in keep-alive mode) and handles queue pages (Queue-It) gracefully.
* **Audio Alarms:** Emits system alarms on success (`Glass`) and blocking/action-required pages (`Basso`) using native macOS audio commands.

---

## 💻 System Requirements & Browser Compatibility

### OS Requirements
* **macOS Only:** The bot utilizes native macOS features like AppleScript (`osascript`) to communicate with the browser and `afplay` to play sound alerts.

### Browser Compatibility
* **Safari (Primary):** The bot is built specifically to control **Safari**. It sends AppleScript commands to read the document status and refresh pages on the frontmost Safari tab.
* *Note on Chrome:* Although a `test_chrome.py` diagnostic file is present for testing Chrome, the active bot script (`dvsa_bot.py`) **only supports Safari**.

---

## ⚙️ Configuration & Customization

All configurations are located at the top of the [dvsa_bot.py](file:///Users/administrator/Code/python/dvsa_bot/dvsa_bot.py) file.

### 1. Bot Mode (`BOT_MODE`)
Select the bot's mode of operation:
```python
BOT_MODE = "keep_alive"  # Options: "keep_alive" or "auto_book"
```
* **`keep_alive` (Recommended for use with Testi):** Refreshes the portal at relaxed intervals to maintain your active session. If it detects a logout, timeout, or CAPTCHA, it sounds the `Basso` alarm every 15 seconds and alerts you via WhatsApp. Once you log back in/solve the CAPTCHA, it automatically resumes keep-alive refreshes.
* **`auto_book`:** Monitors the calendar, searches for slots, and triggers the auto-booking sequence.

### 2. Keep-Alive Delays
Adjust how often Safari refreshes to keep the session alive:
```python
KEEP_ALIVE_MIN_DELAY = 180  # Minimum delay (3 minutes)
KEEP_ALIVE_MAX_DELAY = 300  # Maximum delay (5 minutes)
```
*Refreshes are randomized between these two limits to prevent Cloudflare/Incapsula from detecting the bot.*

### 3. Alert Cooldown
```python
ALERT_COOLDOWN = 15  # Time in seconds between error alarms
```
*When your attention is required (e.g., CAPTCHA/login page detected), the bot plays an alarm and checks the page state again after this delay.*

### 4. Auto-Booking Whitelist (Only for `auto_book` mode)
Specify the exact dates and time windows you want to book in the `ALLOWED_SLOTS` dictionary:
```python
ALLOWED_SLOTS = {
    "2026-06-08": {"start": "08:00", "end": "18:00"},
    "2026-06-09": {"start": "13:00", "end": "18:00"},
}
```

---

## 🚀 How to Run the Bot

1. **Activate the Virtual Environment:**
   If you use `direnv`, the workspace has an `.envrc` that auto-activates `.venv`. Otherwise, activate it manually:
   ```bash
   source .venv/bin/activate
   ```

2. **Open Safari:**
   Open Safari, log into the DVSA booking portal, and navigate to the calendar/booking page. Leave this window active in the background.

3. **Start the Script:**
   ```bash
   python dvsa_bot.py
   ```

4. **Initialize:**
   Press **ENTER** in the terminal once you are on the correct page to start monitoring.

---

## 🛡️ WAF & Block Recovery Logic

* **Queue-It Pages:** If Safari is sent to a `queue-it.net` queue page, the bot logs `⏳ Queue page detected...` and waits 30 seconds before rechecking.
* **Transient Page Error Handling:** If Safari fails to read momentarily (e.g., during a refresh), the bot retries 3 times with a 1.5-second sleep before triggering a false alarm.
* **Persistent Alarms:** If a true CAPTCHA or logout is detected, the bot sends a WhatsApp notification and plays the macOS `Basso` audio warning. It will continue doing so at the configured `ALERT_COOLDOWN` interval. 
* **Automatic Recovery:** As soon as you solve the CAPTCHA or log back in manually, the bot will automatically play a success chime (`Glass`), send a WhatsApp confirming recovery, and return to the normal keep-alive loop.

---

## 📝 Logging & Diagnostics

* All logs are outputted to stdout and appended to `dvsa_bot_log.txt`.
* If you run into audio issues, run `python test_alarms.py` to test your macOS audio system.
