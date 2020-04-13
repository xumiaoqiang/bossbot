# -*- coding: utf-8 -*-
# @Time : 2020-03-15 23:24
# @Author : xmq

import json
import logging
from bossbot import BossBot
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger()

class Bot(BossBot):

    def on_text_message(self, data, boss_id, msg):
        '''
        文本 消息回调函数。
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param msg: 文本内容
        :return:
        '''
        print('收到文字消息:' + msg)
        self.send_message(boss_id, "你好")

    def on_request_resume_message(self, data, boss_id, mid):
        '''
        请求发送简历 消息回调函数
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param mid: 消息id，如果需要同意或者拒绝，需要此id
        :return:
        '''
        print('收到boss:%s,请求发送一份简历!' % boss_id)
        # 同意发送简历
        self.accept_resume(boss_id, mid, self.resumes[0]['resumeId'])

    def on_connect(self, client, userdata, flags, rc):
        '''
        websocket连接成功回调函数。
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        '''
        print("websocket 连接成功！")

        # 输出我的简历信息。
        print(json.dumps(self.resumes, ensure_ascii=False))
        # 输出与我最近沟通过的boss信息
        print(json.dumps(self.bosses, ensure_ascii=False))

        boss_id = list(self.bosses.keys())[0]
        resume_id = self.resumes[0]

        # 获取boss的详细信息，包含job信息
        boss_data = self.get_boss_data(boss_id)
        print(json.dumps(boss_data, ensure_ascii=False))

        # 获取与boss的历史聊天记录
        history_msg = self.get_history_msg(boss_id)
        print(json.dumps(history_msg, ensure_ascii=False))

        # 向boss发送文字消息
        # self.send_message(boss_id, "你好")

        # 向boss发送简历
        # self.request_send_resume(boss_id, resume_id)

if __name__ == '__main__':
    bot = Bot(logger)
    # 扫二维码方式登陆
    bot.login()
    # 免扫码登陆，需要先通过扫码登陆，拿到对应账号信息。因为长期有效所以记录下来，直接使用。
    # bot.login(uid='xxx', user_id="xxxx", token="xxxxxxxx")
    bot.start()


