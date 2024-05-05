#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import akshare as ak
import pathlib
import csv
import os
import re
import datetime


class Info(object):

  def __init__(self):
    print('Information init.')

  def GetStockNEWS(self, save_path, code):
    info = ak.stock_news_em(symbol=code)
    info_path = save_path + 'news_' + code + '.csv'
    info.to_csv(info_path, index=None, encoding='utf-8-sig')

