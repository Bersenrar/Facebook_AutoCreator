import time

import requests
import random
import string
from hashlib import md5


class EmailGenerator:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": "c2a168bf65msh394690b1f64e270p1dd8f1jsnaf207a645592",
            "x-rapidapi-host": "privatix-temp-mail-v1.p.rapidapi.com"
        }

        self.domains_url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
        self.emails_url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{}/"

        self.email_address = None
        self.email_hash = None

        self.domains = None

    def get_domain(self):
        if not self.domains:
            response = requests.get(self.domains_url, headers=self.headers)
            if response.status_code == 200:
                self.domains = response.json()
            else:
                print(response.text)
                raise ValueError(f"Can't get list of domains something went wrong code: {response.status_code}")
        return random.choice(self.domains)

    def create_id(self, min_len=7, max_len=11, digits=True):
        chars = string.ascii_lowercase + string.digits if digits else string.ascii_lowercase
        email_id = "".join(random.choice(chars) for _ in range(random.randint(min_len, max_len)))
        return email_id

    def create_email(self):
        domain = self.get_domain()
        self.email_address = u"{0}{1}".format(self.create_id(), domain)
        self.email_hash = md5(self.email_address.encode("utf-8")).hexdigest()
        print(f"Generated Email: {self.email_address}\nHash: {self.email_hash}")

    def get_emails(self):
        response = requests.get(self.emails_url.format(self.email_hash), headers=self.headers)
        print(response.json())
        return response.json()

    def parse_facebook_code(self, retries=0):
        try:
            if retries >= 3:
                return None
            emails_json = self.get_emails()
            return emails_json[0]["mail_subject"].split()[0][3:]
        except Exception:
            time.sleep(10)
            self.parse_facebook_code(retries=retries+1)
