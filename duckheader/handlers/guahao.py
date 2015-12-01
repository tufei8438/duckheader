# coding:utf8

"""
Copyright 2015 tufei

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
import requests
import datetime

from duckheader import app
from duckheader.handlers import BaseRequestHandler


import httplib
import logging
httplib.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


GUAHAO_URL = "http://www.bjguahao.gov.cn/comm/ghao.php"

GUAHAO_CONTENT_URL = "http://www.bjguahao.gov.cn/comm/content.php"

COOKIES = {
    '__c_059itCJ8u5H356cai9059itCJ8u5H356wS29D748d1b': '4ad9150a10b3a20e91f96f81c9f9a554',
    '__c_5wm2Q8E8ZI8486cai95wm2Q8E8ZI848641o09va97117p': '330bb974ee372b4553557987c61797f4',
    'Hm_lvt_65f844e6a6e140ab52d02690ed38a38b': '1448247275',
    'Hm_lpvt_65f844e6a6e140ab52d02690ed38a38b': '1448443150'
}

HEADERS = {
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'
}


QUERY_LIST = [
    {
        'name': '阜外心血管病医院特需',
        'hpid': '140',
        'keid': '1001'
    },

    {
        'name': '阜外心血管病医院',
        'hpid': '4',
        'keid': 'xnk'
    },

    {
        'name': '首都医科大学附属北京安贞医院',
        'hpid': '108',
        'keid': '%D0%C4%C4%DA%BF%C6'
    },

    {
        'name': '首都医科大学附属北京安贞医院特需',
        'hpid': '108',
        'keid': 'TX%D0%C4%C4%DA%BF%C6%B7%BF%B2%FC%C3%C5%D5%EF'
    }
]


def get_doctor_surgery_info(hpid, keid, date):
    params = {
        'hpid': hpid,
        'keid': keid,
        'date1': date
    }
    headers = dict()
    headers.update(HEADERS)
    headers['Referer'] = "%s?hpid=%s&keid=%s" % (GUAHAO_CONTENT_URL, hpid, keid)
    url = "%s?hpid=%s&keid=%s&date1=%s" % (GUAHAO_URL, hpid, keid, date)
    r = requests.get(url, cookies=COOKIES, headers=headers)
    print r.text
    return parse_html(r.text)


def parse_html(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html)

    table = soup.find('table', cellpadding='1', cellspacing='1')
    trs = table.find_all('tr')
    results = []
    for tr in trs:
        tds = tr.find_all('td')
        if tds[0].get('class') is not None:
            continue

        result = dict()
        result['日期'] = tds[0].text
        result['星期'] = tds[1].text
        result['午别'] = tds[2].text
        result['科室'] = tds[3].text
        result['医生'] = tds[4].text
        result['职称'] = tds[5].text
        result['挂号费'] = tds[6].text
        result['专长'] = tds[7].text
        result['可挂号'] = tds[8].text
        result['剩余号'] = tds[9].text
        results.append(result)

    return results


@app.route(r"/guahao")
class GuahaoHandler(BaseRequestHandler):

    def get(self, *args, **kwargs):
        default_date = self.get_default_date()
        date = self.get_argument('date', default_date)
        surgery_infos = self.get_surgery_infos(date)
        self.render('guahao.html', surgery_infos=surgery_infos)

    def get_default_date(self):
        today = datetime.datetime.now()
        date = today.replace(day=today.day+7)
        return date.strftime("%Y-%m-%d")

    def get_surgery_infos(self, date):
        surgery_infos = []
        for query in QUERY_LIST:
            result = get_doctor_surgery_info(query['hpid'], query['keid'], date)
            surgery_info = dict(name=query['name'], surgery=result)
            surgery_infos.append(surgery_info)

        return surgery_infos