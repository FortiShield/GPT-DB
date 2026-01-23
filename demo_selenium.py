import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = False   # অবশ্যই False হতে হবে, যাতে VNC ডেস্কটপে ব্রাউজারের কার্যকলাপ দেখা যায়

driver = webdriver.Firefox(options=options)

try:
    print("🌍 ওয়েবপেজ খুলছে https://www.python.org ...")
    driver.get("https://www.python.org")

    time.sleep(5)  # পৃষ্ঠা লোড হওয়ার জন্য অপেক্ষা করুন

    title = driver.title
    print(f"✅ ওয়েবপেজের শিরোনাম: {title}")

    screenshot_path = "/root/screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"📸 স্ক্রিনশট সেভ করা হয়েছে {screenshot_path}")

finally:
    driver.quit()
