# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os

# Get directory one up from settings
ROOT_PATH = os.path.abspath(os.path.dirname(__file__)) or os.getcwd()

BOT_NAME = 'tutorial'

SPIDER_MODULES = ['tutorial.spiders']
NEWSPIDER_MODULE = 'tutorial.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tutorial (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
    'tutorial.pipelines.BwPipeline': 300,
}

#
# LOG
#
LOG_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '..', 'logs'))
LOG_ENABLED = False # Logging is set in Spider init
#LOG_FILE = os.path.join(LOG_ROOT, 'bw-public.log')
#LOG_LEVEL = 'INFO' # CRITICAL ERROR WARNING INFO DEBUG

#
# DATA
#
DATA_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '..', 'data'))


#
# Concurrency, Delay
#

#CONCURRENT_REQUESTS_PER_DOMAIN = 3
# Default: 8
# The maximum number of concurrent (ie. simultaneous) requests
# that will be performed to any single domain.

#CONCURRENT_REQUESTS_PER_IP
# Default: 0
# The maximum number of concurrent (ie. simultaneous) requests
# that will be performed to any single IP.
# If non-zero, the CONCURRENT_REQUESTS_PER_DOMAIN setting is ignored,
# and this one is used instead. In other words,
# concurrency limits will be applied per IP, not per domain.

#DOWNLOAD_DELAY
# Default: 0
# The amount of time (in secs) that the downloader should wait
# before downloading consecutive pages from the same spider.
# This can be used to throttle the crawling speed
# to avoid hitting servers too hard. Decimal numbers are supported.
# Example: DOWNLOAD_DELAY = 0.25    # 250 ms of delay
# This setting is also affected by the RANDOMIZE_DOWNLOAD_DELAY setting
# (which is enabled by default).
# By default, Scrapy doesn't wait a fixed amount of time between requests,
# but uses a random interval between 0.5 and 1.5 * DOWNLOAD_DELAY.

#
# AutoThrottle
# http://doc.scrapy.org/en/latest/topics/autothrottle.html
#

#AUTOTHROTTLE_ENABLED = True
# Default: False
# Enables the AutoThrottle extension.

#AUTOTHROTTLE_START_DELAY
# Default: 5.0
# The initial download delay (in seconds).

#AUTOTHROTTLE_MAX_DELAY
# Default: 60.0
# The maximum download delay (in seconds) to be set in case of high latencies.

#AUTOTHROTTLE_DEBUG
# Default: False
# Enable AutoThrottle debug mode which will display stats
# on every response received, so you can see how the throttling parameters
# are being adjusted in real time.

