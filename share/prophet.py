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

  def IsAveragePriceInTrend(self, file, average, rang, trend_num, ave_trend, cur_position):
    """判断股票是否低于最近的平均值，文件数据是按日期从远到近排列，需要反向遍历！

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average (int): 平均价格天数
        rang (int): 计算天数
        trend_num (int): 持续 trend_num 个均价才确认趋势
        ave_trend (int): @-1:下降; @1:上升;
        cur_position (int): @-1:当前价格低于最近平均价格; @1:当前价格高于最近平均价格
    Returns:
        bool: 股票是否符合趋势
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
    isAvePriceTrendCondOk = False
    for i in range(len(average_price_list)):
      if i == len(average_price_list)-2:
        break
      step = average_price_list[i] - average_price_list[i+1]
      if step * ave_trend > 0:
        continue_count += 1
        if continue_count >= trend_num:
          isAvePriceTrendCondOk = True           
      else:
        break

    ok = False
    if isPositionCondOk and isAvePriceTrendCondOk:
      ok = True
    return ok

  def FilterRising(self, data_path, average, rang):
    """筛选出 data_path 中价格在上涨的股票

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
        if self.IsAveragePriceInTrend(root+file, average, rang, 3, 1, 1):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("共有 %d 支股票可能处于上升状态。" % (len(stocks_code)))
    return stocks_code


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
        if self.IsAveragePriceInTrend(root+file, average, rang, 1, -1):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("共有 %d 支股票可能处于低估值状态。" % (len(stocks_code)))
    return stocks_code


  def FilterBottomOut(self, data_path, short_days, middle_days, rang):
    """筛选出 data_path 中触底反弹的股票

    Args:
        data_path (str): 数据目录
        short_days (int): 短线平均价格天数
        middle_days (int): 中线平均价格天数
        rang (int): 计算天数

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        if self.IsAveragePriceInTrend(root+file, middle_days, rang, 3, -1, 1): # 中线下跌
          if self.IsAveragePriceInTrend(root+file, short_days, rang, 1, 1, 1): # 短线抬头
            code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
            stocks_code.append(code)
            # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("共有 %d 支股票可能触底反弹。" % (len(stocks_code)))
    return stocks_code


  def IsAveragePriceHasPotential(self, file, average, rang, ave_trend, error):
    """判断股票是否低于最近的平均值，文件数据是按日期从远到近排列，需要反向遍历！

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average (int): 平均价格天数
        rang (int): 计算天数
        ave_trend (int): @-1:下降; @1:上升;
        error (float): 最新价格在最新均价附近波动范围
    Returns:
        bool: 股票是否具有潜力
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
    isInRang = False
    diff = abs(float(revr_list[0][2]) - average_price_list[0])
    price_delta = diff / average_price_list[0]
    if price_delta < error:
      # print("file:%s, price delta %f, error %f" % (file, price_delta, error))
      isInRang = True

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
    if isInRang and isAvePriceTrendCondOk:
      ok = True
    return ok


  def FilterPotential(self, data_path, average, rang, error):
    """筛选出 data_path 中具有潜力的股票

    Args:
        data_path (str): 数据目录
        average (int): 平均价格天数
        rang (int): 计算天数
        error (float): 股价波动范围

    Returns:
        list: 股票代码列表
    """     
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        if self.IsAveragePriceHasPotential(root+file, average, rang, 1, error):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    print("共有 %d 支股票具有潜力。" % (len(stocks_code)))
    return stocks_code


  def GetAverage(self, file, average, rang):
    """计算股价均值，文件数据是按日期从远到近排列，需要反向遍历！

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average (int): 平均价格天数
        rang (int): 计算天数
    Returns:
        list: 移动平均股价，从最近到最远的日期排序
    """    
    csv_reader = csv.reader(open(file))
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
    return average_price_list


  def GetMACD(self, file, rang, short_ave, long_ave, dem_ave, dif_trend_num ,osc_trend_num, strict=False):
    """计算 MACD, 通过'金叉'和'死叉'判断买卖信号

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        rang (int): 计算天数
        short_ave (int): 短线平均天数
        long_ave (int): 长线平均天数
        dem_ave (int): dem 平均天数，拿多少个差离值 dif 来平均
        dif_trend_num (int): 持续 dif_trend_num 个均价才确认 dif 趋势
        osc_trend_num (int): 持续 osc_trend_num 个均价才确认 osc 趋势
        strict (bool): 是否严格执行，金叉要求 osc 为负，死叉要求 osc 为正

    Returns:
        int: 0@没有信号, 1@上涨趋势，买入信号, -1@下降趋势，卖出信号
    """    
    # 计算短线，长线均值
    short_line = self.GetAverage(file, short_ave, rang) # 短线数据可能比长线多
    long_line = self.GetAverage(file, long_ave, rang)

    # 差离值 dif = 短线均值 short - 长线均值 long
    dif=[]
    for i in range(len(long_line)):
      dif.append(short_line[i]-long_line[i])
    # print("short num %d, long num %d, dif num %d" % (len(short_line), len(long_line), len(dif)))

    # 讯号线 dem/macd = dif 均值
    dem=[]
    for i in range(len(dif)):
      ave = 0.0
      k = 0
      for j in range(dem_ave):
        if i + j >= len(dif):
          break
        ave += dif[i+j]
        k += 1
      ave = ave / k
      dem.append(ave)
    # print("dif num %d, dem num %d" %  (len(dif), len(dem)))

    # osc = 差离值 dif - 讯号线 dem，osc 为正说明趋势上涨
    # 均值天数越多，osc 滞后性越大
    osc=[]
    for i in range(len(dif)):
      osc.append(dif[i]-dem[i])

    # 下面是趋势判断， osc 和 dif&dem
    # osc 上升/下降判断
    continue_count = 0
    osc_orit=0 # 初始趋势
    osc_trend = 0 # 趋势方向，0 没有趋势, 1 上涨趋势, -1 下降趋势
    for i in range(len(osc)):
      if i == len(osc)-2:
        break
      step = osc[i] - osc[i+1]
      # 趋势方向
      if i == 0:
        if step < 0:
          osc_orit = -1
        elif step > 0:
          osc_orit = 1
      if step * osc_orit > 0: # 趋势相同
        continue_count += 1
        if continue_count >= osc_trend_num:
          osc_trend = osc_orit
          break
      else: # 没有趋势，结束
        break

    # 判断 dif 由下到上穿过 dem 还是 dif 由上到下穿过 dem
    current_rising = 0
    dif_rising_count = 0
    continue_count = 0
    dif_orit=0
    dif_trend = 0
    for i in range(len(dif)):
      if i == len(dif)-2:
        break
      step = dif[i] - dif[i+1]
      if i == 0:
        if step < 0:
          dif_orit = -1
        elif step > 0:
          dif_orit = 1
      if step * dif_orit > 0: # 趋势相同
        continue_count += 1
        if continue_count >= dif_trend_num:
          dif_trend = dif_orit
          break
      else: # 没有趋势，结束
        break

    dif_rising_cross = False
    dif_falling_cross = False
    if dif_trend == 1:
      if dif[0] > dem[0] and dif[dif_trend_num] < dem[dif_trend_num]:
        dif_rising_cross = True
    elif dif_trend == -1:
      if dif[0] < dem[0] and dif[dif_trend_num] > dem[dif_trend_num]:
        dif_falling_cross = True

    # '金叉'和'死叉'判断
    final_trend = 0
    if strict == True:
      if osc_trend > 0 and osc[0]<0 and dif_rising_cross == True:
        final_trend = 1
      elif osc_trend < 0 and osc[0]>0 and dif_falling_cross == True:
        final_trend = -1
    else:
      if osc_trend > 0 and dif_rising_cross == True:
        final_trend = 1
      elif osc_trend < 0 and dif_falling_cross == True:
        final_trend = -1
    return final_trend


  def FilterMACD(self, data_path, rang, short_ave, long_ave, dem_ave, dif_trend_num, osc_trend_num, trend=1):
    """筛选出 data_path 中 MACD 上涨趋势或下跌趋势的股票

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        rang (int): 计算天数
        short_ave (int): 短线平均天数
        long_ave (int): 长线平均天数
        dem_ave (int): dem 平均天数，拿多少个差离值 dif 来平均
        dif_trend_num (int): 持续 dif_trend_num 个均价才确认 dif 趋势
        osc_trend_num (int): 持续 osc_trend_num 个均价才确认 osc 趋势
        trend (int): @-1: 筛选下跌趋势，“死叉”股票；@1:筛选上涨趋势，“金叉”股票

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        cross = self.GetMACD(root+file, rang, short_ave, long_ave, dem_ave, dif_trend_num, osc_trend_num)
        if cross * trend > 0:
            code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
            stocks_code.append(code)
            # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    type = "上涨趋势"
    if trend < 0: type = "下跌趋势"
    print("共有 %d 支股票用 MACD 观测到%s 。" % (len(stocks_code), type))
    return stocks_code

