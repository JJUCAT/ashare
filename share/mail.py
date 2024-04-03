#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText

class Mail(object):

  def __init__(self, mail_host, mail_user, mail_sender, mail_pass):
    """类初始化

    Args:
        mail_host (str): 邮箱服务器
        mail_user (str): 用户名
        mail_sender (str): 发送邮件的账号
        mail_pass (str): 密码 / 授权码
    """    
    print('Mail init.')
    self.mail_host = mail_host
    self.mail_user = mail_user
    self.mail_sender = mail_sender
    self.mail_pass = mail_pass


  def SetReceiver(self, receivers):
    """设置接收邮箱

    Args:
        receiver (list): 接收邮件的邮箱，可以设置多个
    """     
    self.receivers = receivers


  def Send(self, Message, File):
    """发送邮件

    Args:
        Message (str): 字符串
        File (...): 附件
    """     
    #设置 email 信息
    message = MIMEText(Message,'plain','utf-8')     
    message['Subject'] = 'title' 
    message['From'] = self.mail_sender
    message['To'] = self.receivers[0]  

    #登录并发送邮件
    try:
      smtpObj = smtplib.SMTP() 
      smtpObj.connect(self.mail_host, 25)
      smtpObj.login(self.mail_user, self.mail_pass) 
      smtpObj.sendmail(self.mail_sender, self.receivers, message.as_string()) 
      smtpObj.quit()
      print('success')
    except smtplib.SMTPException as e:
      print('error',e)


