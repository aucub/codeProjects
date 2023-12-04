import requests
import traceback

# 设置API的基本URL
base_url = "https://copilot.github1s.tk"


class gpt:
    def check(sec):
        # 设置聊天内容
        payload = {
            "model": "Balanced",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": "我希望你充当简历投递助手，你将检查职位描述是否完全符合以下所有要求。请提供一个“true”或“false”的结果，无需任何解释。要求：1.该职位必须与计算机软件相关，例如Java开发、软件测试、软件运维开发、软件实施或软件运维。2.不要求线下面试、线下笔试、线下投递简历。3.职位描述不应提及不接受应届毕业生，不应要求工作经验。4.不应涉及与硬件相关的任务，比如管理网络交换机、路由器、计算机硬件、公司资产、桌面支持、网络运营、数据中心运营或设备安装。它也不应该是硬件测试或硬件开发的角色。5.该工作不应涉及回复客户询问、提供售后支持、售前支持、销售活动或营销等任务。6.该工作不应是外包、派遣工作。没有轮班、夜班工作。职位说明："
                    + sec,
                },
            ],
        }
        try:
            # 发送请求
            response = requests.post(f"{base_url}/v1/chat/completions", json=payload)

            # 检查响应
            if response.status_code == 200:
                print(sec)
                print("Response from API:", response.json())
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                content = content.lower()
                print(content)
                if "true" in content:
                    return True
                else:
                    return False
            else:
                print("Error:", response.status_code, response.text)
                return False
        except:
            traceback.print_exc()
