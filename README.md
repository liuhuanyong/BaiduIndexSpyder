
# BaiduIndexSpyder
self complemented BaiduIndexSpyder based on Selenium , index image decode and num image transfer
# 项目介绍
基于关键词的百度搜索指数自动采集。本项目的例子主要实现了指定关键词的百度指数历时数据采集。百度指数的总体搜索指数提供2011年至今的所有指数数据。  
# 项目思想  
百度指数历史数据采集，通过模拟浏览器，获取指数图片，最后进行图片数字识别与转写，实现指数采集。主要包括以下几个步骤：  
1、进入百度指数搜索入口，用户指定百度账号和密码，登录百度指数平台  
2、基于关键词和日期段，构造百度指数请求  
3、对百度指数请求返回的数据指纹和指纹图片进行存储，存储至本地，作为中间结果  
4、基于数据指纹和指纹图片，进行指纹解码，将指纹图片转换为实际数据图片，存储，作为数据转写来源  
5、对指数数据图片进行去噪，增强处理，同时进行图片数字识别，识别成相应的数字序列  
6、对数字序列与对应的日期进行对应，形成日期-百度指数格式的最终结果  
7、基于结果，进行人工检测，因为基于Pytesseract的数字识别，准确率约97%，需要人工对错误部分进行核查  
# 项目结构
BaiduIndex.py:百度指数采集类脚本  
index_spyder.py:历史指数数据采集测试脚本  
中兴:‘中兴’关键词下的数据采集数据   
中兴.txt:‘中兴’关键词的历史指数数据文件  
# 历时数据的采集  
目标：以‘中兴’为例，采集出从2011年至今的所有指数数据  
![Image text](https://github.com/liuhuanyong/BaiduIndexSpyder/blob/master/img/zx_index_pre.png)

实现：
# index_spyder.py
    def demo():
        # 用户的百度账号
        user_name = '××××××××'
        # 用户的百度账号密码
        password = '×××'
        # selenium调用chromepath，需要配置chrome主程序path
        chromepath = '/×××××××××/chromedriver'
        # 新建百度指数抓取实例，传入百度账号，密码以及chrome路径
        baidu = BaiduIndex(user_name, password, chromepath)
        # 将需要采集的关键词加入到keyword_list当中
        keyword_list = ['中兴']
        # 为了得到历时数据，需要按年去采集，包括两个方面：
        # 1）如果不以年去采集，得到的指数数据粒度为周平均，这与实际需求不符
        # 2）2012年与2016年比较特殊，需要分为上半年和下半年进行，这样才能得到以天为粒度的指数数据
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
            # 以关键词为一个单元，在本地进行图片存储
            if not os.path.exists('%s'% keyword):
                os.mkdir('%s'%keyword)
            for date in date_dict:
                year = date[0]
                start_date = date[1]
                end_date = date[2]
                baidu.spider(year, keyword, start_date, end_date)

# 采集流程：
    def spider(self, year, word, start_date, end_date):
        print('step1, spider data..')
        region_dict, date_dict = self.get_image(year, word, start_date, end_date)
        print('step2, deocde image..')
        self.decode_image(word, year, region_dict, date_dict)
        print('step3, transfer image..')
        self.transwrite_image(year, word)
        print('step4, merge index..')
        self.merge_index(word)

# 运行实例  
python index_spyder.py   

# 结果
'中兴.txt'    
date index_value  
2011-01-01	1967  
2011-01-02	1987  
2011-01-03	2140  
2011-01-04	2500  
2011-01-05	2471  
2011-01-06	2378  
2011-01-07	2393  
2011-01-08	2033  
2011-01-09	2074  
2011-01-10	2625  
...............  
2018-05-16	13028  
2018-05-17	11068  
2018-05-18	14763  
2018-05-19	11981  
2018-05-20	12950  
2018-05-21	12580  
2018-05-22	16696  
2018-05-23	14929  
2018-05-24	10314  
2018-05-25	8044  

![Image text](https://github.com/liuhuanyong/BaiduIndexSpyder/blob/master/img/zx_index_post.png)
# 总结
1、本项目接口只需要用户提供百度账户和密码，绕开验证码输入入口，减少人工干预  
2、本项目采用的方式是构造指数数据请求，讲请求到的数据指纹进行解码拼接，与指数图片滑动截屏不同，可以提高准确率与速度。以本项目为例，从采集到转换，8年的数据采集大约花费20分钟左右。速度方面提升方法：没采集一个指纹需要进行timesleep(seconds),可缩小seconds的值加快速度，本示例采用的是time.sleep(random.uniform(0,1))  
3、基于pytesseract的数字识别接口准确率需要提升，以本项目为例，在2011-01-01至2018-05-28共2702个数据中，错误个数为66，准确率为0.9707623，可以自行训练数字识别模型进行识别   
4、百度指数查询可以支持三个关键词一同查询，即以‘中国’为例，如果想得到‘中国’的综合指数，可以构造成‘中国+china+中华人民共和国’，进行采集 
