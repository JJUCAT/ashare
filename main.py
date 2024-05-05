#!/usr/bin/python3.9
# -*- coding: UTF-8 -*-

import os
import csv
from share.stock import *
from share.prophet import *
from share.mail import *
from share.task import *
import pathlib
import shutil


if __name__ == '__main__':
  print(' --------- 财源滚滚 --------- ')
  # TimerTask()
  # TaskBuyMonitor()
  TaskSellMonitor()

