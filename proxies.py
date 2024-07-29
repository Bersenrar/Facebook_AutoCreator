import queue
import random

import requests
import threading
import os


class ProxiesValidator:
    def __init__(self):
        self.valid_proxies = []
        self.proxies = queue.Queue()

    def __load_data(self):
        with open("data_files/proxies", "rt", encoding="utf-8") as f:
            proxies = f.read().split("\n")
            for p in proxies:
                self.proxies.put(p)

    def __validate_proxies(self):
        while not self.proxies.empty():
            proxie = self.proxies.get()
            try:
                response = requests.get("https://uk-ua.facebook.com/", proxies={
                    "http": proxie,
                    "https": proxie
                }, timeout=10)
                print(response.status_code)
            except Exception:
                continue
            if response.status_code == 200:
                print(proxie)
                self.valid_proxies.append(proxie)

    def __check_proxies(self):
        self.__load_data()
        threads = []
        for _ in range(15):
            t = threading.Thread(target=self.__validate_proxies)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        print(self.valid_proxies)

    def receive_proxies(self, recheck=False):
        if not os.path.exists("data_files/valid_proxies") or recheck:
            self.__check_proxies()
            with open("data_files/valid_proxies", "wt") as f:
                f.write("\n".join(self.valid_proxies))
            self.valid_proxies.sort(key=lambda x: random.random())
            return self.valid_proxies

        with open("data_files/valid_proxies", "rt") as f:
            self.valid_proxies = f.read().split("\n")
        self.valid_proxies.sort(key=lambda x: random.random())
        return self.valid_proxies


if __name__ == "__main__":
    p = ProxiesValidator()
    print(p.receive_proxies(recheck=True))
