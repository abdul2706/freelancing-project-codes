import os
import time
import pandas as pd

from tqdm import tqdm
from urllib import parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def expand_number(str_num):
    postfix = str_num[-1] if str_num[-1] in ['K', 'M'] else ''
    num = float(str_num[:-1]) if str_num[-1] in ['K', 'M'] else float(str_num)
    if postfix == 'K':
        num = num * 1e3
    elif postfix == 'M':
        num = num * 1e6
    return int(num)

def scrap_videos_div(following, followers, likes):
    TAG = '[scrap_videos_div]'
    columns = ['username', 'following', 'followers', 'likes', 'video_views', 'video_link', 'scrap_date', 'scrap_time']
    if os.path.exists(USER_PAGE_DATA_CSV_PATH):
        df_user_page_data = pd.read_csv(USER_PAGE_DATA_CSV_PATH)
    else:
        df_user_page_data = pd.DataFrame(columns=columns)
    
    # get links of all videos on page loaded so far
    videos_div = driver.find_elements(By.CSS_SELECTOR, 'div.tiktok-x6y88p-DivItemContainerV2.e1z53d07')
    print(TAG, '[videos_div]', len(videos_div))
    new_rows = {'video_views': [], 'video_link': [], 'scrap_date': [], 'scrap_time': []}
    for i, video_div in tqdm(enumerate(videos_div), total=len(videos_div)):
        video_link_tag = video_div.find_element(By.CSS_SELECTOR, 'a')
        video_link = video_link_tag.get_attribute('href').strip()
        if not df_user_page_data['video_link'].str.contains(video_link).any():
            video_views_tag = video_div.find_element(By.CSS_SELECTOR, 'strong.video-count.tiktok-1p23b18-StrongVideoCount.eor0hs42')
            video_views = expand_number(video_views_tag.text.strip())
            current_datetime = pd.Timestamp(time.time(), unit='s', tz=TIMEZONE)
            new_rows['video_views'].append(video_views)
            new_rows['video_link'].append(video_link)
            new_rows['scrap_date'].append(current_datetime.date())
            new_rows['scrap_time'].append(current_datetime.time())

    new_rows = pd.DataFrame(new_rows)
    new_rows['username'] = username
    new_rows['following'] = following
    new_rows['followers'] = followers
    new_rows['likes'] = likes
    print(TAG, '[new_rows]', new_rows.shape)
    df_user_page_data = pd.concat([df_user_page_data, new_rows], ignore_index=True)
    df_user_page_data.to_csv(USER_PAGE_DATA_CSV_PATH, index=False)
    print(TAG, '[df_user_page_data]\n', df_user_page_data)

def scrap_user_page(username):
    TAG = '[scrap_user_page]'
    URL = parse.urljoin(BASE_URL, '@' + username)
    print(TAG, '[URL]', URL)
    scroll_retry_counter = 0
    loop_counter = 0
    consecutive_same_height = False
    driver.get(URL)

    channel_stats = driver.find_elements(By.CSS_SELECTOR, 'div.tiktok-xeexlu-DivNumber.e1awr0pt1')
    print('[channel_stats]', len(channel_stats))
    for i, channel_stat in enumerate(channel_stats):
        text = channel_stat.text.replace('\n', ' ')
        print(i, '[channel_stat.text]', text)
        if 'following' in text.lower():
            following = expand_number(text.split(' ')[0].strip())
        elif 'followers' in text.lower():
            followers = expand_number(text.split(' ')[0].strip())
        elif 'likes' in text.lower():
            likes = expand_number(text.split(' ')[0].strip())

    # get scroll height
    last_height = driver.execute_script('return document.body.scrollHeight')
    while scroll_retry_counter < SCROLL_RETRIES:
        # scroll down to bottom
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script('return document.body.scrollHeight')
        
        # this condition indicates two things:
        # 1. end of page is reached, so all videos are loaded
        # 2. page is still loading, so give another try until loop condition is true
        if new_height == last_height:
            scroll_retry_counter += 1
            print(TAG, '[scroll_retry_counter]', scroll_retry_counter)

            if not consecutive_same_height:
                scrap_videos_div(following, followers, likes)
                consecutive_same_height = True
        else:
            consecutive_same_height = False
        
        if loop_counter % 25 == 0:
            scrap_videos_div(following, followers, likes)
            # print(TAG, 'breaking out of while loop')
            # break

        last_height = new_height
        loop_counter += 1

print('[starts]')

SCROLL_RETRIES = 10
SCROLL_PAUSE_TIME = 5
TIMEZONE = 'US/Eastern'
BASE_URL = f'https://www.tiktok.com'
BASE_PATH = 'scrapped-data'
if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)
USER_PAGE_DATA_CSV_PATH = os.path.join(BASE_PATH, 'df_user_page_data.csv')

usernames = ['fernandassep', 'omfgitsrama', 'laslocurasdeleoyara']
service = Service('/Users/abdulrehmankhan/Programs/chromedriver')
options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('start-maximized')
# options.add_argument('--start-fullscreen')
driver = webdriver.Chrome(service=service, options=options)
driver.set_window_rect(290, 0, 1150, 800)

for username in usernames:
    scrap_user_page(username)

print('[end]')
