import requests, rsa, sys, json, base64, time
import send
from config import USERNAME,PASSWORD
api = {
    'login': 'https://changjiang.yuketang.cn/pc/login/verify_pwd_login/',
    'onlesson': 'https://changjiang.yuketang.cn/v/course_meta/on_lesson_courses',
    'attendlesson': 'https://changjiang.yuketang.cn/v/lesson/lesson_info_v2',
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
        onlessons = response.json()['data']['on_lessons']
        return onlessons
    else:
        send.sendmsg('debug', json.dumps(response.json()))
        onlessons = []
        return onlessons


def attendLesson(cookies, lesson_id):
    params = {
        'lesson_id': lesson_id
    }
    response = requests.get(url=api['attendlesson'], cookies=cookies, params=params)
    data = response.json()
    if data['success']:
        lesson_name = data['data']['classroom']['courseName']
        print(lesson_name)
        return lesson_name


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
                    lesson_id = i['lesson_id']
                    lesson_name = attendLesson(cookies=cookies, lesson_id=lesson_id)
                    if (lesson_name in successLessons) is False:
                        send.sendmsg(title='签到成功', msg='签到成功\n课程：'+lesson_name)
                        successLessons.append(lesson_name)
            else:
                print('暂无课程')
        counts += 1
        time.sleep(60)


startup(counts=counts, times=times)
