#!/usr/bin/python3
# encoding: utf-8
# Author:BinhuaLiao
# Created Time:Mon Dec  4 21:52:17 2017
# File Name:main.py
# Description:

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "jobbole"])
execute(["scrapy", "crawl", "zhihu"])
