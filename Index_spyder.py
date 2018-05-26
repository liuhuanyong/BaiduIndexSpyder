#!/usr/bin/env python3
# coding: utf-8
# File: Index_spyder.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-5-26

from BaiduIndex import BaiduIndex
import os

def demo():
    user_name = '××××××××'
    password = '×××'
    chromepath = '/×××××××××/chromedriver'
    baidu = BaiduIndex(user_name, password, chromepath)
    keyword_list = ['中兴']
    date_dict = [
        ['2018', '2018-01-01', '2018-12-31'],
        ['2017', '2017-01-01', '2017-12-31'],
        ['201606', '2016-01-01', '2016-06-30'],
        ['201612', '2016-07-01', '2016-12-31'],
        ['2015', '2015-01-01', '2015-12-31'],
        ['2014', '2014-01-01', '2014-12-31'],
        ['2013', '2013-01-01', '2013-12-31'],
        ['201206', '2012-01-01', '2012-06-30'],
        ['201212', '2012-07-01', '2012-12-31'],
        ['2011', '2011-01-01', '2011-12-31']
        ]

    for keyword in keyword_list:
        if not os.path.exists('%s'%keyword):
            os.mkdir('%s'%keyword)
        for date in date_dict:
            year = date[0]
            start_date = date[1]
            end_date = date[2]
            baidu.spider(year, keyword, start_date, end_date)

demo()