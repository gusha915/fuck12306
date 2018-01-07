# coding=utf-8
import json
import urllib

from hcutil import *

LOGIN_CODE_URL = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&0.35194760309320317'
BUY_CODE_URL = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&0.9432281084680152'
CHECK_CODE_URL = "https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn"
LOGIN_POST_URL = 'https://kyfw.12306.cn/otn/login/loginAysnSuggest'
USER_LOGIN_URL = 'https://kyfw.12306.cn/otn/login/userLogin'
INIT_PAGE_URL = "https://kyfw.12306.cn/otn/index/initMy12306"
QUERY_A_URL = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={0}&leftTicketDTO.from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'
LOG_URL = "https://kyfw.12306.cn/otn/leftTicket/log?leftTicketDTO.train_date={0}&leftTicketDTO.from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT"
begin_time = 0
end_time = 0
NEED_LOGIN = -1
FAIL = 0
SUCCESS = 1
EXIT = -99
NEED_CODE = 2
SEAT_TYPES = {"yz": '1', "yw": '3', "rw": '4', 'ze': 'O', 'zy': 'M'}
TICKET_TYPES = {"成人票": 1, "儿童票": 2, "学生票": 3, "残军票": 4}
ACCOUNT = None
PASSWORD = None


class Client:
	def __init__(self, account, password):
		self._s = requests.Session()
		self._account = account
		self._password = password

	def get_img(self, t=1):
		while True:
			try:
				c_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36', 'Host': 'kyfw.12306.cn',
							 'Referer': 'https://kyfw.12306.cn/otn/login/init'}
				url = LOGIN_CODE_URL
				if t == 0:
					url = BUY_CODE_URL
				imgstream = self._s.get(url, stream=True, headers=c_headers, verify=False, timeout=3)
				if imgstream.status_code == 200:
					with open("./tmp.jpg", 'wb') as fp:
						for chunk in imgstream.iter_content():
							fp.write(chunk)
					break
			except requests.exceptions.ReadTimeout or requests.exceptions.ConnectionError:
				print "get code timeout "
				time.sleep(1)

	def get_html(self, url):
		c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					 'Accept-Encoding': 'gzip, deflate, sdch, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'Upgrade-Insecure-Requests': '1',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}
		response = self._s.get(url, headers=c_headers, verify=False)
		response.encoding = "UTF-8"
		return response.text

	def login(self):
		self.get_img()
		# 输入验证码
		verifycode = ''
		while not verifycode:
			verifycode = raw_input("请输入验证码图片序号，以空格或逗号分割:")
		randcode = getpoint(verifycode)
		post_data = {
			'randCode': randcode,
			'rand': 'sjrand'
		}
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/login/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest'}
		while True:
			checkcode = self._s.post(CHECK_CODE_URL, data=post_data, headers=c_headers, verify=False)
			checkcode.encoding = "utf-8"
			if "200" in checkcode.text and "TRUE" in checkcode.text:
				break
			else:
				print "验证码错误，请重新输入"
			self.get_img()
			verifycode = ''
			while not verifycode:
				verifycode = raw_input("请输入验证码图片序号，以空格或逗号分割:")
			randcode = getpoint(verifycode)
			post_data = {
				'randCode': randcode,
				'rand': 'sjrand'
			}
		post_data = {
			'loginUserDTO.user_name': self._account,
			'userDTO.password': self._password,
			'randCode': randcode
		}
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/login/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		login = self._s.post(LOGIN_POST_URL, data=urllib.urlencode(post_data), headers=c_headers, verify=True)
		login.encoding = "utf-8"
		json_text = None
		try:
			json_text = json.loads(login.text)
		except ValueError:
			print "网络错误，请重试"
			return False
		if json_text['httpstatus'] == 200:
			if not json_text['status']:
				print json_text['messages'][0]
				return False
			else:
				if json_text['data']['loginCheck'] == 'Y':
					print "登录成功"
				self.check_login()
				return True

	def check_login(self):
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/login/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		post_data = {
			'_json_att': ''
		}
		response = self._s.post(USER_LOGIN_URL, data=post_data, headers=c_headers, verify=False, allow_redirects=True)
		c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					 'Accept-Encoding': 'gzip, deflate, sdch, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': 'max-age=0',
					 'Connection': 'keep-alive',
					 'Upgrade-Insecure-Requests': '1',
					 'Referer': 'https://kyfw.12306.cn/otn/login/init',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}
		response = self._s.get(response.url, headers=c_headers, verify=False)
		response.encoding = "utf-8"
		content = response.text.encode("utf-8")
		if "我的12306" in content:
			print "验证登录 success"
			return True
		else:
			print "=================验证登录 fail"
			return False

	def myorder(self):
		url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrder'
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/queryOrder/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		# 获得当前时间时间戳
		now = int(time.time())
		timearray = time.localtime(now)
		otherstyletime = time.strftime("%Y-%m-%d", timearray)
		post_data = {
			"queryType": "1",  # 1：按订票日期查询  2：按乘车日期查询
			"queryStartDate": "2016-12-01",
			"queryEndDate": otherstyletime,
			"come_from_flag": "my_resign",  # my_order：所有	my_resign：可改签  my_cs_resign：变更到站  my_refund：可退票
			"pageSize": "8",
			"pageIndex": "0",
			"query_where": "G",  # G 代表未出行订单  H 代表历史订单
			"sequeue_train_name": ""  # 搜索关键字 订单号／车次／乘客姓名
		}
		orders_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		orders_response.encoding = "UTF-8"
		json_orders = json.loads(orders_response.text)
		if json_orders['httpstatus'] == 200 and bool(json_orders['status']):
			data = json_orders['data']
			if data['order_total_number'] == '':  # 订单数
				return []
			else:
				try:
					# saveinfile("", "orders.txt", str(data).encode("utf8"))
					orderlist = data['OrderDTODataList']
					ticketlist = []
					for i in range(0, len(orderlist)):
						order = orderlist[i]
						array_passser_name_page = order['array_passser_name_page']  # 乘客名 list
						from_station_name_page = order['from_station_name_page']  # 始发站名 list
						to_station_name_page = order['to_station_name_page']  # 终点站 list
						order_date = order['order_date']  # 下单时间
						recordcount = order['recordCount']
						sequence_no = order['sequence_no']  # 订单号
						start_time_page = order['start_time_page']  # 开车时间 07:45
						start_train_date_page = order['start_train_date_page']  # 开车时间 2017-01-11 07:45
						ticket_price_all = order['ticket_price_all']  # 总票价 分
						ticket_total_price_page = order['ticket_total_price_page']  # 总票价 元
						ticket_totalnum = order['ticket_totalnum']  # 数量
						train_code_page = order['train_code_page']  # 车次

						tickets = order['tickets']
						for t in tickets:
							ticket = {'sequence_no': sequence_no}
							batch_no = t['batch_no']
							ticket['batch_no'] = batch_no
							coach_no = t['coach_no']
							ticket['coach_no'] = coach_no

							passenger = t['passengerDTO']
							passenger_id_no = passenger['passenger_id_no']  # 身份证
							passenger_id_type_code = passenger['passenger_id_type_code']  # 身份证类型
							passenger_id_type_name = passenger['passenger_id_type_name']  # 身份证类型名
							ticket['passenger_id_type_code'] = passenger_id_type_code
							ticket['passenger_id_no'] = passenger_id_no
							passenger_name = passenger['passenger_name']  # 姓名
							ticket['passenger_name'] = passenger_name
							reserve_time = t['reserve_time']  # 下单时间
							pay_limit_time = t['pay_limit_time']  # 最晚支付时间
							seat_flag = t['seat_flag']
							seat_no = t['seat_no']  # 座位号 0026
							ticket['seat_no'] = seat_no
							seat_name = t['seat_name']  # 座位名 026号
							ticket['seat_name'] = seat_name
							seat_type_code = t['seat_type_code']  # 座位类型
							seat_type_name = t['seat_type_name']  # 座位类型名
							t_sequence_no = t['sequence_no']  # 订单号
							ticket['t_sequence_no'] = t_sequence_no
							start_train_date_page = t['start_train_date_page']  # 开车时间 2017-01-11 07:45
							ticket['start_train_date_page'] = start_train_date_page
							stationtrain = t['stationTrainDTO']
							arrive_time = stationtrain['arrive_time']  # 到达时间 1970-01-01 09:26:00
							ticket['arrive_time'] = arrive_time
							distance = stationtrain['distance']  # 距离
							from_station_telecode = stationtrain['from_station_telecode']  # 始发站代码
							ticket['from_station_telecode'] = from_station_telecode
							from_station_name = stationtrain['from_station_name']  # 始发站名称
							ticket['from_station_name'] = from_station_name
							start_time = stationtrain['start_time']  # 开车时间 1970-01-01 07:45:00
							station_train_code = stationtrain['station_train_code']  # 车次
							ticket['station_train_code'] = station_train_code
							to_station_name = stationtrain['to_station_name']  # 终点站
							ticket['to_station_name'] = to_station_name
							to_station_telecode = stationtrain['to_station_telecode']  # 终点站代码
							ticket['to_station_telecode'] = to_station_telecode
							str_ticket_price_page = t['str_ticket_price_page']  # 票价  元
							ticket_no = t['ticket_no']  # 车票号
							ticket['ticket_no'] = ticket_no
							ticket_price = t['ticket_price']  # 票价 分
							ticket_status_code = t['ticket_status_code']  # 车票状态代码
							ticket_status_name = t['ticket_status_name']  # 车票状态
							ticket_type_code = t['ticket_type_code']  # 车票类型代码
							ticket_type_name = t['ticket_type_name']  # 车票类型名称
							print sequence_no, t_sequence_no, ticket_no, passenger_name, station_train_code, seat_name, from_station_name + "-" + to_station_name, start_train_date_page, arrive_time
							ticketlist.append(ticket)
						# ticketlist.append(
						# 	(sequence_no, t_sequence_no, ticket_no, passenger_name, station_train_code, seat_name,
						# 	 from_station_name, to_station_name, start_train_date_page, arrive_time,
						# 	 batch_no, coach_no, seat_no, from_station_telecode, to_station_telecode))
					return ticketlist
				except StandardError, e:
					print "解析错误", e
					saveinfile("", "order_error.txt", str(data).encode("utf8"))
					return []

	def jumpresignticket(self, ticket):
		url = "https://kyfw.12306.cn/otn/queryOrder/resginTicket"
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/queryOrder/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		ticketkey = ticket['t_sequence_no'] + "," + ticket['batch_no'] + "," + ticket['coach_no'] + "," + ticket['seat_no'] + "," + ticket['start_train_date_page'] + "#"
		post_data = {
			"ticketkey": ticketkey,
			"sequenceNo": ticket['t_sequence_no'],
			"changeTSFlag": "N",
			"_json_att": ""
		}
		self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		url = 'https://kyfw.12306.cn/otn/leftTicket/init'
		c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': 'max-age=0',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/queryOrder/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'Upgrade-Insecure-Requests': '1',
					 'Content-Type': 'application/x-www-form-urlencoded'}
		post_data = {
			"pre_step_flag": 'gcInit',
			"_json_att": ""
		}
		resign_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		resign_response.encoding = "utf-8"
		print "正在跳转.."
		if "var train_tour_flag = 'gc';" in resign_response.text:
			print "跳转成功"
			return SUCCESS
		else:
			saveinfile("", "jump_error.txt", resign_response.text.encode("utf-8"))
			return FAIL

	def refresh(self, train_date, from_station_code, to_station_code, ft=None):
		log_url = LOG_URL.format(train_date, from_station_code, to_station_code)
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, sdch, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': 'no-cache',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'If-Modified-Since': '0',
					 'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest'}
		log_response = self._s.get(log_url, headers=c_headers, verify=False, timeout=2)
		log_response.encoding = "UTF-8"
		json_log = json.loads(log_response.text)
		if not (json_log['httpstatus'] == 200 and bool(json_log['status'])):
			print "=================request log error"
		url = QUERY_A_URL.format(train_date, from_station_code, to_station_code)
		query_response = self._s.get(url, headers=c_headers, verify=False, timeout=2)
		query_response.encoding = "UTF_8"
		query_json = json.loads(query_response.text)
		if query_json['httpstatus'] == 200 and bool(query_json['status']):
			canbuylist = parsequery1(query_response, ft=ft)
			return canbuylist
		else:
			print "=================query error"
			return []

	def check_user(self):
		global end_time
		end_time = int(time.time())
		url = 'https://kyfw.12306.cn/otn/login/checkUser'
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': 'no-cache',
					 'Connection': 'keep-alive',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'If-Modified-Since': '0',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest'}
		post_data = {
			'_json_att': ''
		}
		check_user_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False, timeout=2)
		check_user_response.encoding = "UTF-8"
		json_check_user = json.loads(check_user_response.text)
		if not (json_check_user['httpstatus'] == 200 and bool(json_check_user['status']) and bool(json_check_user['data']['flag'])):
			print "=================check user error"
			# if self.check_login():
			# 	return True
			return False
		else:
			return True

	def jumptobuypage(self, canbuy, train_date, from_station_name, to_station_name, tour_flag):
		if not self.check_user():
			return NEED_LOGIN
		url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest'}
		secretstr = urllib.unquote(canbuy[0])
		print "正在购买[", train_date, "]，车次", canbuy[1], "[", canbuy[2], "-", canbuy[3], "][" + canbuy[4] + "-" + canbuy[5] + "]"
		post_data = {
			'secretStr': secretstr,
			'train_date': train_date,
			'back_train_date': train_date,
			'tour_flag': tour_flag,
			'purpose_codes': 'ADULT',
			'query_from_station_name': from_station_name,
			'query_to_station_name': to_station_name,
			'undefined': ''
		}
		submitorder_response = self._s.post(url, data=post_data, headers=c_headers, verify=False)
		submitorder_response.encoding = "UTF-8"
		submitorder_json = json.loads(submitorder_response.text)
		if not (submitorder_json['httpstatus'] == 200 and bool(submitorder_json['status'])):
			print submitorder_json['messages'][0]
			if "initNoComplete" in submitorder_json['messages'][0]:
				return EXIT
			return FAIL
		return SUCCESS

	def payfinishinit(self, referer):
		url = 'https://kyfw.12306.cn/otn/payfinish/init'
		c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': "max-age=0",
					 'Connection': 'keep-alive',
					 'Content-Type': 'application/x-www-form-urlencoded;',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'Upgrade-Insecure-Requests': '1'}
		post_data = {
			"_json_att": "",
			"get_ticket_pass": "pay_success",
		}
		finish_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		finish_response.encoding = "UTF-8"
		print "payfinishinit", finish_response.text
		if "已改签" in finish_response.text.encode("utf-8"):
			print "改签成功"
			return SUCCESS

	def payconfirmt(self, referer):
		url = 'https://kyfw.12306.cn/otn/pay/payConfirmT'
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest'}
		# todo 参数
		post_data = {
			# "parOrderDTOJson": '{"sequence_no":"EB33049142","order_date":"2017-01-01 00:00:00","ticket_totalnum":1,"ticket_price_all":1650.0,"epayFlag":"Y","orders":[{"sequence_no":"EB33049142","order_date":"2017-01-01 00:00:00","ticket_totalnum":1,"ticket_price_all":1650.0,"tickets":[{"stationTrainDTO":{"station_train_code":"D3126","from_station_telecode":"IOQ","from_station_name":"深圳北","start_time":"1970-01-01 07:00:00","to_station_telecode":"KNQ","to_station_name":"惠州南","arrive_time":"1970-01-01 07:33:00","distance":"56"},"passengerDTO":{"passenger_name":"邹冬冬","passenger_id_type_code":"1","passenger_id_type_name":"二代身份证","passenger_id_no":"360122199204050656","total_times":"98"},"ticket_no":"EB33049142211012C","sequence_no":"EB33049142","batch_no":"2","train_date":"2017-01-11 00:00:00","coach_no":"11","coach_name":"11","seat_no":"012C","seat_name":"12C号","seat_flag":"0","seat_type_code":"O","seat_type_name":"二等座","ticket_type_code":"1","ticket_type_name":"成人票","reserve_time":"2017-01-01 00:00:00","limit_time":"2017-01-01 18:38:30","lose_time":"2017-01-01 19:08:30","pay_limit_time":"2017-01-01 19:08:30","realize_time_char":"2017-01-01 18:38:30","ticket_price":1650.0,"old_ticket_price":1850.0,"return_total":200.0,"return_cost":200.0,"eticket_flag":"Y","pay_mode_code":"T","payOrderString":"2017-01-01 18:38:30","payOrderId":"3EB33049142002002183830206","amount":"1650","amount_char":1,"start_train_date_page":"2017-01-11 07:00","str_ticket_price_page":"16.5","come_go_traveller_ticket_page":"N","return_rate":"5","return_deliver_flag":"N","deliver_fee_char":"","is_need_alert_flag":false,"is_deliver":"00","dynamicProp":"","return_fact":0.0,"fee_char":"","sepcial_flags":"","column_nine_msg":""}],"isNeedSendMailAndMsg":"N","ticket_total_price_page":"16.5","come_go_traveller_order_page":"N","canOffLinePay":"N","if_deliver":"N"}]}',
			# "oldTicketDTOJson": '[{"stationTrainDTO":{"trainDTO":{},"station_train_code":"K446","from_station_telecode":"SZQ","from_station_name":"深圳","start_time":"1970-01-01 07:45:00","to_station_telecode":"HCQ","to_station_name":"惠州","arrive_time":"1970-01-01 09:26:00","distance":"115"},"passengerDTO":{"passenger_name":"邹冬冬","passenger_id_type_code":"1","passenger_id_type_name":"二代身份证","passenger_id_no":"360122199204050656","mobile_no":"18779187305","total_times":"98"},"ticket_no":"EB330491421060026","sequence_no":"EB33049142","batch_no":"1","train_date":"2017-01-11 00:00:00","coach_no":"06","coach_name":"06","seat_no":"0026","seat_name":"026号","seat_flag":"0","seat_type_code":"1","seat_type_name":"硬座","ticket_type_code":"1","ticket_type_name":"成人票","reserve_time":"2017-01-01 17:27:55","limit_time":"2017-01-01 17:27:55","lose_time":"2017-01-01 17:58:00","pay_limit_time":"2017-01-01 17:58:00","ticket_price":1850.0,"print_eticket_flag":"Y","resign_flag":"1","return_flag":"Y","confirm_flag":"N","pay_mode_code":"N","ticket_status_code":"a","ticket_status_name":"已支付","cancel_flag":"N","amount_char":0,"trade_mode":"E","start_train_date_page":"2017-01-11 07:45","str_ticket_price_page":"18.5","come_go_traveller_ticket_page":"N","return_deliver_flag":"N","deliver_fee_char":"","is_need_alert_flag":false,"is_deliver":"N","dynamicProp":"","fee_char":"","insure_query_no":""}]',
			# "sequence_no": "",
			"batch_no": "",
			"_json_att": ""
		}
		confirm_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		confirm_response.encoding = "UTF-8"
		print "payconfirmt", confirm_response.text

	def confirmresign(self, ticket, canbuy, seat_type):
		train_date = ticket['start_train_date_page'].split(" ")[0]
		jump_result = self.jumptobuypage(canbuy, train_date, ticket['from_station_name'], ticket['to_station_name'], 'gc')
		if jump_result != SUCCESS:
			return jump_result
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		post_data = {
			'_json_att': ''
		}
		c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': 'max-age=0',
					 'Connection': 'keep-alive',
					 'Content-Type': 'application/x-www-form-urlencoded',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
					 'Upgrade-Insecure-Requests': '1',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}
		initgc_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		initgc_response.encoding = "UTF-8"
		content = initgc_response.text.encode("utf-8")
		if not ("原票信息" in content):
			print "=================init gc error"
			return FAIL
		print "正在提交订单"
		m = re.search(r"var globalRepeatSubmitToken = '(\w{32})';", content)
		token = str(m.group(1))
		if len(token) != 32:
			print "获取token失败", token
			return FAIL
		print "获取token成功", token
		m = re.search(r"'train_no':'(\w{12})'", content)
		train_no = str(m.group(1))
		if len(train_no) != 12:
			print "获取train_no失败", train_no
			return FAIL
		print "获取train_no成功", train_no
		m = re.search(r"'leftTicketStr':'(\S.*?)'", content)
		if m is None:
			saveinfile("", "find leftTicketStr error,initDc_error.txt", content)
		leftticketstr = str(m.group(1))
		if len(leftticketstr) <= 0:
			print "获取leftticketstr失败", leftticketstr
			return FAIL
		print "获取leftticketstr成功", leftticketstr
		m = re.search(r"'purpose_codes':'(\d{2})'", content)
		purpose_codes = str(m.group(1))
		if len(purpose_codes) != 2:
			print "获取purpose_codes失败", purpose_codes
			return FAIL
		print "获取purpose_codes成功", purpose_codes
		m = re.search(r"'train_location':'(\w{2})'", content)
		train_location = str(m.group(1))
		if len(train_location) != 2:
			print "获取train_location失败", train_location
			return FAIL
		print "获取train_location成功", train_location
		m = re.search(r"'key_check_isChange':'(\w{56})'", content)
		key_check_ischange = str(m.group(1))
		if len(key_check_ischange) != 56:
			print "获取key_check_isChange失败", key_check_ischange
			return FAIL
		m = re.search(r"'mobile_no':'(\d{11})'", content)
		mobile_no = str(m.group(1))
		if len(mobile_no) != 11:
			print "获取手机号码失败，", mobile_no
			return FAIL
		print "获取key_check_isChange成功", key_check_ischange
		passenger = {"passenger_name": ticket['passenger_name'], "passenger_id_type_code": ticket['passenger_id_type_code'], "passenger_id_no": ticket['passenger_id_no'], "mobile_no": mobile_no,
					 "passenger_type": "1"}
		seatinfo = [seat_type, "成人票"]
		from_code = ticket['from_station_telecode']
		to_code = ticket['to_station_telecode']
		tour_flag = 'gc'
		if self.checkorderinfo(token, passenger, seatinfo, tour_flag) != SUCCESS:
			return FAIL
		print "checkorderinfo success"
		if self.getqueuecount(token, train_date, train_no, canbuy[1], leftticketstr, purpose_codes, train_location, seat_type, from_code, to_code, tour_flag) != SUCCESS:
			return FAIL
		print "getqueuecount success"
		if self.confirmforqueue(token, passenger, seatinfo, leftticketstr, purpose_codes, train_location, key_check_ischange, tour_flag) != SUCCESS:
			return FAIL
		flag, orderid = self.queryorderwaittime(token, tour_flag)
		while flag == 0:
			time.sleep(3)
			flag, orderid = self.queryorderwaittime(token, tour_flag)
		# 执行到这里差不多就成功了，所以下面的不需要做判断，都可以返回SUCCESS（其实也不用去执行）
		if orderid != '':
			if self.resultorderforqueue(orderid, token, tour_flag) != SUCCESS:
				return SUCCESS
			rand = int(time.time())
			if self.init(token, tour_flag, rand) != SUCCESS:
				return SUCCESS
			referer = 'https://kyfw.12306.cn/otn//payOrder/init?random=' + str(rand)
			self.payconfirmt(referer)
			if self.payfinishinit(referer) == SUCCESS:
				print "改签成功"
				return SUCCESS
		else:
			return SUCCESS

	# buy step 10
	def init(self, token, tour_flag, rand):
		referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		if tour_flag == 'gc':
			referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		url = 'https://kyfw.12306.cn/otn//payOrder/init?random=' + str(rand)
		if tour_flag == 'dc':
			c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
						 'Accept-Encoding': 'gzip, deflate, br',
						 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
						 'Connection': 'keep-alive',
						 'DNT': "1",
						 'Host': 'kyfw.12306.cn',
						 'Origin': 'https://kyfw.12306.cn',
						 'Referer': referer,
						 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
						 'X-Requested-With': 'XMLHttpRequest',
						 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		else:
			c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
						 'Accept-Encoding': 'gzip, deflate, br',
						 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
						 'Cache-Control': 'max-age=0',
						 'Connection': 'keep-alive',
						 'DNT': "1",
						 'Host': 'kyfw.12306.cn',
						 'Origin': 'https://kyfw.12306.cn',
						 'Referer': referer,
						 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
						 'Upgrade-Insecure-Requests': '1',
						 'Content-Type': 'application/x-www-form-urlencoded;'}
		post_data = {
			'_json_att': "",
			"REPEAT_SUBMIT_TOKEN": token
		}
		response = self._s.post(url, data=post_data, headers=c_headers, verify=False)
		response.encoding = 'UTF-8'
		# print response.text
		if tour_flag == 'dc':
			if "网上支付" in response.text.encode("utf-8"):
				print "购买成功，快去支付吧"
				return SUCCESS
			else:
				# print "购买失败"
				return FAIL
		else:
			if "立即改签" in response.text.encode("utf-8"):
				return SUCCESS
			else:
				return FAIL

	# buy step 9
	def resultorderforqueue(self, orderId, token, tour_flag):
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
		referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		if tour_flag == 'gc':
			url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForGcQueue'
			referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		post_data = {
			"orderSequence_no": orderId,
			'_json_att': "",
			"REPEAT_SUBMIT_TOKEN": token
		}
		response = self._s.post(url, data=post_data, headers=c_headers, verify=False)
		response.encoding = 'UTF-8'
		print "resultorderforqueue", response.text
		json_resp = json.loads(response.text)
		if json_resp['httpstatus'] == 200 and json_resp['status']:
			data = json_resp['data']
			if data['submitStatus']:
				print "提交成功"
				return SUCCESS
			else:
				print data['errMsg']
				if "继续支付" in data['errMsg'].encode("utf-8"):
					return SUCCESS
				else:
					return FAIL

	# buy step 8
	def queryorderwaittime(self, token, tourflag):
		now_time = int(time.time()) * 1000
		referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		if tourflag == 'gc':
			referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={0}&tourFlag={1}&_json_att=&REPEAT_SUBMIT_TOKEN={2}'
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest'}
		response = self._s.get(url.format(now_time, tourflag, token), headers=c_headers, verify=False)
		response.encoding = 'UTF-8'
		json_resp = json.loads(response.text)
		# print "queryorderwaittime", response.text
		if not (json_resp['httpstatus'] == 200 and json_resp['status']):
			print "queryorderwaittime fail", response.text
			return 0, ""
		else:
			data = json_resp['data']
			waitcount = int(data['waitCount'])
			print "waitCount", waitcount
			if data['queryOrderWaitTimeStatus']:
				print "貌似购买成功了？"
				return 1, ""
			return 1, data['orderId']

	# buy step 7
	def confirmforqueue(self, token, passenger, seatinfo, leftticketstr, purpose_codes, train_location, key_check_ischange, tour_flag, randcode=None):
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
		referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		if tour_flag == 'gc':
			url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmResignForQueue'
			referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		passengerticketstr = str(seatinfo[0]) + ",0," + str(TICKET_TYPES[seatinfo[1]]) + "," + passenger["passenger_name"] + "," + str(passenger['passenger_id_type_code']) + "," + passenger[
			'passenger_id_no'] + "," + passenger['mobile_no'] + ","
		if tour_flag == 'gc':
			passengerticketstr += "Y"
		else:
			passengerticketstr += "N"
		oldpassengerstr = passenger["passenger_name"] + "," + str(passenger['passenger_id_type_code']) + "," + passenger['passenger_id_no']
		if tour_flag == "gc":
			oldpassengerstr += ",_"
		else:
			oldpassengerstr += ("," + passenger['passenger_type'] + "_")
		post_data = {
			"passengerTicketStr": passengerticketstr,
			"oldPassengerStr": oldpassengerstr,
			"randCode": "",
			"purpose_codes": purpose_codes,
			"key_check_isChange": key_check_ischange,
			"leftTicketStr": leftticketstr,
			"train_location": train_location,
			"choose_seats": "",
			# seatDetailType  座位类型
			# var v = $("#x_no").text(); 下铺
			# var
			# w = $("#z_no").text();	# 中铺
			# var
			# x = $("#s_no").text();	# 下铺
			# return v + w + x
			"seatDetailType": "000",  # 暂不支持，所以全是0
			# var W = "";
			# if ($("#nvbbf").is (":checked")) {
			# W = "1"
			# } else {
			# W = "0"
			# }
			# if ($("#jtbf").is (":checked")) {
			# W = W + "1"
			# } else {
			# W = W + "0"
			# }
			"roomType": "00",  # 暂时不知道什么鬼，默认
			"_json_att": "",
			"REPEAT_SUBMIT_TOKEN": token
		}
		if randcode is not None:
			post_data['randCode'] = randcode
		# Y.dwAll = "N";
		# if ($("#chooseAllDW")[0] & & $("#chooseAllDW").is (":checked")) {
		# Y.dwAll = "Y"
		# }
		# "dwAll": "N",  # 不知道什么鬼，默认
		if tour_flag == 'dc':
			post_data['dwAll'] = "N"
		# print post_data
		response = self._s.post(url, data=post_data, headers=c_headers, verify=False)
		response.encoding = 'UTF-8'
		json_resp = json.loads(response.text)
		if json_resp['httpstatus'] == 200 and json_resp['status']:
			if json_resp['data']['submitStatus']:
				return SUCCESS
			else:
				print json_resp['data']['errMsg'], response.text
				return SUCCESS
		else:
			print "confirmforqueue fail", json_resp['data']['errMsg'], response.text
			return FAIL

	# buy step 6
	def getqueuecount(self, token, train_date, train_no, train_code, leftticketstr, purpose_codes, train_location, seat_type, from_code, to_code, tour_flag):
		referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		if tour_flag == 'gc':
			referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

		train_date = time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(time.mktime(time.strptime(train_date + " 08:00:00", "%Y-%m-%d %H:%M:%S")))) + " GMT+0800 (CST)"
		post_data = {
			"train_date": train_date,
			"train_no": train_no,
			"stationTrainCode": train_code,
			"seatType": seat_type,
			"fromStationTelecode": from_code,
			"toStationTelecode": to_code,
			"leftTicket": leftticketstr,
			"purpose_codes": purpose_codes,
			"train_location": train_location,
			"_json_att": "",
			"REPEAT_SUBMIT_TOKEN": token
		}
		# print post_data
		response = self._s.post(url, data=post_data, headers=c_headers, verify=False)
		response.encoding = 'UTF-8'
		# print "getqueuecount", response.text
		json_resp = json.loads(response.text)
		if not (json_resp['httpstatus'] == 200 and json_resp['status']):
			print "getqueuecount fail", response.text
			return FAIL
		else:
			ticketnum = json_resp['data']['ticket']
			# todo 这里ticket可能还有问题
			if ticketnum == '' or ticketnum == '0':
				print "没有余票了"
				return FAIL
		return SUCCESS

	# buy step 5
	def checkorderinfo(self, token, passenger, seatinfo, tour_flag):
		referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		if tour_flag == 'gc':
			referer = 'https://kyfw.12306.cn/otn/confirmPassenger/initGc'
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
		c_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': referer,
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		passengerticketstr = str(seatinfo[0]) + ",0," + str(TICKET_TYPES[seatinfo[1]]) + "," + passenger["passenger_name"] + "," + str(passenger['passenger_id_type_code']) + "," + passenger[
			'passenger_id_no'] + "," + passenger['mobile_no'] + ","
		if tour_flag == 'dc':
			passengerticketstr += 'N'
		else:
			passengerticketstr += 'Y'
		oldpassengerstr = passenger["passenger_name"] + "," + str(passenger['passenger_id_type_code']) + "," + passenger['passenger_id_no'] + "," + passenger['passenger_type'] + "_"
		post_data = {
			"cancel_flag": "2",
			"bed_level_order_num": "000000000000000000000000000000",
			"passengerTicketStr": passengerticketstr,
			"oldPassengerStr": oldpassengerstr,
			"tour_flag": tour_flag,
			"randCode": "",
			"_json_att": "",
			"REPEAT_SUBMIT_TOKEN": token
		}
		# print post_data
		# cancel_flag:2
		# bed_level_order_num:000000000000000000000000000000
		# passengerTicketStr:3, 0, 1, 邹冬冬, 1, 360122199204050656, 18779187305, N
		# oldPassengerStr:邹冬冬, 1, 360122199204050656, 1_
		# tour_flag:dc
		# randCode:
		# _json_att:
		# REPEAT_SUBMIT_TOKEN:b9c7e0dba3ffdce8a79441e3c30f20fe
		check_response = self._s.post(url, data=post_data, headers=c_headers, verify=False)
		check_response.encoding = "utf-8"
		check_json = json.loads(check_response.text)
		print "checkorderinfo", check_response.text
		if not (check_json['httpstatus'] == 200 and check_json['status']):
			print "check user error\t", check_response.text
			return FAIL
		if check_json['data']:
			show_code = check_json['data'].get("ifShowPassCode")
			if show_code is not None and show_code == 'Y':
				print "需要输入验证码"
				self.get_img(1)
				return NEED_CODE
			submit_status = check_json['data'].get("submitStatus")
			if submit_status is not None and not submit_status:
				print check_json['data'].get("errMsg")
				return FAIL
		return SUCCESS

	# buy step 4
	def getpassengers(self, token):
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
		c_headers = {'Accept': '*/*',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Connection': 'keep-alive',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
					 'X-Requested-With': 'XMLHttpRequest',
					 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		post_data = {
			"_json_att": "",
			"REPEAT_SUBMIT_TOKEN": token
		}
		passengers_response = self._s.post(url, data=post_data, headers=c_headers, verify=False, timeout=3)
		passengers_response.encoding = "utf-8"
		passengers_json = json.loads(passengers_response.text)
		passengerlist = []
		if passengers_json['httpstatus'] == 200 and passengers_json['status']:
			passengers = passengers_json['data']['normal_passengers']
			for passenger in passengers:
				p = {
					"address": passenger['address'],
					"born_date": passenger['born_date'],
					"email": passenger['email'],
					"mobile_no": passenger['mobile_no'],
					"passenger_id_no": passenger['passenger_id_no'],
					"passenger_id_type_code": passenger['passenger_id_type_code'],
					"passenger_id_type_name": passenger['passenger_id_type_name'],
					"passenger_name": passenger['passenger_name'],
					"passenger_type": passenger['passenger_type'],
					"passenger_type_name": passenger['passenger_type_name'],
					"sex_code": passenger['sex_code'],
					"sex_name": passenger['sex_name'],
					"total_times": passenger['total_times'],
					"phone_no": passenger['phone_no'],
					"postalcode": passenger['postalcode']
				}
				passengerlist.append(p)
		return passengerlist

	# step 3
	def submitbuyticket(self, canbuy, buyinfo):
		jump_result = self.jumptobuypage(canbuy, buyinfo['train_date'], buyinfo['from_station'][0], buyinfo['to_station'][0], 'dc')
		if jump_result != SUCCESS:
			return jump_result
		url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
		post_data = {
			'_json_att': ''
		}
		c_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					 'Accept-Encoding': 'gzip, deflate, br',
					 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
					 'Cache-Control': 'max-age=0',
					 'Connection': 'keep-alive',
					 'Content-Type': 'application/x-www-form-urlencoded',
					 'DNT': "1",
					 'Host': 'kyfw.12306.cn',
					 'Origin': 'https://kyfw.12306.cn',
					 'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
					 'Upgrade-Insecure-Requests': '1',
					 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}
		initgc_response = self._s.post(url, data=urllib.urlencode(post_data), headers=c_headers, verify=False)
		initgc_response.encoding = "UTF-8"
		content = initgc_response.text.encode("utf-8")
		if not ("列车信息" in content and "乘客信息" in content):
			print "=================init dc error"
			return FAIL
		m = re.search(r"var globalRepeatSubmitToken = '(\w{32})';", content)
		token = str(m.group(1))
		if len(token) != 32:
			print "获取token失败", token
			return FAIL
		print "获取token成功", token
		m = re.search(r"'train_no':'(\w{12})'", content)
		train_no = str(m.group(1))
		if len(train_no) != 12:
			print "获取train_no失败", train_no
			return FAIL
		print "获取train_no成功", train_no
		m = re.search(r"'leftTicketStr':'(\S.*?)'", content)
		if m is None:
			saveinfile("", "find leftTicketStr error,initDc_error.txt", content)
		leftticketstr = str(m.group(1))
		if len(leftticketstr) <= 0:
			print "获取leftticketstr失败", leftticketstr
			return FAIL
		print "获取leftticketstr成功", leftticketstr
		m = re.search(r"'purpose_codes':'(\d{2})'", content)
		purpose_codes = str(m.group(1))
		if len(purpose_codes) != 2:
			print "获取purpose_codes失败", purpose_codes
			return FAIL
		print "获取purpose_codes成功", purpose_codes
		m = re.search(r"'train_location':'(\w{2})'", content)
		train_location = str(m.group(1))
		if len(train_location) != 2:
			print "获取train_location失败", train_location
			return FAIL
		print "获取train_location成功", train_location
		m = re.search(r"'key_check_isChange':'(\w{56})'", content)
		key_check_ischange = str(m.group(1))
		if len(key_check_ischange) != 56:
			print "获取key_check_isChange失败", key_check_ischange
			return FAIL
		print "获取key_check_isChange成功", key_check_ischange
		passengers = self.getpassengers(token)
		if len(passengers) <= 0:
			print "乘客为空，请先添加"
			return EXIT
		# 这里过滤乘客
		passenger = None
		if buyinfo['user_idcard'] is not None:
			for i in range(0, len(passengers)):
				p = passengers[i]
				if p['passenger_id_no'] == buyinfo['user_idcard']:
					passenger = p
					break
		else:
			passenger = passengers[0]
		if passenger is None:
			print "没有找到该乘客信息", buyinfo['user_idcard']
			return EXIT
		tour_flag = 'dc'
		seatinfo = [buyinfo['seat_type'], "成人票"]
		check_result = self.checkorderinfo(token, passenger, seatinfo, tour_flag)
		if check_result == FAIL:
			return FAIL
		randcode = None
		if check_result == NEED_CODE:
			verifycode = ''
			while not verifycode:
				verifycode = raw_input("请输入验证码:")
			randcode = getpoint(verifycode)
			while True:
				post_data = {
					'randCode': randcode,
					'rand': 'randp',
					'_json_att': "",
					'REPEAT_SUBMIT_TOKEN': token
				}
				checkcode = self._s.post(CHECK_CODE_URL, data=post_data, headers=c_headers, verify=False)
				checkcode.encoding = "utf-8"
				print checkcode.text
				checkcode_json = json.loads(checkcode.text)
				if checkcode_json['status'] and checkcode_json['httpstatus'] == 200 and checkcode_json['data']['result'] == "0":
					break
				else:
					print "验证码输入错误，请重新输入"
				self.get_img(1)
				verifycode = ''
				while not verifycode:
					verifycode = raw_input("请输入验证码:")
				randcode = getpoint(verifycode)

		if self.getqueuecount(token, buyinfo['train_date'], train_no, canbuy[1], leftticketstr, purpose_codes, train_location, buyinfo['seat_type'], buyinfo['from_station'][1], buyinfo['to_station'][1],
							  tour_flag) != SUCCESS:
			return FAIL
		self.confirmforqueue(token, passenger, seatinfo, leftticketstr, purpose_codes, train_location, key_check_ischange, tour_flag, randcode=randcode)
		flag, orderid = self.queryorderwaittime(token, tour_flag)
		while flag == 0:
			time.sleep(3)
			flag, orderid = self.queryorderwaittime(token, tour_flag)
		# 执行到这里差不多就成功了，下面不需要判断是否成功与否，所以都可以返回SUCCESS
		if orderid != '':
			if self.resultorderforqueue(orderid, token, tour_flag) != SUCCESS:
				return SUCCESS
			if self.init(token, tour_flag, int(time.time())) == SUCCESS:
				print "提交成功"
				return SUCCESS
			else:
				return SUCCESS
		else:
			return SUCCESS


# 刷票： 登录-》跳转到车票查询页面-》不断刷新车票（并检测是否掉线）-》如果有车票则进行购买
def buyticket(buyinfo, ft=None, train_ft=None):
	global begin_time
	begin_time = int(time.time())
	client = Client(ACCOUNT, PASSWORD)
	client.get_html("https://kyfw.12306.cn/otn/login/init")
	while not client.login():
		client.get_html("https://kyfw.12306.cn/otn/login/init")
	buyinfo['from_station'] = querystationcode(buyinfo['from_station_name'])
	buyinfo['to_station'] = querystationcode(buyinfo['to_station_name'])
	count = 0
	while True:
		try:
			count += 1
			print "第", count, "次尝试"
			if count % 10 == 0:
				if not client.check_user():  # 检测用户是否登录
					return NEED_LOGIN
			canbuylist = client.refresh(buyinfo["train_date"], buyinfo['from_station'][1], buyinfo['to_station'][1], ft=ft)
			if canbuylist is not None and len(canbuylist) > 0:
				canbuy = None
				# 过滤优先车次
				if train_ft is None:
					canbuy = canbuylist[0]
				else:
					for cb in canbuylist:
						for train_f in train_ft:
							if cb[1] == train_f:
								canbuy = cb
								break
						if canbuy is not None:
							break
				if canbuy is None:
					print "无票..."
				else:
					# Email.send("抢票提醒", "有票了～～～")
					seat_type = SEAT_TYPES[getseattype(canbuy, ft)[1]]
					buyinfo['seat_type'] = seat_type
					print "有票..."
					flag = client.submitbuyticket(canbuy, buyinfo)
					if flag == NEED_LOGIN or flag == SUCCESS or flag == EXIT:
						return flag
		except (requests.exceptions.ReadTimeout, ValueError, AttributeError, requests.exceptions.ConnectionError), e:
			print e
		time.sleep(1)


def buy(buyinfo, ft=None, train_ft=None):
	while True:
		flag = buyticket(buyinfo, ft=ft, train_ft=train_ft)
		if flag == NEED_LOGIN:
			print "掉线，请重新登录 time:", begin_time, end_time, (end_time - begin_time)
			verifycode = raw_input("login again?:")
			if verifycode == 'yes':
				continue
			else:
				break
		elif flag == SUCCESS:
			break
		elif flag == EXIT:
			break


# 改签： 登录-》获取订单车票列表-》选择要改签的车票-》跳转到车票查询页面-》不断刷新车票（并检测是否掉线）-》如果有车票则进行改签
def doresign(resign_train_code, resign_train_date, ft=None, train_ft=None):
	global begin_time
	begin_time = int(time.time())
	client = Client(ACCOUNT, PASSWORD)
	client.get_html("https://kyfw.12306.cn/otn/login/init")
	while not client.login():
		client.get_html("https://kyfw.12306.cn/otn/login/init")
	ticketlist = client.myorder()
	if len(ticketlist) > 0:
		# 过滤要改签的火车票
		ticket = None
		for i in range(0, len(ticketlist)):
			t = ticketlist[i]
			if t['station_train_code'] == resign_train_code and resign_train_date in t['start_train_date_page']:
				# todo 注意这里可能会有问题
				ticket = t
				break
		if ticket is None:
			print "没有找到要改签的车票", resign_train_code, resign_train_date
			return EXIT
		print "正在改签车票", resign_train_code, resign_train_date, ticket['sequence_no']
		while client.jumpresignticket(ticket) != SUCCESS:
			print "跳转失败..."
			return EXIT
		count = 0
		while True:
			try:
				count += 1
				if count % 2 == 0:
					if not client.check_user():  # 检测用户是否登录
						return NEED_LOGIN
				canbuylist = client.refresh(ticket['start_train_date_page'].split(" ")[0], ticket['from_station_telecode'], ticket['to_station_telecode'], ft=ft)
				if len(canbuylist) > 0:
					canbuy = None
					# 过滤优先车次
					if train_ft is None:
						canbuy = canbuylist[0]
					else:
						for cb in canbuylist:
							for train_f in train_ft:
								if cb[1] == train_f:
									canbuy = cb
									break
					if canbuy is None:
						print "无票"
					else:
						# Email.send("抢票提醒", "有票了～～～")
						print "有票，改签中..."
						seat_type = SEAT_TYPES[getseattype(canbuy, ft)[1]]
						flag = client.confirmresign(ticket, canbuy, seat_type)
						if flag == NEED_LOGIN or flag == SUCCESS or flag == EXIT:
							return flag
				print "第", count, "次尝试"
			except (requests.exceptions.ReadTimeout, ValueError, requests.exceptions.ConnectionError), ee:
				print ".第", count, "次尝试", ee
			time.sleep(1)


def resign(resign_train_code, resign_train_date, ft=None, train_ft=None):
	while True:
		flag = doresign(resign_train_code, resign_train_date, ft=ft, train_ft=train_ft)
		if flag == NEED_LOGIN:
			print "掉线，请重新登录 time:", begin_time, end_time, (end_time - begin_time)
			Email.send("警告", "自动刷票已掉线，请重新登录")
			verifycode = raw_input("login again?:")
			if verifycode == 'yes':
				continue
			else:
				break
		elif flag == SUCCESS:
			break
		elif flag == EXIT:
			break


if __name__ == "__main__":
	ACCOUNT = "xxoo@qq.com"
	PASSWORD = "password"
	# 刷票
	# train_date 出发时间
	# from_station_name 始发
	# to_station_name 终点
	# user_idcard 身份证号码
	# ft 座位类型 目前只支持：硬座 硬卧 软卧 一等座 二等座
	# train_ft 车次
	buy({"train_date": "2018-01-18", "from_station_name": "深圳", "to_station_name": "惠州", "user_idcard": ""}, ft=["二等座"])  # , train_ft=["D2322"]

	# 改签
	# resign("K101", "2017-01-11", ft=["二等座", "硬座"], train_ft=["K101"])
	print "over..."
