import os
import undetected_chromedriver as uc
import time
import pickle

# 创建浏览器实例
driver = uc.Chrome(
    headless=False,
    user_data_dir=os.path.expanduser("~") + "/.config/google-chrome",
)

# 访问登录页面
driver.get("https://www.zhipin.com")

# 等待一段时间
time.sleep(15)

# 获取当前浏览器的cookie
cookies = driver.get_cookies()

# 保存cookie到文件
with open("cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

time.sleep(5)

# 关闭浏览器
driver.quit()
