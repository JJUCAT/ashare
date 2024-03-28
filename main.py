#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
from share.stock import *
import pathlib

if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')
  stock = Stock()

  current_path = os.getcwd()
  print('当前路径：%s' % (current_path))
  csv_path = current_path + '/data/csv/'

  # A 股所有股票
  stocks_path = csv_path + 'stocks.csv'
  file = pathlib.Path(stocks_path)
  if not file.is_file():
    stock.GetStock(stocks_path)

  # 东方财富热门股票排行
  hot_rank_path = csv_path + 'hot_rank.csv'
  file = pathlib.Path(hot_rank_path)
  if not file.is_file():
    stock.GetHotRank(hot_rank_path)

  # 1，3，5，10 天资金流向排行
  daynum_list = [1, 3, 5, 10]
  for daynum in daynum_list:
    fund_flow_path = csv_path + 'fund_flow_' + str(daynum) + '.csv'
    file = pathlib.Path(fund_flow_path)
    if not file.is_file():
      stock.GetFundFlow(fund_flow_path, daynum)

  # 大盘资金流向历史数据
  market_fund_flow_path = csv_path + 'market_fund_flow.csv'
  file = pathlib.Path(market_fund_flow_path)
  if not file.is_file():  
    stock.GetMarketFundFlow(market_fund_flow_path)

  # 1，5，10 天板块资金流向排行
  daynum_list = [1, 5, 10]
  for daynum in daynum_list:
    sector_fund_flow_path = csv_path + 'sector_fund_flow_' + str(daynum) + '.csv'
    file = pathlib.Path(sector_fund_flow_path)
    if not file.is_file(): 
      stock.GetSectorFundFlow(sector_fund_flow_path, daynum)

  # 主力净流入排行
  main_fund_flow_path = csv_path + 'main_fund_flow.csv'
  file = pathlib.Path(main_fund_flow_path)
  if not file.is_file():  
    stock.GetMainFundFlow(main_fund_flow_path)

  # 行业流入排行
  industry = '电源设备'
  daynum_list = [1, 5, 10]
  for daynum in daynum_list:
    industry_fund_flow_path = csv_path + 'industry_' + industry + '_fund_flow_' + str(daynum) + '.csv'
    file = pathlib.Path(industry_fund_flow_path)
    if not file.is_file():  
      stock.GetIndustryFundFlow(industry_fund_flow_path, industry, daynum)

  # 行业资金流向历史
  industry_fund_history_path = csv_path + 'industry_' + industry + '_fund_histroy.csv'
  file = pathlib.Path(industry_fund_history_path)
  if not file.is_file():  
    stock.GetIndustryFundHistory(industry_fund_history_path, industry)

  # 概念资金流向历史
  concept = '锂电池'
  concept_fund_history_path = csv_path + 'concept_' + concept + '_fund_histroy.csv'
  file = pathlib.Path(concept_fund_history_path)
  if not file.is_file():  
    stock.GetConceptFundHistory(concept_fund_history_path, concept)









