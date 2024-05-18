#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
import csv
from share.stock import *
from share.prophet import *
from share.mail import *
from share.task import *
import pathlib
import shutil


if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')

  config_path = '/home/lmr/ws/ashare/ashare/config/datapath.json'
  config_dict = TaskLoadConfigurations(config_path) # 加载参数
  TaskClearData(config_dict) # 清除数据
  TaskPullData(config_dict) # 拉取数据



  # TimerTask()
  # TaskBuyMonitor()
  # TaskSellMonitor()

