# -*- coding: utf-8 -*-
# @Time : 2020-03-15 23:09
# @Author : xmq
import logging
import threading
import time
import re
import json
import requests
import qrcode
import paho.mqtt.client as mqtt
from bossbot import protobuf_json
from bossbot.proto_pb2 import TechwolfChatProtocol


class BossBot(threading.Thread):
    uid = None
    user_id = None
    token = None

    bosses = {}
    resumes = []

    hostname = 'ws.zhipin.com'
    port = 443
    clientId = '19833398'
    timeout = 60
    keepAlive = 100
    topic = '/chatws'
    client = None
    session = requests.session()

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "sec-fetch-dest": "empty",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36\
                            (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://login.zhipin.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "referer": "https://login.zhipin.com/?ka=header-login",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    def __init__(self, logger=None):
        super().__init__()
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

    def _gen_qrcode(self):
        """
        生成二维码
        :return:
        """
        url = "https://login.zhipin.com/wapi/zppassport/captcha/randkey"
        resp = requests.get(url, headers=self.headers, verify=False)
        qr_id = resp.json()['zpData']['qrId']
        # 实例化QRCode生成qr对象
        qr_code = qrcode.QRCode()
        # 传入数据
        qr_code.add_data(qr_id)
        qr_code.make(fit=True)
        # 生成二维码
        img = qr_code.make_image()
        # 展示二维码
        img.show()
        return qr_id

    def _scan(self, qr_id):
        """
        扫码及获取登陆信息
        :param qr_id: 二维码的qr_id
        :return:
        """
        url = "https://login.zhipin.com/scan?uuid=%s&_%s" % (qr_id, str(int(time.time() * 1000)))
        self.session.get(url, headers=self.headers)

        url = "https://login.zhipin.com/wapi/zppassport/qrcode/dispatcher?qrId=%s&_=%s" % (
            qr_id, str(int(time.time() * 1000)))
        self.session.get(url, headers=self.headers)

        url = "https://www.zhipin.com/wapi/zpgeek/common/data/header.json"
        resp = self.session.get(url, headers=self.headers)
        zp_data = resp.json()['zpData']
        self.uid = re.search(r'uid:(\d*)', zp_data).group(1)
        self.user_id = requests.utils.dict_from_cookiejar(self.session.cookies)['t']
        self.token = re.search(r'token: ?"(.*)"', zp_data).group(1)

    def login(self, uid=None, user_id=None, token=None):
        """
        登陆账号
        使用扫码登陆后，会打印下面的3个参数值，长期有效。之后可以直接它们登陆，跳过扫码步骤
        :param uid: 登陆后返回的uid
        :param user_id: 登陆后返回的user_id
        :param token: 登陆后返回的token
        :return:
        """
        if uid is None or user_id is None or token is None:
            qr_id = self._gen_qrcode()
            self._scan(qr_id)
        else:
            self.uid = uid
            self.user_id = user_id
            self.token = token
            requests.utils.add_dict_to_cookiejar(self.session.cookies,
                                                 {"t": user_id, "wt": user_id})

        print('已登陆: uid: %s, user_id: %s, token: %s' % (self.uid, self.user_id, self.token))

        self.get_boss_list()
        self.get_resumes()

    def _on_connect(self, client, userdata, flags, rc):
        """
        即时通讯 websocket 连接成功
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        self.logger.info("Connected with result code %s", str(rc))
        # client.subscribe(self.topic)
        self.on_connect(client, userdata, flags, rc)

    def on_connect(self, client, userdata, flags, rc):
        """
        即时通讯 websocket 连接成功
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        pass


    def _on_disconnect(self, client, userdata, rc):
        """
        即时通讯 websocket 断开连接
        :param client:
        :param userdata:
        :param rc:
        :return:
        """
        if rc != 0:
            self.logger.info("Unexpected disconnection.")

    def _on_message(self, client, userdata, msg):
        """
        收到消息
        :param client:
        :param userdata:
        :param msg: 收到的消息内容
        :return:
        """
        protocol = TechwolfChatProtocol()
        protocol.ParseFromString(msg.payload)
        data = protobuf_json.pb2json(protocol)
        self.logger.debug('receive: %s', json.dumps(data, ensure_ascii=False))
        if data['type'] == 1:
            message = data['messages'][-1]
            body = message['body']
            if body['type'] == 1:
                # 文字消息

                self.on_text_message(data, message['from']['uid'], body['text'])
            elif body['type'] == 7 and message['from']['uid'] != int(self.uid):
                # 求简历
                self.on_request_resume_message(data, message['from']['uid'], message['mid'])
        elif data['type'] == 4:
            # /message/suggest
            pass
        elif data['type'] == 6:
            # 同步已读未读
            pass

    def on_text_message(self, data, boss_id, msg):
        """
        文本 消息回调函数。
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param msg: 文本内容
        :return:
        """
        self.logger.info('收到文字消息:%s', msg)

    def on_request_resume_message(self, data, boss_id, mid):
        """
        请求发送简历 消息回调函数
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param mid: 消息id，如果需要同意或者拒绝，需要此id
        :return:
        """
        self.logger.info('收到boss:%s,请求发送一份简历', boss_id)
        self.accept_resume(boss_id, mid, self.resumes[0]['resumeId'])


    def send_message(self, boss_id: str, msg: str):
        """
        发送文本消息
        :param boss_id: 对方boss_id
        :param msg: 消息内容
        :return:
        """
        mid = int(time.time() * 1000)
        chat = {
            "type": 1,
            "messages": [
                {
                    "from": {
                        "uid": "0"
                    },
                    "to": {
                        "uid": "0",
                        "name": self.bosses[boss_id]['encryptBossId']
                    },
                    "type": 1,
                    "mid": mid,
                    "time": int(time.time() * 1000),
                    "body": {
                        "type": 1,
                        "templateId": 1,
                        "text": msg
                    },
                    "cmid": mid
                }
            ]
        }
        chat_protocol = protobuf_json.json2pb(TechwolfChatProtocol(), chat)
        self.client.publish(self.topic, payload=chat_protocol.SerializeToString(), qos=0)

    def run(self):
        self.client = mqtt.Client(client_id="ws-CD090DC8307DE0AC", clean_session=True,
                                  transport="websockets")
        self.client.username_pw_set(self.token, self.user_id)
        headers = {
            "Cookie": "t=%s; wt=%s;" % (self.user_id, self.user_id)
        }
        self.client.ws_set_options(path=self.topic, headers=headers)
        self.client.tls_set()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.enable_logger(self.logger)

        ##30秒ping一次。60秒的话会断开连接
        self.client.connect(self.hostname, self.port, 30)
        self.client.loop_forever()

    def get_boss_list(self):
        """
        获取沟通过的boss信息
        :return:
        """
        for page in range(1, 10):
            url = "https://www.zhipin.com/wapi/zprelation/friend/getGeekFriendList.json?page=" \
                  + str(page)
            resp = self.session.get(url, headers=self.headers)
            new_friends = resp.json()['zpData'].get('result', [])
            for friend in new_friends:
                self.bosses[str(friend['uid'])] = friend

    def get_boss_data(self, boss_id, source_type="0"):
        """
        获取某个boss的详细信息（包含当前沟通的职位信息等）
        :param boss_id:
        :param source_type: 未知
        :return: boss的相信信息
        """
        if self.bosses[boss_id].get('bossData', None):
            return self.bosses[boss_id]['bossData']

        url = "https://www.zhipin.com/wapi/zpgeek/chat/bossdata.json"
        params = {
            "bossId": self.bosses[boss_id]['encryptBossId'],
            "bossSource": source_type,
            "securityId": self.bosses[boss_id]['securityId']
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        self.bosses[boss_id]['bossData'] = resp.json()['zpData']
        return self.bosses[boss_id]['bossData']

    def get_history_msg(self, boss_id):
        """
        获取与某个boss的历史聊天数据
        :param boss_id: boss_id
        :return: 聊天数据
        """
        if self.bosses[boss_id].get('messages', None):
            return self.bosses[boss_id]['messages']

        url = "https://www.zhipin.com/wapi/zpchat/geek/historyMsg"
        params = {
            "bossId": self.bosses[boss_id]['encryptBossId'],
            "groupId": self.bosses[boss_id]['encryptBossId'],
            "maxMsgId": "0",
            "c": "20",
            "page": "1",
            "src": "0",
            "securityId": self.bosses[boss_id]['securityId'],
            "loading": "true",
            "_t": str(int(time.time() * 1000))
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        self.bosses[boss_id]['messages'] = resp.json()['zpData'].get('messages', [])
        return self.bosses[boss_id]['messages']

    def request_send_resume(self, boss_id, resum_id):
        """
        请求发送简历
        :param boss_id: boss_id
        :param resum_id: 简历id
        :return: 发送成功与否结果
        """
        url = "https://www.zhipin.com/geek/new/requestSendResume.json"
        params = {
            "bossId": boss_id,
            "resumeId": resum_id,
            "toSource": "0"
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()

    def accept_resume(self, boss_id, mid, resume_id):
        """
        同意发送简历
        :param boss_id: boss_id
        :param mid: boss发送的请求简历消息的mid
        :param resume_id: 要发送的简历id
        :return: 发送成功与否结果
        """
        url = "https://www.zhipin.com/geek/new/acceptResume.json"
        params = {
            "bossId": boss_id,
            "mid": mid,
            "toSource": "0",
            "resumeId": resume_id
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        return resp.json()

    def get_resumes(self):
        """
        获取我的简历列表
        :return: 简历列表
        """
        url = "https://www.zhipin.com/wapi/zpgeek/resume/attachment/checkbox.json"
        params = {
        }
        resp = self.session.get(url=url, params=params, headers=self.headers)
        self.resumes = resp.json()['zpData'].get('resumeList', [])
        return self.resumes
