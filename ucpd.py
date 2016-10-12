#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import time
import datetime

now = datetime.datetime.now()
start_date = '06%2F01%2F2015'  # inputting earlier date results in error
end_date = '%s%%2F%s%%2F%s' % (now.strftime('%m'), now.strftime('%d'), now.strftime('%y'))

base_url = ('https://incidentreports.uchicago.edu/' +
            'trafficStopsArchive.php?startDate=%s&endDate=%s' % (start_date, end_date))

offset = 0
records = []
while True:
    url = base_url + '&offset=%d' % offset
    html = requests.get(url, timeout=3.1).text
    soup = BeautifulSoup(html)
    page = soup.find('li', {'class': 'page-count'}).find('span').text
    current_page, page_count = (int(page.split()[0]), int(page.split()[2]))
    print "Requesting page %d" % current_page

    table = soup.find('table', {'class': 'table ucpd'})
    if offset == 0:
        header = table.find('thead')
        columns = header.find('tr').text.strip().split('\n')
    body = table.find('tbody')
    rows = body.findAll('tr')
    for row in rows:
        records.append([td.text for td in row.findAll('td')])
    print "Total records: %d" % len(records)

    if current_page == page_count:
        break
    offset += 5
    time.sleep(0.5)

with open('trafficstops.csv', 'w') as f:
    f.write(','.join(columns) + '\n')
    for record in records:
        f.write(','.join(record) + '\n')

