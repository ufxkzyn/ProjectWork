import csv

from flask import Blueprint, jsonify, render_template, request, Flask
import datetime
import os  # Import the os module to cehck if json file exist or not
import matplotlib
import requests  # Import the requests module to make HTTP requests
from bs4 import BeautifulSoup  # Import BeautifulSoup from bs4 to parse HTML
import json  # Import the json module to work with JSON data
import re
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


pd.set_option('display.max_columns', None)  # Show all columns in the DataFrame

data = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')

#print(data.head())

#print(data.describe())
#print(data.info(verbose=True, show_counts=True))
#sns.regplot(x='csat20', y='goldat20', data=data)

#print(data.info(verbose=True, show_counts=True))

#plot = data.groupby('result')['goldat20'].plot(kind='bar')

matplotlib.style.use('ggplot')

def find_unique_data_points(input_value):
    unique_data_matches = []

    value_to_pull = f'{input_value}'  # Replace with the specific value you want to pull (e.g., 'T1')

    

    unique_data_matches = data[value_to_pull].unique().dropna()  # Get unique values from the specified column

    with open(f'./Data/unsorted/2026_{value_to_pull}_data.csv', 'w', newline='', encoding='utf-8') as csv_data_filepointer:
        writer = csv.writer(csv_data_filepointer)
        writer.writerow([value_to_pull])  # Write the column name as header
        for value in unique_data_matches:
            writer.writerow([value])  # Write each unique value in a new row

    return unique_data_matches



def data_filtering(row_value, coloumn_value):

    filtered_data = data[data[f'{coloumn_value}'] == row_value]  # Filter the DataFrame based on the specified team name
    if filtered_data.empty:
        print(f"No data found for {row_value} in column {coloumn_value}.")
        return
    filtered_data.to_csv(f'./Data/unsorted/{row_value}_{coloumn_value}_data.csv', index=False)  # Save the filtered data to a new CSV file


def main():
    for unique in find_unique_data_points('position'):
        data_filtering(unique, 'position')  # Call the data_filtering function for each unique team name

main()




