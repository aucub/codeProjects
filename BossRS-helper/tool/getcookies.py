import os
import undetected_chromedriver as uc
import time
import pickle

driver = uc.Chrome(
    headless=False,
    user_data_dir=os.path.expanduser("~") + "/.config/google-chrome",
)

driver.get("https://www.zhipin.com")

time.sleep(5)

cookies = driver.get_cookies()

with open("../cookies/cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

time.sleep(5)

driver.quit()
