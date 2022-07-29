import os
import pandas as pd

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

def scrap_video_page(df_user_page_data):
    TAG = '[scrap_video_page]'
    columns = ['username', 'following', 'followers', 'likes', 'video_views', 'video_link', 'scrap_date', 'scrap_time', 'video_description', 'video_likes', 'video_comments', 'video_shares']
    mapping = {'like-count': 'video_likes', 'comment-count': 'video_comments', 'share-count': 'video_shares'}
    if os.path.exists(TIKTOK_SCRAP_DATA_CSV_PATH):
        df_tiktok_scrap_data = pd.read_csv(TIKTOK_SCRAP_DATA_CSV_PATH)
    else:
        df_tiktok_scrap_data = pd.DataFrame(columns=columns)
    print(TAG, '[df_tiktok_scrap_data]', df_tiktok_scrap_data)
    new_rows = {key: [] for key in columns}
    for idx, row in df_user_page_data.iterrows():
        video_link = row['video_link']
        print(TAG, '[idx]', idx, '[video_link]', video_link)
        if not df_tiktok_scrap_data['video_link'].str.contains(video_link).any():
            # copy relevant data from df_user_page_data
            user_page_data_row = df_user_page_data.loc[df_user_page_data['video_link'] == video_link]
            for col in user_page_data_row.columns:
                value = user_page_data_row[col].values.tolist()
                value = value[0] if type(value) is list else value
                new_rows[col].append(value)
            
            # goto video_link
            driver.get(video_link)
            # get video description
            video_container = driver.find_element(By.CSS_SELECTOR, 'div.tiktok-10gdph9-DivContentContainer.e1eulw5o1')
            video_description = video_container.find_element(By.CSS_SELECTOR, 'div.tiktok-1ejylhp-DivContainer.e11995xo0')
            new_rows['video_description'].append(repr(video_description.text))
            # get video statistics
            video_stats_divs = video_container.find_elements(By.CSS_SELECTOR, 'strong.tiktok-1y2yo26-StrongText.e1bs7gq22')
            for i, video_stat_div in enumerate(video_stats_divs):
                video_stat_text = video_stat_div.text.strip()
                video_stat_text = expand_number(video_stat_text) if 48 <= ord(video_stat_text[0]) <= 57 else 0
                video_stat_data = video_stat_div.get_attribute('data-e2e')
                new_rows[mapping[video_stat_data]].append(video_stat_text)

        # save csv file after every 100 iterations
        if idx > 0 and idx % 25 == 0:
            new_rows = pd.DataFrame(new_rows, columns=columns)
            print(TAG, '[new_rows]', new_rows.shape)
            df_tiktok_scrap_data = pd.concat([df_tiktok_scrap_data, new_rows], ignore_index=True)
            df_tiktok_scrap_data.to_csv(TIKTOK_SCRAP_DATA_CSV_PATH, index=False)
            new_rows = {key: [] for key in columns}

print('[starts]')

TIMEZONE = 'US/Eastern'
BASE_URL = f'https://www.tiktok.com'
BASE_PATH = 'scrapped-data'
if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)
USER_PAGE_DATA_CSV_PATH = os.path.join(BASE_PATH, 'df_user_page_data.csv')
TIKTOK_SCRAP_DATA_CSV_PATH = os.path.join(BASE_PATH, 'tiktok_scrap_data.csv')

usernames = ['fernandassep', 'omfgitsrama', 'laslocurasdeleoyara']
service = Service('/Users/abdulrehmankhan/Programs/chromedriver')
options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('start-maximized')
# options.add_argument('--start-fullscreen')
driver = webdriver.Chrome(service=service, options=options)
driver.set_window_rect(290, 0, 1150, 800)

if os.path.exists(USER_PAGE_DATA_CSV_PATH):
    df_user_page_data = pd.read_csv(USER_PAGE_DATA_CSV_PATH)
    scrap_video_page(df_user_page_data)
else:
    print(f'{USER_PAGE_DATA_CSV_PATH} does not exists, run script "scrap_user_page.py" before running this script.')

print('[end]')
