import requests
import traceback

base_url = "https://copilot.github1s.tk/api"


class gpt:
    def check(sec):
        # 设置聊天内容
        payload = {
            "model": "Balanced",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": "你需要扮演一个简历投递助手，你负责检查职位说明是否满足我的要求，返回true或者false，不需要额外的说明。要求：1.职位必须和Java开发或者软件测试，软件实施，软件运维，Python，Linux等计算机软件相关。2.没有要求线下面试或笔试或线下投递简历。3.没有说明不接受应届生，没有要求1年以上工作经验。注意1-2年经验要求等视为不符合要求。4.不是管理网络交换机，路由器，计算机硬件，公司资产，机房运维，设备安装等工作。不是与软件技术无关的工作。不是硬件测试或硬件开发的工作。5.没有解答客户问题，售后服务，售前服务等工作内容。没有销售，推广等工作内容。6.不是外包，外派，驻场等工作。职位说明："
                    + sec,
                },
            ],
        }
        try:
            # 发送请求
            response = requests.post(f"{base_url}/v1/chat/completions", json=payload)

            # 检查响应
            if response.status_code == 200:
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
            print("Error")
