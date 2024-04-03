#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
import csv
from share.stock import *
from share.prophet import *
from share.mail import *
import pathlib
import shutil


if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')
  stock = Stock()

  current_path = os.getcwd()
  print('当前路径：%s' % (current_path))
  csv_path = current_path + '/data/csv/'
  print('数据路径：%s' % (csv_path))
  filtered_path = csv_path + 'filtered_stocks/'
  print('过滤后的数据路径：%s' % (filtered_path))

  mail_host = 'smtp.163.com'
  mail_user = '17688010148'
  mail_sender = 'lmr2887@163.com'
  mail_pass = 'CHLURCFITAQCLOKO'
  mail = Mail(mail_host, mail_user, mail_sender, mail_pass)
  mail.SetReceiver(mail_sender)
  mail.Send('hollo, smtp.', 'empty')
  exit(0)

  if os.path.exists(csv_path):
    print('清空目录')
    shutil.rmtree(csv_path)
  if not os.path.exists(csv_path):
    print('创建目录')
    os.mkdir(csv_path)
    os.mkdir(filtered_path)


  #0 拉取原始数据
  stock.GetData(csv_path);

  #1 在近期资金流动热门股票中筛选价格适宜的股票
  price = 20
  main_fund = 10.0
  force_rise = True 
  stock.GetPriceStocksMoreDay(csv_path, price, main_fund, force_rise)

  #2 拉取股票近期数据
  rang = 3 # 查看 3 天内的资金流向  
  days = 30
  fund_file = csv_path + 'price_stock_' + str(rang) + '.csv'
  today_fund_file = csv_path + 'price_stock_1.csv'
  save_path = csv_path + 'filtered_stocks/'
  stock.GetRecentStocks(fund_file, today_fund_file, save_path, days)

  #3 挑选股票
  prophet = Prophet()
  prophet.FilterBelowRecentAveragePriceStocks(save_path, 3, 5)



