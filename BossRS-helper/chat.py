import requests
import traceback

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
                    "content": "我希望你充当简历投递助手，你将检查职位描述是否完全符合以下所有要求。请提供一个“true”或“false”的结果，无需任何解释。要求：1.该职位必须与计算机软件相关，例如Java开发、软件测试、软件运维开发、软件实施或软件运维。2.不要求线下投递简历。不应指定居住地。3.职位描述不应提及不接受应届毕业生，不应要求相关工作经验。4.不应涉及与硬件相关的任务，比如管理网络交换机、路由器、计算机硬件、公司资产、数据中心运营或设备安装。它也不应该是硬件测试或硬件开发的角色。5.该工作不应涉及销售活动或营销等及类似任务。6.该工作没有轮班、夜班工作。7.不应要求英语cet六级或其他证书。7.不应要求熟练C#，PHP，Golang或Android。职位说明："
                    + description,
                },
            ],
        }
        try:
            response = requests.post(f"{base_url}/v1/chat/completions", json=payload)
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
