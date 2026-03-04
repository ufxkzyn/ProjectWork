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
cleaned_data = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')


dont_repeat_urself = { ## making a dict to we can easier do everything, cause i cba typing the same thing 5 times
    "ADC": pd.read_csv('./Data/positiondata/bot_position_data.csv'),
    "Top": pd.read_csv('./Data/positiondata/top_position_data.csv'),
    "Mid": pd.read_csv('./Data/positiondata/mid_position_data.csv'),
    "Support": pd.read_csv('./Data/positiondata/sup_position_data.csv'),
    "Jungle": pd.read_csv('./Data/positiondata/jng_position_data.csv')
    }


def plot_gold_over_time_all_roles():
    columns_to_extract = ['goldat10', 'goldat15', 'goldat20', 'goldat25']  # List of columns to extract
    for roles, goldvalues in dont_repeat_urself.items():
        extracted_mean_winner = goldvalues[columns_to_extract][goldvalues['result'] == 1].mean().tolist()  # Calculate the mean of the specified columns
        extracted_mean_loser = goldvalues[columns_to_extract][goldvalues['result'] == 0].mean().tolist()  # Calculate the mean of the specified columns for losers

        gold_at_5_guess = np.interp(5, [0, 10], [500, extracted_mean_winner[0]])  # Estimate gold at 5 minutes with np interpolation(guess based on values at 0 and 10)
        gold_at_5_guess_loser = np.interp(5, [0, 10], [500, extracted_mean_loser[0]])  # Estimate gold at 5 minutes for losers with np interpolation(guess based on values at 0 and 10)

        plotted_data = [500] + [gold_at_5_guess] + extracted_mean_winner  # Add the initial gold value at 0 minutes (500) to the list of means
        plotted_data_loser = [500] + [gold_at_5_guess_loser] + extracted_mean_loser  # Add the initial gold value at 0 minutes (500) to the list of means for losers

        sns.lineplot(data=plotted_data, label=f"{roles}_winner")  # Plot the line graph for the winners of the current role, marking our valuepoints
        sns.lineplot(data=plotted_data_loser, label=f"{roles}_loser")  # Plot the line graph for the losers of the current role, marking our valuepoints
        plt.xticks([0, 1, 2, 3, 4, 5], ['0', '5', '10', '15', '20', '25'])  # Set x-ticks to match the time intervals
        plt.grid() 
        plt.title('Average Gold at 10, 15, 20, and 25 Minutes')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Average Gold')
        plt.legend()
        plt.figure() 

##### % diffrence for each role based on winning and losing ########
    role_gold_info = cleaned_data.groupby(['position', 'result'])[columns_to_extract].mean() 
    role_winner = role_gold_info.xs(1, level='result')  # splits it into winners (1) and losers (0) based on the result level
    role_loser = role_gold_info.xs(0, level='result')  # 
    diffrence_resuts = ((role_winner - role_loser) / role_loser * 100)


    ####stuff to make the out look better when printing####
    diffrence_resuts.columns = ["10min", "15min", "20min", "25min"]
    role_names = {'bot': 'ADC', 'top': 'Top', 'mid': 'Mid', 'sup': 'Support', 'jng': 'Jungle', 'team': 'Team average'}
    diffrence_resuts = diffrence_resuts.rename(index=role_names)
    diffrence_resuts = diffrence_resuts.reindex(["Team average", "Support", "Top","Mid","Jungle",  "ADC",]) 
    print(f'Percantage diffrence between winning and losing for each role:\n{diffrence_resuts.round(2).astype(str) + "%"}')
    ### more stuff specificly for the heatmap ###
    annot_labels = diffrence_resuts.round(2).astype(str) + "%"  # Create annotation labels with percentage values
    the_heatmap = sns.heatmap(diffrence_resuts, annot=annot_labels, fmt="", cmap="coolwarm")  # Heatmap
    the_heatmap.axhline(1, color='white', linewidth=8)
    plt.xlabel('Time (minutes)')
    plt.xticks([0, 1, 2, 3], ['10', '15', '20', '25'])  # Set x-ticks to match the time intervals
    plt.title('Average Gold lead in "%" for winning teams compared to losing teams by Position')
    plt.ylabel('Position')
   

    plt.show()  # Show all the plots at the end 


plot_gold_over_time_all_roles()