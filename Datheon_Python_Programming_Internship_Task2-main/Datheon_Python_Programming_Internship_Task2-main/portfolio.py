"""Stock Portfolio Performance Tracker.

Enter tickers, buy prices and share quantities. Current prices come from, in
order: a price column in the CSV (if it has one), live data via yfinance
(pip install yfinance), or a price you type in. The S&P 500 CSV is also used to
check that tickers are valid. Results are printed and saved to
portfolio_summary.csv.

Usage:
    python portfolio.py                      # uses sp500.csv in this folder
    python portfolio.py path/to/dataset.csv  # custom price CSV
"""

import csv
import sys
from datetime import datetime

DEFAULT_PRICE_FILE = "sp500.csv"
OUTPUT_FILE = "portfolio_summary.csv"

# Column names we accept in the downloaded dataset (case-insensitive).
TICKER_COLUMNS = ("symbol", "ticker", "name")
PRICE_COLUMNS = ("price", "current price", "close", "adj close", "last")


# ---------- Price lookup ----------
def load_prices(path):
    """Read the CSV. Return ({TICKER: price}, {known tickers}).

    The prices dict is empty if the file has no price column (the usual S&P 500
    constituents list has only Symbol, Security, Sector, etc.).
    """
    prices, known = {}, set()
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = {name.strip().lower(): name for name in (reader.fieldnames or [])}
            t_col = next((fields[c] for c in TICKER_COLUMNS if c in fields), None)
            p_col = next((fields[c] for c in PRICE_COLUMNS if c in fields), None)
            if not t_col:
                print(f"Note: no ticker column found in {path}; skipping ticker validation.")
                return prices, known
            for row in reader:
                ticker = (row.get(t_col) or "").strip().upper()
                if not ticker:
                    continue
                known.add(ticker)
                if p_col:
                    try:
                        prices[ticker] = float(row[p_col])
                    except (ValueError, TypeError):
                        pass
            if not p_col:
                print(f"Note: {path} has no price column; prices will come from yfinance or manual entry.")
    except FileNotFoundError:
        print(f"Note: '{path}' not found; skipping ticker validation.")
    return prices, known


_live_cache = {}


def live_price(ticker):
    """Fetch the latest close with yfinance, if installed and online."""
    if ticker in _live_cache:
        return _live_cache[ticker]
    price = None
    try:
        import yfinance as yf

        # Yahoo uses dashes for share classes, e.g. BRK.B -> BRK-B
        hist = yf.Ticker(ticker.replace(".", "-")).history(period="5d")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
    except Exception:
        pass
    _live_cache[ticker] = price
    return price


def get_price(ticker, prices):
    """CSV price -> live price -> ask the user. Returns None if all fail."""
    if ticker in prices:
        return prices[ticker]
    price = live_price(ticker)
    if price is not None:
        return price
    print(f"Could not fetch a live price for {ticker} "
          "(is yfinance installed and are you online?).")
    answer = input(f"  Enter the current price for {ticker} (or press Enter to skip): ").strip()
    try:
        value = float(answer)
        return value if value > 0 else None
    except ValueError:
        return None


# ---------- User input ----------
def read_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("  Please enter a number greater than 0.")
        except ValueError:
            print("  Invalid number, try again.")


def collect_portfolio(known=frozenset()):
    """Return {ticker: {'buy_price': float, 'shares': float}}."""
    portfolio = {}
    print("Enter your holdings. Press Enter on an empty ticker to finish.\n")
    while True:
        ticker = input("Ticker symbol: ").strip().upper()
        if not ticker:
            break
        if known and ticker not in known:
            print(f"  Warning: {ticker} is not in the S&P 500 dataset (continuing anyway).")
        buy_price = read_positive_float("  Buy price per share: ")
        shares = read_positive_float("  Number of shares: ")
        if ticker in portfolio:
            # Merge repeat purchases using a weighted-average buy price.
            old = portfolio[ticker]
            total = old["shares"] + shares
            old["buy_price"] = (old["buy_price"] * old["shares"] + buy_price * shares) / total
            old["shares"] = total
        else:
            portfolio[ticker] = {"buy_price": buy_price, "shares": shares}
    return portfolio


# ---------- Calculations ----------
def evaluate(portfolio, prices):
    """Build one result row per holding."""
    rows = []
    for ticker, pos in portfolio.items():
        current = get_price(ticker, prices)
        if current is None:
            print(f"Skipping {ticker}: no current price available.")
            continue
        invested = pos["buy_price"] * pos["shares"]
        value = current * pos["shares"]
        rows.append({
            "Ticker": ticker,
            "Shares": pos["shares"],
            "Buy Price": pos["buy_price"],
            "Current Price": current,
            "Invested": invested,
            "Market Value": value,
            "Gain/Loss ($)": value - invested,
            "Gain/Loss (%)": (value - invested) / invested * 100,
        })
    return rows


# ---------- Output ----------
def print_report(rows):
    header = (f"{'Ticker':<8}{'Shares':>9}{'Buy':>11}{'Current':>11}"
              f"{'Invested':>13}{'Value':>13}{'Gain/Loss':>13}{'%':>9}")
    line = "-" * len(header)
    print("\n" + line)
    print(header)
    print(line)
    for r in rows:
        print(f"{r['Ticker']:<8}{r['Shares']:>9.2f}{r['Buy Price']:>11.2f}"
              f"{r['Current Price']:>11.2f}{r['Invested']:>13,.2f}"
              f"{r['Market Value']:>13,.2f}{r['Gain/Loss ($)']:>+13,.2f}"
              f"{r['Gain/Loss (%)']:>+8.2f}%")
    print(line)

    invested = sum(r["Invested"] for r in rows)
    value = sum(r["Market Value"] for r in rows)
    diff = value - invested
    pct = diff / invested * 100 if invested else 0.0
    print(f"Total invested : ${invested:,.2f}")
    print(f"Current value  : ${value:,.2f}")
    print(f"Total gain/loss: {diff:+,.2f} ({pct:+.2f}%)")
    return invested, value, diff, pct


def write_csv(rows, totals, path=OUTPUT_FILE):
    invested, value, diff, pct = totals
    fields = ["Timestamp", "Ticker", "Shares", "Buy Price", "Current Price",
              "Invested", "Market Value", "Gain/Loss ($)", "Gain/Loss (%)"]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            out = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
            out["Timestamp"] = stamp
            writer.writerow(out)
        writer.writerow({
            "Timestamp": stamp, "Ticker": "TOTAL",
            "Invested": round(invested, 2), "Market Value": round(value, 2),
            "Gain/Loss ($)": round(diff, 2), "Gain/Loss (%)": round(pct, 2),
        })
    print(f"\nSummary saved to {path}")


def main():
    price_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PRICE_FILE
    prices, known = load_prices(price_file)
    print(f"Loaded {len(known)} tickers from {price_file}\n")

    portfolio = collect_portfolio(known)
    if not portfolio:
        print("No holdings entered. Exiting.")
        return

    rows = evaluate(portfolio, prices)
    if not rows:
        print("No holdings could be priced. Nothing to report.")
        return

    totals = print_report(rows)
    write_csv(rows, totals)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing was saved.")