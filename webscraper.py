#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import time
import datetime

now = datetime.datetime.now()
start_date = '06%2F01%2F2015'  # inputting earlier date results in error
end_date = now.strftime('%m%%2F%d%%2F%y')

base_url = ('https://incidentreports.uchicago.edu/' +
            'trafficStopsArchive.php?' +
            'startDate=%s&endDate=%s' % (start_date, end_date))

offset = 0
records = []
while True:
    url = base_url + '&offset=%d' % offset
    html = requests.get(url, timeout=5.1).text
    soup = BeautifulSoup(html, 'html.parser')

    page_info = soup.find('li', {'class': 'page-count'}).find('span').text
    current_page = int(page_info.split()[0])
    page_count = int(page_info.split()[2])
    print "Requesting page %d" % current_page

    table = soup.find('table', {'class': 'table ucpd'})
    if offset == 0:
        header = table.find('thead')
        column_names = header.find('tr').text.strip().split('\n')
    data_rows = table.find('tbody').findAll('tr')
    for row in data_rows:
        records.append([td.text for td in row.findAll('td')])

    if current_page == page_count:
        break

    offset += 5
    time.sleep(0.5)

with open('data/trafficstops.%s.tsv' % now.strftime('%Y%m%d%H%M%S'), 'w') as f:
    f.write('\t'.join(column_names) + '\n')
    for record in records:
        if len(record) > 1 and "NO TRAFFIC STOPS" not in record[0].upper():
            f.write('\t'.join(record) + '\n')

