# coding:utf8

"""
Copyright 2016 Smallpay Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import MySQLdb
import random
import requests
import threading
import traceback
import time
from bs4 import BeautifulSoup
from rdoclient import RandomOrgClient

API_KEY = "d804e23a-795a-42c5-88af-d29e9426d737"


def random_lottery():
    r = RandomOrgClient(API_KEY)
    redballs = r.generate_integers(6, 1, 33, False)
    redballs.sort()
    return "".join(["%02d" % ball for ball in redballs])


def get_lottery_from_random_org():
    lotteris = []
    r = requests.get("https://www.random.org/quick-pick/?tickets=50&lottery=6x33.1x16")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        element = soup.find("pre", class_="data")
        lottery_text = element.get_text()
        lottery_arrray = lottery_text.split()

        for data in lottery_arrray:
            if len(data) == 17:
                lotteris.append(data.replace("-", ""))
    return lotteris


def save_lottery(lottery):
    conn = MySQLdb.connect(host="localhost", user="lottery", passwd="lottery", db="lottery")
    cursor = conn.cursor()
    sql = "INSERT INTO ticket_repository(lottery_no) VALUES (%s)"
    if isinstance(lottery, list):
        values = []
        for l in lottery:
            values.append((l,))
        cursor.executemany(sql, values)
    else:
        cursor.execute(sql, (lottery,))
    cursor.close()
    conn.commit()
    conn.close()


class LotterThread(threading.Thread):

    def get_sleep_second(self):
        return random.randint(1, 2)

    def run(self):
        while True:
            try:
                print "[%s] 开始获取随机号码..." % (self.getName())
                lottery = get_lottery_from_random_org()
                print "[%s] 随机号码：%s" % (self.getName(), lottery)
                save_lottery(lottery)
                second = self.get_sleep_second()
                print "[%s] 休息%d秒" % (self.getName(), second)
                time.sleep(second)
            except:
                print "[%s] 异常信息：%s" % (self.getName(), traceback.format_exc())


def main():
    threads = []
    for i in xrange(0, 1):
        thread = LotterThread()
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()