#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
import csv
from share.stock import *
import pathlib

if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')
  stock = Stock()

  current_path = os.getcwd()
  print('当前路径：%s' % (current_path))
  csv_path = current_path + '/data/csv/'
  print('数据路径：%s' % (csv_path))

  # 拉取原始数据
  stock.GetData(csv_path);

  # 
  stocks_csv = csv_path + 'fund_flow_5.csv';
  price_stock_csv = csv_path + 'price_stock.csv';
  price = 10
  # stock.GetPriceStocks(stocks_csv, price_stock_csv, price)
  stock.GetPriceStocksMoreDay(csv_path, price)




