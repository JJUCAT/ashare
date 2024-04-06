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

  def IsAveragePriceAnalysis(self, file, average, rang, ave_trend, cur_position):
    """判断股票是否低于最近的平均值，文件数据是按日期从远到近排列，需要反向遍历！

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average (int): 平均价格天数
        rang (int): 计算天数
        ave_trend (int): @-1:下降; @1:上升;
        cur_position (int): @-1:当前价格低于最近平均价格; @1:当前价格高于最近平均价格
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

    # 判断最近价格在最近平均值上下
    isPositionCondOk = False    
    price_delta = float(revr_list[0][2]) - average_price_list[0]
    if cur_position * price_delta > 0:
      isPositionCondOk = True

    # 判断平均价格趋势
    continue_count = 0
    rise_count = 3
    isAvePriceTrendCondOk = False
    for i in range(len(average_price_list)):
      if i == len(average_price_list)-2:
        break
      step = average_price_list[i] - average_price_list[i+1]
      if step * ave_trend > 0:
        continue_count += 1
        if continue_count >= rise_count:
          isAvePriceTrendCondOk = True           
      else:
        break

    ok = False
    if isPositionCondOk and isAvePriceTrendCondOk:
      ok = True
    return ok


  def FilterUnderestimate(self, data_path, average, rang):
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
        if self.IsAveragePriceAnalysis(root+file, average, rang, 1, -1):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("共有 %d 支股票可能处于低估值状态。" % (len(stocks_code)))
    return stocks_code


  def FilterBottomOut(self, data_path, average, rang):
    """筛选出 data_path 中触底反弹的股票

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
        if self.IsAveragePriceAnalysis(root+file, average, rang, -1, 1):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("共有 %d 支股票可能触底反弹。" % (len(stocks_code)))
    return stocks_code
