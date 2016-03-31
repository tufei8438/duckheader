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
import redis
from duckheader import app
from duckheader.handlers import BaseRequestHandler


@app.route('/lottery')
class WelfareLotteryHandler(BaseRequestHandler):

    def get(self, *args, **kwargs):
        self.render('lottery.html', lotteries=self.get_lottery_statics())

    def get_lottery_statics(self):
        redis_cli = redis.Redis()
        result = []
        for i in xrange(0, 16):
            value = redis_cli.get('BlueBall:%d' % (i+1))
            count = value and int(value) or 0
            result.append(dict(name=i+1, count=count))

        def compare_count(dct):
            return dct['count']
        return sorted(result, key=compare_count)

