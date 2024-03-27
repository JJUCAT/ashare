#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import akshare as ak


class Stock(object):

  def __init__(self):
    print('Stock init.')

  def GetStock(self, path):
    astocks = ak.stock_info_a_code_name()
    astocks.to_csv(path, index=None, encoding='utf-8-sig')
