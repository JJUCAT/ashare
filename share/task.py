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


def TaskBuyMonitor():
  """定时任务，买入信号
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
  short_days = 20 # 均价天数
  middle_days = 30
  total_day = 40

  prophet = Prophet()
  rising_stocks = prophet.FilterAveragePrice(save_path, short_days, total_day, 1, 1)

  # MACD 金叉 判断
  short_ave = 12
  long_ave = 26
  dem_ave = 9
  dif_trend_num = 5
  osc_trend_num = 3  
  macdrising_stocks = prophet.FilterMACD(save_path, 40, short_ave, long_ave, dem_ave, dif_trend_num, osc_trend_num, 1)

  # K 线分析
  local_scale = 0.25 # 当天实体线对当天 K 线占比
  global_scale = 0.02 # 当天实体线对收盘价占比
  kanalyse_stocks = prophet.FilterKAnalyse(save_path, local_scale, global_scale, 1)

  # 换手率判断趋势是否成型
  turnover_flip = 2.0 # 换手率，单位 %，高换手率意味着趋势要翻转
  turnover_continue = 0.8 # 换手率，单位 %，低换手率意味着趋势保持
  turnover_rang = 3 # 检查天数
  turnover_flip_stocks = prophet.FilterTurnoverRate(save_path, turnover_flip, turnover_rang, True)
  print("共有 %d 支股票用换手率检测到趋势翻转" % (len(turnover_flip_stocks)))
  turnover_continue_stocks = prophet.FilterTurnoverRate(save_path, turnover_continue, turnover_rang, False)
  print("共有 %d 支股票用换手率检测到趋势保持" % (len(turnover_continue_stocks)))

  # 均线分析和换手率趋势保持交集
  rmt = list(set(macdrising_stocks) & set(turnover_continue_stocks) & set(rising_stocks))
  print("共有 %d 支股票用 MACD 和换手率和均线分析观测到保持趋势" % (len(rmt)))

  # 均线分析和 macd 交集
  rm = list(set(macdrising_stocks) & set(rising_stocks))
  print("共有 %d 支股票用 MACD 和均线分析观测到上涨趋势" % (len(rm)))

  # macd 和 k 线分析交集
  mk = list(set(macdrising_stocks) & set(kanalyse_stocks))
  print("共有 %d 支股票用 MACD 和 K 线分析观测到上涨趋势" % (len(mk)))

  #4 发送邮件
  now = time.time()
  current = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
  msg = current + '\n'
  # if len(rising_stocks) > 0:
  #   msg += "均价上涨，新价上涨的股票：" + '\n'
  #   msg += reduce(lambda x, y: x+'\n'+y+'\n', rising_stocks)
  # msg += '\n'
  if len(kanalyse_stocks) > 0:
    msg += "k 线分析预测上涨的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', kanalyse_stocks)
  msg += '\n'
  if len(macdrising_stocks) > 0:
    msg += "macd 预测上涨的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', macdrising_stocks)
  msg += '\n'
  if len(rmt) > 0:
    msg += "macd和换手率和均线分析交集预测保持上涨的股票:" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', rmt)
  msg += '\n'
  if len(rm) > 0:
    msg += "macd 和均线分析交集预测上涨的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', rm)
  msg += '\n'
  if len(mk) > 0:
    msg += "macd 和 k 分析交集预测上涨的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', mk)
  msg += '\n'
  lmrmail = LMRMail()
  lmrmail.Send(msg, 'empty')



def TaskSellMonitor():
  """定时任务，卖出信号检测
     爬取股市数据，整理后发送邮件
  """  

  base_path = '/home/lmr/ws/ashare/'
  data_path = base_path + '/data/'
  print('数据保存路径:%s' % (base_path))
  mystocks_path = data_path + 'mystocks/'
  mystocks_file = mystocks_path + '/mystocks.csv'
  save_path = mystocks_path + 'data/'

  if not os.path.exists(data_path):
    print('创建数据目录')
    os.mkdir(data_path)
  if not os.path.exists(mystocks_path):
    print('创建用户数据目录')
    os.mkdir(mystocks_path)
  if os.path.exists(save_path):
    print('清空用户股票数据目录')
    shutil.rmtree(save_path)
  os.mkdir(save_path)

  stock = Stock()
  prophet = Prophet()

  #0 拉取用户股票数据
  days = 60
  stock.GetMyStocks(mystocks_file, save_path, days)

  # 均线分析
  short_days = 20 # 均价天数
  middle_days = 30
  total_day = 40
  falling_stocks = prophet.FilterAveragePrice(save_path, short_days, total_day, -1, -1)

  # K 线分析
  local_scale = 0.25 # 当天实体线对当天 K 线占比
  global_scale = 0.02 # 当天实体线对收盘价占比
  kanalyse_stocks = prophet.FilterKAnalyse(save_path, local_scale, global_scale, -1)

  # MACD 死叉 判断
  short_ave = 12
  long_ave = 26
  dem_ave = 9
  dif_trend_num = 5
  osc_trend_num = 3  
  macdrising_stocks = prophet.FilterMACD(save_path, 40, short_ave, long_ave, dem_ave, dif_trend_num, osc_trend_num, -1)

  # 换手率判断趋势是否成型
  turnover_flip = 2.0 # 换手率，单位 %，高换手率意味着趋势要翻转
  turnover_continue = 0.8 # 换手率，单位 %，低换手率意味着趋势保持
  turnover_rang = 3 # 检查天数
  turnover_flip_stocks = prophet.FilterTurnoverRate(save_path, turnover_flip, turnover_rang, True)
  print("共有 %d 支股票用换手率检测到趋势翻转" % (len(turnover_flip_stocks)))
  turnover_continue_stocks = prophet.FilterTurnoverRate(save_path, turnover_continue, turnover_rang, False)
  print("共有 %d 支股票用换手率检测到趋势保持" % (len(turnover_continue_stocks)))

  # 均线分析和换手率趋势保持交集
  rmt = list(set(macdrising_stocks) & set(turnover_continue_stocks) & set(falling_stocks))
  print("共有 %d 支股票用 MACD 和换手率和均线分析观测到保持趋势" % (len(rmt)))

  # 均线分析和 macd 交集
  rm = list(set(macdrising_stocks) & set(falling_stocks))
  print("共有 %d 支股票用 MACD 和均线分析观测到下跌趋势" % (len(rm)))

  # macd 和 k 线分析交集
  mk = list(set(macdrising_stocks) & set(kanalyse_stocks))
  print("共有 %d 支股票用 MACD 和 K 线分析观测到下跌趋势" % (len(mk)))

  #4 发送邮件
  now = time.time()
  current = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
  msg = current + '\n'
  # if len(rising_stocks) > 0:
  #   msg += "均价下跌，新价下跌的股票：" + '\n'
  #   msg += reduce(lambda x, y: x+'\n'+y+'\n', rising_stocks)
  # msg += '\n'
  if len(kanalyse_stocks) > 0:
    msg += "k 线分析预测下跌的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', kanalyse_stocks)
  msg += '\n'
  if len(macdrising_stocks) > 0:
    msg += "macd 预测下跌的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', macdrising_stocks)
  msg += '\n'
  if len(rmt) > 0:
    msg += "macd和换手率和均线分析交集预测保持下跌的股票:" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', rmt)
  msg += '\n'
  if len(rm) > 0:
    msg += "macd 和均线分析交集预测下跌的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', rm)
  msg += '\n'
  if len(mk) > 0:
    msg += "macd 和 k 分析交集预测下跌的股票：" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', mk)
  msg += '\n'
  lmrmail = LMRMail()
  lmrmail.Send(msg, 'empty')




def TimerTask():
  """设置定时任务
  """  

  # 设置定时任务
  # schedule.every().day.at("09:45").do(Task0)
  # schedule.every().day.at("23:06").do(Task0)
  # schedule.every().day.at("22:54").do(Task0)

  while True:
    schedule.run_pending() # 运行所有可以运行的任务
    time.sleep(1)

