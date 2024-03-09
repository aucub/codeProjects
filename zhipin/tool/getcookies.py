import json
import os
import time
import undetected_chromedriver as uc


class GetCookies:
    def test_get_cookies(self):
        driver = uc.Chrome(
            headless=False,
            user_data_dir=os.path.expanduser("~") + "/.config/google-chrome",
        )
        driver.get("https://www.zhipin.com")
        time.sleep(5)
        cookies = driver.get_cookies()
        cookies_json = json.dumps(cookies)
        current_file_path = os.path.abspath(__file__)
        parent_dir_path = os.path.dirname(current_file_path)
        grandparent_dir_path = os.path.dirname(parent_dir_path)
        if not os.path.exists(grandparent_dir_path + "/saved_cookies/"):
            os.makedirs(grandparent_dir_path + "/saved_cookies/", exist_ok=True)
        with open(grandparent_dir_path + "/saved_cookies/cookies.txt", "w") as f:
            f.write(cookies_json)
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    gc = GetCookies()
    gc.test_get_cookies()
