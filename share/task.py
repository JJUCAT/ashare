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
from share.info import *
import shutil
from functools import reduce

import json


def TaskLoadConfigurations(config_path):
  """加载参数

  Returns:
      dict: 参数字典
  """  

  # 加载配置参数
  print('config path: %s' % config_path)
  f = open(config_path)
  json_context = f.read()
  config_dict = json.loads(json_context)
  print(config_dict)
  return config_dict



def TaskClearData(config_dict):
  # 检查路径
  data_path = config_dict['base_path']+config_dict['data_path']
  rawdata_path = data_path+config_dict['rawdata_path']
  historydata_path = rawdata_path+config_dict['historydata_path']
  print('data path: %s' % data_path)
  print('data rawdata_path: %s' % rawdata_path)
  print('data historydata_path: %s' % historydata_path)

  if not os.path.exists(data_path):
    print('创建数据目录')
    os.mkdir(data_path)
  if os.path.exists(rawdata_path):
    print('清空目录')
    shutil.rmtree(rawdata_path)
  os.mkdir(rawdata_path)
  os.mkdir(historydata_path)



def TaskPullData(config_dict):
  """拉取数据

  Args:
      config_dict (dict): 配置参数
  """  
  stockslist_file = config_dict['base_path']+config_dict['data_path']+config_dict['rawdata_path']+config_dict['stockslist']
  print('stocks list path: %s' % stockslist_file)

  stock = Stock()
  print('pull stocks list.')
  stock.GetRealTime(stockslist_file)

  days = config_dict['history_data_days']
  market_value = config_dict['history_data_market']
  price_low = config_dict['history_data_price_low']
  price_high = config_dict['history_data_price_high']
  historydata_path = config_dict['base_path']+config_dict['data_path']+config_dict['rawdata_path']+config_dict['historydata_path']
  stock.GetRecentStocks(stockslist_file, historydata_path, days, market_value, price_low, price_high)



def TaskAnalyse(config_dict):

  prophet = Prophet()
  historydata_path = config_dict['base_path']+config_dict['data_path']+config_dict['rawdata_path']+config_dict['historydata_path']

  # macd 金叉买入判断
  macd_config = config_dict['analysis']['macd']
  short_days = macd_config['short_days']
  long_days = macd_config['long_days']
  dem_days = macd_config['dem_days']
  dif_trend_num = macd_config['dif_trend_num']
  osc_trend_num = macd_config['osc_trend_num'] 
  macdrising_stocks = prophet.FilterMACD(historydata_path, 60, short_days, long_days, dem_days, dif_trend_num, osc_trend_num, 1)
  print('筛选金叉股票共 %d 支。' % (len(macdrising_stocks)))











def TaskBuyMonitor(realtime=False):
  """定时任务，买入信号
     爬取股市数据，整理后发送邮件
  """  

  base_path = '/home/lmr/ws/ashare/'
  data_path = base_path + 'data/'
  csv_path = data_path + 'csv/'
  reasonable_price_stocks_dir = 'reasonable_price_stocks/'
  price_filtered_path = csv_path + reasonable_price_stocks_dir
  realtime_file = csv_path + 'realtime.csv'
  print('数据保存路径:%s\ncsv 路径:%s' % (base_path, csv_path))

  if not os.path.exists(data_path):
    print('创建数据目录')
    os.mkdir(data_path)
  if os.path.exists(csv_path):
    print('清空目录')
    shutil.rmtree(csv_path)
  os.mkdir(csv_path)
  os.mkdir(price_filtered_path)

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
  market_value = 80.0 # 总市值 100E
  fund_file = csv_path + 'price_stock_' + str(rang) + '.csv'
  save_path = csv_path + reasonable_price_stocks_dir
  stock.GetRecentStocks(fund_file, save_path, days, market_value)

  #3 挑选股票
  short_days = 20 # 均价天数
  middle_days = 30
  total_day = 40

  prophet = Prophet(realtime_file)
  prophet.UseRealtime(realtime)
  rising_stocks = prophet.FilterAveragePrice(save_path, short_days, total_day, 1, 1)
  falling_stocks = prophet.FilterAveragePrice(save_path, short_days, total_day, -1, 1)

  # MACD 金叉 判断
  short_ave = 12
  long_ave = 26
  dem_ave = 9
  dif_trend_num = 4
  osc_trend_num = 3  
  macdrising_stocks = prophet.FilterMACD(save_path, 40, short_ave, long_ave, dem_ave, dif_trend_num, osc_trend_num, 1)

  # K 线分析
  local_scale = 0.25 # 当天实体线对当天 K 线占比
  global_scale_min = 0.02 # 当天实体线对收盘价占比，锤头和射击之星的参考
  global_scale_max = 0.05 # 当天实体线对收盘价占比，看涨吞噬和看跌吞噬的参考
  kanalyse_stocks = prophet.FilterKAnalyse(save_path, local_scale, global_scale_min, global_scale_max, 1)

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
  
  # 均线检测到下跌突破，k 线检测到上涨
  fk = list(set(falling_stocks) & set(kanalyse_stocks))

  #4 发送邮件
  now = time.time()
  current = time.strftime("%Y-%m-%d %H:%M:%S 买入信号", time.localtime(now))
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
  if len(fk) > 0:
    msg += "!!! 均线检测到下跌突破和 k 分析交集预测上涨的股票!!!: " + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', fk)
  msg += '\n'
  lmrmail = LMRMail()
  lmrmail.Send(msg, 'empty')



def TaskSellMonitor(realtime=False):
  """定时任务，卖出信号检测
     爬取股市数据，整理后发送邮件
  """  

  base_path = '/home/lmr/ws/ashare/'
  data_path = base_path + 'data/'
  csv_path = data_path + 'csv/'
  print('数据保存路径:%s' % (base_path))
  mystocks_path = data_path + 'mystocks/'
  mystocks_file = mystocks_path + '/mystocks.csv'
  save_path = mystocks_path + 'data/'
  realtime_file = csv_path + 'realtime.csv'

  if not os.path.exists(data_path):
    print('创建数据目录')
    os.mkdir(data_path)
  if not os.path.exists(mystocks_path):
    print('创建用户数据目录')
    os.mkdir(mystocks_path)

  stock = Stock()
  prophet = Prophet(realtime_file)
  prophet.UseRealtime(realtime)
  #0 拉取用户股票数据
  days = 60
  stock.GetMyStocks(mystocks_file, save_path, days)

  # 均线分析
  short_days = 20 # 均价天数
  middle_days = 30
  total_day = 40
  falling_stocks = prophet.FilterAveragePrice(save_path, short_days, total_day, -1, -1)
  rising_stocks = prophet.FilterAveragePrice(save_path, short_days, total_day, 1, 1)

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

  # 均线上涨但是换手率增加
  rt = list(set(turnover_continue_stocks) & set(falling_stocks))

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
  current = time.strftime("%Y-%m-%d %H:%M:%S 卖出信号", time.localtime(now))
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
  if len(rt) > 0:
    msg += "！！！均线上涨但是换手率提高的股票，可能触顶了！！！:" + '\n'
    msg += reduce(lambda x, y: x+'\n'+y+'\n', rt)
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

def TimerOffline():
  TaskBuyMonitor(False)
  TaskSellMonitor(False)

def TimerOnline():
  TaskBuyMonitor(True)
  TaskSellMonitor(True)


def TimerTask():
  """设置定时任务
  """  

  # 设置定时任务
  schedule.every().day.at("09:25").do(TimerOnline)
  schedule.every().day.at("09:45").do(TimerOnline)
  schedule.every().day.at("11:15").do(TimerOnline)
  schedule.every().day.at("13:15").do(TimerOnline)
  schedule.every().day.at("14:45").do(TimerOnline)
  schedule.every().day.at("22:00").do(TimerOffline)

  while True:
    schedule.run_pending() # 运行所有可以运行的任务
    time.sleep(1)

