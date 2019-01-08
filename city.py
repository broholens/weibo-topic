"""
通过微博API，获取每个省份的城市以及城市编码，最终保存在city.csv中
其中辽宁的朝阳市和北京的朝阳区因为朝阳而重叠，发帖的地址里没有朝阳区，所以手动删除掉北京的朝阳区
"""

token = '2.009Qu1BGfGTFPBc4a8525ba90S17_a'

provinces = [{"001011":u"北京"},{"001012":u"天津"},{"001013":u"河北"},{"001014":u"山西"},{"001015":u"内蒙古"},{"001021":u"辽宁"},{"001022":u"吉林"},{"001023":u"黑龙江"},{"001031":u"上海"},{"001032":u"江苏"},{"001033":u"浙江"},{"001034":u"安徽"},{"001035":u"福建"},{"001036":u"江西"},{"001037":u"山东"},{"001041":u"河南"},{"001042":u"湖北"},{"001043":u"湖南"},{"001044":u"广东"},{"001045":u"广西"},{"001046":u"海南"},{"001050":u"重庆"},{"001051":u"四川"},{"001052":u"贵州"},{"001053":u"云南"},{"001054":u"西藏"},{"001061":u"陕西"},{"001062":u"甘肃"},{"001063":u"青海"},{"001064":u"宁夏"},{"001065":u"新疆"},{"001071":u"台湾"},{"001081":u"香港"},{"001082":u"澳门"}]

import requests


def get_cities(province):
    p_code, p_name = list(province.items())[0]
    url = 'https://api.weibo.com/2/common/get_city.json?access_token=2.009Qu1BGfGTFPBc4a8525ba90S17_a&province=' + p_code
    result = requests.get(url).json()
    for i in result:
        c_code, c_name = list(i.items())[0]
        city_map = c_name.strip(u'市'), c_code[-2:].lstrip('0'), p_code[-2:]
        print(city_map)
        yield city_map


results = []

for province in provinces:
    results.extend(get_cities(province))

import pandas as pd

data = pd.DataFrame.from_records(data=results, columns=['city_name', 'city_code', 'province_code'])
data.to_csv('city.csv', index=False)
