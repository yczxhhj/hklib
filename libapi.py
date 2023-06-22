#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import requests
import json


# 图书馆api
class libAPI(object):
    def __init__(self):
        self._student_ID = '000000000000'
        self._password = '000000'
        self._libUrl = 'http://seat.ncist.edu.cn:80'
        self._api = {
            'token': f'{self._libUrl}/rest/auth',
            'user': f'{self._libUrl}/rest/v2/user',
            'roomStats': f'{self._libUrl}/rest/v2/room/stats2/1',
            'seatStartTime': f'{self._libUrl}/rest/v2/startTimesForSeat',
            'seatEndTime': f'{self._libUrl}/rest/v2/endTimesForSeat',
            'layoutByDate': f'{self._libUrl}/rest/v2/room/layoutByDate',
            'cancel': f'{self._libUrl}/rest/v2/cancel',
            'reserve': f'{self._libUrl}/rest/v2/freeBook'
        }
        self._headers = {
            "User-Agent": 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 Edg/112.0.1722.58',
        }
        self._session = requests.session()

    @property
    def api(self):
        return self._api

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

    # 获取token
    def getToken(self, student_id: str = None, password: str = None):
        # 获取的 token 具有时效性，无法存在较长时间
        if len(student_id) != 12:
            raise AttributeError('Student id length should be 12 digits!')
        params = {
            'username': student_id,
            'password': password,
        }
        token_json = json.loads(self._session.get(self.api['token'], headers=self._headers, params=params).text)
        if token_json['status'] == 'success':
            token = token_json['data']['token']
            return token
        if token_json['status'] == 'fail':
            raise AttributeError(token_json['message'])

    # 获取用户信息
    def user(self, token):
        if len(token) != 48:
            raise AttributeError("You are not logged in yet, please login!!!")
        params = {
            'token': token
        }
        user_json = json.loads(self._session.get(self.api['user'], params=params).text)
        if user_json['status'] == 'success':
            user = {
                'name': user_json['data']['name'],
                'student_id': user_json['data']['username'],
                'lastLogin': user_json['data']['lastLogin'],
                'lastIn': user_json['data']['lastIn'],
                'lastOut': user_json['data']['lastOut'],
                'reservationStatus': user_json['data']['reservationStatus']
            }
            return user
        if user_json['status'] == 'fail':
            raise AttributeError(user_json['message'])

    # 获取图书馆各个楼层的信息
    def roomStatus(self, token):
        if len(token) != 48:
            raise AttributeError("You are not logged in yet, please login!!!")
        params = {
            'token': token
        }
        room_json = json.loads(self._session.get(self.api['roomStats'], params=params).text)
        if room_json['status'] == 'success':
            room_data = room_json['data']
            room_dict = dict()
            for room in room_data:
                room_dict[room['room']] = {
                    'roomId': room['roomId'],
                    'inUse': room['inUse'],
                    'away': room['away'],
                    'totalSeats': room['totalSeats'],
                    'free': room['free'],
                }
            return room_dict
        if room_json['status'] == 'fail':
            raise AttributeError(room_json['message'])

    # 获取指定 id 座位的可开始使用时间和结束时间
    def seatTimes(self, token, seat_id: int = None, date: str = 'Today'):
        # 如果输入的座位 id 是整数型则报错
        if not isinstance(seat_id, int):
            raise AttributeError("The seat id is not an int type.")
        # 如果没有 token 则视为没有登入
        if len(token) != 48:
            raise AttributeError("You are not logged in yet, please login!!!")
        params = {
            'token': token
        }
        date_dict = {
            'Today': datetime.date.today(),
            'Tomorrow': datetime.date.today() + datetime.timedelta(days=1),
        }
        start_url = f"{self.api['seatStartTime']}/{seat_id}/{date_dict[date]}"
        start_json = json.loads(self._session.get(start_url, params=params).text)
        start_min = '450'
        if start_json['status'] == 'fail':
            raise AttributeError(start_json['message'])
        start_times = list()
        for time in start_json['data']['startTimes']:
            start_times.append(time['value'])
        if len(start_json['data']['startTimes']) != 0:
            start_min = start_json['data']['startTimes'][0]['id']
        end_url = f"{self.api['seatEndTime']}/{seat_id}/{date_dict[date]}/{start_min}"
        end_json = json.loads(self._session.get(end_url, params=params).text)
        end_times = list()
        if end_json['status'] == 'fail':
            if end_json['data']['endTimes'] is None:
                end_times = []
                return {'startTimes': start_times, 'endTimes': end_times}
            if end_json['data']['endTimes'] == "Cannot get property 'enabled' on null object":
                raise AttributeError(f"fail {end_json['message']}")
        for time in end_json['data']['endTimes']:
            end_times.append(time['value'])
        return {'startTimes': start_times, 'endTimes': end_times}

    # 根据 room 的 id 和座位号获取座位号的各项信息
    def seatDate(self, token, room_id: int = None, seat_num: int = None, date: str = 'Today'):
        # 如果输入的座位 id 是整数型则报错
        if not isinstance(room_id, int):
            raise AttributeError("The room id is not an int type.")
        if not isinstance(seat_num, int):
            raise AttributeError("The number of seat is not an int type.")
        # 如果输入的座位 id 长度大于 4 小于 1 则报错
        if len(str(seat_num)) > 3 or len(str(seat_num)) < 1:
            raise AttributeError("The number of seat must exceed 3 less than 1.")
        # 如果没有 token 则视为没有登入
        if len(token) != 48:
            raise AttributeError("You are not logged in yet, please login!!!")
        params = {
            'token': token
        }
        date_dict = {
            'Today': datetime.date.today(),
            'Tomorrow': datetime.date.today() + datetime.timedelta(days=1),
        }
        seat_num = '{:0>3d}'.format(seat_num)
        seat_url = f"{self.api['layoutByDate']}/{room_id}/{date_dict[date]}"
        seat_json = json.loads(self._session.get(seat_url, params=params).text)
        if seat_json['status'] == 'fail':
            print(seat_json['message'])
            return None
        for key, value in seat_json['data']['layout'].items():
            if 'name' not in value:
                continue
            if value['name'] == str(seat_num):
                return {
                    'seat': int(value['name']),
                    'seat_type': value['type'],
                    'seat_id': value['id'],
                    'status': value['status'],
                    'window': value['window'],
                    'power': value['power'],
                    'computer': value['computer'],
                }
        return None

    # 取消座位
    def cancel(self, date):
        pass

    # 预约座位
    def reserve(self, date):
        pass


if __name__ == "__main__":
    a = libAPI()
    b = a.getToken('000000000000', '000000')
    print(a.seatDate(b, room_id=3, seat_num=15, date='Tomorrow'))
