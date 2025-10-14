import argparse
from pathlib import Path
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Remove 'yesterror' row from shares CSV if present")
    parser.add_argument(
        "-s", "--shares", required=True, type=Path, help="CSV file with shares data"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    shares_df = pd.read_csv(args.shares)
    
    if 'yesterror' in shares_df['name'].values:
        shares_df = shares_df[shares_df['name'] != 'yesterror']
        shares_df.to_csv(args.shares, index=False)
        print(f"'yesterror' row removed from {args.shares}")
    else:
        print(f"No 'yesterror' row found in {args.shares}")

if __name__ == "__main__":
    main()