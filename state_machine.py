import time
import random
from dvsa_bot import get_safari_data, monitor_for_slots, click_start_again_button, inject_credentials_and_login, click_change_booking_button, confirm_test_centre, wait_for_queue, sound_alarm_and_wait_for_human

def determine_current_state():
    """Reads the URL and HTML to figure out where we are."""
    url, html = get_safari_data()

    if "queue-it.net" in url: return "QUEUE"
    elif "incapsula" in html: return "CAPTCHA"
    elif "login" in url: return "LOGIN_PAGE"
    elif "manage" in url: return "DASHBOARD"
    elif "changeTestCentre" in html: return "TEST_CENTRE_SELECT"
    elif "BookingCalendar-dates" in html: return "CALENDAR"
    elif "timeout" in url or "oops" in html: return "TIMEOUT"
    else: return "UNKNOWN"

def run_state_machine():
    while True:
        state = determine_current_state()

        if state == "CALENDAR":
            monitor_for_slots() # Our current logic
        elif state == "TIMEOUT":
            click_start_again_button()
        elif state == "LOGIN_PAGE":
            inject_credentials_and_login(LICENCE_NUM, REF_NUM)
        elif state == "DASHBOARD":
            click_change_booking_button()
        elif state == "TEST_CENTRE_SELECT":
            confirm_test_centre()
        elif state == "QUEUE":
            wait_for_queue()
        elif state == "CAPTCHA":
            sound_alarm_and_wait_for_human()

        time.sleep(random.uniform(2, 5)) # Pause between actions