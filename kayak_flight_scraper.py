# @Time    : 2021/04/09 
# @Author  : alexanderdutchak@gmail.com
# @Software: PyCharm

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 8)

depart = 'DEN'
destinations = ['IAD', 'DCA', 'BWI']
dates = ['2021-04-14', '2021-04-15', '2021-04-16', '2021-04-17']

final_df = pd.DataFrame({'depart_from': [],
                         'arrive_at': [],
                         'date': [],
                         'depart_time': [],
                         'arrival_time': [],
                         'price': [],
                         'airline': [],
                         'flight_duration': []})

for destination in destinations:

    time.sleep(10)

    for date in dates:

        url = f'https://www.kayak.com/flights/{depart}-{destination}/{date}?sort=price_a'

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.implicitly_wait(20)
        driver.get(url)

        time.sleep(20)

        soup = BeautifulSoup(driver.page_source, 'lxml')

        # departure times
        d_times_lst = []
        d_times = soup.findAll('span', attrs={'class': 'depart-time base-time'})
        for tm1 in d_times:
            d_times_lst.append(tm1.text)

        # arrival times
        a_times_lst = []
        a_times = soup.findAll('span', attrs={'class': 'arrival-time base-time'})
        for tm2 in a_times:
            a_times_lst.append(tm2.text)

        # prices
        price_lst = []
        price_tag = re.compile('Common-Booking-MultiBookProvider(.*) Theme-featured-large(.*) multi-row(.*)')
        prices = soup.findAll('div', attrs={'class': price_tag})
        for price in prices:
            price_lst.append(price.text.split('\n')[4].strip())

        # airlines
        airline_lst = []
        airlines = soup.findAll('div', attrs={'class': 'bottom', 'dir': 'ltr'})
        for airline in airlines:
            airline_lst.append(airline.text.replace('\n', ''))

        # durations
        duration_lst = []
        durations = soup.findAll('div', attrs={'class': 'section duration allow-multi-modal-icons'})
        for duration in durations:
            duration_lst.append(' '.join(duration.text.split(' ')[:2]).replace('\n', ''))

        df = pd.DataFrame({'depart_from': depart,
                           'arrive_at': destination,
                           'date': date,
                           'depart_time': d_times_lst[:15],
                           'arrival_time': a_times_lst[:15],
                           'price': price_lst[:15],
                           'airline': airline_lst[:15],
                           'flight_duration': duration_lst[:15]})

        final_df = pd.concat([final_df, df], ignore_index=True, sort=False)

        driver.close()

        time.sleep(20)

final_df.to_csv('kayak_flight_data.csv')
