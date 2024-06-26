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

    code = file.split("_")[0][-6:] # 在 . 的位置切片，获取前面部分
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

    new_price = float(revr_list[0][2])

    # 判断最近价格在最近平均值上下
    isPositionCondOk = False    
    price_delta = new_price - average_price_list[0]
    diff = abs(price_delta)/average_price_list[0]
    if cur_position * price_delta > 0 and diff < 0.1:
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

  def FilterAveragePrice(self, data_path, average, rang, ave_trend, cur_position):
    """筛选出 data_path 中价格在上涨的股票

    Args:
        data_path (str): 数据目录
        average (int): 平均价格天数
        rang (int): 计算天数
        ave_trend (int): @-1:下降; @1:上升;
        cur_position (int): @-1:当前价格低于最近平均价格; @1:当前价格高于最近平均价格

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        if self.IsAveragePriceInTrend(root+file, average, rang, 3, ave_trend, cur_position):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    trend="上升"
    if ave_trend < 0:
      trend="下跌"
    print("共有 %d 支股票可能处于%s状态。" % (len(stocks_code), trend))
    return stocks_code


  def GetEMA(self, file, average, rang):
    """计算股价 ema 值，从第一日开始计算起步，需要完整的历史数据

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        average (int): 平均价格天数
        rang (int): 计算天数
    Returns:
        list: 移动平均股价，从最近到最远的日期排序
    """   
    csv_reader = csv.reader(open(file))
    list_csv = list(csv_reader) # 转 list
    num = len(list_csv)
    start = num - rang
    if start < 0:
      start = 0
    start += 1 # 文件行首是项目名

    ema_list = []
    den = average+1
    mol = den-2
    for i in range(rang):
      if i+start >= len(list_csv):
        break

      ema = 0.0
      if i == 0:
        ema = float(list_csv[i+start][2])
      elif i == 1:
        ema = ema_list[0]+((float(list_csv[i+start][2])-ema_list[0])*2/den)
      else:
        ema = ema_list[i-1]*mol/den + float(list_csv[i+start][2])*2/den
      ema_list.append(ema)
    revr_ema_list = ema_list[::-1]
    return revr_ema_list

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

    code = file.split("_")[0][-6:] # 在 . 的位置切片，获取前面部分

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
      list_end = False
      for j in range(average):
        if i + j >= len(revr_list)-1:
          list_end = True
          break
        ave += float(revr_list[i+j][2])
        k += 1
      if list_end:
        break
      ave = ave / k
      average_price_list.append(ave)
    return average_price_list


  def GetMACD(self, file, rang, short_ave, long_ave, dea_ave, dif_trend_num ,macd_trend_num, strict=False):
    """计算 MACD, 通过'金叉'和'死叉'判断买卖信号

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        rang (int): 计算天数
        short_ave (int): 短线平均天数
        long_ave (int): 长线平均天数
        dea_ave (int): dea 平均天数，拿多少个差离值 dif 来平均
        dif_trend_num (int): 持续 dif_trend_num 个均价才确认 dif 趋势
        macd_trend_num (int): 持续 macd_trend_num 个均价才确认 macd 趋势
        strict (bool): 是否严格执行，金叉要求 macd 为负，死叉要求 macd 为正

    Returns:
        int: 0@没有信号, 1@上涨趋势，买入信号, -1@下降趋势，卖出信号
    """    
    # 计算短线，长线均值
    # short_line = self.GetAverage(file, short_ave, rang) # 短线数据可能比长线多
    # long_line = self.GetAverage(file, long_ave, rang)
    short_line = self.GetEMA(file, short_ave, rang) # 短线数据可能比长线多
    long_line = self.GetEMA(file, long_ave, rang)

    # 差离值 dif = 短线均值 short - 长线均值 long
    dif=[]
    for i in range(len(long_line)):
      dif.append(short_line[i]-long_line[i])
      # print('dif[%d]:%f' % (i, dif[i]))
    # print("short num %d, long num %d, dif num %d" % (len(short_line), len(long_line), len(dif)))

    # 讯号线 dea = dif 均值
    dea=[]
    for i in range(len(dif)):
      ave = 0.0
      k = 0
      for j in range(dea_ave):
        if i + j >= len(dif):
          break
        ave += dif[i+j]
        k += 1
      ave = ave / k
      dea.append(ave)
      # print('dea[%d]:%f' % (i, dea[i]))
    # print("dif num %d, dea num %d" %  (len(dif), len(dea)))

    # macd = 差离值 dif - 讯号线 dea，macd 为正说明趋势上涨
    # 均值天数越多，macd 滞后性越大
    macd=[]
    for i in range(len(dif)):
      macd.append(dif[i]-dea[i])
      # print('macd[%d]:%f' % (i, macd[i]))

    # 下面是趋势判断， macd 和 dif&dea
    # macd 上升/下降判断
    continue_count = 0
    macd_orit=0 # 初始趋势
    macd_trend = 0 # 趋势方向，0 没有趋势, 1 上涨趋势, -1 下降趋势
    for i in range(len(macd)):
      if i == len(macd)-2:
        break
      step = macd[i] - macd[i+1]
      # 趋势方向
      if i == 0:
        if step < 0:
          macd_orit = -1
        elif step > 0:
          macd_orit = 1
      if step * macd_orit > 0: # 趋势相同
        continue_count += 1
        if continue_count >= macd_trend_num:
          macd_trend = macd_orit
          break
      else: # 没有趋势，结束
        break

    # 判断 dif 由下到上穿过 dea 还是 dif 由上到下穿过 dea
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
      if dif[0] > dea[0] and dif[dif_trend_num-1] < dea[dif_trend_num-1]:
        dif_rising_cross = True
    elif dif_trend == -1:
      if dif[0] < dea[0] and dif[dif_trend_num-1] > dea[dif_trend_num-1]:
        dif_falling_cross = True

    # '金叉'和'死叉'判断
    final_trend = 0
    if strict == True:
      if macd_trend > 0 and macd[0]<0 and dif_rising_cross == True:
        final_trend = 1
      elif macd_trend < 0 and macd[0]>0 and dif_falling_cross == True:
        final_trend = -1
    else:
      if macd_trend > 0 and dif_rising_cross == True:
        final_trend = 1
      elif macd_trend < 0 and dif_falling_cross == True:
        final_trend = -1
    return final_trend


  def FilterMACD(self, data_path, rang, short_ave, long_ave, dea_ave, dif_trend_num, macd_trend_num, trend=1):
    """筛选出 data_path 中 MACD 上涨趋势或下跌趋势的股票

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        rang (int): 计算天数
        short_ave (int): 短线平均天数
        long_ave (int): 长线平均天数
        dea_ave (int): dea 平均天数，拿多少个差离值 dif 来平均
        dif_trend_num (int): 持续 dif_trend_num 个均价才确认 dif 趋势
        macd_trend_num (int): 持续 macd_trend_num 个均价才确认 macd 趋势
        trend (int): @-1: 筛选下跌趋势，“死叉”股票；@1:筛选上涨趋势，“金叉”股票

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        cross = self.GetMACD(root+file, rang, short_ave, long_ave, dea_ave, dif_trend_num, macd_trend_num)
        if cross * trend > 0:
            code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
            stocks_code.append(code)
            # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    type = "上涨趋势"
    if trend < 0: type = "下跌趋势"
    print("共有 %d 支股票用 MACD 观测到%s 。" % (len(stocks_code), type))
    return stocks_code


  def GetKAnalyse(self, file, scale_local, scale_global_min, scale_global_max):
    """通过 K 线分析涨跌, 锤头和看涨吞噬认为上涨趋势，射击之星和看跌吞噬认为下跌趋势

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        scale_local (float): 实体线占当天比例
        scale_global_min (float): 实体线占整体价格比例，给锤头和射击之星参考
        scale_global_max (float): 实体线占整体价格比例，给看涨吞噬和看跌吞噬参考

    Returns:
        int: 0@没有信号, 1@上涨趋势，买入信号, -1@下降趋势，卖出信号
    """    
    csv_reader = csv.reader(open(file))
    list_csv = list(csv_reader) # 转 list
    revr_list = list_csv[::-1]
    today_price = revr_list[0]
    yesterday_price = revr_list[1]
    today_price_start = float(today_price[1]) # 开盘价
    today_price_end = float(today_price[2]) # 收盘价
    today_price_high = float(today_price[3]) # 最高价
    today_price_low = float(today_price[4]) # 最低价
    yesterday_price_start = float(yesterday_price[1])
    yesterday_price_end = float(yesterday_price[2])
    today_entity = today_price_end-today_price_start # 实体线=收盘价-开盘价
    yesterday_entity = yesterday_price_end-yesterday_price_start
    today_entirety = today_price_high-today_price_low # 整体线=最高价-最低价
    today_over_shadow = 0.0 # 上影线=最高价-开盘或者收盘价
    today_under_shadow = 0.0 # 下影线=开盘或者收盘价-最低价    
    if today_entity > 0: # 阳线
      today_over_shadow = today_price_high - today_price_end
      today_under_shadow = today_price_start - today_price_low
    elif today_entity < 0: # 阴线
      today_over_shadow = today_price_high - today_price_start
      today_under_shadow = today_price_end - today_price_low

    final_trend = 0
    # 判断实体线是否合格
    global_scl = abs(today_entity)/today_price_end
    if global_scl>abs(scale_global_min):
      # print("[ka] global scale ok, limit %f, cur %f" % (scale_global, global_scl))
      local_scl = abs(today_entity)/abs(today_entirety)
      if local_scl>abs(scale_local): # 判断锤头和射击之星
        # print("[ka] local scale ok, limit %f, cur %f" % (scale_local, local_scl))
        over_shadow_scale = abs(today_over_shadow)/abs(today_entirety)
        under_shadow_scale = abs(today_under_shadow)/abs(today_entirety)
        # print("[ka] oss %f, uss %f" % (over_shadow_scale, under_shadow_scale))
        if today_entity > 0 and over_shadow_scale < 0.1 and abs(today_under_shadow) > 2*abs(today_entity):
          final_trend=1
        elif today_entity < 0 and under_shadow_scale < 0.1 and abs(today_over_shadow) > 2*abs(today_entity):
          final_trend=-1
      if global_scl>abs(scale_global_max):
        if yesterday_entity < 0 and today_entity > 0: # 判断看涨吞噬
          if today_price_end > yesterday_price_start and today_price_start < yesterday_price_end:
            final_trend=1
        if yesterday_entity > 0 and today_entity < 0: # 判断看跌吞噬
          if today_price_end < yesterday_price_start and today_price_start > yesterday_price_end:
            final_trend=-1
    return final_trend


  def FilterKAnalyse(self, data_path, scale_local, scale_global_min, scale_global_max, trend=1):
    """筛选出 data_path 中 MACD 上涨趋势或下跌趋势的股票

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        scale_local (float): 实体线占当天比例
        scale_global_min (float): 实体线占整体价格比例，给锤头和射击之星参考
        scale_global_max (float): 实体线占整体价格比例，给看涨吞噬和看跌吞噬参考
        trend (int): @-1: 筛选下跌趋势；@1:筛选上涨趋势

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        ka = self.GetKAnalyse(root+file, scale_local, scale_global_min, scale_global_max)
        if ka * trend > 0:
            code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
            stocks_code.append(code)
            # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    type = "上涨趋势"
    if trend < 0: type = "下跌趋势"
    print("共有 %d 支股票用 K 线分析，观测到%s 。" % (len(stocks_code), type))
    return stocks_code


  def GetTurnoverRate(self, file, turnover, rang, greater=True):
    """通过近期的换手率判断趋势是否确定

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        turnover (float): 换手率指标
        rang (int): 查看天数
        greater (bool): @True: 大于 turnover 的筛选; @False: 小于 turnover 的筛选

    Returns:
        bool: 平均换手率达标
    """    
    csv_reader = csv.reader(open(file))
    list_csv = list(csv_reader) # 转 list
    revr_list = list_csv[::-1]
    ave = 0.0
    k = 0

    for i in range(len(revr_list)):
      # 行首项目名
      if i == len(revr_list)-1:
        break

      # csv 中字符 '-' 表示空栅格
      if revr_list[i] == '-':
        continue

      if (k >= rang):
        break

      ave += float(revr_list[i][10])
      k += 1

    ave = ave / k
    if greater:
      if (ave > turnover):
        return True
    else:
      if (ave < turnover):
        return True
    return False


  def FilterTurnoverRate(self, data_path, turnover, rang, greater=True):
    """筛选出 data_path 中近期的换手率趋势确定的取票

    Args:
        file (str): 股票文件，数据公式由 Stock 的 GetRecentStocks 提供
        turnover (float): 换手率指标
        rang (int): 查看天数

    Returns:
        list: 股票代码列表
    """    
    stocks_code = []

    for root, dirs, files in os.walk(data_path):
      for file in files:
        if self.GetTurnoverRate(root+file, turnover, rang, greater):
          code = file.split(".")[0] # 在 . 的位置切片，获取前面部分
          stocks_code.append(code)
          # print("%s is below recent price." % (code))
      break # 跳过 os.walk 对子目录 dirs 的遍历
    return stocks_code
