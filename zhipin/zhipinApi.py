from zhipin import ZhiPin


class ZhiPinApi(ZhiPin):
    def test_jobs(self):
        self.iterate_job_parameters()

    def execute_find_jobs(self, city, query, salary, page):
        try:
            self.find_jobs(
                self.URL12
                + query
                + self.URL7
                + city
                + self.URL2
                + salary
                + self.URL3
                + str(page)
            )
        except Exception as e:
            self.handle_exception(e)
            pass

    def find_jobs(self, page_url):
        query_list = self.query_jobs(page_url)
        pass_card_list = self.check_card(query_list)
        self.process_detail(pass_card_list)

    def process_detail(self, url_list):
        for url in url_list:
            self.append_to_file("job.txt", url)
            print(f"已处理：\n{url}")


if __name__ == "__main__":
    zpa = ZhiPinApi()
    zpa.test_jobs()
