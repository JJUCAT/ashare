#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import akshare as ak
import pathlib
import csv
import os
import re
import datetime



class Prophet(object):

  def __init__(self):
    print('Prophet init.')

  def IsBelowRecentAveragePrice(self, file, average_min, average_max):
    """判断股票是否低于最近的平均值，文件数据是按日期从远到近排列，需要反向遍历！

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average_min (int): 平均价格最小天数
        average_max (int): 平均价格最大天数

    Returns:
        bool: 股票最新价格是否低于最近平均值
    """    
    rise = False
    csv_reader = csv.reader(open(file))
    # row_count = sum(1 for row in csv_reader) # 获取 csv 文件总行数，这里会让 csv_reader 指针遍历到末尾
    num = 0
    new_price = 0.0
    min_sum = 0.0
    max_sum = 0.0
    dayend_price_index = 2
    list_csv = list(csv_reader) # 转 list
    for row in reversed(list_csv): # list 逆序
      # csv 中字符 '-' 表示空栅格
      if row[dayend_price_index] == '-':
        continue

      if num >= average_max:
        break

      num += 1
      if num == 1: # 最新收盘价
        new_price = float(row[dayend_price_index])

      if num <= average_min:
        min_sum += float(row[dayend_price_index])
      if num <= average_max:
        max_sum += float(row[dayend_price_index])

    average_min_price = min_sum / average_min
    average_max_price = max_sum / average_max
    if new_price <= average_min_price and new_price <= average_max_price:
      print("new price: %f, average[%d] price: %f, average[%d] price: %f" %
            (new_price, average_min, average_min_price, average_max, average_max_price))      
      print("Is Below Recent Price.")
      rise = True

    return rise


  def FilterBelowRecentAveragePriceStocks(self, data_path, average_min, average_max):
    """筛选出 data_path 中价格低于最近平均值的股票

    Args:
        data_path (str): 数据目录
        average_min (int): 平均价格最小天数
        average_max (int): 平均价格最大天数

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        if self.IsBelowRecentAveragePrice(root+file, average_min, average_max):
          code = file[0:6]
          stocks_code.append(code)
          print("code %s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("total %d stocks are below recent price." % (len(stocks_code)))
    return stocks_code
