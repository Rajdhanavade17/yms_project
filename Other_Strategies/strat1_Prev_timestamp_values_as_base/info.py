import pandas as pd
from pathlib import Path
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="calculate the error info of the generated csv file")
    parser.add_argument(
        "-r", "--result", required= True, type= Path, help="csv with columns timestamp, bn_index, bn_constructed_index"
    )
    return parser.parse_args()

def main():
    args= parse_args()

    data = pd.read_csv(args.result)
    data['error'] = (data['bn_constructed_index']-data['bn_index'])
    data['absolute_error'] = (data['bn_constructed_index']-data['bn_index']).abs()
    print("max:", data["error"].max())
    print("min:", data["error"].min())
    print("mean:", data["error"].mean())
    print("std:", data["error"].std())
    print("abs_mean:",data["absolute_error"].mean())

if __name__ == '__main__':
    main()