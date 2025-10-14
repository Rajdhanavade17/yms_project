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
    data['absolute_error'] = (data['bn_constructed_index']-data['bn_index'])
   
    print("max:", data["absolute_error"].max())
    print("min:", data["absolute_error"].min())
    print("mean:", data["absolute_error"].mean())
    print("std:", data["absolute_error"].std())

if __name__ == '__main__':
    main()