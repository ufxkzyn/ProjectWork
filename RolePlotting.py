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
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

pd.set_option('display.max_columns', None)  # Show all columns in the DataFrame
cleaned_data = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')


##using one for every time###
scaler_10min = StandardScaler()
scaler_15min = StandardScaler()
scaler_20min = StandardScaler()
scaler_25min = StandardScaler()

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

        sns.lineplot(data=plotted_data, label=f"{roles} (Win)", linestyle='-') 
        sns.lineplot(data=plotted_data_loser, label=f"{roles} (Loss)", linestyle='--') 
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
    plt.xticks([0.5, 1.5, 2.5, 3.5], ['10', '15', '20', '25'])  # Set x-ticks to match the time intervals
    plt.title('Average Gold lead in "%" for winning teams compared to losing teams by Position')
    plt.ylabel('Position')
   

    plt.show()  # Show all the plots at the end 


def cs_kills_all_roles():
    fig, axes = plt.subplots(1, 5, figsize=(20, 5), sharey=True)
    
    columns_to_check = ['csat10', 'csat15', 'csat20', 'csat25']
    time_intervals = [0, 5, 10, 15, 20, 25]
    
    win_color = '#2ca02c'
    loss_color = '#d62728' 

    for ax, (roles, csvalues) in zip(axes, dont_repeat_urself.items()):
        
        extracted_mean_winner = csvalues[csvalues['result'] == 1][columns_to_check].mean().tolist()
        extracted_mean_loser = csvalues[csvalues['result'] == 0][columns_to_check].mean().tolist()

        cs_at_5_guess = np.interp(5, [0, 10], [0, extracted_mean_winner[0]])
        cs_at_5_guess_loser = np.interp(5, [0, 10], [0, extracted_mean_loser[0]])

        plotted_data = [0] + [cs_at_5_guess] + extracted_mean_winner
        plotted_data_loser = [0] + [cs_at_5_guess_loser] + extracted_mean_loser

        # Plot the lines
        sns.lineplot(x=time_intervals, y=plotted_data, 
                     ax=ax, label="Winner", color=win_color, marker='o', linewidth=2)
        sns.lineplot(x=time_intervals, y=plotted_data_loser, 
                     ax=ax, label="Loser", color=loss_color, marker='X', linestyle='--', linewidth=2)

        # Calculate and display the difference at the final point ---
        final_win_cs = plotted_data[-1]
        final_loss_cs = plotted_data_loser[-1]
        cs_diff = final_win_cs - final_loss_cs
        
        # Calculate the middle point between the two lines to place the text perfectly
        y_position = (final_win_cs + final_loss_cs) / 2
        
        # Add the text to the chart at x=25.5 (slightly to the right of the last dot)
        ax.text(x=25.5, y=y_position, s=f"+{cs_diff:.1f}", 
                color='black', fontsize=11, fontweight='bold', va='center')

        # Format the specific mini-chart
        ax.set_title(roles.upper(), fontsize=14) 
        ax.set_xlabel('Time (min)', fontsize=10)
        ax.set_xticks(time_intervals)


        ax.grid(True, alpha=0.3)
        ax.get_legend().remove()

    axes[0].set_ylabel('Average CS', fontsize=12)

    # Add master legend
    #handles, labels = axes[0].get_legend_handles_labels()
    #fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fontsize=12)

    fig.suptitle('Average CS and the difference between winning and losing by Role', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()



    role_cs_info = cleaned_data.groupby(['position', 'result'])[columns_to_check].mean()
    role_winner = role_cs_info.xs(1, level='result')  #
    role_loser = role_cs_info.xs(0, level='result')  #
    diffrence_resuts = role_winner - role_loser  # Calculate the difference between winners and losers

    diffrence_resuts.columns = ["10min", "15min", "20min", "25min"]
    role_names = {'bot': 'ADC', 'top': 'Top', 'mid': 'Mid', 'sup': 'Support', 'jng': 'Jungle', 'team': 'Team average'}
    diffrence_resuts = diffrence_resuts.rename(index=role_names)
    diffrence_resuts = diffrence_resuts.reindex(["Team Total", "Support", "Top","Mid","Jungle",  "ADC",]) 

    annot_labels = diffrence_resuts.round(2).astype(str)  # 
    the_heatmap = sns.heatmap(diffrence_resuts, annot=annot_labels, fmt="", cmap="coolwarm", vmax=17, vmin=0,)  # Heatmap
    the_heatmap.axhline(1, color='white', linewidth=8)


    plt.xlabel('Time (minutes)')
    plt.xticks([0.5, 1.5, 2.5, 3.5], ['10', '15', '20', '25'])  # Set x-ticks to match the time intervals
    plt.title('Average CS lead for winning teams compared to losing teams by Position')
    plt.ylabel('Position')
    plt.show()  # Show all the plots at the end 


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
    the_heatmap = sns.heatmap(diffrence_resuts, annot=annot_labels, fmt="", cmap="coolwarm", vmax=4, vmin=-2, center=0,) #vmax or the team thing fucks it all
    the_heatmap.axhline(1, color='gray', linewidth=5)
    for i in range(3, diffrence_resuts.shape[1], 3):  # Add horizontal lines after every 3 columns (kills, deaths, assists)
        the_heatmap.axvline(i, color='gray', linewidth=3)
    

    #### y axis stuff ###
    ay1_notation = the_heatmap
    ay1_notation.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])  # Set y-ticks for the primary axis
    ay1_notation.set_yticklabels(labels=["Team total average", "Support", "Top","Mid","Jungle",  "ADC",], fontsize=10, fontweight='bold')  # Set y-tick labels for the primary axis
    ay1_notation.set_ylabel('Position', fontsize=10, fontweight='bold')  # Set y-axis label
    ay1_notation.tick_params(axis='y', which='both', length=0)  # Hide tick marks on the y-axis

    #the bottom x axis
    ax1_notation = the_heatmap
    ax1_notation.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5])  # Set x-ticks for the bottom axis
    ax1_notation.set_title('Average Kills, Deaths, and Assists comparing winning teams to losing teams by Position', fontsize=12, fontweight='bold')  # Set the title for the heatmap
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


def winrate():
    aggreggesion_rules = {
    'killsat10': 'sum',
    'deathsat10': 'sum',
    'assistsat10': 'sum',
    'goldat10': 'sum',
    'csat10': 'sum',
    'xpat10': 'sum',
    'killsat15': 'sum',
    'deathsat15': 'sum',
    'assistsat15': 'sum',
    'goldat15': 'sum',
    'csat15': 'sum',
    'xpat15': 'sum',
    'killsat20': 'sum',
    'deathsat20': 'sum',
    'assistsat20': 'sum',
    'goldat20': 'sum',
    'csat20': 'sum',
    'xpat20': 'sum',
    'killsat25': 'sum',
    'deathsat25': 'sum',
    'assistsat25': 'sum',
    'goldat25': 'sum',
    'csat25': 'sum',
    'xpat25': 'sum',
    'teamname': 'first',
    'gamelength': 'first',
    'result': 'first',
    'gameid': 'first'}

    new_cleaned_data = cleaned_data.copy().fillna(0)  # Fills NaN values with 0 for the relevant columns
    new_cleaned_data = new_cleaned_data.groupby(['gameid', 'teamname']).agg(aggreggesion_rules)  # makes it so we only check it on a per team basis
    

    columns_to_check_10min = ['killsat10', 'deathsat10', 'assistsat10', 'goldat10', 'csat10', 'xpat10']  # List of columns to check for the 10-minute model
    columns_to_check_15min = ['killsat15', 'deathsat15', 'assistsat15', 'goldat15', 'csat15', 'xpat15']  # List of columns to check for the 15-minute model
    columns_to_check_20min = ['killsat20', 'deathsat20', 'assistsat20', 'goldat20', 'csat20', 'xpat20']  # List of columns to check for the 20-minute model
    columns_to_check_25min = ['killsat25', 'deathsat25', 'assistsat25', 'goldat25', 'csat25', 'xpat25']  # List of columns to check for the 25-minute model

    

    valid_10min_row = new_cleaned_data[new_cleaned_data['gamelength'] >= 10*60]
    valid_15min_row = new_cleaned_data[new_cleaned_data['gamelength'] >= 15*60]
    valid_20min_row = new_cleaned_data[new_cleaned_data['gamelength'] >= 20*60]
    valid_25min_row = new_cleaned_data[new_cleaned_data['gamelength'] >= 25*60]


    y_10min_train = valid_10min_row['result']
    y_15min_train = valid_15min_row['result']
    y_20min_train = valid_20min_row['result']
    y_25min_train = valid_25min_row['result']

    x_10min_train_scaled = scaler_10min.fit_transform(valid_10min_row[columns_to_check_10min])
    x_15min_train_scaled = scaler_15min.fit_transform(valid_15min_row[columns_to_check_15min])
    x_20min_train_scaled = scaler_20min.fit_transform(valid_20min_row[columns_to_check_20min])
    x_25min_train_scaled = scaler_25min.fit_transform(valid_25min_row[columns_to_check_25min])



    model_10min = LogisticRegression(verbose=2)
    model_10min.fit(x_10min_train_scaled, y_10min_train)
    model_15min = LogisticRegression(verbose=2)
    model_15min.fit(x_15min_train_scaled, y_15min_train)
    model_20min = LogisticRegression(verbose=2)
    model_20min.fit(x_20min_train_scaled, y_20min_train)
    model_25min = LogisticRegression(verbose=2)
    model_25min.fit(x_25min_train_scaled, y_25min_train)
    


    winprob_10min = model_10min.predict_proba(x_10min_train_scaled)[:, 1]  # start from first column go through all values
    winprob_15min = model_15min.predict_proba(x_15min_train_scaled)[:, 1]  # start from first column go through all values
    winprob_20min = model_20min.predict_proba(x_20min_train_scaled)[:, 1]  # start from first column go through all values
    winprob_25min = model_25min.predict_proba(x_25min_train_scaled)[:, 1]  # start from first column go through all values


    new_cleaned_data.loc[valid_10min_row.index, 'Win_prob_10min'] = winprob_10min
    new_cleaned_data.loc[valid_15min_row.index, 'Win_prob_15min'] = winprob_15min
    new_cleaned_data.loc[valid_20min_row.index, 'Win_prob_20min'] = winprob_20min
    new_cleaned_data.loc[valid_25min_row.index, 'Win_prob_25min'] = winprob_25min
    
    
    columns_to_show_10min = ['killsat10', 'deathsat10', 'assistsat10', 'xpat10', 'goldat10', 'csat10', 'Win_prob_10min', 'result', 'teamname', 'gamelength', 'gameid']  # Columns to show in the output
    columns_to_show_15min = ['killsat15', 'deathsat15', 'assistsat15', 'xpat15', 'goldat15', 'csat15', 'Win_prob_15min', 'result', 'teamname', 'gamelength', 'gameid']  # Columns to show in the output
    columns_to_show_20min = ['killsat20', 'deathsat20', 'assistsat20', 'xpat20', 'goldat20', 'csat20', 'Win_prob_20min', 'result', 'teamname', 'gamelength', 'gameid']  # Columns to show in the output
    columns_to_show_25min = ['killsat25', 'deathsat25', 'assistsat25', 'xpat25', 'goldat25', 'csat25', 'Win_prob_25min', 'result', 'teamname', 'gamelength', 'gameid']  # Columns to show in the output  


    models = {
        "10min": model_10min,
        "15min": model_15min,
        "20min": model_20min,
        "25min": model_25min
    }

    scaled_models = {
        "10min": x_10min_train_scaled,
        "15min": x_15min_train_scaled,
        "20min": x_20min_train_scaled,
        "25min": x_25min_train_scaled
    }

    labels = {
        "10min": y_10min_train,
        "15min": y_15min_train,
        "20min": y_20min_train,
        "25min": y_25min_train
    }

    column_collector = {
        "10min": columns_to_check_10min,
        "15min": columns_to_check_15min,
        "20min": columns_to_check_20min,
        "25min": columns_to_check_25min
    }

    
      

    #predictor based of time, checks if they won or lost, then how accuracy the model is to guess
    all_coeficients = {}
    final_accuracy_of_models = {}
    for window, model in models.items():
        coefs = dict(zip(column_collector[window], model.coef_[0]))
        all_coeficients[window] = coefs
        print(f"\n[{window}] Coefficients:")
        for feature, coef in sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True):
            print(f"{feature}: {coef:.4f}")

        acc = accuracy_score(labels[window], model.predict(scaled_models[window]))
        final_accuracy_of_models[window] = acc

    print(f"\nFinal Accuracy of Models: {final_accuracy_of_models}")

    ## ['killsat10', 'deathsat10', 'assistsat10', 'goldat10', 'csat10', 'xpat10']# that order
    ## for manual testing ###
    manual_testing = np.array([[5, 5, 7, 34000, 714, 41000]])

    manual_testing_scaled = scaler_10min.transform(manual_testing)
    manual_testing_probablity = model_10min.predict_proba(manual_testing_scaled)[:, 1]
    print(f"\nManual Testing Win Probability at 10 minutes: {manual_testing_probablity[0]:.2%}")

    print(valid_10min_row[columns_to_check_10min].apply(pd.to_numeric, errors='coerce').mean())
    print(columns_to_check_10min)


    feature_map = {
        'kills':   ['killsat10',   'killsat15',   'killsat20',   'killsat25'],
        'deaths':  ['deathsat10',  'deathsat15',  'deathsat20',  'deathsat25'],
        'assists': ['assistsat10', 'assistsat15', 'assistsat20', 'assistsat25'],
        'gold':    ['goldat10',    'goldat15',    'goldat20',    'goldat25'],
        'cs':      ['csat10',      'csat15',      'csat20',      'csat25'],
        'xp':      ['xpat10',      'xpat15',      'xpat20',      'xpat25'],
    }

    windows = ['10min', '15min', '20min', '25min']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})  # top gets more space

    ### top graphs, coefficients values###
    for label, feat_keys in feature_map.items():
        values = [all_coeficients[w][k] for w, k in zip(windows, feat_keys)]
        ax1.plot(windows, values, marker='o', linewidth=2, label=label)

    ax1.axhline(0, color='gray', linestyle='--', alpha=0.4)
    ax1.set_ylabel('Coefficient Value')
    ax1.set_title('Importance of each stat for predicting win probability and Model Accuracy')
    ax1.legend(loc='upper left')
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    ##### Bottom Graph, model accuracy ###
    acc_values = [final_accuracy_of_models[w] for w in windows]
    ax2.plot(windows, acc_values, marker='s', linewidth=2.5, color='black')
    for i, acc in enumerate(acc_values):
        ax2.text(i, acc + 0.012, f"{acc:.1%}", ha='center', fontsize=9)  
    ax2.set_ylabel('Accuracy')
    ax2.set_ylim(0.5, 1.0)
    ax2.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

    #print(dict(zip(columns_to_check_10min, model_10min.coef_[0]))




cs_kills_all_roles()
#gold_over_time_all_roles()
#kda_heatmap()
#winrate()