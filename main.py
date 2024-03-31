#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
import csv
from share.stock import *
from share.prophet import *
import pathlib

if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')
  stock = Stock()

  current_path = os.getcwd()
  print('当前路径：%s' % (current_path))
  csv_path = current_path + '/data/csv/'
  print('数据路径：%s' % (csv_path))

  #0 拉取原始数据
  stock.GetData(csv_path);

  #1 在近期资金流动热门股票中筛选价格适宜的股票
  rang = 3
  stocks_csv = csv_path + 'fund_flow_' + str(rang) + '.csv'
  price_stock_csv = csv_path + 'price_stock.csv'
  price = 20
  main_fund = 10.0
  force_rise = True 
  # stock.GetPriceStocksMoreDay(csv_path, price, main_fund, force_rise)

  #2 拉取股票近期数据
  days = 15
  csv_file = csv_path + 'price_stock_' + str(rang) + '.csv'
  save_path = csv_path + 'filtered_stocks/'
  # stock.GetRecentStocks(csv_file, save_path, days)

  #3 挑选股票
  prophet = Prophet()
  prophet.FilterBelowRecentAveragePriceStocks(save_path, 3, 5)



