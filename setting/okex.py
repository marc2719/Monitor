from os import path as os_path
from sys import path as sys_path
from datetime import datetime, timedelta
from configparser import ConfigParser


# 时差
time_difference = timedelta(hours=8)

# 当前时间
def current_datetime():
    return datetime.now() + time_difference

BASE_DIR = os_path.abspath(os_path.dirname(os_path.dirname(__file__)))
sys_path.append(BASE_DIR)
configure_file = f'{BASE_DIR}/conf/configure.json'
sql_json_file = f'{BASE_DIR}/db/sql.json'
log_dir = f'{BASE_DIR}/log/'

config = ConfigParser()
config.read(filenames=f'{BASE_DIR}/setting/config.ini', encoding='utf-8')

# access
access = config['access']
access_key = access.get('access_key')
access_pass_phrase = access.get('access_pass_phrase')
access_secret_key = access.get('access_secret_key')

# url
url = config['url']
web_site = url.get('web_site')
link_v5_time = url.get('link_v5_time')

# mysql
mysql = config['mysql']
mysql_host = mysql.get('mysql_host')
mysql_port = int(mysql.get('mysql_port'))
database = mysql.get('database')
mysql_user = mysql.get('mysql_user')
mysql_password = mysql.get('mysql_password')
mysql_charset = mysql.get('mysql_charset')

#ticker
ticker = config['ticker']
TICKER_MAX_COUNT = int(ticker.get('ticker_max_count'))
sleep_sec = int(ticker.get('sleep_sec'))
