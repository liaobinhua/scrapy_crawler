#!/usr/bin/python3
# encoding: utf-8
# Author:BinhuaLiao
# Created Time:Tue Jun  5 08:11:03 2018
# File Name:reptile_scrapy/utils/zhihu_login_requests.py
# Description:

import re
import time
import hmac
import json
import base64
import requests
import http.cookiejar as cookielib
from PIL import Image
from hashlib import sha1

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4)'
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/66.0.3359.181 Safari/537.36'
         )
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    "User-Agent": agent,
    "Connection": 'keep-alive'
}

try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie 未能加载")


def is_login():
    response = session.get("https://www.zhihu.com/inbox", headers=header,
                           allow_redirects=False)
    if response.status_code != 200:
        zhihu_login("account", "password")
    else:
        print("你已经登录了")


def get_xsrf_dc0():
    # 获取 xsrf code和d_c0
    # 在请求登录页面的时候页面会将xsrf code 和d_c0加入到cookie中返回给客户端
    response = session.get("https://www.zhihu.com/signup", headers=header)
    return response.cookies["_xsrf"], response.cookies["d_c0"]


def get_signature(time_str):
    h = hmac.new(key='d1b964811afb40118a12068ff74a12f4'.encode('utf-8'),
                 digestmod=sha1)
    grant_type = "password"
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    source = 'com.zhihu.web'
    now = time_str
    h.update((grant_type + client_id + source + now).encode('utf-8'))
    return h.hexdigest()


def get_identifying_code(headers):
    response = session.\
        get('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
            headers=headers)
    r = re.findall('"show_captcha":(\w+)', response.text)
    if r[0] == 'false':
        return ''
    else:
        response = session.\
            put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                headers=headers)
        show_captcha = json.loads(response.text)['img_base64']
        with open('captcha.jpg', 'wb') as f:
            f.write(base64.b64decode(show_captcha))
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
        captcha = input('输入验证码:')
        session.post('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                     headers=header,
                     data={"input_text": captcha})
        return captcha


def zhihu_login(account, password):
    post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
    XXsrftoken, XUDID = get_xsrf_dc0()
    header.update({
        # 固定值
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",
        "x-xsrftoken": XXsrftoken
    })
    time_str = str(int((time.time() * 1000)))

    post_data = {
        "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
        "grant_type": "password",
        "timestamp": time_str,
        "source": "com.zhihu.web",
        "password": password,
        "username": account,
        "captcha": "",
        "lang": "en",
        "ref_source": "homepage",
        "utm_source": "",
        "signature": get_signature(time_str),
        "cptcha": get_identifying_code(header)
    }

    response = session.post(post_url, data=post_data, headers=header,
                            cookies=session.cookies)
    if response.status_code == 201:
        session.cookies.save()
        is_login()
    else:
        print("登录失败")


if __name__ == '__main__':
    is_login()
