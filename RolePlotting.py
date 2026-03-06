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


########## Gold over time for all roles with heatmap of % diffrence between winning and losing teams for each role ##
def gold_over_time_all_roles():
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


##### same as above but for cs instead of gold #############
def cs_kills_all_roles():
    columns_to_check = ['csat10', 'csat15', 'csat20', 'csat25']  # List of columns to extract
    for roles, csvalues in dont_repeat_urself.items():
        extracted_mean_winner = csvalues[columns_to_check][csvalues['result'] == 1].mean().tolist()  # Calculate the mean of the specified columns
        extracted_mean_loser = csvalues[columns_to_check][csvalues['result'] == 0].mean().tolist()  # Calculate the mean of the specified columns for losers

        cs_at_5_guess = np.interp(5, [0, 10], [0, extracted_mean_winner[0]])  # Estimate cs at 5 minutes with np interpolation(guess based on values at 0 and 10)
        cs_at_5_guess_loser = np.interp(5, [0, 10], [0, extracted_mean_loser[0]])  # Estimate cs at 5 minutes for losers with np interpolation(guess based on values at 0 and 10)

        plotted_data = [0] + [cs_at_5_guess] + extracted_mean_winner  # Add the initial cs value at 0 minutes (0) to the list of means
        plotted_data_loser = [0] + [cs_at_5_guess_loser] + extracted_mean_loser  # Add the initial cs value at 0 minutes (0) to the list of means for losers

        #sns.boxenplot(data=plotted_data, label=f"{roles}_winner")  # Plot the line graph for the winners of the current role, marking our valuepoints
        #sns.boxenplot(data=plotted_data_loser, label=f"{roles}_loser")  # Plot the line graph for the losers of the current role, marking our valuepoints

        sns.lineplot(data=plotted_data, label=f"{roles}_winner")  # Plot the line graph for the winners of the current role, marking our valuepoints
        sns.lineplot(data=plotted_data_loser, label=f"{roles}_loser")  # Plot the line graph for the losers of the current role, marking our valuepoints

        plt.xticks([0, 1, 2, 3, 4, 5], ['0', '5', '10', '15', '20', '25'])  # Set x-ticks to match the time intervals
        plt.grid() 
        plt.title('Average CS at 10, 15, 20, and 25 Minutes')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Average CS')
        plt.legend()
        plt.figure()

    role_cs_info = cleaned_data.groupby(['position', 'result'])[columns_to_check].mean()
    role_winner = role_cs_info.xs(1, level='result')  #
    role_loser = role_cs_info.xs(0, level='result')  #
    diffrence_resuts = role_winner - role_loser  # Calculate the difference between winners and losers

    diffrence_resuts.columns = ["10min", "15min", "20min", "25min"]
    role_names = {'bot': 'ADC', 'top': 'Top', 'mid': 'Mid', 'sup': 'Support', 'jng': 'Jungle', 'team': 'Team average'}
    diffrence_resuts = diffrence_resuts.rename(index=role_names)
    diffrence_resuts = diffrence_resuts.reindex(["Team average", "Support", "Top","Mid","Jungle",  "ADC",]) 

    annot_labels = diffrence_resuts.round(2).astype(str)  # 
    the_heatmap = sns.heatmap(diffrence_resuts, annot=annot_labels, fmt="", cmap="coolwarm")  # Heatmap
    the_heatmap.axhline(1, color='white', linewidth=8)
    plt.xlabel('Time (minutes)')
    plt.xticks([0, 1, 2, 3], ['10', '15', '20', '25'])  # Set x-ticks to match the time intervals
    plt.title('Average CS lead for winning teams compared to losing teams by Position')
    plt.ylabel('Position')
    plt.show()  # Show all the plots at the end 


#### same as above but looking at k/d/a and their relevance to win/loss #####
def kda_threashold():
    data_to_pull = cleaned_data[['killsat10', 'deathsat10', 'assistsat10', 'killsat15', 'deathsat15', 'assistsat15', 'killsat20', 'deathsat20', 'assistsat20', 'killsat25', 'deathsat25', 'assistsat25', 'result', 'position']]  # List of columns to extract
    
    for time in [10, 15, 20, 25]:
        k = f'killsat{time}'
        d = f'deathsat{time}'
        a = f'assistsat{time}'
        data_to_pull[f'kda_at_{time}'] = ((data_to_pull[k] + data_to_pull[a]) / data_to_pull[d].clip(lower=1))

    kda_coloumns = [f'kda_at_{time}' for time in [10, 15, 20, 25]]  
    melted_data = data_to_pull.melt(id_vars=['result', 'position'], value_vars=kda_coloumns, var_name='time', value_name='kda')  # Melt the DataFrame to long format for seaborn
    melted_data['time'] = melted_data['time'].str.extract(r'kda_at_(\d+)').astype(int)  # Extract the time from the 'time' column and convert it to integer

    stats_group = melted_data.groupby(['position', 'result', 'time'])['kda'].agg(['mean', 'max', 'min']).reset_index()  # Group by position, result, and time, and calculate mean, max, and min KDA
    
    
    g = sns.FacetGrid(stats_group, col='position', hue='result', palette={0: 'tab:blue', 1: 'tab:red'}, col_order=["top", "jng", "mid", "sup", "bot", "team"])  # Create a FacetGrid for each position, colored by result

    
    g.map_dataframe(sns.lineplot, x='time', y='mean', marker='o', linestyle='-')
    g.map_dataframe(sns.lineplot, x='time', y='max', marker='o', linestyle='--')
    g.map_dataframe(sns.lineplot, x='time', y='min', marker='o', linestyle=':')

    
    positions = [ax.get_title().split('=')[-1].strip() for ax in g.axes.flat]
    for ax_axel, pos in zip(g.axes.flat, positions):
        for res, color in zip([0, 1], ['tab:blue', 'tab:red']):
            subset = stats_group[(stats_group['position'] == pos) & (stats_group['result'] == res)]
            ax_axel.fill_between(subset['time'], subset['min'], subset['max'], color=color, alpha=0.2)
        ax_axel.grid(True)

    g.add_legend()
    plt.show()


#### heamat for kda ###
def kda_heatmap():
    columns_to_check = ['killsat10', 'deathsat10', 'assistsat10', 'killsat15', 'deathsat15', 'assistsat15', 'killsat20', 'deathsat20', 'assistsat20', 'killsat25', 'deathsat25', 'assistsat25']  # List of columns to extract
    role_kda_info = cleaned_data.groupby(['position', 'result'])[columns_to_check].mean()
    role_winner = role_kda_info.xs(1, level='result')  #
    role_loser = role_kda_info.xs(0, level='result')  
    diffrence_resuts = role_winner - role_loser  # Calculate the difference between winners and losers

    diffrence_resuts.columns = ['killsat10', 'deathsat10', 'assistsat10', 'killsat15', 'deathsat15', 'assistsat15', 'killsat20', 'deathsat20', 'assistsat20', 'killsat25', 'deathsat25', 'assistsat25']
    role_names = {'bot': 'ADC', 'top': 'Top', 'mid': 'Mid', 'sup': 'Support', 'jng': 'Jungle', 'team': 'Team average'}
    diffrence_resuts = diffrence_resuts.rename(index=role_names)
    diffrence_resuts = diffrence_resuts.reindex(["Team average", "Support", "Top","Mid","Jungle",  "ADC",])
    annot_labels = diffrence_resuts.round(2).astype(str)  #


    #actual basis for heatmap #
    the_heatmap = sns.heatmap(diffrence_resuts, annot=annot_labels, fmt="", cmap="coolwarm", vmax=3.5, vmin=-3.5, center=0,) #vmax or the team thing fucks it all
    the_heatmap.axhline(1, color='gray', linewidth=5)
    for i in range(3, diffrence_resuts.shape[1], 3):  # Add horizontal lines after every 3 columns (kills, deaths, assists)
        the_heatmap.axvline(i, color='gray', linewidth=3)
    

    #### y axis stuff ###
    ay1_notation = the_heatmap
    ay1_notation.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])  # Set y-ticks for the primary axis
    ay1_notation.set_yticklabels(labels=["Team average", "Support", "Top","Mid","Jungle",  "ADC",], fontsize=10, fontweight='bold')  # Set y-tick labels for the primary axis
    ay1_notation.set_ylabel('Position', fontsize=10, fontweight='bold')  # Set y-axis label
    ay1_notation.tick_params(axis='y', which='both', length=0)  # Hide tick marks on the y-axis

    #the bottom x axis
    ax1_notation = the_heatmap
    ax1_notation.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5])  # Set x-ticks for the bottom axis
    ax1_notation.set_title('Average Kills, Deaths, and Assists lead in for winning teams compared to losing teams by Position')
    ax1_notation.set_xticklabels(labels=["Kills", "Deaths", "Assists"]*4, fontsize=10, fontweight='bold', rotation=45)  # Set x-tick labels for the primary axis
    

    ### setting up the heatmap ##
    ### adding the 2nd x axsis to clearify
    ax2_notation = the_heatmap.twiny()  # Create a secondary x-axis for the Kills/Deaths/Assists labels
    ax2_notation.set_xlim(ax1_notation.get_xlim())  # gives us same x values as ax1 set xtics
    ax2_notation.set_xticks([1.5, 4.5, 7.5, 10.5])  # Sets x-ticks for top axis
    ax2_notation.set_xticklabels(['10 minutes', '15 minutes', '20 minutes', '25 minutes'], fontsize=10, fontweight='bold', )  # Set x-tick labels for the secondary axis
    ax2_notation.tick_params(axis='x', which='both', length=0)  # Hide tick marks on the secondary x-axis


    plt.xlabel('Time (minutes)')
    plt.show()  # Show all the plots at the end




#cs_kills_all_roles()
#gold_over_time_all_roles()
#kda_heatmap()
kda_threashold()
