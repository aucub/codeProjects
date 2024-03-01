from seleniumbase import BaseCase

BaseCase.main(__name__, __file__)


class GetCookies(BaseCase):
    # pytest tool/getcookies.py --user-data-dir=/home/uymi/.config/google-chrome --account=Default  --browser=chrome --headed -v -s --junit-xml=junit/test-results.xml
    def test_get_cookies(self):
        self.open("https://www.zhipin.com")
        self.sleep(5)
        self.save_cookies()
        self.sleep(5)
