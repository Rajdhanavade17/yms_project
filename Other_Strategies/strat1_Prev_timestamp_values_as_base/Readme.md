
# Approach:
Shareholdings and base values are read from a shares CSV file, which includes a list of stock names and their respective share counts.

Market data is loaded from another CSV file, filtered for NSECM exchange stocks excluding BANKNIFTY itself.

The total stock value per timestamp is calculated by multiplying share counts with last traded prices (ltp).

The true Bank Nifty index price is extracted from market data.

The constructed Bank Nifty index is calculated iteratively, using a rolling formula that references the previous timestamp’s total stock value and previous Bank Nifty price as the base for the current timestamp calculation:

constructed_price:
constructed_price_t = (total_stock_value_t / total_stock_value_{t-1}) * index_price_{t-1}

For each timestamp `t`, the previous timestamp `t-1`'s total stock valuation and index price are used as the base values to compute the index at `t`.

Previous total value and Bank Nifty price are stored in the shares CSV file as special entries (prev_total_value, prev_total_price) for use as base values in the next run, ensuring seamless rolling continuation over multiple runs.

The calculation outputs a CSV file containing timestamps, true Bank Nifty prices, and the constructed index values.
