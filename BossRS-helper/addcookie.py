import undetected_chromedriver as uc
import time
import pickle

# 创建浏览器实例
driver = uc.Chrome(
    headless=False,
)

# 访问登录页面
driver.get("https://www.zhipin.com")

# 等待一段时间
time.sleep(5)

# 加载之前保存的cookie
with open("cookies.pkl", "rb") as f:
    cookies = pickle.load(f)

# 将 cookies 转换为字符串
cookies_string = str(cookies)

# 打印或保存 cookies 字符串
print(cookies_string)

# 将cookie添加到浏览器中
for cookie in cookies:
    driver.add_cookie(cookie)

time.sleep(5)

driver.get("https://www.zhipin.com")

time.sleep(5)

# 关闭浏览器
driver.quit()
