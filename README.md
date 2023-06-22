## [华北科技学院图书馆](http://seat.ncist.edu.cn)座位预约系统

Create by [YCZX](https://yczxvip.top)

## 文件目录

```python
hklib
	│  __init__.py
	│  hklib.py # 主程序
	│  requirements.txt # 环境依赖
	│  libapi.py # 图书馆 API 接口
	│  README.md
	│
	├─__pycache__
	│      libapi.cpython-38.pyc
	│
	└─codeocr
    	│  common_det.onnx
    	│  common.onnx
    	│  __init__.py
    	│  ocr.py # 图书馆 Web 端验证码识别
    	│
    	└─__pycache__
            	__init__.cpython-38.pyc
            	ocr.cpython-38.pyc
```

## 说明

**项目仅供学习交流使用，<font color='red'>滥用占座实属无耻</font>。**

该项目主要起因是苦抢图书馆座位已久，便有想法自己弄一个程序一劳永逸，于是便那这个项目来练手了。这个项目是一个很不错的 `爬虫` 练手项目，从 2023/5/1 期间因期末考试搁浅一段时间，到 2023/6/22 正式完工，难度不高，适合初学者（本身自己也是初学者）。

## hklib.libapi.libAPI 类

该类主要是调用网站 API 来实现 `获取用户信息`、`获取图书馆各楼层信息`、`获取座位信息`、`预约座位`、`取消预约座位` 等功能。

| 属性（property） |                                         |
| :--------------- | --------------------------------------- |
| api              | dict 类型，API 链接                     |
| studentID        | str 类型，学生学号                      |
| password         | str 类型，学生图书馆账户，默认为 000000 |


| 方法（）method                            |                                                              |
| ----------------------------------------- | ------------------------------------------------------------ |
| getToken(student_id, password)            | 获取 token ，使用该 token 调用所有 API                       |
| user(token)                               | 获取 token 对应的用户信息                                    |
| roomStatus(token)                         | 获取图书馆所有楼层的信息                                     |
| seatTimes(token, seat_id, date)           | 获取指定 id 座位可预约时间信息，date只有两个选项 `Today`(默认) 和 `Tomorrow` |
| seatDate(token, room_id, steat_num, date) | 获取指定楼层，指定座位号的座位信息                           |

### 属性（property）

```python
>>> from libapi import libAPI
>>> api = libAPI()
{'token': 'http://seat.ncist.edu.cn:80/rest/auth', 
 'user': 'http://seat.ncist.edu.cn:80/rest/v2/user',
 'roomStats':'http://seat.ncist.edu.cn:80/rest/v2/room/stats2/1',
 'seatStartTime': 'http://seat.ncist.edu.cn:80/rest/v2/startTimesForSeat',
 'seatEndTime': 'http://seat.ncist.edu.cn:80/rest/v2/endTimesForSeat',
 'layoutByDate': 'http://seat.ncist.edu.cn:80/rest/v2/room/layoutByDate',
 'cancel': 'http://seat.ncist.edu.cn:80/rest/v2/cancel', 
 'reserve': 'http://seat.ncist.edu.cn:80/rest/v2/freeBook'
}
>>> api.studentID
'000000000000'
>>> api.password
'000000'
```

### 方法（method）

```python
>>> token = api.getToken('000000000000', '000000')
>>> token
'8ac544cadc0e0852e122f36f9ded238684f8ee0506221336'
>>> user = api.user(token)
>>> user
{'name': 'Yczx', 
 'student_id': '000000000000', 
 'lastLogin': '2023-06-22T20:11:15.000',
 'lastIn': '18:19', 
 'lastOut': '17:44',
 'reservationStatus': None
}
>>> room = api.roomStatus(token)
>>> room
{'一层大厅': {'roomId': 21, 'inUse': 11, 'away': 1, 'totalSeats': 16, 'free': 4},
 '一层阅览室': {'roomId': 24, 'inUse': 73, 'away': 7, 'totalSeats': 182, 'free': 102}, 
 '二层休闲区': {'roomId': 22, 'inUse': 3, 'away': 2, 'totalSeats': 18, 'free': 13}, 
 '二楼北001-128区': {'roomId': 3, 'inUse': 31, 'away': 3, 'totalSeats': 127, 'free': 93},
 '二楼北129-244区': {'roomId': 4, 'inUse': 14, 'away': 3, 'totalSeats': 115, 'free': 98}, 
 '二楼北245-284区': {'roomId': 5, 'inUse': 2, 'away': 3, 'totalSeats': 40, 'free': 35}, 
 '二楼南001-096区': {'roomId': 7, 'inUse': 22, 'away': 1, 'totalSeats': 95, 'free': 72}, 
 '二楼南097-280区': {'roomId': 6, 'inUse': 23, 'away': 1, 'totalSeats': 182, 'free': 158}, 
 '二楼南281-316区': {'roomId': 19, 'inUse': 6, 'away': 0, 'totalSeats': 36, 'free': 30}, 
 '三层休闲区': {'roomId': 23, 'inUse': 5, 'away': 1, 'totalSeats': 18, 'free': 12}, 
 '三楼北001-112区': {'roomId': 8, 'inUse': 27, 'away': 0, 'totalSeats': 111, 'free': 84}, 
 '三楼北113-236区': {'roomId': 9, 'inUse': 22, 'away': 2, 'totalSeats': 123, 'free': 99},
 '三楼北237-280区': {'roomId': 10, 'inUse': 10, 'away': 0, 'totalSeats': 44, 'free': 34},
 '三楼南001-096区': {'roomId': 12, 'inUse': 22, 'away': 5, 'totalSeats': 95, 'free': 68},
 '三楼南097-264区': {'roomId': 11, 'inUse': 30, 'away': 8, 'totalSeats': 166, 'free': 128},
 '三楼南265-384区': {'roomId': 13, 'inUse': 17, 'away': 4, 'totalSeats': 120, 'free': 98}, 
 '四楼北001-172区': {'roomId': 14, 'inUse': 52, 'away': 5, 'totalSeats': 166, 'free': 109},
 '四楼北173-272区': {'roomId': 15, 'inUse': 25, 'away': 3, 'totalSeats': 102, 'free': 74},
 '四楼南001-164区': {'roomId': 16, 'inUse': 37, 'away': 8, 'totalSeats': 162, 'free': 117},
 '四楼南165-196区': {'roomId': 17, 'inUse': 8, 'away': 3, 'totalSeats': 32, 'free': 21}}
>>> seatTimes = api.seatTimes(b, seat_id=4629, date='Tomorrow')
>>> seatTimes
{'startTimes': ['07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00'], 
 'endTimes': ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30']}
>>> seatDate = api.seatDate(b, room_id=3, seat_num=15, date='Tomorrow')
>>> seatDate
{'seat': 15, 'seat_type': 'seat', 'seat_id': 4763, 'status': 'FREE', 'window': False, 'power': False, 'computer': False}
```

## hklib.hklib.HKLib 类

属性继承 libAPI ，该类大部分方法是通过爬取网页，`预约`，`取消预约` 则是使用 `libAPI` 调用来实现的，该类是程序主类。

| 属性（property） |                                    |
| ---------------- | ---------------------------------- |
| roomDict         | dict 类型，返回图书馆各层对应的 id |
| url              | str 类型，图书馆链接               |
| loginUrl         | str 类型，登入链接                 |
| headers          | str 类型，请求 headers             |
| studentID        | str 类型，学生学号                 |
| password         | str 类型，账号密码                 |
| authCode         | str 类型，图形验证码               |
| loginStatus      | bool 类型，是否登入                |
| codeID           | str 类型，图形验证码，对应的 id    |
| index            | str 类型，爬取的主页面             |
| token            | str 类型，调用 api 的 token        |
| session          | request，request 对话 session      |
| status           | dict 类型，用户的状态              |
| menu             | dict 类型，菜单链接列表            |

| 属性（property）                                   |                                                            |
| -------------------------------------------------- | ---------------------------------------------------------- |
| login(student_id, password)                        | 登入 web 端图书馆，并获取 token                            |
| getCode()                                          | 获取 web 端登入图像验证码                                  |
| userData()                                         | 获取用户信息                                               |
| getMenu()                                          | 获取 web 端网站菜单列表                                    |
| getStatus()                                        | 获取用户状态                                               |
| fuzzySearch(date, room, start, end, power, window) | 模糊搜索座位                                               |
| search(seat_name, date)                            | 根据座位名(eg. 二楼北15号)查询座位信息                     |
| reserve(seat_name, start, end, date)               | 根据座位名称预约座位，默认为预约时间为今天从 现在 -> 22:00 |
| cancel(date)                                       | 取消预约座位，默认取消今天预约的座位                       |
| favSeat()                                          | 获取经常使用的座位                                         |
| history()                                          | 获取所有预约记录                                           |
| violations()                                       | 获取所有违约记录                                           |
| exit()                                             | 退出网页端                                                 |

### 属性（property）

```python
>>> from hklib import HKLib
>>> lib = HKLib()
>>> lib
账户：000000000000
密码：000000
>>> lib.login('000000000000', '000000')
>>> lib.roomDict
{'一层大厅': 21, '二层休闲区': 22, '三层休闲区': 23, '一层阅览室': 24, '二楼北001-128区': 3, '二楼北129-244区': 4, '二楼北245-284区': 5, '二楼南001-096区': 7, '二楼南097-280区': 6, '二楼南281-361区': 19, '三楼北001-112区': 8, '三楼北113-236区': 9, '三楼北237-280区': 10, '三楼南001-096区': 12, '三楼南097-264区': 11, '三楼南265-384区': 13, '四楼北001-172区': 14, '四楼北173-272区': 15, '四楼南001-164区': 16, '四楼南165-196区': 17, None: 'null'}
>>> lib.url
http://seat.ncist.edu.cn
>>> lib.loginUrl
http://seat.ncist.edu.cn/auth/signIn
>>> lib.headers
{'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 Edg/112.0.1722.58'}
>>> lib.studentID
'000000000000'
>>> lib.password
'000000'
>>> lib.authCode
'w57d'
>>> lib.codeID
'qe73h9y0jdbs'
>>> lib.loginStatus
True
>>> lib.token
'8ac544cadc0e0852e122f36f9ded238684f8ee0506222950'
>>> lib.session
<requests.sessions.Session object at 0x000002144CEBEDC0>
>>> lib.status
{'Today': {}, 'Tomorrow': {'id': '2042622', 'start': '20:00', 'end': '22:00', 'seat': '图书馆2层二楼北001-128区015号', 'status': 'Reserve'}}
>>> lib.menu
{'self': 'http://seat.ncist.edu.cn/self', 
 'map': 'http://seat.ncist.edu.cn/map',
 'fav': 'http://seat.ncist.edu.cn/freeBook/fav',
 'history':'http://seat.ncist.edu.cn/historytype=SEAT', 
 'violations':'http://seat.ncist.edu.cn/user/violations', 
 'logout': 'http://seat.ncist.edu.cn/logout'
}

```

### 属性（property）

### login(student_id, password)

在进行所有操作前都需要登入

```python
>>> login = lib.login('000000000000', '000000')
True
```

### getCode() 

获取 web 端登入的所有信息

```python
>>> code = lib.getCode()
('af800a20-c50f-4185-ab01-997b12364ba5', 'skydy35wu0c9', 'ebxd')
```

### userData()

获取用户的所有信息

```python
>>> userData = lib.userData()
{'name': 'Yczx', 'student_id': '202001074214', 'lastLogin': '2023-06-22T23:13:49.000', 'lastIn': '18:19', 'lastOut': '21:55', 'reservationStatus': None}
```

### getMenu()

获取 web 端登入所有的菜单链接

```python
>>> menu = lib.getMenu()
{'self': 'http://seat.ncist.edu.cn/self',
'map':'http://seat.ncist.edu.cn/map','fav':'http://seat.ncist.edu.cn/freeBook/fav',
'history':'http://seat.ncist.edu.cn/historytype=SEAT',
'violations':'http://seat.ncist.edu.cn/user/violations,
'logout': 'http://seat.ncist.edu.cn/logout'
}
```

### getStatus()

获取用户在图书馆状态

```python
>>> status = lib.getStatus()
{'Today': {}, 'Tomorrow': {'id': '2042622', 'start': '20:00', 'end': '22:00', 'seat': '图书馆2层二楼北001-128区015号', 'status': 'Reserve'}}
```

### fuzzySearch(date, room, start, end, power, window)

根据日期，楼层，开始时间，结束时间，靠近电源，靠近窗户来模糊搜索座位

```python
>>> result = lib.fuzzySearch(date='Tomorrow', room='二楼南001-096区', start='7:30', end='22:00')
{'free': {'num': 26, 'seat': {'二楼南001-096 010号': '797', '二楼南001-096 013号': '799', '二楼南001-096 018号': '780', '二楼南001-096 019号': '765', '二楼南001-096 021号': '782', '二楼南001-096 024号': '767', '二楼南001-096 029号': '752', '二楼南001-096 040号': '709', '二楼南001-096 042号': '692', '二楼南001-096 043号': '677', '二楼南001-096 050号': '662', '二楼南001-096 051号': '647', '二楼南001-096 052号': '646', '二楼南001-096 053号': '664', '二楼南001-096 056号': '649', '二楼南001-096 058号': '638', '二楼南001-096 063号': '636', '二楼南001-096 064号': '635', '二楼南001-096 069号': '809', '二楼南001-096 073号': '792', '二楼南001-096 075号': '778', '二楼南001-096 077号': '762', '二楼南001-096 084号': '719', '二楼南001-096 088号': '689', '二楼南001-096 092号': '659', '二楼南001-096 094号': '645'}}, 'using': {'num': 0, 'seat': {}}, 'order': {'num': 0, 'seat': {}}, 'leave': {'num': 0, 'seat': {}}}
```

### search(seat_name, date)

根据座位名称获取座位信息

```python
>>> search = lib.search('二楼南15号', date='Tomorrow')
{'seat_date': {'seat': 15, 'seat_type': 'seat', 'seat_id': 843, 'status': 'FREE', 'window': False, 'power': False, 'computer': False}, 'seat_times': {'startTimes': ['07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'], 'endTimes': ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00']}}
```

### reserve(seat_name, start, end, date)

预约座位

```python
>>> status = lib.getStatus()
{'Today': {}, 'Tomorrow': {}}
>>> reserve = lib.reserve('二楼北15号', start='9:00', end='22:00', date='Tomorrow')
True
>>> status = lib.getStatus()
{'Today': {}, 'Tomorrow': {'id': '2042622', 'start': '09:00', 'end': '22:00', 'seat': '图书馆2层二楼北001-128区015号', 'status': 'Reserve'}}
```

### cancel(date)

取消预约座位

```python
>>> status = lib.getStatus()
{'Today': {}, 'Tomorrow': {'id': '2042622', 'start': '20:00', 'end': '22:00', 'seat': '图书馆2层二楼北001-128区015号', 'status': 'Reserve'}}
>>> cancel = lib.cancel('Tomorrow')
True
>>> status = lib.getStatus()
{'Today': {}, 'Tomorrow': {}}
```



### favSeat()

获取经常使用的座位

```python
>>> favor = lib.favSeat()
['图书馆2楼二楼北001-128区教室015座位', '图书馆2楼二楼北001-128区教室030座位', '图书馆2楼二楼南001-096区教室033座位', '图书馆2楼二楼北001-128区教室032座位', '图书馆2楼二楼南001-096区教室085座位']
```

### history()

获取所有预约历史

```python
>>> history = lib.history()
{'明天 20:00 -- 22:00': ['图书馆2层二楼北001-128区015号'], '明天 09:30 -- 22:00': ['图书馆2层二楼北001-128区015号', '已取消'], '明天 07:30 -- 22:00': ['图书馆2层二楼北001-128区015号', '已取消'], '今天 19:38 -- 22:00': ['图书馆2层二楼北001-128区015号', '已完成'], '今天 14:30 -- 22:00': ['图书馆2层二楼北001-128区015号', '已结束使用'], '今天 11:00 -- 22:00': ['图书馆2层二楼北001-128区015号', '已结束使用'], '今天 10:25 -- 22:00': ['图书馆2层二楼北001-128区019号', '已结束使用'], '今天 09:00 -- 22:00': ['图书馆2层二楼北001-128区026号', '已取消'], '今天 08:38 -- 22:00': ['图书馆2层二楼北001-128区019号', '早退'], '今天 08:00 -- 22:00': ['图书馆2层二楼北001-128区004号', '已取消'], '今天 07:30 -- 09:30': ['图书馆2层二楼北001-128区001号', '已取消'], '今天 07:30 -- 22:00': ['图书馆2层二楼北001-128区127号', '已取消']...}
```

### violations()

获取所有违约记录

```python
>>> violations = lib.violations()
{'今天 09:48 早退违约': '早退违约, 预约: 图书馆2层二楼北001-128区019号 [2023-06-22 08:38 ~ 22:00]', '昨天 18:29 早退违约': '早退违约, 预约: 图书馆2层二楼北001-128区026号 [2023-06-21 14:52 ~ 22:00]', '昨天 13:22 早退违约': '早退违约, 预约: 图书馆2层二楼北001-128区015号 [2023-06-21 08:50 ~ 22:00]', '2023-06-19 19:44 早退违约': '早退违约, 预约: 图书馆2层二楼南001-096区033号 [2023-06-19 14:30 ~ 22:00]', '2023-06-19 13:07 早退违约': '早退违约, 预约: 图书馆2层二楼南001-096区033号 [2023-06-19 08:43 ~ 22:00]', '2023-06-18 11:24 早退违约': '早退违约, 预约: 图书馆2层二楼南001-096区028号 [2023-06-18 08:43 ~ 22:00]', '2023-06-17 13:09 早退违约': '早退违约, 预约: 图书馆2层二楼南001-096区071号 [2023-06-17 10:26 ~ 22:00]'...}
```

### exit()

退出登入网页端

```python
>>> lib.exit()
Successful exit.
```





