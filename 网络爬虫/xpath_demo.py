import csv

import requests
from fake_useragent import UserAgent
from lxml import etree
from time import sleep
from random import randint

def get_html(url):
    """获得html"""
    headers = {'User-Agent': str(UserAgent(path="C:/Users/Hanrey/Desktop/ua.json").random)}
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/68.0.3440.106 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    sleep(randint(5,8))
    if response.status_code == 200:
        return response.text
    else:
        return 'error'


def parse_index(html):
    """获得电影详细页面的url"""
    e = etree.HTML(html)
    all_url = e.xpath('//div[@class="channel-detail movie-item-title"]/a/@href')
    print(all_url)
    return ['https://maoyan.com{}'.format(url) for url in all_url]


def parse_grade(html):
    "在全部页面获得电影评分"
    grade_lst = []
    e = etree.HTML(html)
    grade_int = e.xpath('//div[@class="channel-detail channel-detail-orange"]/i[@class="integer"]/text()')
    grade_fra = e.xpath('//div[@class="channel-detail channel-detail-orange"]/i[@class="fraction"]/text()')
    for i in range(len(grade_fra)):
        grade_lst.append("%s%s"%(grade_int[i],grade_fra[i]))
    return grade_lst



def parse_info(html):
    """电影名、类型、国家、上映时间"""
    e = etree.HTML(html)
    name = e.xpath('//h1[@class="name"]/text()')
    type = e.xpath('//li[@class="ellipsis"][1]/a[@class="text-link"]/text()')
    country = e.xpath('//li[@class="ellipsis"][2]/text()')
    time = e.xpath('//li[@class="ellipsis"][3]/text()')
    return {
        "name": name,
        "type": type,
        "country": country,
        "time": time
    }


def main():
    pages = 10      #输入要爬取的页面
    header = ['name', 'type', 'country', 'time', 'grade']
    datas = []
    for i in range(0, 30*pages, 30):
        index_url = 'https://maoyan.com/films?showType=3&sortId=3&offset=' + str(i)
        html = get_html(index_url)
        grade = parse_grade(html)   #得到该页评分列表
        movies_html = parse_index(html)
        i = 0
        for url in movies_html:
            movies_html = get_html(url)
            moive = parse_info(movies_html)
            moive['grade'] = grade[i]   #添加评分数据
            if moive['name'] != []:     #数据清洗
                name = moive['name'][0]
                moive['name'] = name
                country = str(moive['country']).split('/')[0].strip("['").strip().strip("\\n").strip()    #格式化国家
                moive['country'] = country
                time = moive['time'][0]
                moive['time'] = time
                i += 1
                datas.append(moive)
                print(moive)
            else:
                print("数据丢失！")
    with open("movie_info.csv", 'a', newline='', encoding='utf-8') as csv_file:
        write = csv.DictWriter(csv_file, fieldnames=header)
        write.writeheader()
        write.writerows(datas)


if __name__ == '__main__':
    main()