import requests
import traceback
import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from rsinfo import RsInfo

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

    def generate_letter(rsinfo: RsInfo):
        with open("resume.txt", "r", encoding="utf-8") as file:
            context = file.read()
        prompt = (
            """
            你正在进行一次职位申请，你需要根据提供的简历内容和申请工作的职位描述，撰写一条120字以内的求职消息。这需要你以专业的语言和表达，准确地聚焦你的优势。以下是一些注意事项：
            1、这是一条直接的求职消息，不是邮件格式。
            2、使用简体中文进行消息的撰写，确保消息清晰易懂。
            3、措词需要简洁、专业，尽量避免过于口语化的表达。
            4、在开头，使用“你好”称呼对方，避免添加任何其他的敬语，不需要结尾词。
            4、避免使用任何具体的个人信息，如你的姓名或是个人经历等。
            5、不得添加任何情绪化的语言，如“非常高兴能向您推荐我自己”等。
            6、消息需要一次完成，避免加入任何括号或中括号标注的内容，避免加入任何如"[工作名]"、"[你的名字]"等需要二次修改的内容。
            7、只包含和求职直接相关的内容，避免无关的信息，如“我来帮您写一条求职消息”。
            8、避免使用任何非实际或者假设性的信息，例如不需要“我是一名应届本科毕业生，我有3年经验，我是一位自动化测试工程师”这一类内容。
            9、注意职位描述可能存在的拼写错误，不能容许出现在求职消息中。
            职位名称: """
            + rsinfo.name
            + """
            职位描述: """
            + rsinfo.description
            + """
            简历内容:"""
            + context
            + """
            要求:
            根据职位描述，寻找出简历里最合适的技能和求职者的优势。
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
