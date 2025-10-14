import argparse
from pathlib import Path
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Calculate adjusted values based on shares and market data")
    parser.add_argument(
        "-s", "--shares", required=True, type=Path, help="CSV/TXT file with columns: name,shares"
    )
    parser.add_argument(
        "-d", "--data", required=True, type=Path, help="CSV file containing market data"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    shares_df = pd.read_csv(args.shares)
    if 'name' not in shares_df.columns or 'shares' not in shares_df.columns:
        raise ValueError("Shares file must have columns named 'name' and 'shares'")
    shares_dict = pd.Series(shares_df.shares.values, index=shares_df.name).to_dict()

    print(f"Loading market data from {args.data}")
    data_df = pd.read_csv(args.data)

    # Filter NSECM excluding BANKNIFTY
    spot_df = data_df[(data_df['exchange'] == 'NSECM') & (data_df['name'] != 'BANKNIFTY')].copy()
    spot_df['stock_value'] = spot_df.apply(lambda row: row['ltp'] * shares_dict.get(row['name'], 0), axis=1)

    total_valuations = spot_df.groupby('time')['stock_value'].sum().reset_index()
    total_valuations.rename(columns={'stock_value': 'total_stock_value'}, inplace=True)

    banknifty_df = data_df[(data_df['exchange'] == 'NSECM') & (data_df['name'] == 'BANKNIFTY')][['time', 'ltp']].copy()
    banknifty_df.rename(columns={'ltp': 'bn_index'}, inplace=True)

    result_df = pd.merge(total_valuations, banknifty_df, on='time', how='inner')

    base_total_value = shares_dict['value']
    base_banknifty_value = shares_dict['price']
    error = shares_dict.get("yesterror",0)

    result_df['bn_constructed_index'] = ((result_df['total_stock_value'] / base_total_value) * base_banknifty_value) - error

    result_df.rename(columns={'time':'timestamp'},inplace=True)
    output_df = result_df[['timestamp', 'bn_index', 'bn_constructed_index']]

    # Define output path in results folder with same filename as input data CSV
    output_folder = Path("Solutions")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / args.data.name  # Same filename as input CSV

    output_df.to_csv(output_file, index=False)
    print(f"Calculation complete. Output saved to {output_file}")

    new_error = error + (output_df['bn_constructed_index'] - output_df['bn_index']).mean()
    
    if 'yesterror' in shares_df['name'].values:
        shares_df.loc[shares_df['name'] == 'yesterror', 'shares'] = new_error
    else:
    # Append new row using pd.concat()
        new_row_df = pd.DataFrame([{'name': 'yesterror', 'shares': new_error}])
        shares_df = pd.concat([shares_df, new_row_df], ignore_index=True)


    shares_df.to_csv(args.shares, index=False)

if __name__ == "__main__":
    main()
