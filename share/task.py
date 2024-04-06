#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-
import sys

# 指定路径导入第三方模块，在 pip install 后会有提示安装路径
sys.path.append('/home/lmr/.local/lib/python3.8/site-packages')
import schedule

import time
from share.stock import *
from share.prophet import *
from share.mail import *
import shutil
from functools import reduce


def Task0():
  """定时任务0
     爬取股市数据，整理后发送邮件
  """  

  base_path = '/home/lmr/ws/ashare/'
  data_path = base_path + '/data/'
  csv_path = data_path + '/csv/'
  filtered_path = csv_path + 'filtered_stocks/'  
  print('数据保存路径:%s\ncsv 路径:%s\n过滤后的数据路径:%s' %
        (base_path, csv_path, filtered_path))

  if not os.path.exists(data_path):
    print('创建数据目录')
    os.mkdir(data_path)
  if os.path.exists(csv_path):
    print('清空目录')
    shutil.rmtree(csv_path)
  os.mkdir(csv_path)
  os.mkdir(filtered_path)


  #0 拉取原始数据
  stock = Stock()
  stock.GetData(csv_path);

  #1 在近期资金流动热门股票中筛选价格适宜的股票
  price = 20
  main_fund = 10.0
  force_rise = True 
  stock.GetPriceStocksMoreDay(csv_path, price, main_fund, force_rise)

  #2 拉取股票近期数据
  rang = 3 # 查看 3 天内的资金流向  
  days = 40
  fund_file = csv_path + 'price_stock_' + str(rang) + '.csv'
  today_fund_file = csv_path + 'price_stock_1.csv'
  save_path = csv_path + 'filtered_stocks/'
  stock.GetRecentStocks(fund_file, today_fund_file, save_path, days)

  #3 挑选股票
  average_day = 5
  total_day = 30
  prophet = Prophet()
  underestimate_stocks = prophet.FilterUnderestimate(save_path, average_day, total_day)
  bottomout_stocks = prophet.FilterBottomOut(save_path, average_day, total_day)

  #4 发送邮件
  now = time.time()
  current = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
  msg = current + '\n'
  if len(underestimate_stocks) > 0:
    msg += msg + "低估股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', underestimate_stocks)
    msg += '\n'
  if len(bottomout_stocks) > 0:
    msg += msg + "反弹股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', bottomout_stocks)
    msg += '\n'
  lmrmail = LMRMail()
  lmrmail.Send(msg, 'empty')



def TimerTask():
  """设置定时任务
  """  

  # 设置定时任务
  schedule.every().day.at("14:25").do(Task0)
  schedule.every().day.at("15:00").do(Task0)
  schedule.every().day.at("18:00").do(Task0)

  while True:
    schedule.run_pending() # 运行所有可以运行的任务
    time.sleep(1)


