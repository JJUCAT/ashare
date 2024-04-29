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
  reasonable_price_stocks_dir = 'reasonable_price_stocks/'
  potential_stocks_dir = 'potential_stocks/'
  price_filtered_path = csv_path + reasonable_price_stocks_dir  
  potential_filtered_path = csv_path + potential_stocks_dir
  print('数据保存路径:%s\ncsv 路径:%s\n过滤后的数据路径:%s' %
        (base_path, csv_path, price_filtered_path))

  if not os.path.exists(data_path):
    print('创建数据目录')
    os.mkdir(data_path)
  if os.path.exists(csv_path):
    print('清空目录')
    shutil.rmtree(csv_path)
  os.mkdir(csv_path)
  os.mkdir(price_filtered_path)
  os.mkdir(potential_filtered_path)

  #0 拉取原始数据
  stock = Stock()
  stock.GetData(csv_path);

  #1 在近期资金流动热门股票中筛选价格适宜的股票
  price_low = 8.0
  price_high = 20.0
  main_fund = 0.01
  force_rise = False 
  stock.GetPriceStocksMoreDay(csv_path, price_low, price_high, main_fund, force_rise)

  #2 拉取股票近期数据
  rang = 1 # 查看 rang 天内的资金流向
  days = 60
  market_value = 100.0 # 总市值 100E
  fund_file = csv_path + 'price_stock_' + str(rang) + '.csv'
  save_path = csv_path + reasonable_price_stocks_dir
  stock.GetRecentStocks(fund_file, save_path, days, market_value)

  #3 挑选股票
  short_days = 5 # 短线均价天数
  middle_days = 10
  total_day = 20
  prophet = Prophet()
  # rising_stocks = prophet.FilterRising(save_path, short_days, total_day) # 简单些，量大，容易挑到个别异常跳动的股
  # underestimate_stocks = prophet.FilterUnderestimate(save_path, short_days, total_day)
  bottomout_stocks = prophet.FilterBottomOut(save_path, short_days, middle_days, total_day)
  # potential_stocks = prophet.FilterPotential(save_path, short_days, total_day, 0.05)
  macdrising_stocks = prophet.FilterMACDRising(save_path, 40, 7, 14, 3, 3)

  #4 发送邮件
  now = time.time()
  current = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
  msg = current + '\n'
  # if len(rising_stocks) > 0:
  #   msg += "均价上涨，新价上涨的股票：" + '\n'
  #   msg += reduce(lambda x, y: x+'\n'+y+'\n', rising_stocks)
  # msg += '\n'
  # if len(underestimate_stocks) > 0:
  #   msg += "均价上涨，新价较低的低估股票：" + '\n'
  #   msg += reduce(lambda x, y: x+'\n'+y+'\n', underestimate_stocks)
  # msg += '\n'
  if len(bottomout_stocks) > 0:
    msg += "均价下跌，新价上涨的反弹股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', bottomout_stocks)
  msg += '\n'
  # if len(potential_stocks) > 0:
  #   msg += "均价上涨，新价波动小的潜力股票：" + '\n'
  #   msg += reduce(lambda x, y: x+'\n'+y+'\n', potential_stocks)
  # msg += '\n'
  if len(macdrising_stocks) > 0:
    msg += "macd 预测上涨的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', macdrising_stocks)
  msg += '\n'
  lmrmail = LMRMail()

  lmrmail.Send(msg, 'empty')



def TimerTask():
  """设置定时任务
  """  

  # 设置定时任务
  schedule.every().day.at("09:45").do(Task0)
  schedule.every().day.at("23:06").do(Task0)
  schedule.every().day.at("22:54").do(Task0)

  while True:
    schedule.run_pending() # 运行所有可以运行的任务
    time.sleep(1)

