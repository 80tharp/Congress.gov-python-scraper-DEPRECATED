import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import requests
# Enables easier troubleshooting
pd.options.display.max_colwidth = 100
# Format is 'YYYY-MM-DD' 'YYYY-MM-DD' 'task you want'
START_DATE = '2021-12-01'
END_DATE = '2022-06-01'
TASK = 'PRAYER'
# Converts date string to proper datetime format
START_DATE = datetime.strptime(START_DATE, "%Y-%m-%d").date()
END_DATE = datetime.strptime(END_DATE, "%Y-%m-%d").date()
day = START_DATE.strftime('%d')
month = START_DATE.strftime('%m')
year = START_DATE.strftime('%Y')
URL_TEMPLATE = 'https://www.congress.gov/congressional-record/{}/{}/{}/senate-section'
# Connects years to session for url creation
session_dict = {'congress':
                # This is required to build URLs as years are converted to the index below
                [104, 104, 105, 105, 106, 106, 107, 107, 108, 108, 109, 109, 110, 110, 111, 111, 112, 112, 113, 113,
                 114, 114, 115, 115, 116, 116, 117, 117, 118, 118],
                'year':
                ['1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006',
                 '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
                 '2020', '2021', '2022', '2023', '2024']}
# Builds URL and returns parsed HTML data. Adds columns for date, section, page
URL = URL_TEMPLATE.format(year, month, day)
html_doc = requests.get(URL).text
soup = BeautifulSoup(html_doc, 'html.parser')
print(soup)
table = soup.find_all(class_='item_table')
df = pd.read_html(str(table), na_values=['---'], header=0)[0]
df.drop(df.shape[0] - 1, inplace=True)
df.columns = ['section', 'page']
df['date'] = START_DATE
# Parses records to return task keys used in later urls
parse_key = df['section'].str.split('.', n=1, expand=True)
df['item'] = parse_key[0]
df['task_dirty'] = parse_key[1]
df.drop(columns=['section'], inplace=True)
# Solves formatting differences in 1996-2005 records urls then parses url data
left_limit = datetime.strptime('1996', "%Y").date()
right_limit = datetime.strptime('2005', "%Y").date()
if left_limit < START_DATE < right_limit:
    parse_record2 = df['task_dirty'].str.split('|', n=1, expand=True)
    df['task'] = parse_record2[0]
    df.drop(columns=['task_dirty'], inplace=True)
else:
    parse_section = df['task_dirty'].str.split(';', n=1, expand=True)
    df['task'] = parse_section[0]
    df['record_dirty'] = parse_section[1]
    df.drop(columns=['task_dirty'], inplace=True)
    parse_record1 = df['record_dirty'].str.split('Record', n=1, expand=True)
    df['record_dirty1'] = parse_record1[1]
    parse_record2 = df['record_dirty1'].str.split('|', n=1, expand=True)
    df['record'] = parse_record2[0]
    df.drop(columns=['record_dirty'], inplace=True)
    df.drop(columns=['record_dirty1'], inplace=True)
# Creates URL specific to the task input
session_df = pd.DataFrame(data=session_dict)
session_df.set_index('year', inplace=True)
session_df = session_df.loc[year]
SESS = session_df[0]
SESS = str(SESS)
line = df[df['task'].str.contains(TASK, case=False)]
url_date = (year + '-' + month + '-' + day), (year + '/' + month + '/' + day)
# Simplifies url builds
url_core = 'https://www.congress.gov/'
if left_limit < START_DATE < right_limit:
    url2 = url_core + 'crec/' + url_date[1] + '/modified/CREC-' + url_date[2] + '-pt1-Pg' + line['page'] + '-' + line['item']+'.htm'
else:
    url2 = url_core + SESS + '/crec/' + url_date[1] + '/modified/CREC-' + url_date[2] + '-pt1-Pg' + line['page'] + '-' + line['item'] + '.htm'
# Prepares url for use in request/bs scraping
URL2_STR = str(url2)
URL2_STR = URL2_STR[1:-14]
URL2_STR = URL2_STR.strip()
# Scrapes new url for required text
html_doc2 = requests.get(URL2_STR).text
soup2 = BeautifulSoup(html_doc2, 'html.parser')
# Cleans everything and prints
TASK_TXT = str(soup2)
TASK_TXT = re.split(TASK, TASK_TXT, 1, flags=re.IGNORECASE)
print(TASK_TXT)
