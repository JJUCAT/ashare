#!/usr/bin/python3.9
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

  def IsBelowRecentAveragePrice(self, file, average, rang):
    """判断股票是否低于最近的平均值，文件数据是按日期从远到近排列，需要反向遍历！

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average (int): 平均价格天数
        rang (int): 计算天数

    Returns:
        bool: 股票最新价格是否低于最近平均值
    """    
    csv_reader = csv.reader(open(file))
    # row_count = sum(1 for row in csv_reader) # 获取 csv 文件总行数，这里会让 csv_reader 指针遍历到末尾
    list_csv = list(csv_reader) # 转 list
    revr_list = list_csv[::-1]
    average_price_list = []
    for i in range(len(revr_list)):
      # 行首项目名
      if i == len(revr_list)-1:
        break

      # csv 中字符 '-' 表示空栅格
      if revr_list[i] == '-':
        continue

      # 检查天数
      if i >= rang:
        break

      ave = 0.0
      k = 0
      for j in range(average):
        if i + j >= len(revr_list)-1:
          break
        ave += float(revr_list[i+j][2])
        k += 1
      ave = ave / k
      average_price_list.append(ave)

    # 最新价格 < 最近的平均价格
    isBelowAvePrice = False
    if average_price_list[0] > float(revr_list[0][2]):
      isBelowAvePrice = True

    # 判断平均价格趋势
    continue_count = 0
    rise_count = 2
    isRecentlyAvePriceRise = False
    for i in range(len(average_price_list)):
      if i == len(average_price_list)-2:
        break
      if average_price_list[i] >= average_price_list[i+1]:
        continue_count += 1
        if continue_count >= rise_count:
          isRecentlyAvePriceRise = True           
      else:
        break

    rise = False
    if isRecentlyAvePriceRise and isBelowAvePrice:
      rise = True
    return rise


  def FilterBelowRecentAveragePriceStocks(self, data_path, average, rang):
    """筛选出 data_path 中价格低于最近平均值的股票

    Args:
        data_path (str): 数据目录
        average (int): 平均价格天数
        rang (int): 计算天数

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        if self.IsBelowRecentAveragePrice(root+file, average, rang):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          print("%s is below recent price." % (file))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("total %d stocks are below recent price." % (len(stocks_code)))
    return stocks_code
