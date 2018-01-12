# coding=utf-8
import requests
import smtplib
from email.mime.text import MIMEText
from prettytable import *
import time
from warnings import filterwarnings
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import os

filterwarnings('ignore', category=InsecureRequestWarning)
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
}
QUERY_Z_URL = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={0}&leftTicketDTO.from_station={1}&leftTicketDTO.to_station={2}&purpose_codes=ADULT'
stations = []
SITE_MAP = {"商务座": "swz", "特等座": "tz", "一等座": "zy", "二等座": "ze", "高级软卧": "gr", "软卧": "rw", "硬卧": "yw", "软座": "rz", "硬座": "yz", "无座": "wz"}
INDEX_MAP = {1: "37,47", 2: "110,40", 3: "176,40", 4: "260,40", 5: "39,100", 6: "99,110", 7: "183,111", 8: "250,110"}
mail_host = 'smtp.163.com'
mail_user = 'sherlock_001@163.com'
mail_pass = 'password'
sender = 'sherlock_001@163.com'
DEFAULT_RECE = ['sherlock_65535@163.com']


class Email:
	def __init__(self):
		pass

	@staticmethod
	def send(subject, content, receivers=None):
		if receivers is None:
			receivers = DEFAULT_RECE
		message = MIMEText(content, 'plain', 'utf-8')
		message['subject'] = subject
		message['From'] = sender
		message['To'] = ','.join(receivers)
		try:
			smtpobj = smtplib.SMTP()
			smtpobj.connect(mail_host, 25)
			smtpobj.login(mail_user, mail_pass)
			smtpobj.sendmail(sender, receivers, message.as_string())
			smtpobj.quit()
		except smtplib.SMTPException, ee:
			print('Error: ', ee)


def saveinfile(base, filename, content):
	f = open(os.path.join(base, filename), "a")
	f.write(content)
	f.close()


def getstations():
	global stations
	f = open("/Users/winter-pc/Desktop/projects/fuck12306/stations.txt")
	content = f.read()
	infos = content.split("@")
	for info in infos:
		if info == '':
			continue
		infoarr = info.split("|")
		stations.append((infoarr[0], infoarr[1], infoarr[2], infoarr[3], infoarr[4], infoarr[5]))


def querystationcode(name):
	if len(stations) == 0:
		init()
	for station in stations:
		if name == station[1]:
			return station[1], station[2]
	return "", ""


def checkseat1(detail, ft):
	if 'zy' in ft and detail[31] != u'空' and detail[31] != u'无':
		return True
	if 'ze' in ft and detail[30] != u'空' and detail[30] != u'无':
		return True
	if 'rw' in ft and detail[23] != u'空' and detail[23] != u'无':
		return True
	if 'yw' in ft and detail[28] != u'空' and detail[28] != u'无':
		return True
	if 'rz' in ft and detail[25] != u'空' and detail[25] != u'无':
		return True
	if 'yz' in ft and detail[29] != u'空' and detail[29] != u'无':
		return True
	if 'wz' in ft and detail[26] != u'空' and detail[26] != u'无':
		return True
	return False


def converttocode(ft):
	result = []
	for f in ft:
		result.append(SITE_MAP[f])
	return result


def _getpoint(indexs):
	points = []
	for index in indexs:
		points.append(INDEX_MAP[int(index)])
	return ",".join(points)


def getpoint(indexs):
	ins = re.split(",| ", indexs)
	return _getpoint(ins)


def parsequery1(response, ft=None):
	response.encoding = "utf-8"
	table = PrettyTable(["车次", "出发站", "到达站", "出发时间", "到达时间", "历时", "商务座/特等座", "一等座", "二等座", "高级软卧", "软卧", "硬卧", "软座", "硬座", "无座"])
	data = response.json()['data']
	canbuylist = []
	for info in data["result"]:
		detail = info.split("|")
		canbuy = 0
		size = len(detail)
		for i in range(0, size):
			if len(detail[i]) == 0:
				detail[i] = u'空'
		if ft is not None and checkseat1(detail, ft=converttocode(ft)):
			canbuy = 1
		if canbuy == 1 or ft is None:
			table.add_row([detail[3], detail[4], detail[5], detail[8], detail[9], detail[10], detail[32], detail[31],
						   detail[30], detail[22], detail[23], detail[28], detail[25], detail[29], detail[26]])
		if canbuy == 1:
			if len(detail[0]) > 10:
				canbuylist.append((detail[0], detail[3], detail[4], detail[5], detail[8], detail[9], detail[10],
								   detail[32], detail[31],
								   detail[30], detail[22], detail[23], detail[28], detail[25], detail[29], detail[26]))
	print table
	return canbuylist


def getseattype(detail, ft=None):
	if detail[7] != '空' and detail[7] != '无':
		if ft is None or "特等座" in ft:
			return "特等座", "tz"
	if detail[8] != '空' and detail[8] != '无':
		if ft is None or "一等座" in ft:
			return "一等座", "zy"
	if detail[9] != '空' and detail[9] != '无':
		if ft is None or "二等座" in ft:
			return "二等座", "ze"
	if detail[10] != '空' and detail[10] != '无':
		if ft is None or "高级软卧" in ft:
			return "高级软卧", "gr"
	if detail[11] != '空' and detail[11] != '无':
		if ft is None or "软卧" in ft:
			return "软卧", "rw"
	if detail[12] != '空' and detail[12] != '无':
		if ft is None or "硬卧" in ft:
			return "硬卧", "yw"
	if detail[13] != '空' and detail[13] != '无':
		if ft is None or "软座" in ft:
			return "软座", "rz"
	if detail[14] != '空' and detail[14] != '无':
		if ft is None or "硬座" in ft:
			return "硬座", "yz"
	return "无座", "ze"


def init():
	getstations()


def listen():
	while True:
		try:
			pass
		except requests.exceptions.ReadTimeout:
			print "time out"
		time.sleep(1)


if __name__ == '__main__':
	saveinfile("", "order_error.txt", "error")
