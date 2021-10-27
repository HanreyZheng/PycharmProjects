import csv
import re
from time import sleep
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from numpy.random import randint


def get_html(url):
    """获得html"""
    headers = {'User-Agent': str(UserAgent(path="C:/Users/Hanrey/Desktop/ua.json").random)}
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/68.0.3440.106 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    sleep(randint(2, 5))
    if response.status_code == 200:
        return response.text
    else:
        return 'error'


def prase_index(html):
    """获取页面所有电影"""
    all_url = []
    soup = BeautifulSoup(html, 'lxml')
    for k in soup.find_all("a", attrs={"target": "_blank", "data-act": "movies-click"}):
        x = k.get('href')
        all_url.append(x)
    return ['https://maoyan.com{}'.format(url) for url in all_url]


def parse_grade(html):
    grade_lst = []
    soup = BeautifulSoup(html, 'lxml')
    grade_int = soup.select('i[class="integer"]')
    grade_fra = soup.select('i[class="fraction"]')
    for i in range(len(grade_int)):
        grade_lst.append("%s%s"%(grade_int[i].string,grade_fra[i].string))
    return grade_lst


def prase_info_bs4(html):
    soup = BeautifulSoup(html, 'lxml')
    if soup.select('h1') != []:
        name = soup.select('h1')[0].string
        type_lst = []
        types = soup.select('.text-link')
        for type in types:
            type_lst.append(type.string)
        country = soup.select('li.ellipsis')[1].string.split('/')[0].strip("['").strip().strip("\\n").strip()
        time = soup.find('li', text=re.compile('\d{4}-\d{2}-\d{2}')).string  # 获得上映时间
        return {
            "name": name,
            "type": type_lst,
            "country": country,
            "time": time,
            "state": 1
        }
    else:
        return {"数据丢失": 0, "state": 0}



if __name__ == '__main__':
    pages = 10      #输入要爬取的页面
    header = ['name', 'type', 'country', 'time', 'grade', 'state']
    datas = []
    for i in range(0, 30*pages, 30):
        index_url = 'https://maoyan.com/films?showType=3&sortId=3&offset=' + str(i)
        html = get_html(index_url)
        grade = parse_grade(html)       #评分
        movies_url = prase_index(html)
        i = 0
        for url in movies_url:
            movie_html = get_html(url)
            movie_info = prase_info_bs4(movie_html)
            movie_info['grade'] = grade[i]
            i += 1
            if movie_info['state'] == 1:
                datas.append(movie_info)
            print(movie_info)

    with open("movie_info_bs4.csv", 'a', newline='', encoding='utf-8') as csv_file:
        write = csv.DictWriter(csv_file, fieldnames=header)
        write.writeheader()
        write.writerows(datas)