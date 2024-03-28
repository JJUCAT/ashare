#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import akshare as ak


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



