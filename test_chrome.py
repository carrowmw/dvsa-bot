import undetected_chromedriver as uc
import traceback
import time

def run_diagnostic():
    print("🚀 Attempting to launch Chrome...")
    try:
        options = uc.ChromeOptions()
        # Adding a few flags that sometimes help stabilize macOS M-series chips
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # FIX: Force the driver to match your installed Chrome version (v147)
        driver = uc.Chrome(options=options, version_main=147)

        print("✅ Chrome successfully launched!")
        driver.get("https://google.com")

        print("Keeping browser open for 15 seconds to verify stability...")
        time.sleep(15)
        driver.quit()

    except Exception as e:
        print("\n❌ CRASH DETECTED! Here is the exact error:")
        print("-" * 40)
        traceback.print_exc()
        print("-" * 40)

if __name__ == "__main__":
    run_diagnostic()