# -*- coding: utf-8 -*-
import re
import pdb
import time
import hmac
import json
import base64
import scrapy
import datetime
import requests
from PIL import Image
from hashlib import sha1
from urllib import parse
import http.cookiejar as cookielib
from scrapy.loader import ItemLoader
from reptile_scrapy.items import ZhihuAnswerItem
from reptile_scrapy.items import ZhihuQuestionItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = (
        'https://www.zhihu.com/api/v4/questions/{0}/answers?'
        'include=data%5B*%5D.is_normal%2Cadmin_closed_comment%'
        '2Creward_info%2Cis_collapsed%2Cannotation_action%2'
        'Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2'
        'Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2'
        'Ccan_comment%2Ccontent%2Ceditable_content%2'
        'Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2'
        'Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2'
        'Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2'
        'Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B*%5D.mark_infos%5B*%5'
        'D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3D'
        'best_answerer)%5D.topics&offset=&limit={1}&sort_by={2}'
    )

    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
    agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4)'
             'AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/66.0.3359.181 Safari/537.36')
    header = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": agent,
        "Connection": 'keep-alive',
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",
        "x-udid": "AIBCAsCGVQuPTvXRtARrQR1KlhPV_LGetJs="
    }

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False,
                          all_urls)
        print(all_urls)
        for url in all_urls:
            # 如果提取到question相关的页面则下载后交由提取函数进行提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                yield scrapy.Request(
                    request_url,
                    headers=self.header,
                    callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(
                    url,
                    headers=self.header,
                    callback=self.parse)

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        if (("QuestionHeader-title" in response.text) and
                ("List-headerText" in requests.text)):
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*",
                                 response.url)
            if match_obj:
                question_id = match_obj.group(2)
            item_loader = ItemLoader(item=ZhihuQuestionItem(),
                                     response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css(
                "comments_num",
                ".QuestionHeader-Comment button::text")
            item_loader.add_css(
                "watch_user_num",
                ".NumberBoard-itemValue::text")
            item_loader.add_css(
                "topics",
                ".QuestionHeader-topics .Popover div::text")
            question_item = item_loader.load_item()
            item_loader.add_css("answer_num", ".List-headerText span::text")
            yield scrapy.Request(
                self.start_answer_url.format(question_id, 20, 0),
                headers=self.header,
                callback=self.parse_answer
            )
            yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(
                next_url,
                headers=self.header,
                callback=self.parse_answer
            )

    def start_requests(self):
        XXsrftoken, XUDID = self.get_xsrf()
        self.header.update({
            # 固定值
            "x-xsrftoken": XXsrftoken
        })
        yield scrapy.Request(
            'https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
            headers=self.header,
            callback=self.login)

    def get_xsrf(self):
        # 获取 xsrf code和d_c0
        # 在请求登录页面的时候页面会将xsrf code和d_c0加入到cookie中返回给客户端
        response = self.session.get("https://www.zhihu.com/signup",
                                    headers=self.header)
        return response.cookies["_xsrf"], response.cookies["d_c0"]

    def get_signature(self, time_str):
        h = hmac.new(key='d1b964811afb40118a12068ff74a12f4'.encode('utf-8'),
                     digestmod=sha1)
        grant_type = "password"
        client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
        source = 'com.zhihu.web'
        now = time_str
        h.update((grant_type + client_id + source + now).encode('utf-8'))
        return h.hexdigest()

    def login(self, response):
        post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
        time_str = str(int((time.time() * 1000)))

        post_data = {
            "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
            "grant_type": "password",
            "timestamp": time_str,
            "source": "com.zhihu.web",
            "password": 'password',
            "username": 'account',
            "lang": "en",
            "ref_source": "homepage",
            "utm_source": "",
            "signature": self.get_signature(time_str),
            "captcha": self.get_identifying_code(response)
        }

        # t = str(int(time.time() * 1000))
        # response = self.session.post(post_url, data=post_data,
        #                              headers=self.header,
        #                              cookies=self.session.cookies)

        return [scrapy.FormRequest(
            post_url,
            formdata=post_data,
            headers=self.header,
            callback=self.check_login)]

    def get_identifying_code(self, response):
        # response = self.session.get(
        #     'https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
        #     headers=self.header)
        r = re.findall('"show_captcha":(\w+)', response.text)
        if r[0] == 'false':
            return ''
        else:
            response = self.session.\
                put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                    headers=self.header)
            show_captcha = json.loads(response.text)['img_base64']
            with open('captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(show_captcha))
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
            captcha = input('输入验证码:')
            # self.session.post(
            #     'https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
            #     headers=self.header,
            #     data={"input_text": captcha})
        return captcha

    def check_login(self, response):
        # 验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        print(text_json)
        print(response)
        yield scrapy.Request(
            "https://www.zhihu.com",
            headers=self.header)
