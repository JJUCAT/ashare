#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import akshare as ak
import pathlib
import csv
import os
import re
import datetime



class Stock(object):

  def __init__(self):
    print('Stock init.')

  def GetStock(self, path):
    """获取 A 股所有股票

    Args:
        path (str): 文件保存路径
    """    
    astocks = ak.stock_info_a_code_name()
    astocks.to_csv(path, index=None, encoding='utf-8-sig')


  def GetHotRank(self, path):
    """东方财富人气榜
    股票受关注程度、资金流入情况进行综合评估，点击率
    Args:
        path (str): 文件保存路径
    """    
    hotrank = ak.stock_hot_rank_em()
    hotrank.to_csv(path, index=None, encoding='utf-8-sig')

  def GetMarket(self, code):
    """根据股票代码获取交易所

    Args:
        code (str): 股票代码

    Returns:
        str: 交易所代号 @'sh'：上海交易所，@'sz'：深圳交易所，@'bj'：北京交易所
    """    
    market = 'bj'
    header = code[0:3]
    if header == '600' or header == '601' or header == '603' or header == '688':
      market = 'sh'
    elif header == '000' or header == '001' or header == '003' or header == '300':
      market = 'sz'
    return market

  def GetHotUp(self, path):
    """东方财富飙升榜，没用
    人气上升程度排名
    Args:
        path (str): 文件保存路径
    """    
    hotup = ak.stock_hot_up_em()
    hotup.to_csv(path, index=None, encoding='utf-8-sig')


  def GetHotKey(self, path):
    """东方财富热门关键词，没用
    点击，热门关键词
    Args:
        path (str): 文件保存路径
    """    
    hotkey = ak.stock_hot_keyword_em()
    hotkey.to_csv(path, index=None, encoding='utf-8-sig')


  def GetHotFollow(self, path):
    """雪球热门关注，无用
    股票被添加关注数量，长期无变化
    Args:
        path (str): 文件保存路径
    """    
    hotfollow = ak.stock_hot_follow_xq()
    hotfollow.to_csv(path, index=None, encoding='utf-8-sig')


  def GetStrongStock(self, path, date):
    """东方财富强势股池

    Args:
        path (str): 文件保存路径
        date (str): 查阅的日期
    """    
    strongstock = ak.stock_zt_pool_strong_em(date=date)
    strongstock.to_csv(path, index=None, encoding='utf-8-sig')


  def GetFundFlow(self, path, day):
    """个股资金流向

    Args:
        path (str): 文件保存路径
        day (int): 查阅天数
    """    
    daynum = '今日'
    if day > 1:
      daynum = str(day)+"日"

    fundflow = ak.stock_individual_fund_flow_rank(indicator=daynum)
    fundflow.to_csv(path, index=None, encoding='utf-8-sig')


  def GetMarketFundFlow(self, path):
    """大盘资金流向

    Args:
        path (str): 文件保存路径
    """    
    marketfundflow = ak.stock_market_fund_flow()
    marketfundflow.to_csv(path, index=None, encoding='utf-8-sig')


  def GetSectorFundFlow(self, path, day):
    """板块资金流向

    Args:
        path (str): 文件保存路径
        day (int): 查阅天数
    """    
    daynum = '今日'
    if day > 1:
      daynum = str(day)+"日"

    sectorfundflow = ak.stock_sector_fund_flow_rank(indicator=daynum, sector_type="行业资金流")
    sectorfundflow.to_csv(path, index=None, encoding='utf-8-sig')


  def GetMainFundFlow(self, path):
    """主力净流向排行，按占比排行，靠前的基本是小市值股票，反应出一天交易中主力意向
    主力净流占比 = 主力净流入资金（超大单+大单）/ 总净流入资金
    Args:
        path (str): 文件保存路径
    """    
    mainfundflow = ak.stock_main_fund_flow(symbol="全部股票")
    mainfundflow.to_csv(path, index=None, encoding='utf-8-sig')


  def GetIndustryFundFlowRanking(self, path, day):
    """行业资金流向排行，接口有问题 !

    Args:
        path (str): 文件保存路径
        day (int): 查阅天数 @[“即时”, "3日排行", "5日排行", "10日排行", "20日排行"]
    """    
    daynum = '即时'
    if day > 1:
      daynum = str(day)+"日排行"
    industryfundflowranking = ak.stock_fund_flow_industry(symbol=daynum)
    industryfundflowranking.to_csv(path, index=None, encoding='utf-8-sig')


  def GetIndustryFundFlow(self, path, industry, day):
    """行业资金流向排行
    列出行业个股的资金流入排行
    Args:
        path (str): 文件保存路径
        industry (str): 行业
        day (int): 查阅天数 @['今日', '5日', '10日']
    """    
    daynum = '今日'
    if day > 1:
      daynum = str(day)+"日"
    industryfundflow = ak.stock_sector_fund_flow_summary(symbol=industry, indicator=daynum)
    industryfundflow.to_csv(path, index=None, encoding='utf-8-sig')

  def GetIndustryFundHistory(self, path, industry):
    """行业资金流向历史

    Args:
        path (str): 文件保存路径
        industry (str): 行业
    """    
    industryfundhistory = ak.stock_sector_fund_flow_hist(symbol=industry)
    industryfundhistory.to_csv(path, index=None, encoding='utf-8-sig')


  def GetConceptFundHistory(self, path, concept):
    """概念资金流向历史

    Args:
        path (str): 文件保存路径
        concept (str): 概念
    """    
    conceptfundhistory = ak.stock_concept_fund_flow_hist(symbol=concept)
    conceptfundhistory.to_csv(path, index=None, encoding='utf-8-sig')


  def GetStockHistory(self, save_path, code, days):
    """获取股票历史数据，数据从日期远到日期近排序

    Args:
        save_path (str): 保存路径
        code (str): 股票代码
        days (int): 查询天数
    """    
    end = datetime.datetime.now()
    start = end + datetime.timedelta(days=-days)
    end_date = end.strftime("%Y%m%d") 
    start_date = start.strftime("%Y%m%d") 
    # print("start date: %s, end date %s" % (start_date, end_date))
    stock_history = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
    stock_history.to_csv(save_path, index=None, encoding='utf-8-sig')


  def GetBigFund(self, path):
    """大单资金流向，即时

    Args:
        path (str): 文件保存路径
    """    
    bigdealfund = ak.stock_fund_flow_big_deal()
    bigdealfund.to_csv(path, index=None, encoding='utf-8-sig')


  def GetIndividualFund(self, path, code):
    """个股资金流向

    Args:
        path (str): 保存路径
        code (str): 股票代码
    """    
    market = self.GetMarket(market)
    individualfund = ak.stock_individual_fund_flow(stock=code, market=market)
    individualfund.to_csv(path, index=None, encoding='utf-8-sig')


  def GetIndividualIndustry(self, code):
    """个股信息，个股所在行业

    Args:
        path (str): 保存路径
        code (str): 股票代码
    """    
    individualinfo = ak.stock_individual_info_em(symbol=code)
    industry = individualinfo[2][1]
    print("code %s is in industry %s" % (code, industry))
    return 


  def GetData(self, data_path):
    """获取股票数据

    Args:
        data_path (str): 数据保存路径
    """   
    # A 股所有股票
    # stocks_path = data_path + 'stocks.csv'
    # file = pathlib.Path(stocks_path)
    # if not file.is_file():
    #   self.GetStock(stocks_path)

    # 东方财富热门股票排行
    # hot_rank_path = data_path + 'hot_rank.csv'
    # file = pathlib.Path(hot_rank_path)
    # if not file.is_file():
    #   self.GetHotRank(hot_rank_path)

    # 1，3，5，10 天资金流向排行
    daynum_list = [1, 3, 5, 10]
    for daynum in daynum_list:
      fund_flow_path = data_path + 'fund_flow_' + str(daynum) + '.csv'
      file = pathlib.Path(fund_flow_path)
      if not file.is_file():
        self.GetFundFlow(fund_flow_path, daynum)

    # 大盘资金流向历史数据
    market_fund_flow_path = data_path + 'market_fund_flow.csv'
    file = pathlib.Path(market_fund_flow_path)
    if not file.is_file():  
      self.GetMarketFundFlow(market_fund_flow_path)

    # 1，5，10 天板块资金流向排行
    # daynum_list = [1, 5, 10]
    # for daynum in daynum_list:
    #   sector_fund_flow_path = data_path + 'sector_fund_flow_' + str(daynum) + '.csv'
    #   file = pathlib.Path(sector_fund_flow_path)
    #   if not file.is_file(): 
    #     self.GetSectorFundFlow(sector_fund_flow_path, daynum)

    # 主力净流入排行
    # main_fund_flow_path = data_path + 'main_fund_flow.csv'
    # file = pathlib.Path(main_fund_flow_path)
    # if not file.is_file():  
    #   self.GetMainFundFlow(main_fund_flow_path)

    # 行业流入排行
    # industry = '电源设备'
    # daynum_list = [1, 5, 10]
    # for daynum in daynum_list:
    #   industry_fund_flow_path = data_path + 'industry_' + industry + '_fund_flow_' + str(daynum) + '.csv'
    #   file = pathlib.Path(industry_fund_flow_path)
    #   if not file.is_file():  
    #     self.GetIndustryFundFlow(industry_fund_flow_path, industry, daynum)

    # 行业资金流向历史
    # industry_fund_history_path = data_path + 'industry_' + industry + '_fund_histroy.csv'
    # file = pathlib.Path(industry_fund_history_path)
    # if not file.is_file():  
    #   self.GetIndustryFundHistory(industry_fund_history_path, industry)

    # 概念资金流向历史
    # concept = '锂电池'
    # concept_fund_history_path = data_path + 'concept_' + concept + '_fund_histroy.csv'
    # file = pathlib.Path(concept_fund_history_path)
    # if not file.is_file():  
    #   self.GetConceptFundHistory(concept_fund_history_path, concept)

    # # 强势股池
    # strong_date = '20240329'
    # strong_stock_path = data_path + 'strong_stock_' + strong_date + '.csv'
    # file = pathlib.Path(strong_stock_path)
    # if not file.is_file():  
    #   self.GetStrongStock(strong_stock_path, strong_date)


  def GetPriceStocks(self, stocks_csv, price_stock_csv, price, main_fund, force_rise=True):
    """筛选价格低于 price 的股票，同时超大单和大单都是买入

    Args:
        stocks_csv (str): GetFundFlow 函数获取 csv 数据
        price_stock_csv (str): 保存筛选后的股票 csv 数据
        price (float): 筛选的股价上限
        main_fund (float): 主力涨幅，百分比
        force_rise (bool): 是否需要超大单和大单都是上涨的
    """    
    csv_reader = csv.reader(open(stocks_csv))
    num = 0

    with open(price_stock_csv, "a", encoding="utf-8", newline="") as f:
      csv_writer = csv.writer(f) # 基于文件对象构建 csv写入对象
      for row in csv_reader:
        # csv 中字符 '-' 表示空栅格
        if row[3] == '-':
          break

        num += 1 # 第一行是项目标题
        if num == 1:
          csv_writer.writerow(row)
          continue

        if float(row[3]) <= price and float(row[6]) >= main_fund:
          write = True
          if force_rise == True:
            if float(row[8]) < 0 or float(row[10]) < 0:
              write = False
          if write == True:
            csv_writer.writerow(row)

      f.close()


  def GetPriceStocksByRanking(self, stocks_csv, price_stock_csv, price, rise, count, force_rise=True):
    """筛选价格低于 price 的股票，同时主力是买入

    Args:
        stocks_csv (str): GetFundFlow 函数获取 csv 数据
        price_stock_csv (str): 保存筛选后的股票 csv 数据
        price (float): 筛选的股价上限
        rise (float): 涨幅
        count (int): 筛选前 count 支股票
        force_rise (bool): 是否需要超大单和大单都是上涨的
    """    
    csv_reader = csv.reader(open(stocks_csv))
    num = 0

    with open(price_stock_csv, "a", encoding="utf-8", newline="") as f:
      csv_writer = csv.writer(f) # 基于文件对象构建 csv写入对象
      for row in csv_reader:
        # csv 中字符 '-' 表示空栅格
        if row[3] == '-':
          break

        if num >= count + 1:
          break

        num += 1 # 第一行是项目标题
        if num == 1:
          csv_writer.writerow(row)
          continue

        if float(row[3]) <= price and float(row[6]) >= 0:
          if float(row[4]) >= rise and float(row[4]) <= rise+3.0:
            csv_writer.writerow(row)

      f.close()


  def GetPriceStocksMoreDay(self, csv_path, price, main_fund, force_rise):
    """获取价格低于 price 的多只股票多日数据

    Args:
        csv_path (str): csv 数据目录
        price (float): 价格
        main_fund (float): 主力涨幅，百分比
        force_rise (bool): 是否需要超大单和大单都是上涨的
    """    
    for root, dirs, files in os.walk(csv_path):
      # print("root:", root)
      # print("dirs:", dirs)
      for file in files:
        pattern = r'^fund_flow_'
        if re.match(pattern, file):
          read_path = csv_path+file
          tail = re.findall('(?<=fund_flow_).*$', file)
          save_path = csv_path+'price_stock_'+tail[0]
          # print("file:", file)
          # print("read path: %s, save path %s" % (read_path, save_path))
          self.GetPriceStocks(read_path, save_path, price, main_fund, force_rise)
          # self.GetPriceStocksByRanking(read_path, save_path, price, 3.0, 500, force_rise)
      break # 跳过 os.walk 对子目录 dirs 的遍历


  def GetRecentStocks(self, csv_file, today_fund_file, save_path, days):
    """获取 csv_path 文件内股票最近 days 天的数据

    Args:
        csv_file (str): 要读文件，格式由 GetPriceStocksMoreDay() 提供
        today_fund_file (str): 今日资金流向文件，格式由 GetPriceStocksMoreDay() 提供
        save_path (str): 保存路径
        days (int): 要查阅的天数
    """    
    csv_reader = csv.reader(open(csv_file))
    num = 0

    for row in csv_reader:
      # csv 中字符 '-' 表示空栅格
      if row[3] == '-':
        break

      num += 1 # 第一行是项目标题
      if num == 1:
        continue

      pattern = r'^2' # '2'开头的股票代码不看
      if re.match(pattern, row[1]):
        continue
      pattern = r'^9' # '9'开头的股票代码不看
      if re.match(pattern, row[1]):
        continue
      pattern = r'^退市' # '退市'不看
      if re.match(pattern, row[2]):
        continue

      code_index = 1
      name_index = 2
      main_fund_index = 6
      super_fund_index = 8
      large_fund_index = 10
      today_csv_reader = csv.reader(open(today_fund_file))
      for r in today_csv_reader:
        if r[code_index] == row[code_index] and float(r[large_fund_index]) > 0 and float(r[super_fund_index]) > 0:
          code = row[code_index]      
          name = row[name_index]
          stock_history_path = save_path + code + '_' + name + '.csv'
          self.GetStockHistory(stock_history_path, code, days)

