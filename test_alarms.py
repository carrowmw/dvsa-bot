import os
import time
from dvsa_bot import play_success_alarm, play_error_alarm

if __name__ == "__main__":
    print("Testing success alarm...")
    for _ in range(15):
        play_success_alarm()

    print("Testing error alarm...")
    for _ in range(5):
        play_error_alarm()