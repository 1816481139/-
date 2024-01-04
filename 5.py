#导入库
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import date

# 定义函数，用来处理User-Agent和Cookie
def ua_ck():
    '''
    网站需要登录才能采集，需要从Network--Doc里复制User-Agent和Cookie，Cookie要转化为字典
    '''

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    cookies = 'bid=5GY-aPBpd54; ll="108288"; _ga_Y4GN1R87RG=GS1.1.1703731251.1.0.1703731251.0.0.0; _ga=GA1.2.1076105826.1703731252; _gid=GA1.2.1510627853.1703731253; __utmc=30149280; __utmc=223695111; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1703731290%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.4cf6=744becef7ebec41e.1703731290.; _pk_ses.100001.4cf6=1; ap_v=0,6.0; _vwo_uuid_v2=D8A63FDE9606C213ECA1DAC3A8942AB41|aa9096fd8ca98293b4a03a55514b02c3; __yadk_uid=8UGAoJUKdnl5Fmmr5NUui89xVS9GvB3U; douban-fav-remind=1; __utma=30149280.1076105826.1703731252.1703731268.1703731384.2; __utmb=30149280.0.10.1703731384; __utmz=30149280.1703731384.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=223695111.1076105826.1703731252.1703731290.1703731384.2; __utmb=223695111.0.10.1703731384; __utmz=223695111.1703731384.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); dbcl2="276754763:hdEfpxeJv2k"; ck=U8Ou; push_noty_num=0; push_doumail_num=0; frodotk_db="d00f282bd883b78c702d7883898b26a4"'

    # Cookie转化为字典
    cookies = cookies.split('; ')
    cookies_dict = {}
    for i in cookies:
        cookies_dict[i.split('=')[0]] = i.split('=')[1]

    return user_agent, cookies_dict

# 定义函数，用于获取豆瓣top250每一个页面的网址
def get_urls(n):
    '''
    n:页面数量
    '''

    urls = []  # 用于存放网址
    num = (n-1)*25+1
    for i in range(0, num, 25):
        url = 'https://movie.douban.com/top250?start={}&filter='.format(i)
        urls.append(url)

    return urls

# 定义函数，获取每个页面25部电影的链接
def get_movies_url(url, u_a, c_d):
    '''
    url：每一个页面的链接
    u_a：User-Agent
    c_d：cookies
    '''

    html = requests.get(url,
                        headers=u_a,  # 加载User-Agent
                        cookies=c_d)  # 加载cookie

    #html.encoding = html.apparent_encoding  # 解决乱码的万金油方法
    html.encoding='utf-8'

    if html.status_code == 200:
        print('网页访问成功，代码：{}\n'.format(html.status_code))

    soup = BeautifulSoup(html.text, 'html.parser')  # 用 html.parser 来解析网页
    items = soup.find('ol', class_='grid_view').find_all('li')
    movies_url = []

    for item in items:
        # 电影链接
        movie_href = item.find('div', class_='hd').find('a')['href']
        movies_url.append(movie_href)

    return movies_url
    time.sleep(0.4)    # 设置时间间隔，0.4秒采集一次，避免频繁登录网页


# 定义函数，获取每一部电影的详细信息
def get_movie_info(href, u_a, c_d):
    '''
    href：每一部电影的链接
    u_a：User-Agent
    c_d：cookies
    '''

    html = requests.get(href,
                        headers=u_a,
                        cookies=c_d)
    html.encoding='utf-8'
    soup = BeautifulSoup(html.text, 'html.parser')  # 用 html.parser 来解析网页
    item = soup.find('div', id='content')

    movie = {}  # 新建字典，存放电影信息

    # 电影名称
    movie['电影名称'] = item.h1.span.text

    # 导演、类型、制片国家/地区、语言、上映时间、片长（部分电影这些信息不全，先全部采集，留待数据分析时处理）
    movie['电影其他信息'] = item.find(
        'div', id='info').text.replace(' ', '').split('\n')
    for i in movie['电影其他信息']:
        if ':' in i:
            movie[i.split(':')[0]] = i.split(':')[1]
        else:
            continue

    # 豆瓣评分、评分人数
    movie['评分'] = item.find('div', id='interest_sectl').find(
        'div', class_='rating_self clearfix').find('strong', class_='ll rating_num').text
    movie['评分人数'] = item.find('div', id='interest_sectl').find('div', class_='rating_self clearfix').find(
        'div', class_='rating_sum').find('span', property='v:votes').text
    # 电影获奖情况

    return movie
    time.sleep(0.4)  # 0.4秒采集一次，避免频繁登录网页


# 设置主函数，运行上面设置好的函数
def main():
    '''
    n:页面数量，总共有10个页面
    u_a：User-Agent
    c_d：cookies
    '''
    
    n = 10  # 页面数量，总共有10个页面
    print('开始采集数据，预计耗时2分钟')
    
    # 处理User-Agent和Cookie
    login = ua_ck()
    u_a = login[0]
    c_d = login[1]

    # 获取豆瓣top250每一页的链接，共10页
    urls = get_urls(n)
    print('豆瓣10个网页链接已生成！！')

    # 获取每一页25部电影的链接，共250部
    top250_urls = []
    for url in urls:
        result = get_movies_url(url, u_a, c_d)
        top250_urls.extend(result)
    print('250部电影链接采集完成！！开始采集每部电影的详细信息(预计耗时5分钟).......')

    # 获取每一部电影的详细信息
    top250_movie = []  # 储存每部电影的信息
    error_href = []  # 储存采集错误的网址

    for href in top250_urls[:]:
        try:
            movie = get_movie_info(href, u_a, c_d)
            top250_movie.append(movie)
        except:
            error_href.append(href)
            print('采集失败，失败网址是{}'.format(href))

    print('电影详细信息采集完成！！总共采集{}条数据'.format(len(top250_movie)))
    return top250_movie, error_href

# 启动主函数，开始采集数据
result = main()

df = pd.DataFrame(result[0])
# 保存为本地Excel文件，文件名包含采集时间
df.to_excel(r'./豆瓣电影top250_{}.xlsx'.format(date.today()),engine='openpyxl')
df.to_csv(r'./豆瓣电影top250_{}.csv'.format(date.today()), encoding='utf-8')