import requests, rsa, sys, json, base64, time
import send
from config import USERNAME,PASSWORD
api = {
    'login': 'https://www.yuketang.cn/pc/login/verify_pwd_login/',
    'onlesson': 'https://www.yuketang.cn/api/v3/classroom/on-lesson',
    'attendlesson': 'https://www.yuketang.cn/v/lesson/lesson_info_v2',
    'attendlessonv3': 'https://www.yuketang.cn/api/v3/classroom/basic-info'
}
times = 960
counts = 0


def login(username, password):
    with open("./src/public.pem", mode='rb') as publicfile:
        keydata = publicfile.read()
    public = rsa.PublicKey.load_pkcs1_openssl_pem(keydata)
    pwd = base64.b64encode(rsa.encrypt(password.encode('utf-8'), public)).decode('utf-8')
    data = {
        'type': 'PP',
        'name': username,
        'pwd': pwd,
    }
    data = json.dumps(data)
    response = requests.post(url=api['login'], data=data)
    if response.json()['success']:
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        return cookies
    else:
        return False


def getOnLessonData(cookies):
    response = requests.get(url=api['onlesson'], cookies=cookies)
    if 'data' in response.json():
        if 'onLessonClassrooms' in response.json()['data']:
            onlessons = response.json()['data']['onLessonClassrooms']
            return onlessons
        else:
            send.sendmsg('debug', json.dumps(response.json()))
            onlessons = []
            return onlessons
    else:
        send.sendmsg('debug', json.dumps(response.json()))
        onlessons = []
        return onlessons


def attendLesson(cookies, classroom_id):
    params = {
        'classroom_id': classroom_id
    }
    response = requests.get(url=api['attendlessonv3'], cookies=cookies, params=params)
    data = response.json()
    if data['code'] == 0:
        lesson_name = data['data']['courseName']
        return lesson_name
    else:
        return False


def startup(counts, times):
    successLessons = []
    send.sendmsg(title='自动签到已启动', msg='自动签到已启动')
    cookies = login(USERNAME, PASSWORD)
    if cookies is False:
        send.sendmsg('错误信息', msg='密码错误')
        print('密码错误')
        sys.exit()
    while True:
        if counts >= times:
            send.sendmsg(title='自动签到已关闭', msg='自动签到已关闭')
            sys.exit()
        else:
            onlessons = getOnLessonData(cookies)
            if len(onlessons) != 0:
                for i in onlessons:
                    classroom_id = i['classroomId']
                    lesson_name = attendLesson(cookies=cookies, classroom_id=classroom_id)
                    if (lesson_name in successLessons) is False or lesson_name is not False:
                        send.sendmsg(title='签到成功', msg='签到成功\n\n课程：'+lesson_name)
                        successLessons.append(lesson_name)
            else:
                print('暂无课程')
        counts += 1
        time.sleep(20)


startup(counts=counts, times=times)
