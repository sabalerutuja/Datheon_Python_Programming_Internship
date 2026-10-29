# Stock Portfolio Performance Tracker

A Python command-line tool that tracks an investment portfolio. Enter your stock tickers, buy prices and share quantities, and it calculates your total portfolio value and the percentage gain or loss per holding. It then saves a summary to a CSV file.

## Features

- Stores portfolio positions in a dictionary (repeat purchases of a ticker are merged using a weighted-average buy price)
- Validates tickers against the S&P 500 dataset (`sp500.csv`)
- Gets current prices from live data via `yfinance`, or from manual entry if live data isn't available
- Calculates invested capital, current market value, and gain/loss in dollars and percent, for each holding and for the whole portfolio
- Prints a formatted table to the console
- Saves the results to `portfolio_summary.csv` with a timestamp and a `TOTAL` row

## Requirements

- Python 3
- `yfinance` (optional, for live prices)

```
python -m pip install yfinance
```

## Usage

1. Put `portfolio.py` and `sp500.csv` in the same folder.
2. Run the script:

```
python portfolio.py
```

3. Enter each holding when prompted. Press Enter on an empty ticker to finish:

```
Ticker symbol: AAPL
  Buy price per share: 150
  Number of shares: 10
Ticker symbol:
```

You can also pass a different CSV of tickers: `python portfolio.py path/to/file.csv`

## Example output

```
--------------------------------------------------------------------------------
Ticker     Shares        Buy    Current     Invested        Value    Gain/Loss        %
--------------------------------------------------------------------------------
AAPL        10.00     150.00     200.00     1,500.00     2,000.00      +500.00  +33.33%
--------------------------------------------------------------------------------
Total invested : $1,500.00
Current value  : $2,000.00
Total gain/loss: +500.00 (+33.33%)

Summary saved to portfolio_summary.csv
```

## Output file

`portfolio_summary.csv` contains one row per holding plus a `TOTAL` row, with these columns:

`Timestamp, Ticker, Shares, Buy Price, Current Price, Invested, Market Value, Gain/Loss ($), Gain/Loss (%)`

## Files

| File | Description |
|------|-------------|
| `portfolio.py` | Main script |
| `sp500.csv` | S&P 500 ticker dataset used to validate symbols |
| `portfolio_summary.csv` | Generated summary of your portfolio |

## Notes

- Prices are fetched when you run the script, so results reflect the latest available close.
- If a live price can't be fetched, the script asks you to type the current price.
- Press Ctrl+C at any time to cancel without saving.
