import pandas as pd
import time
import os
import csv
import requests
from lxml.html import etree

def make_file(name):
    return name + '_ok.csv', name + '_error.csv'

def get_file(name):
    return open(name, 'a+', encoding='utf-8', newline='')

def make_writer(name):
    filename1, filename2 = make_file(name)
    f1, f2 = get_file(filename1), get_file(filename2)
    return f1, f2, csv.writer(f1), csv.writer(f2)


keyword_url_dict = {
    '环保': '%E7%8E%AF%E4%BF%9D',
    '环境保护': '%E7%8E%AF%E5%A2%83%E4%BF%9D%E6%8A%A4',
    '污染': '%E6%B1%A1%E6%9F%93',
    '雾霾': '%E9%9B%BE%E9%9C%BE'
}

times = ['2016-01-01:2016-12-31',
         '2015-01-01:2015-12-31', '2014-01-01:2014-12-31', '2013-01-01:2013-12-31',
         '2012-01-01:2012-12-31', '2011-01-01:2011-12-31', '2010-01-01:2010-12-31']

ok_names = ['city', 'keyword', 'year', 'count']
error_names = ['city']
# 微博发帖的excel
origin_data = pd.read_excel('微博发帖.xlsx')
excel_cities = set([i.strip('市').strip('地区') for i in origin_data['城市']])

# qc = set([i.strip('市').strip('地区') for i in origin_data.get(0)['城市']])
# qzcq = set([i.strip('市').strip('地区') for i in origin_data.get(1)['城市']])
# 设置索引
# qc.set_index(qc['城市'], inplace=True,)
# qzcq.set_index(qzcq['城市'], inplace=True, drop=True)
#


# cities = list(i.strip('市') for i in set(cities['城市']))

weibo_cities = pd.read_csv('city.csv', index_col='city_name')
# # data.set_index(data['city_name'], inplace=True, drop=True)

# 加载之前下载过的数据
def load_downloaded(name):
    filename1, filename2 = make_file(name)
    if not os.path.exists(filename1):
        return []
    data2 = pd.read_csv(filename1, names=ok_names, engine='python', encoding='utf-8')
    downloaded = set(data2['city'])
    result = []
    with open(filename2, 'r', encoding='utf-8')as f:
        for i in f.readlines():
            result.append(i.strip('\n'))
    return set(result) | downloaded


# 给定筛选条件  获取该条件下帖子数量
def get_posts_count(url):
    html = requests.get(url).text
    tree = etree.HTML(html)
    lis = tree.xpath('//*[@id="pl_feedlist_index"]/div[3]/div/span/ul/li')
    pages = len(lis) or 1
    if pages != 1:
        last = 'https://s.weibo.com' + lis[-1].xpath('./a/@href')[0]
        html = requests.get(last).text
        tree = etree.HTML(html)
    divs = tree.xpath('//*[@id="pl_feedlist_index"]/div[2]/div')
    items = len(divs) + (pages - 1) * 20
    time.sleep(1)
    return items

# 直辖市
zxs = {'北京': '11:1000', '上海': '31:1000', '天津': '12：1000', '重庆市县': '50:1000'}


def get_region(city, f2, writer2):
    if city in zxs:
        return zxs.get(city)
    try:
        c = weibo_cities.loc[city]
    except:
        print('8'*20, city)
        writer2.writerow([city])
        f2.flush()
        return
    p_code, c_code = str(int(c['province_code'])), str(int(c['city_code']))
    return p_code+':'+c_code


def search(keyword, cities=excel_cities):
    f1, f2, writer1, writer2 = make_writer(keyword)
    encode_keyword = keyword_url_dict[keyword]
    for city in cities:
        if city in load_downloaded(keyword):
            continue
        region = get_region(city, f2, writer2)
        if not region:
            continue
        for i in times:
            url = 'https://s.weibo.com/weibo?q={}&region=custom:{}&typeall=1&suball=1&timescope=custom:{}&Refer=g'.format(encode_keyword, region, i)
            # url2 = 'https://s.weibo.com/weibo?q=%E5%BC%BA%E5%88%B6%E6%8B%86%E8%BF%81&region=custom:{}&typeall=1&suball=1&timescope=custom:{}&Refer=g'.format(region, i)
            # for url in (url1, url2):
            # url = url1 if keyword == '强拆' else url2
            # keyword = '强拆' if url == url1 else '强制拆迁'
            items_count = get_posts_count(url)
            print(city, keyword, i, items_count)
            writer1.writerow((city, keyword, i.split('-', 1)[0], items_count))
            f1.flush()
            time.sleep(1)

def write_to_excel(keys):
    writer = pd.ExcelWriter('output.xlsx')
    for key in keys:
        data = pd.read_csv(make_file(key)[0], names=ok_names, engine='python', encoding='utf-8')
        data.to_excel(writer, key, index=False)
    for key in keys:
        data = pd.read_csv(make_file(key)[1], names=error_names, engine='python', encoding='utf-8')
        data.to_excel(writer, key+'未搜索到', index=False)
    writer.save()

def run(keys):
    for key in keys:
        search(key)
    write_to_excel(keys)


if __name__ == '__main__':
    keys = ['环保', '环境保护']
    write_to_excel(keys)