# -*- coding: utf-8 -*-
import os
import re
import shutil
import time
import itchat
from itchat.content import *

msg_dict = {}

rev_tmp_dir = "E:/repo/PythonCode/src/WechatWithdraw/"
if not os.path.exists(rev_tmp_dir):
    os.mkdir(rev_tmp_dir)

face_bug = None


@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO])
def handler_receive_msg(msg):
    global face_bug

    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    msg_id = msg['MsgId']

    msg_time = msg['CreateTime']

    msg_from = (itchat.search_friends(userName=msg['FromUserName']))["NickName"]

    msg_content = None

    msg_share_url = None

    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']
    elif msg['Type'] == 'Recording' or msg['Type'] == 'Attachment' or msg['Type'] == 'Video' or msg['Type'] == 'Picture':
        msg_content = r"" + msg['FileName']
        msg['Text'](rev_tmp_dir + msg['FileName'])
    elif msg['Type'] == 'Card':
        msg_content = msg['RecommendInfo']['NickName'] + r" 的名片"
    elif msg['Type'] == 'Map':
        x, y, location = re.search("<location x=(.*?) y=(.*?).*label=(.*?).*", msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()
        else:
            msg_content = r"" + location
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        msg_share_url = msg['Url']

    face_bug = msg_content

    msg_dict.update(
        {
            msg_id: {
                "msg_from": msg_from,
                "msg_time": msg_time,
                "msg_time_rec": msg_time_rec,
                "msg_type": msg["Type"],
                "msg_content": msg_content,
                "msg_share_url": msg_share_url
            }
        }
    )


@itchat.msg_register([NOTE])
def send_msg_helper(msg):
    global face_bug
    if re.search(r"<![CDATA[.*撤回了一条消息]]>", msg['Content']) is not None:
        old_msg_id = re.search("<msgid>(.*?)</msgid>", msg['Content']).group(1)
        old_msg = msg_dict.get(old_msg_id, {})
        if len(old_msg_id) < 11:
            itchat.send_file(rev_tmp_dir + face_bug, toUserName='filehelper')
            os.remove(rev_tmp_dir + face_bug)
        else:
            msg_body = "告诉你一个秘密~\n用户【{0}】 撤回了 {1} 消息\n【时间】：\n{2}\n【内容】：\n{3}".format(old_msg.get('msg_from'),
                                                                                     old_msg.get("msg_type"),
                                                                                     old_msg.get('msg_time_rec'),
                                                                                     old_msg.get('msg_content'))

            if old_msg['msg_type'] == "Sharing":
                msg_body += " 【链接】➣ " + old_msg.get('msg_share_url')

            itchat.send(msg_body, toUserName='filehelper')

            if old_msg["msg_type"] == "Picture" or old_msg["msg_type"] == "Recording" or old_msg["msg_type"] == "Video" or old_msg["msg_type"] == "Attachment":
                file = '@fil@%s' % (rev_tmp_dir + old_msg['msg_content'])
                itchat.send(msg=file, toUserName='filehelper')
                os.remove(rev_tmp_dir + old_msg['msg_content'])

            msg_dict.pop(old_msg_id)


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    itchat.run()
