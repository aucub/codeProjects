import undetected_chromedriver as uc
import time
import pickle

driver = uc.Chrome(
    headless=False,
)

driver.get("https://www.zhipin.com")

time.sleep(5)

with open("cookies.pkl", "rb") as f:
    cookies = pickle.load(f)

# cookies_string = str(cookies)

# print(cookies_string)

for cookie in cookies:
    driver.add_cookie(cookie)

time.sleep(5)

driver.get("https://www.zhipin.com")

time.sleep(9999)

driver.quit()
