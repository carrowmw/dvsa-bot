import subprocess
import time
import random
import os
import json
from datetime import datetime
from twilio.rest import Client

# ==========================================
# ⚙️ BOT MODE & CONFIGURATION ⚙️
# "keep_alive" = Relaxed Safari keep-alive mode that alerts on block/logout/CAPTCHA.
# "auto_book"  = Original automated slot search and booking mode.
BOT_MODE = "keep_alive"

# --- Keep-Alive Mode Settings ---
# Frequency (in seconds) to refresh Safari to maintain the active session
KEEP_ALIVE_MIN_DELAY = 180  # 3 minutes
KEEP_ALIVE_MAX_DELAY = 300  # 5 minutes

# Cooldown (in seconds) between error alarms when blocked or session ends
ALERT_COOLDOWN = 15

# --- Auto-Booking Mode Settings ---
# True  = Script stops at the final page so you can click "Confirm changes" manually.
# False = Script clicks "Confirm changes" instantly (Fully automated).
DRY_RUN = True
# ==========================================

# --- TWILIO SETUP ---
TWILIO_ACCOUNT_SID = 'ACfe68286d1170ddec66122720d9619931'
TWILIO_AUTH_TOKEN = '[AuthToken]'
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- YOUR STRICT WHITELIST ---
ALLOWED_SLOTS = {
    "2026-05-10": {"start": "08:00", "end": "18:00"},
    "2026-05-11": {"start": "08:00", "end": "18:00"},
    "2026-05-12": {"start": "08:00", "end": "18:00"},
    "2026-05-13": {"start": "08:00", "end": "18:00"},
    "2026-05-14": {"start": "08:00", "end": "18:00"},
    "2026-05-15": {"start": "08:00", "end": "18:00"},
    "2026-05-16": {"start": "08:00", "end": "18:00"},
    "2026-05-17": {"start": "13:00", "end": "18:00"},
    "2026-05-18": {"start": "13:00", "end": "18:00"},
    "2026-05-19": {"start": "13:00", "end": "18:00"},
    "2026-05-20": {"start": "08:00", "end": "18:00"},
    "2026-05-21": {"start": "08:00", "end": "18:00"},
    "2026-05-26": {"start": "08:00", "end": "18:00"},
    "2026-05-27": {"start": "08:00", "end": "18:00"},
    "2026-05-28": {"start": "08:00", "end": "18:00"},
    "2026-05-29": {"start": "08:00", "end": "18:00"},
    "2026-05-30": {"start": "08:00", "end": "18:00"},
    "2026-05-31": {"start": "08:00", "end": "18:00"},
    "2026-06-01": {"start": "08:00", "end": "18:00"},
    "2026-06-02": {"start": "08:00", "end": "18:00"},
    "2026-06-03": {"start": "08:00", "end": "18:00"},
    "2026-06-04": {"start": "08:00", "end": "18:00"},
    "2026-06-05": {"start": "08:00", "end": "18:00"},
    "2026-06-08": {"start": "08:00", "end": "18:00"},
    "2026-06-09": {"start": "08:00", "end": "18:00"},
    "2026-06-10": {"start": "08:00", "end": "18:00"},
    "2026-06-11": {"start": "08:00", "end": "18:00"},
    "2026-06-12": {"start": "08:00", "end": "18:00"},
    "2026-06-13": {"start": "08:00", "end": "18:00"},
    "2026-06-14": {"start": "08:00", "end": "18:00"},
    "2026-06-15": {"start": "08:00", "end": "18:00"},
    "2026-06-16": {"start": "08:00", "end": "18:00"},
    "2026-06-17": {"start": "08:00", "end": "18:00"},
    "2026-06-19": {"start": "08:00", "end": "18:00"}
}

def log_message(message):
    print(message)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("dvsa_bot_log.txt", "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

def play_success_alarm(): os.system('afplay /System/Library/Sounds/Glass.aiff')
def play_error_alarm(): os.system('afplay /System/Library/Sounds/Basso.aiff')

def send_whatsapp_alert(date_found, time_found):
    log_message("📱 Sending WhatsApp notification...")
    try:
        formatted_date = datetime.strptime(date_found, "%Y-%m-%d").strftime("%d/%m")
        variables = f'{{"1":"{formatted_date}","2":"{time_found}"}}'
        message = TWILIO_CLIENT.messages.create(
            from_='whatsapp:+14155238886',
            content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
            content_variables=variables,
            to='whatsapp:+447551973789'
        )
        log_message(f"✅ WhatsApp sent! SID: {message.sid}")
    except Exception as e:
        log_message(f"⚠️ Failed to send WhatsApp: {e}")

def send_session_whatsapp_alert(status_msg):
    log_message(f"📱 Sending WhatsApp Session Alert: {status_msg}...")
    try:
        # Reusing the existing pre-approved Twilio template to send a custom status message
        variables = f'{{"1":"ALERT!","2":"{status_msg}"}}'
        message = TWILIO_CLIENT.messages.create(
            from_='whatsapp:+14155238886',
            content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
            content_variables=variables,
            to='whatsapp:+447551973789'
        )
        log_message(f"✅ WhatsApp alert sent! SID: {message.sid}")
    except Exception as e:
        log_message(f"⚠️ Failed to send WhatsApp alert: {e}")

def run_applescript(js_code):
    script = f'''
    tell application "Safari"
        return do JavaScript "{js_code}" in document 1
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "error"

def check_waf_block():
    output = run_applescript("document.URL + '|||' + document.title + '|||' + document.documentElement.innerHTML.substring(0, 2000)")
    if output == "error" or "|||" not in output: return "read_error"
    parts = output.lower().split("|||")
    url, title, html = parts[0], parts[1], parts[2] if len(parts) > 2 else ""

    if "queue-it.net" in url: return "queue"
    if "/login" in url: return "blocked"
    exact_phrases = ["incapsula", "error 15", "session timeout", "oops! you went away", "additional security check"]
    for phrase in exact_phrases:
        if phrase in html or phrase in title: return "blocked"
    return "clean"

def is_time_allowed(time_str, date_str):
    """Parses '9:17am' and checks if it falls within the allowed start/end bounds."""
    try:
        t = datetime.strptime(time_str.replace(" ", "").lower(), "%I:%M%p").time()
        start = datetime.strptime(ALLOWED_SLOTS[date_str]['start'], "%H:%M").time()
        end = datetime.strptime(ALLOWED_SLOTS[date_str]['end'], "%H:%M").time()
        return start <= t <= end
    except Exception as e:
        log_message(f"Time parse error on {time_str}: {e}")
        return False

# ==========================================
# AUTO-BOOKING STATE MACHINE
# ==========================================

def get_available_dates():
    js = "Array.from(document.querySelectorAll('td.BookingCalendar-date--bookable a')).map(a => a.getAttribute('data-date')).join(',')"
    dates_csv = run_applescript(js)
    if dates_csv and dates_csv != "error":
        return [d for d in dates_csv.split(',') if d]
    return []

def click_date(target_date):
    js = f"document.querySelector('a[data-date=\"{target_date}\"]').click();"
    run_applescript(js)
    time.sleep(1.5) # Wait for AJAX time slots to load

def get_available_times():
    js = "Array.from(document.querySelectorAll('label[for^=\"slot-\"]')).map(l => l.getAttribute('for') + '|' + l.innerText.trim()).join(',')"
    times_csv = run_applescript(js)
    slots = []
    if times_csv and times_csv != "error":
        for item in times_csv.split(','):
            if '|' in item:
                slot_id, slot_time = item.split('|')
                slots.append({'id': slot_id, 'time': slot_time})
    return slots

def submit_time_and_accept_warning(slot_id):
    js = f"""
    document.getElementById('{slot_id}').click();
    document.getElementById('slot-chosen-submit').click();
    setTimeout(function() {{
        var warningBtn = document.getElementById('slot-warning-continue');
        if(warningBtn) warningBtn.click();
    }}, 600);
    """
    run_applescript(js)

def check_for_final_page():
    """Returns true if the final green 'Confirm changes' button is on screen."""
    js = "document.getElementById('confirm-changes') !== null"
    return run_applescript(js) == "true"

def finalize_booking():
    if DRY_RUN:
        log_message("🛑 DRY RUN ACTIVE: Pausing on final screen. CLICK IT YOURSELF!")
        return
    log_message("⚡ DRY RUN OFF: INJECTING FINAL CLICK!")
    run_applescript("document.getElementById('confirm-changes').click();")

def refresh_safari(): run_applescript("window.location.reload();")

def main():
    print(f"🍏 DVSA BOT STARTED (Mode: {BOT_MODE}) 🍏")
    input("Press ENTER when looking at the DVSA calendar/booking page in Safari...")
    log_message(f"\n🟢 MONITORING SESSION STARTED ({BOT_MODE} mode) 🟢")

    if BOT_MODE == "keep_alive":
        alert_sent = False
        while True:
            waf_status = check_waf_block()

            if waf_status == "clean":
                if alert_sent:
                    log_message("🟢 Session restored! Resuming keep-alive...")
                    send_session_whatsapp_alert("Session Restored. Keep-alive resumed.")
                    play_success_alarm()
                    alert_sent = False
                
                # Relaxed, randomized keep-alive delay
                delay = random.uniform(KEEP_ALIVE_MIN_DELAY, KEEP_ALIVE_MAX_DELAY)
                log_message(f"Session is clean. Refreshing in {delay:.2f}s to keep-alive...")
                time.sleep(delay)
                refresh_safari()
                # Post-refresh pause for page load
                time.sleep(random.uniform(3.0, 6.0))

            elif waf_status == "queue":
                log_message("⏳ Queue page detected. Waiting 30s to recheck...")
                time.sleep(30)

            elif waf_status in ("blocked", "read_error"):
                # If it's a read error, retry a few times before sounding alarm
                if waf_status == "read_error":
                    retries = 3
                    for i in range(retries):
                        time.sleep(1.5)
                        waf_status = check_waf_block()
                        if waf_status != "read_error":
                            break
                
                # Recheck if still blocked or read_error after retries
                if waf_status in ("blocked", "read_error"):
                    log_message(f"🛑 ACTION REQUIRED: Session ended/blocked (status: {waf_status}).")
                    if not alert_sent:
                        send_session_whatsapp_alert(f"Action required! Session status: {waf_status}")
                        alert_sent = True
                    
                    play_error_alarm()
                    time.sleep(ALERT_COOLDOWN)
    else:
        # Original auto_book mode logic
        while True:
            waf_status = check_waf_block()

            if waf_status == "queue":
                log_message("⏳ Queue detected. Waiting...")
                time.sleep(30)
                continue
            if waf_status == "blocked":
                log_message("🛑 BLOCK DETECTED. Human intervention required.")
                for _ in range(5): play_error_alarm()
                break

            available_dates = get_available_dates()
            target_date = None

            # Find the first available date that is in our whitelist
            for d in available_dates:
                if d in ALLOWED_SLOTS:
                    target_date = d
                    break

            if target_date:
                log_message(f"🚨 FOUND WHITELISTED DATE: {target_date}! Checking times...")
                click_date(target_date)

                available_times = get_available_times()
                target_slot = None

                # Find the first time on this date that fits our bounds
                for slot in available_times:
                    if is_time_allowed(slot['time'], target_date):
                        target_slot = slot
                        break

                if target_slot:
                    log_message(f"🎯 PERFECT TIME FOUND: {target_slot['time']}! Booking now...")
                    submit_time_and_accept_warning(target_slot['id'])

                    # Wait for the next page to load
                    time.sleep(4)

                    if check_for_final_page():
                        send_whatsapp_alert(target_date, target_slot['time'])
                        finalize_booking()
                        for _ in range(15): play_success_alarm(); time.sleep(0.5)
                        break
                    else:
                        log_message("⚠️ Error: Failed to reach final confirmation page.")
                else:
                    log_message("❌ Times found, but none fit the whitelist bounds. Ignoring.")

            # Humanized delay before next refresh
            delay = max(30.0, min(random.gauss(55.0, 12.0), 90.0)) + random.uniform(0.1, 0.9)
            log_message(f"No valid slots. Refreshing in {delay:.2f}s...")
            time.sleep(delay)
            refresh_safari()
            time.sleep(random.uniform(2.5, 4.5))

if __name__ == "__main__":
    main()