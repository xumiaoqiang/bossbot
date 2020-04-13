----------------------------

一、介绍
---------

bossbot 是一个用 python 实现的、基于boss直聘 websocket 协议的机器人，可运行在 Linux, Windows 和 Mac OSX 平台下。

本项目 github 地址： <https://github.com/xmiaoq/bossbot>

你可以通过扩展 bossbot 来实现：

* 监控、收集 boss直聘 消息
* 自动消息推送
* 简历发送
* 聊天机器人

二、安装方法
-------------

在 Python 3.4+ 下使用，用 pip 安装：

    pip install bossbot

三、实现你自己的 boss直聘 机器人
---------------------------

1、继承bossBot类，并重载对应函数

示例代码：
```python
from bossbot import BossBot

class Bot(bossBot):

    def on_text_message(self, data, boss_id, msg):
        '''
        文本 消息回调函数。
        :param data: 收到的完整消息内容
        :param boss_id: 发送次消息的boss的id
        :param msg: 文本内容
        :return:
        '''
        print('收到文字消息:' + msg)
        # 回复文字消息你好
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
        #同意发送简历
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
```

2、登陆你的boss直聘账号
```python
    bot = Bot()
    # 扫二维码方式登陆
    bot.login()
    # 免扫码登陆，需要先通过扫码登陆，拿到对应账号信息。因为长期有效所以记录下来，直接使用。
    # bot.login(uid='xxxx', user_id="xxxxxxxxx", token="xxxxx")
    
    bot.start()
```
3、功能示例
```python
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
```

四、待完成任务清单
---------------------------

- [ ] 实时消息信息记录进历史消息
- [ ] boss端登陆及使用


## 声明

**本项目仅供技术研究，请勿用于任何商业用途，请勿用于非法用途，如有任何人凭此做何非法事情，均于作者无关，特此声明。**