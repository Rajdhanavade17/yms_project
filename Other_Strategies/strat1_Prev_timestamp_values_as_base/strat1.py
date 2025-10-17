import argparse
from pathlib import Path
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Calculate rolling Bank Nifty constructed index")
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

    spot_df = data_df[(data_df['exchange'] == 'NSECM') & (data_df['name'] != 'BANKNIFTY')].copy()
    spot_df['stock_value'] = spot_df.apply(lambda row: row['ltp'] * shares_dict.get(row['name'], 0), axis=1)

    total_valuations = spot_df.groupby('time')['stock_value'].sum().reset_index()
    total_valuations.rename(columns={'stock_value': 'total_stock_value'}, inplace=True)

    banknifty_df = data_df[(data_df['exchange'] == 'NSECM') & (data_df['name'] == 'BANKNIFTY')][['time', 'ltp']].copy()
    banknifty_df.rename(columns={'ltp': 'bn_index'}, inplace=True)

    result_df = pd.merge(total_valuations, banknifty_df, on='time', how='inner')
    result_df.sort_values('time', inplace=True)

    prev_total_value = shares_dict.get('prev_total_value')
    if prev_total_value is None:
        prev_total_value = shares_dict.get('value')

    prev_bn_price = shares_dict.get('prev_total_price')
    if prev_bn_price is None:
        prev_bn_price = shares_dict.get('price')

    constructed_index = []
    for idx, row in result_df.iterrows():
        current_total_value = row['total_stock_value']
        current_bn_price = row['bn_index']

        constructed_bn = (current_total_value / prev_total_value) * prev_bn_price
        constructed_index.append(constructed_bn)

        prev_total_value = current_total_value
        prev_bn_price = current_bn_price

    result_df['bn_constructed_index'] = constructed_index
    result_df.rename(columns={'time': 'timestamp'}, inplace=True)
    output_df = result_df[['timestamp', 'bn_index', 'bn_constructed_index']]

    # Update or create 'prev_total_value' and 'prev_total_price' in shares_df
    if 'prev_total_value' in shares_df['name'].values:
        shares_df.loc[shares_df['name'] == 'prev_total_value', 'shares'] = prev_total_value
    else:
        new_row_df = pd.DataFrame([{'name': 'prev_total_value', 'shares': prev_total_value}])
        shares_df = pd.concat([shares_df, new_row_df], ignore_index=True)

    if 'prev_total_price' in shares_df['name'].values:
        shares_df.loc[shares_df['name'] == 'prev_total_price', 'shares'] = prev_bn_price
    else:
        new_row_df = pd.DataFrame([{'name': 'prev_total_price', 'shares': prev_bn_price}])
        shares_df = pd.concat([shares_df, new_row_df], ignore_index=True)

    shares_df.to_csv(args.shares, index=False)

    output_folder = Path("Solutions")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / args.data.name
    output_df.to_csv(output_file, index=False)

    print(f"Calculation complete. Output saved to {output_file}")
    print(f"Shares CSV updated with prev_total_value and prev_total_price.")


if __name__ == "__main__":
    main()
