import random
import time

from playwright.sync_api import sync_playwright
from fake_useragent import FakeUserAgent

import string

import proxies
import emails_helper


class AccountGenerator:
    def __init__(self):
        self.facebook_url = "https://uk-ua.facebook.com/"

        self.generator_mails = emails_helper.EmailGenerator()

        self.proxies_checker = proxies.ProxiesValidator()
        self.proxies_checker.receive_proxies(recheck=False)

        self.names = None
        self.first_names = None
        self.__load_data()

    def __load_data(self):
        with open("data_files/names", "rt", encoding="utf-8") as names_f, open("data_files/firstnames", "rt", encoding="utf-8") as fnames_f:
            self.names = [n.strip('|').strip() for n in names_f.read().split("\n")]
            self.first_names = [n.strip('|').strip() for n in fnames_f.read().split("\n")]

    @staticmethod
    def __get_agent():
        fa = FakeUserAgent()
        return fa.random

    def __generate_user(self):
        user = dict()
        user["name"] = random.choice(self.names)
        user["first_name"] = random.choice(self.first_names)
        user["birthday_day"] = str(random.randint(1, 23))
        user["birthday_month"] = str(random.randint(1, 11))
        user["birthday_year"] = str(random.randint(1983, 2003))
        user["password"] = "".join(random.choice(string.ascii_lowercase+string.digits+string.ascii_uppercase)
                                   for _ in range(random.randint(9, 14)))
        return user

    def create_account(self):
        self.generator_mails.create_email()
        user_data = self.__generate_user()
        user_data["email"] = self.generator_mails.email_address
        print(user_data)
        while self.proxies_checker.valid_proxies:
            proxy = self.proxies_checker.valid_proxies.pop()
            try:
                with sync_playwright() as p:
                    browser = p.firefox.launch(headless=False, proxy={"server": proxy})
                    # browser = p.firefox.launch(headless=False)
                    page = browser.new_page(user_agent=self.__get_agent())

                    page.goto(self.facebook_url)

                    cookie_button = page.locator("text=Дозволити всі файли cookie").first
                    if cookie_button:
                        cookie_button.click()
                        time.sleep(0.5)
                    time.sleep(0.5)
                    page.locator("text=Створити обліковий запис").click()

                    if page.query_selector("text=Почати"):
                        page.locator("text=Почати").click()
                        time.sleep(10000)
                    else:
                        page.wait_for_selector("input[name='firstname']")
                        page.fill("input[name='firstname']", user_data["name"])
                        time.sleep(random.random())
                        page.fill("input[name='lastname']", user_data["first_name"])
                        time.sleep(random.random())
                        page.locator("input[name='reg_email__']").click()
                        page.fill("input[name='reg_email__']", user_data["email"])
                        time.sleep(random.random())
                        page.locator("input[name='reg_passwd__']").click()
                        time.sleep(random.random())
                        page.fill("input[name='reg_email_confirmation__']", user_data["email"])
                        time.sleep(random.random())
                        page.fill("input[name='reg_passwd__']", user_data["password"])
                        time.sleep(random.random())
                        page.select_option("select[name='birthday_day']", user_data["birthday_day"])
                        time.sleep(random.random())
                        page.select_option("select[name='birthday_month']", user_data["birthday_month"])
                        time.sleep(random.random())
                        page.select_option("select[name='birthday_year']", user_data["birthday_year"])
                        time.sleep(random.random())
                        # Выбор пола (1 - Женский, 2 - Мужской, 3 - Другой)
                        page.locator("input[name='sex'][value='2']").check()
                        time.sleep(random.random())
                        page.screenshot(path="form_filled.png")
                        page.locator("button[name='websubmit']").click()

                        page.wait_for_load_state('networkidle')
                        page.screenshot(path="registration_complete.png")

                        page.wait_for_selector("input[name='code']")
                        verification_code = self.generator_mails.parse_facebook_code()

                        if verification_code:
                            print(verification_code)
                            page.fill("input[name='code']", verification_code)
                            page.locator("button:has-text('Продовжити')").click()
                        time.sleep(random.random())
                        page.locator("button:has-text('Ок')").click()
                        time.sleep(10)
                print(f"User data: {user_data}")
                break
            except Exception as e:
                print(f"Something went wrong: {e}")


if __name__ == "__main__":
    test_class = AccountGenerator()
    test_class.create_account()


