#!/usr/bin/env python

import sys
import time

import requests
from bs4 import BeautifulSoup

import settings


def parse_page_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    page_info = soup.find('li', {'class': 'page-count'}).find('span').text
    current_page = int(page_info.split()[0])
    page_count = int(page_info.split()[2])
    return current_page, page_count


def parse_table_headers(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table ucpd'})
    header = table.find('thead')
    column_names = header.find('tr').text.strip().split('\n')
    return column_names


def parse_table_rows(html):
    """
    Return the data rows contained in the input html, as
    a list of lists.
    """
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table ucpd'})
    rows = table.find('tbody').findAll('tr')

    result_set = []
    for row in rows:
        cols = row.findAll('td')
        result_set.append([col.text for col in cols])
    return result_set


def get_single_page(url, start_date, end_date, offset, headers=False, attempts=3):
    """
    Retrieve a page of data rows from the UCPD site. The site only
    returns a handful of rows at a time, currently 5 (see settings).

    url: base URL to hit without any parameters (see settings file)
    start_date: see settings file
    end_date: see settings file
    offset: determines which page of results to request
    headers: whether to include column names as the first row
    attempts: how many attempts to make before giving up in case of
              errors

    Returns a tuple of (rows, current_page, page_count)
    """
    params = {
        'startDate': start_date,
        'endDate': end_date,
        'offset': offset
    }

    r = None
    for i in range(attempts):
        try:
            r = requests.get(url, params=params, timeout=5)
        except Exception as e:
            print "Error making request (attempt %d/%d): %s" % (i+1, attempts, e)
            continue
        else:
            if r.status_code == 200:
                break
    if r is None:
        raise RuntimeError

    html = r.text
    current_page, page_count = parse_page_info(html)
    rows = parse_table_rows(html)
    if headers:
        rows = [parse_table_headers(html)] + rows
    return rows, current_page, page_count


def write_to_file(filename, rows):
    with open(filename, 'a') as f:
        for row in rows:
            if len(row) > 1 and "NO TRAFFIC STOPS" not in row[0].upper():
                f.write('\t'.join(row) + '\n')


def main():
    offset = 0
    while True:
        try:
            rows, current_page, page_count = get_single_page(
                url=settings.URL,
                start_date=settings.START_DATE,
                end_date=settings.END_DATE,
                offset=offset,
                headers=(offset == 0)  # only include headers with the first page
            )
        except:
            print "Unable to retrieve page, exiting."
            return 1

        print "Retrieved page %d of %d" % (current_page, page_count)
        write_to_file(settings.OUTPUT_FILE_PATH, rows)

        if current_page == page_count:
            break

        offset += settings.ROWS_PER_PAGE
        time.sleep(settings.REQUEST_DELAY)


if __name__ == "__main__":
    sys.exit(main())
