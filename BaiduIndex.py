#!/usr/bin/env python3
# coding: utf-8
# File: BaiduIndex.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-5-23

from selenium import webdriver
from PIL import Image
import requests
import time
import re
import urllib
import pytesseract
import datetime
import os
import urllib.parse
import random
class BaiduIndex:
    '''登录，打开首页'''
    def __init__(self, user_name, password, chromepath):
        self.user_name = user_name
        self.password = password
        self.chromepath = chromepath
        self.current_dir = os.path.abspath(os.path.dirname(__file__))

    def open_homepage(self, search_word):
        keys = search_word.encode('gb2312')
        keys = urllib.parse.quote(keys)
        driver = webdriver.Chrome(self.chromepath)
        url = 'http://index.baidu.com/?tpl=trend&word=%s' % keys
        driver.get(url)
        e1 = driver.find_element_by_id("TANGRAM__PSP_4__userName")
        e1.send_keys(self.user_name)
        e2 = driver.find_element_by_id("TANGRAM__PSP_4__password")
        e2.send_keys(self.password)
        e3 = driver.find_element_by_id("TANGRAM__PSP_4__submit")
        e3.click()
        time.sleep(2)
        return driver

    '''获取指数首页'''
    def get_indexinfo(self, search_word, start_date, end_date):
        date_list = self.collect_days(start_date, end_date)
        driver = self.open_homepage(search_word)
        new_cookies = ''
        cookies = driver.get_cookies()
        for cookie in cookies:
            name = (cookie['name'])
            value = (cookie['value'])
            new_cookie = name + '=' + value + ';'
            new_cookies = new_cookies + new_cookie
        new_cookies = new_cookies[:-1]
        res = driver.execute_script('return PPval.ppt;')
        res2 = driver.execute_script('return PPval.res2;')
        header = {
            'Host': 'index.baidu.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
            'Referer': 'http://index.baidu.com/?tpl=trend&word=%CE%A4%B5%C2',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': new_cookies
        }
        url = 'http://index.baidu.com/Interface/Search/getSubIndex/?res={}&res2={}&type=0&startdate={}&enddate={}&forecast=0&word={}'.format(res, res2, start_date, end_date, search_word)
        req = requests.get(url, headers=header).json()

        return res, res2, req, date_list, header

    '''获取指数细节'''
    def get_image(self, year, search_word, start_date, end_date):
        res, res2, req, date_list, header = self.get_indexinfo(search_word, start_date, end_date)
        res3_list = req['data']['all'][0]['userIndexes_enc']
        res3_list = res3_list.split(',')
        date_pairs = list(zip(date_list, res3_list))
        region_dict = []
        date_dict = {}
        date_index = 0
        if not os.path.exists('%s/%s_tmp1/'%(search_word, year)):
            os.mkdir('%s/%s_tmp1/'%(search_word, year))

        if not os.path.exists('%s/%s_tmp2/'%(search_word, year)):
            os.mkdir('%s/%s_tmp2/'%(search_word, year))

        if not os.path.exists('%s/%s_tmp3/'%(search_word, year)):
            os.mkdir('%s/%s_tmp3/'%(search_word, year))

        for date, res3 in date_pairs:
            date_dict[date_index] = date
            timestamp = int(time.time())
            viewbox_url = 'http://index.baidu.com/Interface/IndexShow/show/?res=%s&res2=%s&classType=1&res3[]=%s&className=view-value&%s' % (
                res, res2, res3, timestamp)
            req = requests.get(viewbox_url, headers=header).json()
            print(search_word, date, '请求成功')
            response = req['data']['code'][0]
            width = re.findall('width:(.*?)px', response)
            margin_left = re.findall('margin-left:-(.*?)px', response)
            width = [int(x) for x in width]
            margin_left = [int(x) for x in margin_left]
            region_dict.append({'width': width, 'margin_left': margin_left})
            img_url = 'http://index.baidu.com' + re.findall('url\("(.*?)"', response)[0]
            img_content = requests.get(img_url, headers=header)
            time.sleep(random.uniform(0,1))
            #time.sleep(0.01)
            if img_content.status_code == requests.codes.ok:
                with open('%s/%s_tmp1/%s.png' % (search_word, year, date_index), 'wb') as file:
                    file.write(img_content.content)
                    print(search_word, date, '下载成功')
                date_index += 1

        return region_dict, date_dict

    '''数据图片解码'''
    def decode_image(self, keyword, year, region_dict, date_dict):
        for index, region in enumerate(region_dict):
            code = Image.open('%s/%s_tmp1/%s.png' % (keyword, year, index))
            hight = code.size[1]
            target = Image.new('RGB', (sum(region['width']), hight))
            for i in range(len(region['width'])):
                img = code.crop((region['margin_left'][i], 0, region['margin_left'][i] + region['width'][i], hight))
                target.paste(img, (sum(region['width'][0:i]), 0, sum(region['width'][0:i + 1]), hight))
                target.save('%s/%s_tmp2/%s.png' % (keyword, year, date_dict[index]))

    '''图片数字转写'''
    def transwrite_image(self, year, word):
        f = open('%s/%s_index.txt' % (word, year), 'w+')
        for root, dirs, files in os.walk('%s/%s_tmp2'%(word, year)):
            for file in files:
                filepath = os.path.join(root, file)
                date = file.split('.')[0]
                num = self.char_to_num(word, year, filepath)
                f.write(date + '\t' + num + '\n')
        f.close()

    '''图片数字识别'''
    def char_to_num(self, keyword, year, filepath):
        jpgzoom = Image.open(filepath)
        (x, y) = jpgzoom.size
        x_s = 2 * x
        y_s = 2 * y
        out = jpgzoom.resize((x_s, y_s), Image.ANTIALIAS)
        file = filepath.split('/')[-1].split('.')[0]
        out.save('%s/%s_tmp3/%s.jpg' % (keyword, year, file), "JPEG", quality=100)
        num = pytesseract.image_to_string(out)
        if num:
            num = num.lower().replace("'", '').replace('!', '').replace('.', '').replace(',', '').replace('?', '7').replace("S", '5').replace(" ","").replace("E", "8").replace("B", "8").replace("I", "1").replace("$", "8").replace("a", "8").replace('n', "11").replace('o', '0')
            print(num)
            return num
        else:
            return 'error'

    '''获取时间段内的日期列表'''
    def collect_days(self, start_date, end_date):
        date_list = []
        begin_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        return date_list

    '''合并指数'''
    def merge_index(self, word):
        index_paths = sorted(['%s/%s'%(word, file) for file in os.listdir(word) if file.endswith('_index.txt')])
        f = open('%s/%s.txt'%(word, word), 'w+')
        index_dict = {}

        for filepath in index_paths:
            for line in open(filepath):
                if not line:
                    continue
                line = line.strip().split('	')
                index_dict[int(line[0].replace('-', ''))] = line[1]

        index_dict = sorted(index_dict.items(), key=lambda asd:asd[0], reverse=False)
        for item in index_dict:
            f.write(str(item[0])[:4] + '-' + str(item[0])[4:6] + '-' + str(item[0])[6:] + '\t' + item[1] + '\n')

        f.close()

    '''采集主函数'''
    def spider(self, year, word, start_date, end_date):
        print('step1, spider data..')
        region_dict, date_dict = self.get_image(year, word, start_date, end_date)
        print('step2, deocde image..')
        self.decode_image(word, year, region_dict, date_dict)
        print('step3, transfer image..')
        self.transwrite_image(year, word)
        print('step4, merge index..')
        self.merge_index(word)

