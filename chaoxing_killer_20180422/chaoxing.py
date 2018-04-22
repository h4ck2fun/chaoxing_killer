#coding=utf-8
#author:xiaoshi

import re
import md5
import time
import random
import requests
import HTMLParser
from bs4 import BeautifulSoup

user_agent = [ \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1", \
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
# 随机UA
header = {
	'User-Agent':random.choice(user_agent),
	'Connection':'close',
	'Accept':'text/html, */*; q=0.01',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Encoding':'gzip, deflate'
}

# 下载验证码图片保存到本地 人工识别
def getCodeImg():
	url = 'http://passport2.chaoxing.com/num/code'
	session = requests.Session()
	response = session.get(url)
	with open('code.jpg','wb') as file:
		file.write(response.content)
	return session

# 登录
def login(uname,password,numcode,session):
	url = 'http://passport2.chaoxing.com/mlogin?refer=http://i.mooc.chaoxing.com'
	data = {
	'pid':'0',
	'pidName':'',
	'fid':'2341',
	'fidName':'%E5%B9%BF%E4%B8%9C%E4%B8%9C%E8%BD%AF%E5%AD%A6%E9%99%A2',
	'allowJoin':'0',
	'isCheckNumCode':'1',
	'f':'0',
	'uname':uname,
	'password':password,
	'numcode':numcode
	}
	response = session.post(url,data)
	# 正则匹配错误
	re_str = re.findall(r'id="show_error">(.+?)&nbsp;</h4>',response.content)
	# 解决中文输出问题
	error = str(re_str).decode('string_escape').decode('utf-8')
	if '错误' in error :
		return error
	else:
		print 'login success'
		return session

# 获取课程
def getCourses(session):
	url = 'http://mooc1-2.chaoxing.com/visit/courses'
	domain = 'https://mooc1-2.chaoxing.com'
	response = session.get(url,headers=header)
	soup = BeautifulSoup(response.content,'lxml')
	# 找到类为clearfix的所有h3标签 返回list
	tag = str(soup.find_all('h3',attrs={'class':'clearfix'}))
	# 处理html转义字符 中文输出问题
	html_parser = HTMLParser.HTMLParser()
	tag = html_parser.unescape(tag).decode('unicode-escape')
	# 正则提取课程名以及课程链接
	# courseList 存放课程名称
	# courseLink 存放课程链接
	courseList = re.findall(r'>(.+?)</a>',tag)
	courseLink = re.findall(r'href="(.+?)"',tag)
	return courseList, courseLink

# 获取任务点 chapterId标识任务点 未解锁的被注释掉了 需要修改
def getTask(link,session):
	# taskName 存放任务点名称
	# taskLink 存放任务点链接
	domain = 'https://mooc1-2.chaoxing.com'
	taskName = []
	taskLink = []
	note = []
	response = session.get(link,headers=header)
	soup = BeautifulSoup(response.content,'lxml')

	# 提取一条链接作为模板
	span_tag = soup.find('span',attrs={'class':'articlename'})
	path = span_tag.a.get('href')

	# 找到类为articlename的所有span标签 返回list 
	# tag = soup.find_all('span',attrs={'class':'articlename'})

	# 找到类为clearfx的所有h3标签 返回list
	h3_tag = soup.find_all('h3',attrs={'class':'clearfix'})
	# 返回当前元素的下一个元素 也就是注释
	for i in range(len(h3_tag)):
		note.append(h3_tag[i].next_element)
	# 通过正则提取chapterId 
		chapterId = re.findall(r'chapterId=(.+?)&',note[i])
	# 将路径与域名拼接 再用正则替换chapterId
		taskLink.append(domain + path)
		taskLink[i] = re.sub(r'chapterId=(.+?)&','chapterId='+chapterId[0]+'&',taskLink[i])
	return taskLink

# 获取任务点信息
def getTaskInfo(clazzId,courseId,chapterId,session):
	
	# 随机延迟 
	time1 = random.randint(1,8)
	time.sleep(time1)

	# 获取 jobId objectId userId
	url1 = 'http://mooc1-2.chaoxing.com/knowledge/cards?clazzid=%s&courseid=%s&knowledgeid=%s' % (clazzId,courseId,chapterId)
	res1 = session.get(url1,headers=header)
	if 'objectid' not in res1.content:
		pass 
	else:
		jobId = re.findall(r'"jobid":"(.+?)"',res1.content)[0]
		objectId = re.findall(r'"objectid":"(.+?)"',res1.content)[0]
		userId = re.findall(r'"userid":"(.+?)"',res1.content)[0]

		# 获取 duration dtoken
		url2 = 'http://mooc1-2.chaoxing.com/ananas/status/%s' % objectId
		res2 = session.get(url2,headers=header)
		duration = re.findall(r'"duration":(.+?),',res2.content)[0]
		dtoken = re.findall(r'"dtoken":"(.+?)",',res2.content)[0]

		return clazzId,userId,jobId,objectId,duration,dtoken,chapterId

# 计算并构造完成任务点的url
def passTask(clazzId,userId,jobId,objectId,duration,dtoken,chapterId,session):
	playingTime = str(int(duration) * 1000)
	a = '[%s]' % clazzId
	b = '[%s]' % userId
	c = '[%s]' % jobId
	d = '[%s]' % objectId
	e = '[%s]' % playingTime
	f = '[d_yHJ!$pdA~5]'
	g = '[0_%s]' % duration
	t = '[%s]' % playingTime
	s = a + b + c + d + t + f + t + g
	enc = md5.new()
	enc.update(s)
	enc = enc.hexdigest()
	url = 'http://mooc1-2.chaoxing.com/multimedia/log/%s?clazzId=%s&clipTime=0_%s&otherInfo=nodeId_%s&duration=%s&userid=%s&rt=0.9&jobid=%s&dtype=Video&objectId=%s&view=pc&playingTime=%s&isdrag=3&enc=%s'\
	% (dtoken,clazzId,duration,chapterId,duration,userId,jobId,objectId,duration,enc)

	return url

# 访问url 完成任务点
def reqTask(taskUrl,session):
	response = session.get(taskUrl,headers=header)
	return response.content
