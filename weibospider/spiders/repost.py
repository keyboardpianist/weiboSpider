#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/14
"""
import re
from lxml import etree
from scrapy import Spider
from scrapy.http import Request
import time
from items import RepostItem
from spiders.utils import extract_repost_content, time_fix

class RepostSpider(Spider):
    name = "repost_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):
        tweet_ids = ['H8L609p4c']
        urls = [f"{self.base_url}/repost/{tweet_id}?page=1" for tweet_id in tweet_ids]

        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                all_page = all_page if all_page <= 50 else 50
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse, dont_filter=True, meta=response.meta)
        tree_node = etree.HTML(response.body)
        repo_nodes = tree_node.xpath('//div[@class="c" and not(contains(@id,"M_"))]')
        for repo_node in repo_nodes:
            #print(etree.tostring(repo_node, encoding='unicode'))
            repo_user_url = repo_node.xpath('.//a[contains(@href,"/u/")]/@href')

            if not repo_user_url:
                #print("continue")
                originStr = etree.tostring(repo_node, encoding='unicode')
                if re.search(":", originStr) and re.search("赞\[", originStr):
                    tempStr = originStr.split("</a>", maxsplit=1)[0]
                    tempStr = tempStr.split('href="/', maxsplit=1)[1]
                    tempStr = tempStr.split('"', maxsplit=1)[0]
                    user_id = tempStr
                else:
                    continue
            else:
                tempStr = repo_node.xpath('.//a[contains(@href,"/u/")]/text()')[0]
                #print(tempStr)
                if re.match("返回", tempStr) and (re.search("微博", tempStr) or re.search("首页", tempStr)):
                    continue
                user_id = re.search(r'/u/(\d+)', repo_user_url[0]).group(1)
            repo_item = RepostItem()
            #repo_item['_id'] = ''
            repo_item['crawl_time'] = int(time.time())
            repo_item['weibo_id'] = response.url.split('/')[-1].split('?')[0]
            repo_item['user_id'] = user_id
            content = extract_repost_content(etree.tostring(repo_node, encoding='unicode'))
            repo_item['content'] = content.split(':', maxsplit=1)[1]
            created_at_info = repo_node.xpath('.//span[@class="ct"]/text()')[0].split('\xa0')
            repo_item['created_at'] = time_fix((created_at_info[0]+created_at_info[1]))
            yield repo_item
            
