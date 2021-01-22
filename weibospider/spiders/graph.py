import datetime
import re
from lxml import etree
from scrapy import Spider,Selector
from scrapy.http import Request
import time
from items import TweetItem,RepostItem,UserItem,CommentItem,RelationshipItem
from spiders.utils import time_fix, extract_weibo_content,extract_repost_content,extract_comment_content

class GraphSpider(Spider):
    name = "graph_spider"
    base_url = "https://weibo.cn"

    def start_requests(self):

        def init_url_by_keywords():
            # crawl tweets include keywords in a period, you can change the following keywords and date
            keywords = ['美国大选']
            date_start = datetime.datetime.strptime("2020-09-01", '%Y-%m-%d')
            date_end = datetime.datetime.strptime("2021-01-20", '%Y-%m-%d')
            time_spread = datetime.timedelta(days=1)
            urls = []
            url_format = "https://weibo.cn/search/mblog?hideSearchFrame=&keyword={}" \
                         "&advancedfilter=1&starttime={}&endtime={}&sort=time&atten=1&page=1"
            while date_start <= date_end:
                for keyword in keywords:
                    one_day_back = date_start - time_spread
                    # from today's 7:00-8:00am to 23:00-24:00am
                    for hour in range(7, 24):
                        # calculation rule of starting time: start_date 8:00am + offset:16
                        begin_hour = one_day_back.strftime("%Y%m%d") + "-" + str(hour + 16)
                        # calculation rule of ending time: (end_date+1) 8:00am + offset:-7
                        end_hour = one_day_back.strftime("%Y%m%d") + "-" + str(hour - 7)
                        urls.append(url_format.format(keyword, begin_hour, end_hour))
                    two_day_back = one_day_back - time_spread
                    # from today's 0:00-1:00am to 6:00-7:00am
                    for hour in range(0, 7):
                        # note the offset change bc we are two-days back now
                        begin_hour = two_day_back.strftime("%Y%m%d") + "-" + str(hour + 40)
                        end_hour = two_day_back.strftime("%Y%m%d") + "-" + str(hour + 17)
                        urls.append(url_format.format(keyword, begin_hour, end_hour))
                date_start = date_start + time_spread
            return urls

        # select urls generation by the following code
        #urls = init_url_by_user_id()
        urls = init_url_by_keywords()
        # url = "https://weibo.cn/search/mblog?hideSearchFrame=&keyword=%E8%90%8C%E8%90%8C%E5%BE%A1%E6%89%80a&advancedfilter=1&starttime=20181001-28&endtime=20181001-5&sort=time&atte"
        # yield Request(url, callback=self.parseUserFromKeyWord)
        for url in urls:
            yield Request(url, callback=self.parseUserFromKeyWord)
    """
    获取指定关键词下的所有微博，并从某条微博获取用户id
    """
    def parseUserFromKeyWord(self, response):
        #print("parseUserFromKeyWord")

        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parseUserFromKeyWord)
        #print("getUsers")
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                user_id = user_tweet_id.group(2)
                url = f'{self.base_url}/{user_id}/info'
                yield Request(url, callback=self.parseUser, priority=10)
            except Exception as e:
                self.logger.error(e)

    def parseUser(self, response):
        #print("parseUser")
        user_item = UserItem()
        user_item.init()
        user_item['crawl_time'] = int(time.time())
        selector = Selector(response)
        user_item['_id'] = re.findall('(\d+)/info', response.url)[0]
        user_info_text = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())
        nick_name = re.findall('昵称;?:?(.*?);', user_info_text)
        gender = re.findall('性别;?:?(.*?);', user_info_text)
        place = re.findall('地区;?:?(.*?);', user_info_text)
        brief_introduction = re.findall('简介;?:?(.*?);', user_info_text)
        birthday = re.findall('生日;?:?(.*?);', user_info_text)
        sex_orientation = re.findall('性取向;?:?(.*?);', user_info_text)
        sentiment = re.findall('感情状况;?:?(.*?);', user_info_text)
        vip_level = re.findall('会员等级;?:?(.*?);', user_info_text)
        authentication = re.findall('认证;?:?(.*?);', user_info_text)
        labels = re.findall('标签;?:?(.*?)更多>>', user_info_text)
        if nick_name and nick_name[0]:
            user_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            user_item["gender"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            user_item["province"] = place[0]
            if len(place) > 1:
                user_item["city"] = place[1]
        if brief_introduction and brief_introduction[0]:
            user_item["brief_introduction"] = brief_introduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            user_item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                user_item["sex_orientation"] = "同性恋"
            else:
                user_item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            user_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            user_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            user_item["authentication"] = authentication[0].replace(u"\xa0", "")
        if labels and labels[0]:
            user_item["labels"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')
        request_meta = response.meta
        request_meta['item'] = user_item
        yield Request(self.base_url + '/u/{}'.format(user_item['_id']),
                      callback=self.parse_further_information,
                      meta=request_meta, dont_filter=False, priority=20)


    def parse_further_information(self, response):

        text = response.text
        user_item = response.meta['item']
        tweets_num = re.findall('微博\[(\d+)\]', text)
        if tweets_num:
            user_item['tweets_num'] = int(tweets_num[0])
        follows_num = re.findall('关注\[(\d+)\]', text)
        if follows_num:
            user_item['follows_num'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', text)
        if fans_num:
            user_item['fans_num'] = int(fans_num[0])
        #print(user_item)
        yield user_item

        user_id = user_item['_id']
        url = f'{self.base_url}/{user_id}/profile?page=1'
        yield Request(url, callback=self.parseTweet,dont_filter=False, meta=response.meta, priority=30)
        # url = f"{self.base_url}/{user_id}/follow?page=1"
        # yield Request(url, callback=self.parseFollower)
        # url = f"{self.base_url}/{user_id}/fans?page=1"
        # yield Request(url, callback=self.parseFan)
        #print("parse_further_information================================")

    """
    获取某个用户的所有关注对象
    """
    def parseFollower(self, response):
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                all_page = min(20, all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parseFollower, dont_filter=False, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/follow', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipItem()
            relationships_item['crawl_time'] = int(time.time())
            relationships_item["fan_id"] = ID
            relationships_item["followed_id"] = uid
            relationships_item["_id"] = ID + '-' + uid
            yield relationships_item

    """
    获取某个用户的所有粉丝
    """
    def parseFan(self, response):
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                all_page = min(20, all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parseFan, dont_filter=False, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="移除"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/fans', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipItem()
            relationships_item['crawl_time'] = int(time.time())
            relationships_item["fan_id"] = uid
            relationships_item["followed_id"] = ID
            relationships_item["_id"] = 'fans' + '-' + uid + '-' + ID
            yield relationships_item
    """
    获取某个用户的所有帖子
    """
    def parseTweet(self, response):
        #print("parseTweet")
        #print("tweet~~~~~~~~~~~~~~~~~~~",response.url)
        # if response.url.endswith('page=1'):
        #     all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
        #     if all_page:
        #         all_page = all_page.group(1)
        #         all_page = int(all_page)
        #         for page_num in range(2, all_page + 1):
        #             page_url = response.url.replace('page=1', 'page={}'.format(page_num))
        #             yield Request(page_url, self.parseTweet, dont_filter=False, meta=response.meta)
        tree_node = etree.HTML(response.body)
        tweet_nodes = tree_node.xpath('//div[@class="c" and @id]')
        year = 2030
        for tweet_node in tweet_nodes:
            try:
                tweet_item = TweetItem()
                tweet_item.init()
                tweet_item['crawl_time'] = int(time.time())
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href')[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                user_id = user_tweet_id.group(2)
                tweet_id = user_tweet_id.group(1)
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_id,tweet_id)
                tweet_item['user_id'] = user_id
                # print("url:", tweet_item['weibo_url'])
                # print("uid:", user_id)
                tweet_item['_id'] = tweet_id
                create_time_info_node = tweet_node.xpath('.//span[@class="ct"]')[-1]
                create_time_info = create_time_info_node.xpath('string(.)')
                if "来自" in create_time_info:
                    tweet_item['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                    tweet_item['tool'] = create_time_info.split('来自')[1].strip()
                else:
                    tweet_item['created_at'] = time_fix(create_time_info.strip())
                if tweet_item['created_at']:
                    year = min(int(tweet_item['created_at'].split("-", maxsplit=1)[0]), year)
                like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['like_num'] = int(re.search('\d+', like_num).group())

                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())
                if tweet_item['repost_num'] > 0:
                    tweet_id = tweet_item['_id']
                    url = f"{self.base_url}/repost/{tweet_id}?page=1"
                    yield Request(url, callback=self.parseRepost, priority=40)

                comment_num = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()')[-1]
                tweet_item['comment_num'] = int(re.search('\d+', comment_num).group())
                if tweet_item['comment_num'] > 0:
                    tweet_id = tweet_item['_id']
                    url = f"{self.base_url}/comment/hot/{tweet_id}?rl=1&page=1"
                    yield Request(url, callback=self.parseComment, priority=45)

                images = tweet_node.xpath('.//img[@alt="图片"]/@src')
                if images:
                    tweet_item['image_url'] = images

                videos = tweet_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['video_url'] = videos

                map_node = tweet_node.xpath('.//a[contains(text(),"显示地图")]')
                if map_node:
                    map_node = map_node[0]
                    map_node_url = map_node.xpath('./@href')[0]
                    map_info = re.search(r'xy=(.*?)&', map_node_url).group(1)
                    tweet_item['location_map_info'] = map_info

                repost_node = tweet_node.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    tweet_item['origin_weibo'] = repost_node[0]

                # all_content_link = tweet_node.xpath('.//a[text()="全文" and contains(@href,"ckAll=1")]')
                # if all_content_link:
                #     all_content_url = self.base_url + all_content_link[0].xpath('./@href')[0]
                #     yield Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item},
                #                   priority=1)
                # else:
                tweet_html = etree.tostring(tweet_node, encoding='unicode')
                tweet_item['content'] = extract_weibo_content(tweet_html)
                yield tweet_item
                if year < 2020:
                    break

            except Exception as e:
                self.logger.error(e)
        if year != 2030 and year >= 2020:
            currentPage = response.url.split("page=", maxsplit=1)[1]
            tempStr = r'/>&nbsp;' + str(currentPage) + r'/(\d+)页</div>'
            #print(tempStr)
            all_page = re.search(tempStr, response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                nextPage = min(int(currentPage) + 1, all_page)
                page_url = response.url.replace('page=' + str(currentPage), 'page={}'.format(nextPage))
                yield Request(page_url, self.parseTweet, dont_filter=False, meta=response.meta)
    """
    展开阅读全文
    """
    def parse_all_content(self, response):
        #print("parse_all_content")
        tree_node = etree.HTML(response.body)
        tweet_item = response.meta['item']
        content_node = tree_node.xpath('//*[@id="M_"]/div[1]')[0]
        tweet_html = etree.tostring(content_node, encoding='unicode')
        tweet_item['content'] = extract_weibo_content(tweet_html)
        yield tweet_item

    """
    获取指定帖子的转发帖子
    """
    def parseRepost(self, response):
        #print("parseRepost")
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                all_page = all_page if all_page <= 50 else 50
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parseRepost, dont_filter=False, meta=response.meta, priority=40)
        tree_node = etree.HTML(response.body)
        repo_nodes = tree_node.xpath('//div[@class="c" and not(contains(@id,"M_"))]')
        for repo_node in repo_nodes:
            # print(etree.tostring(repo_node, encoding='unicode'))
            repo_user_url = repo_node.xpath('.//a[contains(@href,"/u/")]/@href')

            if not repo_user_url:
                # print("continue")
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
                # print(tempStr)
                if re.match("返回", tempStr) and (re.search("微博", tempStr) or re.search("首页", tempStr)):
                    continue
                user_id = re.search(r'/u/(\d+)', repo_user_url[0]).group(1)
            repo_item = RepostItem()
            # repo_item['_id'] = ''
            repo_item['crawl_time'] = int(time.time())
            repo_item['weibo_id'] = response.url.split('/')[-1].split('?')[0]
            repo_item['user_id'] = user_id
            content = extract_repost_content(etree.tostring(repo_node, encoding='unicode'))
            repo_item['content'] = content.split(':', maxsplit=1)[1]
            created_at_info = repo_node.xpath('.//span[@class="ct"]/text()')[0].split('\xa0')
            repo_item['created_at'] = time_fix((created_at_info[0] + created_at_info[1]))
            yield repo_item

    def parseComment(self, response):
        #print("parseComment")
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                all_page = all_page if all_page <= 50 else 50
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parseComment, dont_filter=False, meta=response.meta, priority=45)
        tree_node = etree.HTML(response.body)
        comment_nodes = tree_node.xpath('//div[@class="c" and contains(@id,"C_")]')
        for comment_node in comment_nodes:
            comment_user_url = comment_node.xpath('.//a[contains(@href,"/u/")]/@href')
            if not comment_user_url:
                continue
            comment_item = CommentItem()
            comment_item['crawl_time'] = int(time.time())
            comment_item['weibo_id'] = response.url.split('/')[-1].split('?')[0]
            comment_item['comment_user_id'] = re.search(r'/u/(\d+)', comment_user_url[0]).group(1)
            """
            继续爬取评论微博的用户信息
            """
            user_id = comment_item['comment_user_id']
            url = f'{self.base_url}/{user_id}/info'
            yield Request(url, callback=self.parseUser, priority=10)

            comment_item['content'] = extract_comment_content(etree.tostring(comment_node, encoding='unicode'))
            comment_item['_id'] = comment_node.xpath('./@id')[0]
            created_at_info = comment_node.xpath('.//span[@class="ct"]/text()')[0]
            like_num = comment_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
            comment_item['like_num'] = int(re.search('\d+', like_num).group())
            comment_item['created_at'] = time_fix(created_at_info.split('\xa0')[0])
            yield comment_item