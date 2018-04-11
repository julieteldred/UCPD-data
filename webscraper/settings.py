# Various settings for the web scraping script.
import datetime
import os

URL = 'https://incidentreports.uchicago.edu/trafficStopsArchive.php'

OUTPUT_FILE = 'trafficstops.tsv'
OUTPUT_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', OUTPUT_FILE))

# how long to wait (in seconds) between each page request
REQUEST_DELAY = 0.5

# this doesn't seem to be configurable
ROWS_PER_PAGE = 5

# inputting earlier date results in error
START_DATE = '06/01/2015'

# today's date in mm/dd/yyyy format
END_DATE = datetime.datetime.now().strftime('%m/%d/%y')
