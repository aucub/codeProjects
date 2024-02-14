import traceback
from zhipin import ZhiPin


class ZhiPinApi(ZhiPin):
    def test_query(self):
        for city in self.config_setting.query_city_list:
            if city in self.wheels[0]:
                continue
            for query in self.config_setting.query_list:
                if query in self.wheels[1]:
                    continue
                for salary in self.config_setting.salary_list:
                    if salary in self.wheels[2]:
                        continue
                    for page in range(
                        self.config_setting.page_min, self.config_setting.page_max
                    ):
                        if page <= self.wheels[3]:
                            continue
                        try:
                            self.query_and_process_jobs(
                                self.URL12
                                + query
                                + self.URL7
                                + city
                                + self.URL2
                                + salary
                                + self.URL3
                                + str(page)
                            )
                        except Exception:
                            traceback.print_exc()
                            continue
                        self.wheels[3] = page
                        self.save_state(self.wheels)
                    self.wheels[3] = 0
                    self.wheels[2].append(salary)
                    self.save_state(self.wheels)
                self.wheels[2] = []
                self.wheels[1].append(query)
                self.save_state(self.wheels)
            self.wheels[1] = []
            self.wheels[0].append(city)
            self.save_state(self.wheels)
        self.wheels[0] = []
        self.save_state(self.wheels)

    def query_and_process_jobs(self, page_url):
        self.url_list_process(self.query_jobs(page_url))

    def url_list_process(self, url_list):
        url_list = self.check_url_list(url_list)
        self.conn.commit()
        self.detail(url_list)
        self.conn.commit()

    def check_url_list(self, url_list):
        card_url_list = []
        for url in url_list:
            if self.check_card(url):
                card_url_list.append(url)
        return card_url_list

    def detail(self, url_list):
        for url in url_list:
            self.append_to_file("job.txt", url)
            print(f"已处理：\n{url}")


if __name__ == "__main__":
    zpa = ZhiPinApi()
    zpa.test_query()
