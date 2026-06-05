# DVSA Auto-Booking Bot 🚗💨

A lightweight, background-friendly macOS automation script designed to monitor the UK Driver and Vehicle Standards Agency (DVSA) booking system, check for cancellation slots, and auto-book them based on your strict preferences.

---

## 🌟 Key Features

* **Strict Whitelisting:** Define exact dates and time ranges (e.g., only mornings or afternoons) you are willing to accept.
* **Twilio WhatsApp Alerts:** Instantly receive WhatsApp notifications on your phone when a match is found and/or booked.
* **Anti-Detection Measures:** Uses humanized, randomized delays (between 30s and 90s) and checks for Web Application Firewalls (WAF)/Queue pages.
* **Audio Alarms:** Emits system alarms on success (`Glass`) and blocking errors (`Basso`) using native macOS audio.
* **Safety Switches:** Configurable dry-run mode to ensure you can inspect details before confirming.

---

## 💻 System Requirements & Browser Compatibility

### OS Requirements
* **macOS Only:** The bot relies heavily on macOS system integrations such as AppleScript (`osascript`) to communicate with the browser, and `afplay` for playing audio alerts.

### Browser Compatibility
* **Safari (Primary):** The bot is built specifically to control **Safari**. It sends AppleScript commands to read the HTML context and inject JavaScript directly into the frontmost Safari tab. This allows the bot to run with extremely low overhead and minimal risk of triggering browser-based bot protection.
* *Note on Chrome:* Although a `test_chrome.py` diagnostic file is present for testing `undetected-chromedriver` frameworks, the active auto-booker script (`dvsa_bot.py`) **only supports Safari**.

---

## ⚙️ Configuration & Customization

Before launching the bot, you must configure your settings directly in `dvsa_bot.py`.

### 1. Safety Switch (`DRY_RUN`)
Modify the `DRY_RUN` variable on **Line 13**:
```python
DRY_RUN = True  # Set to False to auto-confirm bookings
```
* **`DRY_RUN = True` (Recommended):** The bot automatically completes all navigation, selects the slot, accepts warnings, and stops on the final page showing the **"Confirm changes"** button. It then plays success alarms and alerts you via WhatsApp so you can review and click the final confirm button manually.
* **`DRY_RUN = False`:** The bot will automatically inject a final click to confirm and lock in the booking without human intervention.

### 2. Setting Your Preferred Times (Date/Time Whitelist)
You must specify the exact dates and times you want to check inside the `ALLOWED_SLOTS` dictionary:

```python
ALLOWED_SLOTS = {
    "2026-06-08": {"start": "08:00", "end": "18:00"},
    "2026-06-09": {"start": "13:00", "end": "18:00"},
    # Format: "YYYY-MM-DD": {"start": "HH:MM", "end": "HH:MM"} (24-hour time)
}
```

* **How it works:**
  1. The bot retrieves the list of bookable dates shown on the calendar page.
  2. If a date is found in your `ALLOWED_SLOTS` keys, it clicks on that date.
  3. It retrieves all time slots for that date (e.g., `"9:17am"`, `"2:45pm"`).
  4. It parses each time and checks if it falls within the `start` and `end` window you defined for that specific day.
  5. If a time slot matches your whitelist, booking begins immediately. If not, it skips the date and continues monitoring.

### 3. WhatsApp Notifications Setup
The bot uses the Twilio API to send WhatsApp messages when a matching slot is found.

Modify the Twilio settings under the `--- TWILIO SETUP ---` section:
* **`TWILIO_ACCOUNT_SID`** & **`TWILIO_AUTH_TOKEN`**: Your Twilio account credentials.
* **Recipient Number:** Update the `to='whatsapp:+447551973789'` parameter inside `send_whatsapp_alert()` to your personal phone number (ensure it is verified in your Twilio Sandbox if using a trial account).
* **Twilio Content Template:** It uses template ID `HXb5b62575e6e4ff6129ad7c8efe1f983e` to bypass Twilio's restrictions on sending free-form outbound WhatsApp messages. This template takes two parameters:
  1. `1`: The date found (formatted as `DD/MM`).
  2. `2`: The time found (e.g., `10:15am`).

---

## 🚀 How to Run the Bot

1. **Activate the Virtual Environment:**
   If you use `direnv`, the workspace has an `.envrc` that auto-activates `.venv`. Otherwise, activate it manually:
   ```bash
   source .venv/bin/activate
   ```

2. **Open Safari:**
   Open Safari and log in to the DVSA booking portal. Navigate through the queue/login and go directly to the page displaying the booking calendar. Keep this Safari window open and visible.

3. **Start the Script:**
   In your terminal, run:
   ```bash
   python dvsa_bot.py
   ```

4. **Initialize:**
   The script will display:
   `🍏 AUTO-BOOKER STARTED (DRY_RUN = True) 🍏`
   `Press ENTER when looking at the DVSA calendar...`
   
   Once you are on the calendar page, press **ENTER** in the terminal to start monitoring.

---

## 🛡️ Anti-Block & Security Features

* **Queue-It Handling:** If the DVSA portal redirects Safari to a `queue-it.net` queue page, the script detects it, logs `⏳ Queue detected. Waiting...`, and sleeps for 30 seconds before rechecking.
* **WAF/Cloudflare Detection:** If the site presents a block page, Cloudflare challenge, session timeout, or additional security checks, the bot:
  1. Logs `🛑 BLOCK DETECTED. Human intervention required.`
  2. Plays 5 loud error alarms using macOS `Basso` sound.
  3. Pauses execution so you don't get banned.
* **Humanized Refreshing:** Refreshes the Safari page at randomized intervals drawn from a Gaussian distribution (averaging ~55 seconds) rather than a fixed rate to look like natural human activity.

---

## 📝 Logging & Diagnostics

* All actions, found slots, warnings, and errors are printed to stdout and saved in `dvsa_bot_log.txt` with timestamps.
* If you run into audio issues, you can run `python test_alarms.py` to diagnose your macOS audio system.
