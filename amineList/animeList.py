import requests
from bs4 import BeautifulSoup
import re

bg_url = 'http://bangumi.tv/calendar'

def download_page(url):
    headers = {
        'User-Agent': 'Chrome/47.0.2526.80'
        #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }
    data = requests.get(url,headers=headers).content
    return data
    
def parse_bg(html):
    bangumi_list = []
    soup = BeautifulSoup(html)
    bangumi_soup = soup.find('div', class_='BgmCalendar')
    if bangumi_soup != None:
        for week_li in bangumi_soup.find_all('li', class_='week'):
            week = ''.join(week_li.find('dd').get('class'))
            week_list = []
            temp_dict = {}
            for bangumi_li in week_li.find('ul').find_all('li'):
                item_dict = {}
                #get bangumi title
                bangumi_title = bangumi_li.find('a').getText()
                if bangumi_title == '':
                    bangumi_title = bangumi_li.find('em').getText()
                item_dict["title"] = bangumi_title
                #get bangumi image
                bangumi_img = bangumi_li.get('style')
                img = re.search(r'lain.*jpg',bangumi_img)
                bangumi_img = "url(http://" + img.group() + ")"
                item_dict["img"] = bangumi_img
                #get info url
                info_url = bangumi_li.find('a').get("href")
                info_url = "http://bangumi.tv" + info_url
                #get bangumi rate and votes
                rv = bg_info(info_url)
                #print(bangumi_title)
                #print(info_url)
                #print(rv)
                item_dict["rate"] = rv[0]
                item_dict["votes"] = rv[1]
                #append bangumi info
                week_list.append(item_dict)
            temp_dict["day"] = week
            temp_dict["item"] = week_list
            bangumi_list.append(temp_dict)
        return bangumi_list
    
def bg_info(url):
    html = download_page(url)
    soup = BeautifulSoup(html)
    info_soup = soup.find('div', class_='SidePanel')
    if info_soup != None:
        temp = []
        rate = info_soup.find(property='v:average').getText()
        votes = info_soup.find(property='v:votes').getText()
        temp.append(rate)
        temp.append(votes)
        return temp
    return ['no','page']

def main():
    bg = parse_bg(download_page(bg_url))
    if bg != None:
        s = str(bg).replace("'","\"")
        print(s)
        f = open('wlist_moreInfo', 'w')
        f.write(s)
        f.close()
    

if __name__ == '__main__':
    main()