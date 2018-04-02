import threading
from queue import Queue
import requests
import time
from lxml import etree

START_URL = 'http://qianmu.iguye.com/2018USNEWS世界大学排名'
link_queue =  Queue()
threads = []
DOWNLOADER_NUM = 20



def fetch(url):
    r = requests.get(url)
    return r.text.replace('\t','')


def parse(html):

    html = etree.HTML(html)
    links = html.xpath('//*[@id="content"]/table/tbody/tr/td[2]/a/@href')
    for link in links:
        if not link.startswith('http://'):
            link = 'http://qianmu.iguye.com/%s' % link
        link_queue.put(link)


def parse_university(html):
    html = etree.HTML(html)
    table = html.xpath('//*[@id="wikiContent"]/div[1]/table/tbody')
    if not table:
        return
    table = table[0]
    keys = table.xpath('./tr/td[1]//text()')
    cols = table.xpath('./tr/td[2]')
    values = [''.join(col.xpath('.//text()')) for col in cols]
    info = dict(zip(keys, values))
    print(info)

def downloader():
    while True:
        link = link_queue.get()
        if link is None:
            break
        parse_university(fetch(link))
        link_queue.task_done()
        print('剩余链接数为%s'%link_queue.qsize())

if __name__ == '__main__':
    start_time = time.time()
    parse(fetch(START_URL))
    for i in range(DOWNLOADER_NUM):
        t = threading.Thread(target=downloader)
        t.start()
        threads.append(t)
    link_queue.join()
    for i in range(DOWNLOADER_NUM):
        link_queue.put(None)
    for t in threads:
        t.join()
    cost_time = time.time() -start_time
    print('一共用了%s秒'%cost_time)