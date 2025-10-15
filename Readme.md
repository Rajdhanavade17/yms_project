# How to generate/calculate required output 

To calculate the index using the its constitutes run construct.py on 'command prompt'/ 'Terminal' giving input parameters -s {shares data csv location} and -d {your csv data files location that contains data for 12 constituents}

    (-s/--shares):	shares data should contain 2 columns(name, shares), name should have name of constituent stock and shares should have number of shares of that particular stock considered to calculate the index market cap with this their should be two more value rows with name (value and price) containing base market capitalization/valuation and base price of index(price of index corresponding to base valuation)

    (-d/--data):	data input file should contain (date, time, exchange, name, ltp) columns in .csv format



the construct.py program will give output as a csv file with same title as input data having columns (timestamp, bn_index, bn_constructed_index) and saves it to a folder named "solutions"

### cmd structure:
```
python construct.py -s 24Q4.csv -d 20250303.data.csv 
```
or

```
python construct.py --shares 24Q4.csv --data 20250303.data.csv
```




## you will be having single shares_data csv file for entire quarter as distribution of number of shares in index changes for every quarter



if you want to check how is your solution you can run info.py giving input parameter -r(/--result) {generated csv file}
```
python info.py -r solutions\20250303.data.csv
```
it will prints the info(max, min, mean, std of construction error) for the the given input file containing columns timestamp, bn_index, bn_constructed_index


# Approch of final solution:

## our main objective was to construct banknifty index value using ltp price of all its constituents 
   so we have 12 prices of 12 constituent stocks of banknifty and now we have to find how they are calculated so we can get the index price
1. for that we need to understand how they are weighted in the banknifty index
   (a) the 12 stocks are weighted using their free float market cap 
            free float market cap is basically the tradeble stocks available in the market 
            how to get free float market cap of a stock:

                 free float market cap = price of a single share * outstanding shares * iwf(investible weight factor)
                 so we need to find iwf using from the recent shareholding pattern availabel on nse website or stocks quaterely reports

   (b) top on this their is a maximum limit on the weitage percentage of single stock in index known as capping
                banknifty uses 2 capping factors:
                   1 weight of single stock should not exceed 33% of index
                   2 combined weight of top 3 stocks should not exceed 62% of index
                if in case weight of single stock exceeds the capping limit then its weitage brought down to 33% and the market cap reduced is redistributed among all other stocks.
                    from this method we can get capping factor of a stock

2. index price formula
        
            banknifty index = (index market cap)/Base Market capital * Base index value

      index market cap = sum(i=1 to 12){ free float market cap of stock * capping factor of stock }

   ### as we dont have accurate values of iwf and capping factor so we will calculate index market cap as:

    ** so besically to construct index value base values are constant so it depends on index market cap, and to calculate index market cap only stocks prices are variable and all other factors are constant

   ##  so in the approch we are using, we will find out the number of shares for each stock for index market cap calculation, so to make it easy and accurate we will use the monthly indices weitage availble on nse website which they publish on last trading day of each month

   #### (important note: on web and nse documentation they wrote that rebalancing(changing the weithage/ number of stocks we are using above) happens twice a year but from available data and calculated results it is clear that this change in number of shares for an index happens four times a year that is you will have the same number of shares for each day in a quarter)

         so we will be having only one shares_data csv file for each quarter for ex. 25Q2.csv

4. how calculations are done

   for each timestamp we have the ltp of 12 stocks and we also have the number of shares for each stock in the index 
   we will use the base market cap and base index value as the index market capital on any day of a corresonding quarter and close price of index on that day respectively (this values should be saved in shares csv file having name: price, value and their corresponding values in the shares columns)

        bn_constructed_index = ['total_stock_value'] / base_total_value * base_banknifty_value

     'total_stock_value' = index market cap    (calculated above)
   
    ### we will calculate total_stock_value by multiplying each stocks ltp with their corresponding number of shares and add them 

6. i observered that until 5th june my mean error(bn_constructed_index - bn_index) of all timestamps of a day is approximately 0
       suddenly from 6th june error become 62 for nearly a week then 120 for few days, it is like the whole values are shifted by respective error numbers (my deviation was nearly same)
   ##### refer to [results_without_error_subtraction.txt](https://github.com/Rajdhanavade17/yms_project/blob/main/results_without_error_subtraction.txt)  file for better understanding the need of error correction.
       
       so to eliminate this error i introduced error corrected formula in which we construct the bn index using the same method and then subtract the mean error we got from previous trading day

#### and this is implemented using our reusable shares csv file, so for first iteration we will have yesterror value in shares csv and it will have 0 in it then after that day we will replace it with the error of that day(so we can use it next day)

   so formula becomes:

           bn_constructed_index = (['total_stock_value'] / base_total_value * base_banknifty_value) - error
           
   and the error for that days index construction will be

           new_error = error + (output_df['bn_constructed_index'] - output_df['bn_index']).mean()

   and we will save this error at the front of the yesterror in the shares_data csv file

    ** so if you are automated program to calculate this for days you need to excecute it in sequence by date(because yesterror is saving error from the last run)

# How to Run this program for data folder

so if you have date csv files in a folder in sequencial manner so you can use loop in command prompt to construct result for all availble files at once
for example
```
for %f in (*data.csv) do python construct.py -s shares_data.csv -d %f
```
*use path of parameters correctly 

you can see info of the all days for index constructed just by running the loop 
```
for %f in (*data.csv) do python info.py -r %f
```
check properly in which folder you are running this loop, first you need to enter the solutions folder and then run the above loop 

## Important Note:
 Use the correct shares_data csv file for the date (if a date is in 2nd financial Quarter(jul-sep) of 2025 then use 25Q2.csv)
 And for single run make sure that yesterror in the shares_data csv is 0 (once confirm it by opening csv or just run the reseterror.py giving input parameter as -s shares_data.csv which will remove yesterror from the file)
    to reset error (so you can run it single time or for first run) 
    ```
    python reseterror.py -s 25Q1.py
    ``` 

 if wanted to run without considering error corection then use constructwithouterror.py program 

 can refer to this [google sheet file](https://docs.google.com/spreadsheets/d/1nKbhW2VH5hEYwq_94FyJrV_xxmWsZu4V2lAOvdqimKg/edit?usp=sharing) to 'how to get base values'.


# Why not used the approch of taking first bn_index value as base index value and total valueation of all 12 constituent stocks using number of shares from shares_data csv file:
-this approch can avoid the problem of error generating 
-but we have to construct index using its 12 components (that means you dont have the banknifty value on 9:15 timestamp of the day )
        -and if we can use banknifty value from the customdata given then it will not asure your mean error is 0 that your prediction is spread in both direction postive and negitive evenly 
        -also if we are have bn_index values from the given data to use in calculation then just take previous timestamps values as base and calculate index
        
-I basically chose the approach of subtracting the error because the predictions are unbiased, meaning they neither over-predict nor under-predict on average.

-For the method without error subtraction, results up to 20250605 are quite good, so you can use that method as well.
