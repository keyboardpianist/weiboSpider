# -*- coding: utf-8 -*-

BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = False

# change cookie to yours
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': 'HXVuDbETrDV6PUJbktANLUPSkW1NQyG3IiZLQU-_1LW4mAkoGGr0IdyIfV1E; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFaR.3G5ZyJdDoMyLO_0rk05NHD95QNSh-4eoefeKzfWs4Dqcjai--ciKL2iKnEi--RiKy2iKn4i--fiK.ci-zfi--fiK.ci-zfi--fiK.ci-zfMcnt; SSOLoginState=1610964747'}

CONCURRENT_REQUESTS = 1

DOWNLOAD_DELAY = 3

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,
}

ITEM_PIPELINES = {
#    'pipelines.MongoDBPipeline': 300,
    'pipelines.MySQLDBPipline': 300,
}

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017

MYSQL_HOST = 'localhost'
MYSQL_DB = 'microblog'
MYSQL_USER = 'root'
MYSQL_PASSWD = ''
MYSQL_PORT = 3306
MYSQL_CHARSET = 'utf8'


JOBDIR='./job.mem'

# 是否启用日志
LOG_ENABLED=True

# 日志使用的编码
LOG_ENCODING='utf-8'

# 日志文件(文件名)
LOG_FILE='./log.log'

# 日志格式
LOG_FORMAT='%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# 日志时间格式
LOG_DATEFORMAT='%Y-%m-%d %H:%M:%S'

# 日志级别 CRITICAL, ERROR, WARNING, INFO, DEBUG
LOG_LEVEL='INFO'

# 如果等于True，所有的标准输出（包括错误）都会重定向到日志，例如：print('hello')
LOG_STDOUT=False

# 如果等于True，日志仅仅包含根路径，False显示日志输出组件
LOG_SHORT_NAMES=False
