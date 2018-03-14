import re, requests, sys, getpass, os
from bs4 import BeautifulSoup

def DoLogin(session, loginUrl, header):
    print("Pending：登陆请求提交中...")
    status = session.get(loginUrl, headers=header).status_code
    while status != 200:
        print("ERROR：登陆失败，即将重试，服务器响应代码：%d" % status)
        status = session.get(loginUrl, headers=header).status_code
    print("OK：登陆成功！")
    
def CheckLogin(status, session, loginUrl, header):
    if status == 302 or status == 500:
        print("ERROR：Session失效，尝试再次登陆")
        DoLogin(session, loginUrl, header)
        
def ListPage(session, listUrl, loginUrl, header):
    print("Pending：获取可选列表中...")
    lessonsListPage = session.get(listUrl, headers = header, timeout = 600)
    status = lessonsListPage.status_code
    while status != 200:
        print("ERROR：列表获取失败，服务器响应代码%d，重新获取中..." % status)
        CheckLogin(status, session, loginUrl, header)
        lessonsListPage = session.get(listUrl, headers = header, timeout = 600)
        status = lessonsListPage.status_code
        
    print("OK：可选列表获取成功")
    return lessonsListPage.content

def GrabLessons(session, lessonsListUrl, loginUrl, header, lessonsListPage, lessonsNameList):
    print("Pending：尝试选课...")
    soup = BeautifulSoup(lessonsListPage, "html.parser")
    i = 0
    while i < len(lessonsNameList):
        lessonObject = soup.find_all('td', text = re.compile(lessonsNameList[i]))
        iflag = 0
        for l in lessonObject:
            if iflag:
                iflag = 0
                continue

            iflag = 1
            s = l.find_next_siblings()
            capacity = s[10].text
            if s[-1].text[1:3] == '退选':
                print("OK：课程-%s-已选课，已从待选列表中删除。" % l.text)
                del lessonsNameList[i]
                i -= 1
            elif s[-1].text[1:3] == '选课':
                print("Pending：课程-%s-未选择，尝试选课..." % l.text)
                if capacity == '已满':
                    print("Warning：课程-%s-容量已满，稍后重试..." % l.text)
                else:
                    __EVENTTARGET = re.search(re.compile('dgData(.+?)Linkbutton2'), s[-1].a.get('href')).group(0)
                    __EVENTVALIDATION = soup.find('input', {'name' : '__EVENTVALIDATION'})['value']
                    __VIEWSTATE       = soup.find('input', {'name' : '__VIEWSTATE'})['value']
                    postData = {'__EVENTTARGET': __EVENTTARGET ,
                               '__EVENTARGUMENT': '' ,
                               '__VIEWSTATE': __VIEWSTATE ,
                               '__EVENTVALIDATION': __EVENTVALIDATION
                               }
                    selectLesson = session.post(lessonsListUrl ,
                                   data = postData,
                                   headers = header,
                                   timeout = 600)
                    status = selectLesson.status_code
                    CheckLogin(status, session, loginUrl, header)
                    if selectLesson.ok:
                        del lessonNameList[i]
                        i -= 1
                        print(i, len(lessonNameList))
                        print("OK：课程-%s-选课成功，已从待选列表中删除。" % l.text)
                        
                    else:
                        while not selectLesson.ok:
                            print("ERROR：服务器响应错误，尝试重新提交请求...")
                            selectLesson = session.post(lessonsListUrl ,
                                   data = postData,
                                   headers = header)
        if i < len(lessonsNameList):
            i += 1
    print("OK：待选列表一轮遍历完毕，剩余", len(lessonsNameList), "门课未选")
    return lessonsNameList

if __name__ == '__main__':
    print("--------------------------")
    print("-Nathaniel Zhou -> 周营成-")
    print("----yczhou94@gmail.com----")
    print("--------------------------")
    lessonsNameList =list()
    with open("lessonList.txt", "r", encoding='utf-8') as f:
        f.readline()
        for ln in f.readlines():
            lessonsNameList.append(ln.strip('\n'))
    username = lessonsNameList[0]
    password = lessonsNameList[1]
    lessonsNameList = lessonsNameList[2:len(lessonsNameList)]
    print("学号：%s" % username)
    # lessonsNameList = lessonsNameList[2:len(lessonsNameList)]
    
    loginUrl = 'http://202.4.152.190:8080/pyxx/MyService.ashx?callback=?&username=%s&password=%s' % (username, password)
    lessonsListUrl = 'http://202.4.152.190:8080/pyxx/pygl/pyjhxk.aspx?xh=%s' % username
    hdListUrl = 'http://202.4.152.190:8080/pyxx/txhdgl/hdlist.aspx?xh=%s' % username
    UA= 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    header = { "User-Agent" : UA}
    grabLessons = requests.Session()
    while 1:
        try:
            DoLogin(grabLessons, loginUrl, header)
        except Exception as e:
            print("ERROR：操作超时，稍后重试...")
        else:
            break
    print(lessonsNameList)
    while len(lessonsNameList) != 0:
        while 1:
            try:
                lessonsListPage = ListPage(grabLessons, lessonsListUrl, loginUrl, header)
                lessonsNameList = GrabLessons(grabLessons, lessonsListUrl, loginUrl, header, lessonsListPage, lessonsNameList)
            except Exception as e:
                print("ERROR：操作超时，稍后重试...")
            else:
                break