import requests
import traceback
import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

default_letter = "您好，不知道这个岗位是否还有在招人，我仔细查看了您发布的职位信息，觉得自己比较适合，希望能得到您的回复~"

base_url = ""
token = ""

headers = {"Authorization": f"Bearer {token}"}


class Chat:
    def check(description):
        payload = {
            "model": "gpt-4",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": "我希望你充当简历投递助手，你将检查职位描述是否完全符合以下所有要求。请提供一个“true”或“false”的结果，无需任何解释。要求：1.该职位必须与计算机软件相关，例如Java开发、软件测试、软件运维开发、软件实施或软件运维。2.不要求线下投递简历。不应指定居住地。3.职位描述不应提及不接受应届毕业生，不应要求相关工作经验。4.不应涉及与硬件相关的任务，比如管理网络交换机、路由器、计算机硬件、公司资产、数据中心运营或设备安装。它也不应该是硬件测试或硬件开发的角色。5.该工作不应涉及销售活动或营销等及类似任务。6.该工作没有轮班、夜班工作，不是工厂/生产线工作。7.不应要求英语cet六级或其他证书，不应要求日语等中英之外语言。7.不应要求熟练C#，PHP，Golang或Android。9.不应要求毕业于985/211等高校。职位说明："
                    + description,
                },
            ],
        }
        try:
            response = requests.post(
                f"{base_url}/v1/chat/completions", json=payload, headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                content = content.lower()
                if "true" in content:
                    return True
                else:
                    return False
            else:
                print("Error:", response.status_code, response.text)
                return True
        except Exception:
            traceback.print_exc()
            return True

    def send(text):
        payload = {
            "model": "gpt-4",
            "stream": False,
            "messages": [
                {"role": "user", "content": text},
            ],
        }
        try:
            response = requests.post(
                f"{base_url}/v1/chat/completions", json=payload, headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                print("Error:", response.status_code, response.text)
        except Exception:
            traceback.print_exc()

    def generate_letter(job_description):
        with open("resume.txt", "r", encoding="utf-8") as file:
            context = file.read()
        prompt = (
            """
            你将扮演一位求职者的角色,根据上下文里的简历内容以及应聘工作的描述,直接给HR写一个礼貌专业且字数严格限制在120字以内的求职消息,要求能够用专业的语言结合简历中的经历和技能,并结合应聘工作的描述来阐述自己的优势,尽最大可能打动招聘者。始终使用中文来进行消息的编写。开头是你好, 结尾没有多余的内容。这是一份求职消息，不要包含求职内容以外的东西,例如“根据您上传的求职要求和个人简历,我来帮您起草一封求职邮件：”这一类的内容，不需要个人姓名这些等待修改的信息比如“[你的名字]”这一类的内容，不需要“非常高兴能向您推荐我自己”这一类情绪内容，不要假设个人信息比如“我是一名2024年应届本科毕业生”这一类的内容，以便于我直接自动化复制粘贴发送。
            工作描述: """
            + job_description
            + """
            简历内容:"""
            + context
            + """
            要求:
            根据工作描述，寻找出简历里最合适的技能都有哪些?求职者的优势是什么?
        """
        )
        letter = Chat.send(prompt)
        if letter:
            letter = letter.replace("\n", " ").replace("  ", "")
        else:
            letter = default_letter
        return letter

    def send_letter_to_chat_box(driver: uc.Chrome, letter):
        chat_box = driver.find_element(By.CSS_SELECTOR, "#chat-input")
        chat_box.clear()
        chat_box.send_keys(letter)
        time.sleep(3)
        driver.find_element(
            By.CSS_SELECTOR,
            "#container > div > div > div.chat-conversation > div.message-controls > div > div.chat-op > button",
        ).click()
        time.sleep(1)


def main():
    letter = Chat.generate_letter(
        """
    岗位职责:
    1、完成领导交办的工作。
    任职要求：
    1、富有责任感和团队协作精神。
    """
    )
    print(letter)


if __name__ == "__main__":
    main()
