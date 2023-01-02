#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import timedelta
import json
import datetime
import os
import re
import sys
import getopt

try:
  from urllib.request import Request, urlopen
except ImportError:  # python 2
  from urllib2 import Request, urlopen

try:
  import urllib.parse as urlParse
except ImportError: # python 2
  import urllib as urlParse

try:
  # Python 2
  xrange
except NameError:
  # Python 3, xrange is now named range
  xrange = range

__author__ = 'arulraj'

DEFAULT_STOCK_CODE_LIST = [
  "^BSESN",
  "^NSEI",
  "BSE-100.BO",
  "BSE-200.BO",
  "BSE-500.BO",
  "BSE-SMLCAP.BO",
  "BSE-MIDCAP.BO",
  "^NSMIDCP"
]

INTERVAL_REGEX = [r'[0-9]+d', r'[0-9]+m', r'[0-9]+y']

DEFAULT_INTERVAL = ['1M', '3M', '6M']

DEFAULT_HEADER = ["Index", "Current", "Change_pts", "Updated_on"]

API_FOR_CURRENT_STOCK="https://query1.finance.yahoo.com/v7/finance/quote?symbols={0}"

API_FOR_HISTORY_STOCK="https://query1.finance.yahoo.com/v8/finance/chart/{0}?includePrePost=false&interval={1}&useYfid=true&range={2}"

given_intervals = None

# TODO :
# if day greater than 50 convert that to month


class Interval(object):
  """

  """
  def __init__(self, _numeric_, _alphabet_):
    self.alphabet = _alphabet_.upper()
    self.numeric = int(_numeric_)

  @classmethod
  def build(cls, str_value):

    if Interval.is_valid_interval(str_value):
      match_obj = re.search(r"[0-9]+", str_value, re.I)
      numeric = match_obj.group(0)
      match_obj = re.search(r"[dmy]", str_value, re.I)
      alphabet = match_obj.group(0)
      return cls(numeric, alphabet)
    else:
      print("The interval '%s' is not valid" % str_value)

  @staticmethod
  def is_valid_interval(str_interval):
    for i_pattern in INTERVAL_REGEX:
      match_obj = re.match(i_pattern, str_interval, re.IGNORECASE)
      if match_obj:
        return True

  def as_table_header(self):
    return "v_" + str(self)

  def __str__(self):
    return ''.join([str(self.numeric), self.alphabet])

  def __repr__(self):
    return self.__str__()

  def __cmp__(self, other):
    """
    This is will not take difference between 120D and 4M.
    """
    if self.alphabet < other.alphabet:
      return -1
    elif self.alphabet > other.alphabet:
      return 1
    else:
      if self.numeric < other.numeric:
        return -1
      elif self.numeric > other.numeric:
        return 1
      else:
        return 0

  def __eq__(self, other):
    return self.alphabet == other.alphabet and self.numeric == other.numeric

  def __ne__(self, other):
    return self.alphabet != other.alphabet or self.numeric != other.numeric

  def __lt__(self, other):
    if self.alphabet < other.alphabet:
      return True
    elif self.alphabet > other.alphabet:
      return False
    else:
      return self.alphabet == other.alphabet and self.numeric < other.numeric

  def __le__(self, other):
    if self.alphabet < other.alphabet:
      return True
    elif self.alphabet > other.alphabet:
      return False
    else:
      return self.alphabet == other.alphabet and self.numeric <= other.numeric

  def __gt__(self, other):
    if self.alphabet > other.alphabet:
      return True
    elif self.alphabet < other.alphabet:
      return False
    else:
      return self.alphabet == other.alphabet and self.numeric > other.numeric

  def __ge__(self, other):
    if self.alphabet > other.alphabet:
      return True
    elif self.alphabet < other.alphabet:
      return False
    else:
      return self.alphabet == other.alphabet and self.numeric >= other.numeric

  def __repr__(self):
    return "%s%s" % (self.numeric, self.alphabet)

class Quote(object):
  """
  Referred from http://trading.cheno.net/downloading-google-intraday-historical-data-with-python/
  """
  def __init__(self, symbol, exchange=''):
    self.symbol = symbol
    self.exchange = exchange
    self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = ([] for _ in range(7))

  def append(self, dt, open_, high, low, close, volume):
    self.date.append(dt.date())
    self.time.append(dt.time())
    self.open_.append(float(open_))
    self.high.append(float(high))
    self.low.append(float(low))
    self.close.append(float(close))
    self.volume.append(int(volume))

  def to_csv(self):
    return ''.join(["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(self.symbol,
                                                                              self.date[bar].strftime('%Y-%m-%d'),
                                                                              self.time[bar].strftime('%H:%M:%S'),
                                                                              self.open_[bar], self.high[bar],
                                                                              self.low[bar], self.close[bar],
                                                                              self.volume[bar])
                  for bar in xrange(len(self.close))])

  def __str__(self):
    return self.to_csv()

  def __repr__(self):
    return self.to_csv()


class Color(object):
  """
  reference from https://gist.github.com/Jossef/0ee20314577925b4027f and modified bit.
  """

  def __init__(self, text, **user_styles):

    styles = {
      # styles
      'reset': '\033[0m',
      'bold': '\033[01m',
      'disabled': '\033[02m',
      'underline': '\033[04m',
      'reverse': '\033[07m',
      'strike_through': '\033[09m',
      'invisible': '\033[08m',
      # text colors
      'fg_black': '\033[30m',
      'fg_red': '\033[31m',
      'fg_green': '\033[32m',
      'fg_orange': '\033[33m',
      'fg_blue': '\033[34m',
      'fg_purple': '\033[35m',
      'fg_cyan': '\033[36m',
      'fg_light_grey': '\033[37m',
      'fg_dark_grey': '\033[90m',
      'fg_light_red': '\033[91m',
      'fg_light_green': '\033[92m',
      'fg_yellow': '\033[93m',
      'fg_light_blue': '\033[94m',
      'fg_pink': '\033[95m',
      'fg_light_cyan': '\033[96m',
      # background colors
      'bg_black': '\033[40m',
      'bg_red': '\033[41m',
      'bg_green': '\033[42m',
      'bg_orange': '\033[43m',
      'bg_blue': '\033[44m',
      'bg_purple': '\033[45m',
      'bg_cyan': '\033[46m',
      'bg_light_grey': '\033[47m'
    }

    self.color_text = ''
    for style in user_styles:
      try:
        self.color_text += styles[style]
      except KeyError:
        raise KeyError('def color: parameter `{}` does not exist'.format(style))

    self.color_text += text

  def __format__(self):
    return '{}\033[0m\033[0m'.format(self.color_text)

  @classmethod
  def red(clazz, text):
    cls = clazz(text, bold=True, fg_red=True)
    return cls.__format__()

  @classmethod
  def orange(clazz, text):
    cls = clazz(text, bold=True, fg_orange=True)
    return cls.__format__()

  @classmethod
  def green(clazz, text):
    cls = clazz(text, bold=True, fg_green=True)
    return cls.__format__()

  @classmethod
  def custom(clazz, text, **custom_styles):
    cls = clazz(text, **custom_styles)
    return cls.__format__()

def get_current_stock_info():
  """

  :return:
  """
  symbol_list = ','.join([stock for stock in given_stock_codes])
  stocks_url = API_FOR_CURRENT_STOCK.format(symbol_list)
  return get_content(stocks_url)


def get_history_stock_info(stock_name, interval, _range):
  """
  :param stock_name:
  :param interval:
  :param _range:
  :return:
  """
  stock_name = stock_name.upper()
  url_string = API_FOR_HISTORY_STOCK.format(stock_name, interval, _range)
  json_content = json.loads(get_content(url_string))

  chart_result = None
  if json_content and json_content["chart"] and json_content["chart"]["result"] and json_content["chart"]["result"][0]:
    chart_result = json_content["chart"]["result"][0]

  timestamp_list = None
  open_list = None
  close_list = None
  high_list = None
  low_list = None
  volume_list = None
  if chart_result:
    timestamp_list = chart_result["timestamp"]
    open_list = chart_result["indicators"]["quote"][0]["open"]
    close_list = chart_result["indicators"]["quote"][0]["close"]
    high_list = chart_result["indicators"]["quote"][0]["high"]
    low_list = chart_result["indicators"]["quote"][0]["low"]
    volume_list = chart_result["indicators"]["quote"][0]["volume"]

  quotes = []

  if timestamp_list and open_list and close_list and high_list and low_list and volume_list:
    for (dt, open_, high, low, close, volume) in zip(timestamp_list, open_list, high_list, low_list, close_list, volume_list):
      q = Quote(stock_name)
      if dt != None and open_ != None and high != None and low != None and close != None and volume != None:
        q.append(datetime.datetime.fromtimestamp(dt), '{0:.2f}'.format(open_), '{0:.2f}'.format(high), '{0:.2f}'.format(low), '{0:.2f}'.format(close), volume)
        quotes.append(q)
  return quotes


def stock_low_high_info(intervals):
  """

  :param intervals:
  :return:
  """
  stock_low_high_dict = dict()

  from datetime import datetime

  now = datetime.now()

  for stock_code in given_stock_codes:
    stock_name = urlParse.unquote(stock_code)
    _range = str(intervals[-1])
    if intervals[-1].alphabet == "D":
      _range = _range.lower()
    if intervals[-1].alphabet == "M":
      _range = _range.lower().replace("m", "mo")
    if intervals[-1].alphabet == "Y":
      _range = _range.lower()
    quotes = get_history_stock_info(stock_name, "1d", _range)

    high_low_dict = dict()

    for interval in intervals:
      interval_time = None
      if interval.alphabet == "D":
        interval_time = daydelta(now, -interval.numeric)
      elif interval.alphabet == "M":
        interval_time = monthdelta(now, -interval.numeric)
      elif interval.alphabet == "Y":
        interval_time = yeardelta(now, -interval.numeric)

      quotes_in_interval = [q for q in quotes if q.date[0] > interval_time.date()]
      sort_by_close = sorted(quotes_in_interval, key=lambda x: x.close)

      if len(sort_by_close) > 0:
        high_low_dict[str(interval)] = {"low": sort_by_close[0].close[0],
                                        "high": sort_by_close[len(sort_by_close) - 1].close[0]}

    if len(high_low_dict.keys()) > 0:
      stock_low_high_dict[stock_name] = high_low_dict

  return stock_low_high_dict


def get_content(url):
  """
  Get content of url as string
  :return:
  """
  req = Request(url)
  resp = urlopen(req)
  return resp.read().decode('ascii', 'ignore').strip()


def parse_content(content):
  """
  Combine current stock info and history stock information into StockInfo object.

  :param content:
  :return:
  """
  stock_resp_list = list()
  json_content = json.loads(content)
  if json_content and json_content["quoteResponse"] and json_content["quoteResponse"]["result"]:
    stock_resp_list = json_content["quoteResponse"]["result"]

  interval_list = list()
  sorted_interval_list = list()
  table_header_list = list()

  for i in given_intervals:
    interval = Interval.build(i)
    if interval:
      interval_list.append(interval)

  sorted_interval_list = sorted(interval_list)
  for interval in sorted_interval_list:
      table_header_list.append(interval.as_table_header())

  stock_high_low_dict = dict()
  if len(sorted_interval_list) > 0:
    stock_high_low_dict = stock_low_high_info(sorted_interval_list)

  DEFAULT_HEADER.extend(table_header_list)

  StockInfo = namedtuple("StockInfo", DEFAULT_HEADER)

  list_stock = list()
  for stock_resp in stock_resp_list:

    stock_high_low = dict()
    if stock_resp["symbol"] in stock_high_low_dict:
      stock_high_low = stock_high_low_dict[stock_resp["symbol"]]

    i_high_low_list = list()
    for interval in sorted_interval_list:
      i_high_low_value = ""
      if str(interval) in stock_high_low:
        i_high_low = stock_high_low[str(interval)]
        i_high_low_value = "⇓ %s, ⇑ %s" % (i_high_low["low"], i_high_low["high"])
      i_high_low_list.append(i_high_low_value)

    stock_updated_on = datetime.datetime.fromtimestamp(stock_resp["regularMarketTime"], tz=datetime.timezone(datetime.timedelta(milliseconds=stock_resp["gmtOffSetMilliseconds"]))).strftime("%b %d, %I:%M%p %Z")
    stock_value = '{0:.2f}'.format(stock_resp["regularMarketPrice"])
    stock_change_value = '{0:.2f}'.format(stock_resp["regularMarketChange"])
    stock_change_percent = '{0:.2f}'.format(stock_resp["regularMarketChangePercent"])

    isPositive = True if stock_change_percent != None and float(stock_change_percent) > 0 else False

    colored_stock_change_percent = stock_change_percent+"%"
    if isPositive:
      colored_stock_change_percent = Color.green(stock_change_percent+"%")
    else:
      colored_stock_change_percent = Color.red(stock_change_percent+"%")

    stockInfo = StockInfo(stock_resp["shortName"], stock_value, "%s(%s)" % (stock_change_value, colored_stock_change_percent), stock_updated_on, *i_high_low_list)
    list_stock.append(stockInfo)
  return list_stock


def nonAsciiStrLength(text):
  return len(str(removeAscii(text)))

def removeAscii(text):
  return re.compile(r'\x1b[^m]*m').sub('', text)

def pprinttable(rows):
    """
    Referred From http://stackoverflow.com/a/5910078/458701 and modified bit to support UTF-8

    :param rows:
    :return:
    """
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        lensWithAscii = []
        for i in range(len(rows[0])):
          lens.append(len(max([str(removeAscii(x[i])) for x in rows] + [headers[i]], key=lambda x: len(str(x)))))
          lensWithAscii.append(len(max([str(x[i]) for x in rows] + [headers[i]], key=lambda x: len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
          if isinstance(rows[0][i], int):
            formats.append("%%%dd" % lensWithAscii[i])
          else:
            formats.append("%%-%ds" % lensWithAscii[i])
          hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        print(hpattern % tuple(headers))
        print(separator)
        _u = lambda t: t if isinstance(t, str) else t
        for line in rows:
          print(pattern % tuple(_u(t) for t in line))
    elif len(rows) == 1:
      row = rows[0]
      hwidth = len(max(row._fields, key=lambda x: len(x)))
      for i in range(len(row)):
        print("%*s = %s" % (hwidth, row._fields[i], row[i]))


def monthdelta(date, delta):
    """

    :param date: datetime object
    :param delta: negative value will subtract from given date. positive value will add from given date.
    :return:
    """
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m: m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def daydelta(date, delta):
    """

    :param date: datetime object
    :param delta: negative value will subtract from given date. positive value will add from given date.
    :return:
    """
    return date + timedelta(hours=24 * delta)


def yeardelta(date, delta):
    """

    :param date: datetime object
    :param delta: negative value will subtract from given date. positive value will add from given date.
    :return:
    """
    return date + timedelta(weeks=52 * delta)


if __name__ == "__main__":
  """
  How to use
  - Copy this into /usr/local/bin folder as 'stockinfo'
  - chmod +x /usr/local/bin/stockinfo
  - Run `stockinfo` as command from anywhere in your terminal
  - Detailed info
      - stockinfo -i 5d,1m,3m,6m,1y
  """

  # To work ANSI escape sequences in windows.
  os.system('color')

  given_intervals = list()
  given_stock_codes = DEFAULT_STOCK_CODE_LIST

  try:
    myopts, args = getopt.getopt(sys.argv[1:], "s:i:")
  except getopt.GetoptError as e:
    print (str(e))
    print("Usage: %s -i intervals. For ex: %s -i 5D,1M,1Y" % (sys.argv[0], sys.argv[0]))
    sys.exit(2)

  for o, a in myopts:
    a_list = [s.strip() for s in str(a).upper().split(',')]
    if o == '-i':
      given_intervals = a_list
    if o == '-s':
      given_stock_codes = a_list

  json_content = get_current_stock_info()
  stock_info_list = parse_content(json_content)
  pprinttable(stock_info_list)
