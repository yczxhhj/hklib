#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .libapi import libAPI
from .codeocr.ocr import CodeOCR
import requests
import json
import base64
import re
from lxml import etree
import datetime


def statusKey(key: str = None):
    status_key = {
        "使用中": 'Using',
        "已结束使用": 'Finish',
        "已预约": 'Reserve',
        "已取消": 'Finish',
        "已完成": 'Finish',
        "早退": 'Finish',
        "失约": 'Finish',
        "已暂时离开": 'StepOut',
        None: 'Finish'
    }
    if key in status_key:
        return status_key[key]
    if key not in status_key:
        return status_key[None]


class HKLib(libAPI):
    def __init__(self):
        super().__init__()
        self._student_ID = '000000000000'
        self._password = '000000'
        self._auth_code = '0000'
        self._captcha_id = None
        self._index_html = None
        self._synchronizer_token = None
        self._token = ''
        self._status = dict.fromkeys(['Today', 'Tomorrow'], {})
        self._login_status = False
        self._menu = {
            'self': 'http://seat.ncist.edu.cn/self',
            'map': 'http://seat.ncist.edu.cn/map',
            'fav': 'http://seat.ncist.edu.cn/freeBook/fav',
            'history': 'http://seat.ncist.edu.cn/history?type=SEAT',
            'violations': 'http://seat.ncist.edu.cn/user/violations',
            'logout': 'http://seat.ncist.edu.cn/logout',
        }
        self.date_dict = {
            'Today': datetime.date.today(),
            'Tomorrow': datetime.date.today() + datetime.timedelta(days=1),
        }
        self._session = requests.session()

        self._url = 'http://seat.ncist.edu.cn'
        self._login_url = 'http://seat.ncist.edu.cn/auth/signIn'
        self._headers = {
            "User-Agent": 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 Edg/112.0.1722.58',
        }

        self.getCode()

    def __repr__(self):
        return f"账户：{self._student_ID}\n密码：{self._password}"

    @property
    def roomDict(self):
        room_dict = {
            '一层大厅': 21, '二层休闲区': 22, '三层休闲区': 23, '一层阅览室': 24,
            '二楼北001-128区': 3, '二楼北129-244区': 4, '二楼北245-284区': 5, '二楼南001-096区': 7,
            '二楼南097-280区': 6, '二楼南281-361区': 19,
            '三楼北001-112区': 8, '三楼北113-236区': 9, '三楼北237-280区': 10, '三楼南001-096区': 12,
            '三楼南097-264区': 11, '三楼南265-384区': 13,
            '四楼北001-172区': 14, '四楼北173-272区': 15, '四楼南001-164区': 16, '四楼南165-196区': 17,
            None: 'null'
        }
        return room_dict

    @property
    def url(self):
        return self._url

    @property
    def loginUrl(self):
        return self._login_url

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def studentID(self):
        return self._student_ID

    @studentID.setter
    def studentID(self, value):
        self._student_ID = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def authCode(self):
        return self._auth_code

    @property
    def loginStatus(self):
        return self._login_status

    @loginStatus.setter
    def loginStatus(self, value: bool):
        self._login_status = value

    @property
    def codeID(self):
        return self._captcha_id

    @property
    def index(self):
        return self._index_html

    @property
    def synchronizerToken(self):
        return self._synchronizer_token

    @property
    def token(self):
        return self._token

    @property
    def session(self):
        return self._session

    @property
    def status(self):
        return self._status

    @property
    def menu(self):
        return self._menu

    # 登入图书馆网站
    def login(self, student_id: str = None, password: str = None):
        if len(student_id) != 12:
            raise AttributeError('Student id length should be 12 digits!')
        self._student_ID = student_id
        self._password = password
        self._token = super().getToken(student_id=student_id, password=password)
        headers = self._headers
        data = {
            "SYNCHRONIZER_TOKEN": self._synchronizer_token,
            "SYNCHRONIZER_URI": '/login',
            "username": student_id,
            "password": password,
            "captchaId": self._captcha_id,
            "answer": self._auth_code,
        }
        login_html = self._session.post(self._login_url, headers=headers, data=data, timeout=10)
        self._login_status = True
        self._index_html = login_html.text
        self.userData()
        self.getStatus()
        return True

    # 获取登入页面的synchronizer_token, cookies, captchaId, 验证码,
    def getCode(self):
        headers = self._headers
        login_html = self._session.get(url='http://seat.ncist.edu.cn/login', headers=headers)
        login_json = self._session.get(url='http://seat.ncist.edu.cn/auth/createCaptcha', headers=headers)
        if login_json.status_code == 200 and login_html.status_code == 200:
            self._synchronizer_token = re.findall(r'''name="SYNCHRONIZER_TOKEN" value="(.*?)"''', login_html.text)[
                0]
            login_json = json.loads(login_json.text)
            self._captcha_id = login_json['captchaId']
            img_base64 = login_json['captchaImage'][22:]
            img = base64.b64decode(img_base64)
            ocr = CodeOCR()
            self._auth_code = ocr.ocr(img)
            return self._synchronizer_token, self._captcha_id, self._auth_code

    # def roomID(self, room_name: str = None):

    # 获取登入账户名称
    def userData(self):
        return super().user(self.token)

    # 获取操作菜单
    def getMenu(self):
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        html = etree.HTML(self.index)
        menu_element = html.xpath('/html/body/div[@class="warp"]/div[@class="menu fl"]/ul//li')
        for element in menu_element:
            element_a_href = self.url + element.xpath('a/@href')[0]
            element_a_text = element_a_href.split('/')[-1].split('?')[0]
            self._menu[element_a_text] = element_a_href
        return self._menu

    def getStatus(self):
        status_url = 'http://seat.ncist.edu.cn/user/viewMoreHistory?offset='
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        num = 0
        while True:
            status_data = self.session.get(status_url + str(num)).text
            status = json.loads(status_data)['resStr']
            if int(json.loads(status_data)['resNum']) == 0:
                break
            if "今天" in status or "明天" in status:
                status_etree = etree.HTML(status)
                for dl in status_etree.xpath('//dl'):
                    dt = dl.xpath('dt/text()')[0]
                    if dt[:2] == "今天" or dt[:2] == "明天":
                        data = {
                            '今天': 'Today',
                            '明天': 'Tomorrow',
                        }
                        self._getStatus(dl, data[dt[:2]])
            else:
                break
            num += 1
        return self.status

    def _getStatus(self, dl, data):
        if len(dl.xpath('*')) == 2:
            dt = dl.xpath('dt/text()')[0]
            self._status[data] = {
                "id": re.findall(r'id=([0-9]+)', dl.xpath('dd/a/@href')[0])[0],
                "start": dt.split(' ')[1],
                "end": dt.split(' ')[-1],
                "seat": dl.xpath('dd/a/@title')[0],
                "status": 'Reserve',
            }
        elif statusKey(dl.xpath('a/text()')[0]) != 'Finish':
            dt = dl.xpath('dt/text()')[0]
            self._status[data] = {
                "id": re.findall(r'id=([0-9]+)', dl.xpath('dd/a/@href')[0])[0],
                "start": dt.split(' ')[1],
                "end": dt.split(' ')[-1],
                "seat": dl.xpath('dd/a/@title')[0],
                "status": statusKey(dl.xpath('a/text()')[0]),
            }

    # 处理输入为 xx:xx 格式的时间转化成 30 倍数的分钟
    @staticmethod
    def _dealTime(times: str = None):
        if len(times) > 5 or re.match(r'\d{1,2}:\d{1,2}', times) is None:
            raise AttributeError(f"Please change the '{times}' format to 'xx:xx'.")
        if int(times.split(':')[0]) < 7:
            times = f'07:{times[3:]}'
        if int(times.split(':')[0]) > 22:
            times = '22:00'
        if int(times.split(':')[1]) > 60:
            times = f'{times[:2]}:00'
        times = int(times.split(':')[0]) * 60 + int(times.split(':')[1]) - int(times.split(':')[1]) % 15
        if times < 450:
            times = 450
        if times > 1320:
            times = 1320
        return times

    # 寻找座位，并返回座位预约状态
    def fuzzySearch(self, date: str = 'Today', room: str = None, start: str = 'null', end: str = 'null',
                    power: bool = 'null', window: bool = 'null'):
        # 模糊搜索后的结果
        search_result = {
            'free': {'num': 0, 'seat': {}},
            'using': {'num': 0, 'seat': {}},
            'order': {'num': 0, 'seat': {}},
            'leave': {'num': 0, 'seat': {}},
        }
        # 预约的日期
        if date not in self.date_dict:
            date = 'Today'
        # 预约的楼层、房间以及座位号区间
        if room not in self.roomDict:
            room = None
        # 预约开始和结束的时间
        if start != 'null':
            start = self._dealTime(start)
        if end != 'null':
            end = self._dealTime(end)
        if isinstance(start, int) and isinstance(end, int):
            if start >= end:
                start = 'null'
                end = 'null'
        else:
            start = 'null'
            end = 'null'
        # 预约的座位是否紧靠电源和需要靠窗
        if power != 'null':
            if bool(power):
                power = 1
            else:
                power = 0
        if window != 'null':
            if bool(window):
                window = 1
            else:
                window = 0
        offset = 0
        while True:
            search_url = 'http://seat.ncist.edu.cn/freeBook/ajaxSearch'
            search_url = f'{search_url}?onDate={self.date_dict[date]}&building=1&room={self.roomDict[room]}&hour=null&startMin={start}&endMin={end}&power={power}&window={window}&offset={offset}'
            search_data = json.loads(self._session.get(search_url).text)
            seatStr = search_data['seatStr']
            seatNum = search_data['seatNum']
            if int(seatNum) == 0:
                break
            seatStr = self._dealSearch(seatStr)
            for key in seatStr.keys():
                for data in seatStr[key]:
                    search_result[key]['seat'].update(data)
                    search_result[key]['num'] += 1
            offset += 1
        return search_result

    # 根据座位名称来进行搜索
    def search(self, seat_name: str = None, date: str = 'Today'):
        pro_name = re.search(r'(\D+?)\d{1,3}号', seat_name).group(1)
        if pro_name in list(self.roomDict.keys())[:4]:
            room_id = self.roomDict[pro_name]
        else:
            if re.match(r'[一二三四]楼[南北]\d{1,3}号', seat_name) is None:
                raise AttributeError("Incorrect seat name, the correct format is '二楼南15号'")
            else:
                seat_name = re.match(r'[一二三四]楼[南北]\d{1,3}号', seat_name)[0]
                room_id = self._judgeRoom(seat_name)['room_id']
        seat_num = int(re.search(r'\d{1,3}', seat_name)[0])
        seat_data = super().seatDate(self.token, room_id, seat_num, date)
        seat_time = super().seatTimes(self.token, int(seat_data['seat_id']), date)
        return {'seat_date': seat_data, 'seat_times': seat_time}

    # 判断座位在图书馆的那个房间
    def _judgeRoom(self, seat_name):
        room_list = {
            '一层大厅': [[1, 16]],
            '一层阅览室': [1, 182],
            '二层休闲区': [[1, 16]],
            '三层休闲区': [[1, 16]],
            '二楼北': [[1, 128], [129, 244], [245, 284]],
            '二楼南': [[1, 96], [97, 280], [281, 361]],
            '三楼北': [[1, 112], [113, 236], [237, 280]],
            '三楼南': [[1, 96], [97, 264], [265, 384]],
            '四楼北': [[1, 172], [173, 272]],
            '四楼南': [[1, 164], [165, 196]]
        }
        room_name = seat_name[:3]
        seat = int(re.search(r'\d{1,3}', seat_name)[0])
        left = 0
        right = len(room_list[room_name]) - 1
        while left <= right:
            among = (left + right) // 2
            extent = room_list[room_name][among]
            if extent[0] < seat < extent[1]:
                seat_min = '{:0>3d}'.format(extent[0])
                seat_max = '{:0>3d}'.format(extent[1])
                room = '{}{}-{}区'.format(room_name, seat_min, seat_max)
                return {'seat': seat, 'room': room, 'room_id': self.roomDict[room]}
            if seat < extent[0]:
                right = among - 1
            if seat > extent[1]:
                left = among + 1
        raise AttributeError(
            f"There is a problem with the entered seat number {seat}, it should be in the range of {room_list[room_name][0][0]}-{room_list[room_name][-1][-1]}.")

    # 处理爬取到的座位信息
    @staticmethod
    def _dealSearch(html):
        search_result = {
            'free': [],
            'using': [],
            'order': [],
            'leave': [],
        }
        seat_etree = etree.HTML(html)
        seat_li = seat_etree.xpath('//ul/li')
        for li in seat_li:
            seat_status = li.xpath('@class')[0].split('_')[0]
            seat_id = li.xpath('@id')[0][5:]
            seat_name = f'{li.xpath("dl/dd/text()")[0]} {li.xpath("dl/dt/text()")[0]}号'
            search_result[seat_status].append({seat_name: seat_id})
        return search_result

    # 预约座位
    def reserve(self, seat_name: str = None, start: str = 'now', end: str = '22:00', date: str = 'Today'):
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        if date not in self._status:
            raise AttributeError("Appointment can only made 'Today' or 'Tomorrow'.")
        if len(self._status[date]) != 0:
            print(f"You have an appointment {date}")
            return False
        if start == 'now':
            start = datetime.datetime.now().strftime("%H:%M")
        start = self._dealTime(start)
        end = self._dealTime(end)
        if start >= end:
            raise AttributeError('The start time cannot be greater than the end time.')
        reserve_url = super().api['reserve']
        seat = self.search(seat_name, date=date)
        seat_id = seat['seat_date']['seat_id']
        data = {
            'token': self.token,
            'startTime': start,
            'endTime': end,
            'seat': seat_id,
            'date': self.date_dict[date]
        }
        reserve_json = json.loads(self.session.post(reserve_url, data=data).text)
        if reserve_json['status'] == 'success':
            self.getStatus()
            return True
        if reserve_json['status'] == 'fail':
            print(reserve_json['message'])
            return False

    # 调用图书馆 api 实现取消座位
    def cancel(self, date: str = 'Today'):
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        if date not in self._status:
            raise AttributeError("Cancellations can only made 'Today' or 'Tomorrow'.")
        if len(self._status[date]) == 0:
            print(f"You don't have an appointment {date}")
            return False
        if self._status[date]['status'] != 'Reserve':
            print(f"The status of your seat {date} is {self._status[date]['status']}")
            return False
        cancel_url = f"{super().api['cancel']}/{self._status[date]['id']}"
        params = {
            'token': self.token
        }
        cancel_json = json.loads(self.session.get(cancel_url, params=params).text)
        if cancel_json['status'] == 'success':
            self.status[date] = {}
            return True
        if cancel_json['status'] == 'fail':
            print(cancel_json['message'])
            return False

    # 获取常使用的座位列表
    def favSeat(self):
        result = []
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        fav_seat_html = self.session.get(self.menu['fav']).text
        fav_seat_etree = etree.HTML(fav_seat_html)
        fav_seat_ul = fav_seat_etree.xpath(
            '/html/body/div[@class="warp"]/div[@class="mainContent fr"]/div[@class="content"]/div[@class="detailContent"]/div[@class="seatList"]/div[@class="items"]/ul//li')
        for li in fav_seat_ul:
            fav_seat = li.xpath('dl/dd/text()')[0]
            result.append(fav_seat)
        return result

    # 获取所有的预约记录
    def history(self):
        reservations_url = 'http://seat.ncist.edu.cn/user/viewMoreHistory?offset='
        data = {}
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        num = 0
        while True:
            violations_data = self.session.get(reservations_url + str(num)).text
            violations_json = json.loads(violations_data)
            violations = violations_json['resStr']
            total = violations_json['resNum']
            if total != 0:
                violations_etree = etree.HTML(violations)
                for dl in violations_etree.xpath('//dl'):
                    dt = dl.xpath('dt/text()')[0]
                    dd = dl.xpath('dd/a/@title') + dl.xpath('a/text()')
                    data[dt] = dd
            if total == 0:
                break
            num += 1
        return data

    # 获取所有的违约记录
    def violations(self):
        more_violations_url = 'http://seat.ncist.edu.cn/user/viewMoreViolations?offset='
        data = {}
        if not self.loginStatus:
            raise AttributeError("You are not logged in yet, please login!!!")
        num = 0
        while True:
            violations_data = self.session.get(more_violations_url + str(num)).text
            violations_json = json.loads(violations_data)
            violations = violations_json['violationStr']
            total = violations_json['total']
            if total != 0:
                violations_etree = etree.HTML(violations)
                for dl in violations_etree.xpath('//dl'):
                    dt = dl.xpath('dt/text()')[0]
                    dd = dl.xpath('dd/text()')[0].strip('\n            ')
                    data[dt] = dd
            if total == 0:
                break
            num += 1
        return data

    # 退出登入
    def exit(self):
        layout = self.session.get(self.menu['logout'])
        if layout.status_code == 200:
            self._index_html = None
            print('Successful exit.')


if __name__ == "__main__":
    lib = HKLib()
    login = lib.login('000000000000', '000000')
    print(lib.reserve('二层休闲区5号', start='7:30', end='9:00', date='Tomorrow'))
