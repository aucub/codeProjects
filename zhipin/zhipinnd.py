import json
import os
import time
import nodriver as nd
from nodriver.cdp import network
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


def test_geek_get_job():
    driver = uc.Chrome(
        headless=False,
        user_data_dir=os.path.expanduser("~") + "/.config/google-chrome",
    )
    driver.get("https://www.zhipin.com")
    time.sleep(5)
    for i in range(1, 25):
        driver.get(
            "https://www.zhipin.com/wapi/zprelation/interaction/geekGetJob?page="
            + str(i)
            + "&tag=5&ka=header-personal&isActive=true"
        )
        time.sleep(5)
        page_source = driver.find_element(value="pre", by=By.TAG_NAME).text
        data = json.loads(page_source)
        if data["message"] == "Success":
            for jd in data["zpData"]["cardList"]:
                print(
                    "UPDATE jd SET communicated=1 WHERE id='" + jd["encryptJobId"] + "'"
                )
    time.sleep(5)
    driver.quit()


async def main():
    with open("saved_cookies/cookies.txt", "r") as file:
        json_cookies = json.load(file)
    cookie_params = []
    for json_cookie in json_cookies:
        cookie_param = network.CookieParam(
            name=json_cookie["name"],
            value=json_cookie["value"],
            url=json_cookie.get("url"),
            domain=json_cookie.get("domain"),
            path=json_cookie.get("path"),
            expires=json_cookie.get("expires"),
            secure=json_cookie.get("secure", False),
        )
        cookie_params.append(cookie_param)
    browser = await nd.start()
    await browser.cookies.set_all(cookies=cookie_params)
    for i in range(1, 25):
        page = await browser.get(
            "https://www.zhipin.com/wapi/zprelation/interaction/geekGetJob?page="
            + str(i)
            + "&tag=5&ka=header-personal&isActive=true"
        )
        await page.sleep(10)
        content = await page.get_content()
        data = json.loads(content)
        if data["message"] == "Success":
            for jd in data["zpData"]["cardList"]:
                print(
                    "UPDATE jd SET communicated=1 WHERE id='" + jd["encryptJobId"] + "'"
                )


if __name__ == "__main__":
    # uc.loop().run_until_complete(main())
    test_geek_get_job()
