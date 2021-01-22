# -*- coding: utf-8 -*-
from scrapy import Item, Field


class TweetItem(Item):
    """Tweet information """
    _id = Field()  # 微博id
    weibo_url = Field()  # 微博URL
    created_at = Field()  # 微博发表时间
    like_num = Field()  # 点赞数
    repost_num = Field()  # 转发数
    comment_num = Field()  # 评论数
    content = Field()  # 微博内容
    user_id = Field()  # 发表该微博用户的id
    tool = Field()  # 发布微博的工具
    image_url = Field()  # 图片
    video_url = Field()  # 视频
    origin_weibo = Field()  # 原始微博，只有转发的微博才有这个字段
    location_map_info = Field()  # 定位的经纬度信息
    crawl_time = Field()  # 抓取时间戳

    def init(self):
        self["content"] = ''
        self["tool"] = ''
        self["image_url"] = ''
        self["video_url"] = ''
        self["origin_weibo"] = ''
        self["location_map_info"] = ''

    def get_insert_sql(self):
        sql = r'insert IGNORE into tweetitem(id, weibo_url, created_at, like_num, repost_num,' \
              r' comment_num, content, user_id, tool, origin_weibo, ' \
              r'location_map_info, crawl_time) ' \
              r'values (%s, %s, %s, %s, %s,' \
              r' %s, %s, %s, %s, %s,' \
              r'%s, %s)'

        params = (self["_id"], self["weibo_url"], self["created_at"], int(self["like_num"]), int(self["repost_num"]),
                  int(self["comment_num"]), self["content"], int(self["user_id"]), self["tool"],
                  self["origin_weibo"], self["location_map_info"], int(self["crawl_time"]))
        return sql, params

class UserItem(Item):
    """ User Information"""
    _id = Field()  # 用户ID
    nick_name = Field()  # 昵称
    gender = Field()  # 性别
    province = Field()  # 所在省
    city = Field()  # 所在城市
    brief_introduction = Field()  # 简介
    birthday = Field()  # 生日
    tweets_num = Field()  # 微博数
    follows_num = Field()  # 关注数
    fans_num = Field()  # 粉丝数
    sex_orientation = Field()  # 性取向
    sentiment = Field()  # 感情状况
    vip_level = Field()  # 会员等级
    authentication = Field()  # 认证
    person_url = Field()  # 首页链接
    labels = Field()  # 标签
    crawl_time = Field()  # 抓取时间戳

    def init(self):
        self["_id"] = ''
        self["nick_name"] = ''
        self["gender"] = ''
        self["province"] = ''
        self["city"] = ''
        self["brief_introduction"] = ''
        self["birthday"] = ''
        self["sex_orientation"] = ''
        self["sentiment"] = ''
        self["vip_level"] = ''
        self["authentication"] = ''
        self["person_url"] = ''
        self["labels"] = ''

    def get_insert_sql(self):
        sql = r'insert IGNORE into useritem(id, nick_name, gender, province, city,' \
              r' brief_introduction, birthday, tweets_num, follows_num, fans_num, ' \
              r'sex_orientation, sentiment, vip_level, authentication, person_url,' \
              r'labels, crawl_time) ' \
              r'values (%s, %s, %s, %s, %s,' \
              r' %s, %s, %s, %s, %s,' \
              r' %s, %s, %s, %s, %s,' \
              r'%s, %s)'

        params = (self["_id"], self["nick_name"], self["gender"], self["province"], self["city"],
                  self["brief_introduction"], self["birthday"], int(self["tweets_num"]), int(self["follows_num"]),
                  int(self["fans_num"]), self["sex_orientation"], self["sentiment"], self["vip_level"],
                  self["authentication"], self["person_url"], self["labels"], int(self["crawl_time"]))
        return sql, params

class RelationshipItem(Item):
    """ 用户关系，只保留与关注的关系 """
    _id = Field()
    fan_id = Field()  # 关注者,即粉丝的id
    followed_id = Field()  # 被关注者的id
    crawl_time = Field()  # 抓取时间戳


class CommentItem(Item):
    """
    微博评论信息
    """
    _id = Field()
    comment_user_id = Field()  # 评论用户的id
    content = Field()  # 评论的内容
    weibo_id = Field()  # 评论的微博的id
    created_at = Field()  # 评论发表时间
    like_num = Field()  # 点赞数
    crawl_time = Field()  # 抓取时间戳

    def init(self):
        _id = ''
        content = ''

    def get_insert_sql(self):
        sql = r'insert IGNORE into commentitem(id, comment_user_id, content, weibo_id, created_at,' \
              r' like_num, crawl_time)' \
              r'values (%s, %s, %s, %s, %s,' \
              r'%s, %s)'

        params = (self["_id"], self["comment_user_id"], self["content"], self["weibo_id"], self["created_at"],
                  int(self["like_num"]), int(self["crawl_time"]))
        return sql, params


class RepostItem(Item):
    """
    微博转发信息
    """
    _id = Field()
    user_id = Field()  # 转发用户的id
    content = Field()  # 转发的内容
    weibo_id = Field()  # 转发的微博的id
    created_at = Field()  # 转发时间
    crawl_time = Field()  # 抓取时间戳

    def init(self):
        content = ''

    def get_insert_sql(self):
        sql = r'insert IGNORE into repostitem(user_id, content, weibo_id, created_at,' \
              r'crawl_time)' \
              r'values (%s, %s, %s, %s,' \
              r'%s)'

        params = (int(self["user_id"]), self["content"], self["weibo_id"], self["created_at"],
                  int(self["crawl_time"]))
        return sql, params