#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
from share.stock import *


if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')
  stock = Stock()

  current_path=os.getcwd()
  print('当前路径：%s' % (current_path))
  stocks_path = current_path + '/data/stocks.csv'
  stock.GetStock(stocks_path)
  
