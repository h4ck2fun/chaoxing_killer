#coding=utf-8
#author:xiaoshi

import os
import chaoxing
import re
session = chaoxing.getCodeImg()
username = raw_input('username:')
password = raw_input('password:')
code = raw_input('code:')
session = chaoxing.login(username,password,code,session)

os.system('cls')

passTaskUrl = []

courseList, courseLink = chaoxing.getCourses(session)
print 'courses:'
for i in range(len(courseList)):
	print '%d.%s' % (i+1,courseList[i])

domain = 'https://mooc1-2.chaoxing.com'
for i in range(len(courseLink)):
	courseLink[i] = domain + courseLink[i]

choice = int(raw_input('enter a number(1~%d):'%len(courseLink)))

taskLink = chaoxing.getTask(courseLink[choice-1],session)

for i in range(len(taskLink)):
		clazzId = re.findall(r'clazzid=(.+?)&',taskLink[i])[0]
		courseId = re.findall(r'courseId=(.+?)&',taskLink[i])[0]
		chapterId = re.findall(r'chapterId=(.+?)&',taskLink[i])[0]
		try:
			clazzId,userId,jobId,objectId,duration,dtoken,chapterId = chaoxing.getTaskInfo(clazzId,courseId,chapterId,session)
			passTaskUrl.append(chaoxing.passTask(clazzId,userId,jobId,objectId,duration,dtoken,chapterId,session))
			# passTaskUrl[i]
		except Exception,e:
			print '[+] oh.. something wrong',e
		else:
			print chaoxing.reqTask(passTaskUrl[i],session)