Yahoo Finance API
-------------------

* [Yahoo Finance API](#yahoo-finance-api)
  * [Get current Stock](#get-current-stock)
  * [Get history Stock](#get-history-stock)
* [Alternative](#alternative)

## Get current Stock

https://query1.finance.yahoo.com/v7/finance/quote?symbols=^BSESN,bse-100.bo&include=revenue,grossMargin,debtToEquity,currentRatio

symbols = Comma Separated stock code

## Get history Stock

https://query1.finance.yahoo.com/v8/finance/chart/^BSESN?includePrePost=false&interval=1d&range=5d

range = this is to get the history info

# Alternative

Yahoo Finance API alternative for indian stock market

Refer these repo's for NSE/BSE API's to get data

https://github.com/vsjha18/nsetools/blob/master/nse.py

https://github.com/swapniljariwala/nsepy

https://github.com/maanavshah/stock-market-india/blob/master/bse/constant.js
