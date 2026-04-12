import csv
from flask import Blueprint, jsonify, render_template, request, Flask
import os  # Import the os module to check if json file exist or not
import matplotlib
from bs4 import BeautifulSoup  # Import BeautifulSoup from bs4 to parse HTML
import re
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

roles = {
    "ADC": "./Data/positiondata/bot_position_data.csv",
    "Top": "./Data/positiondata/top_position_data.csv",
    "Mid": "./Data/positiondata/mid_position_data.csv",
    "Support": "./Data/positiondata/sup_position_data.csv",
    "Jungle": "./Data/positiondata/jng_position_data.csv"
}

def champ_list_creater():
    for role, df in roles.items():
        winners = df[df['result'] == 1]
        losers = df[df['result'] == 0]

    mean_winner = winners.mean(numeric_only=True)
    mean_loser = losers.mean(numeric_only=True)

    print(f"{role} winners mean:\n", mean_winner)
    print(f"{role} losers mean:\n", mean_loser)

def Champ_save():  # just gives basic stats
    Champ_statsKDA = "Champ_selected_folder/Champ_statsKDA"

    for role, path in roles.items():
        df = pd.read_csv(path)

        filtered = df[["champion", "kills", "deaths", "assists"]]
        filtered = filtered[(filtered[["kills","deaths","assists"]] != 0).any(axis=1)]

        filtered.to_csv(
            os.path.join(Champ_statsKDA, f"{role}_filtered.csv"),
            index=False
        )



def grath_KDA_stats(folder="Champ_selected_folder/Champ_statsKDA"):
    # Default folder should contain files like "<role>_filtered.csv" created by Champ_save().
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    dataframes = []

    # Load every filtered file
    for file in os.listdir(folder):
        if file.endswith("_filtered.csv"):
            path = os.path.join(folder, file)
            df = pd.read_csv(path)
            dataframes.append(df)

    if not dataframes:
        print(f"No filtered CSV files found in {folder}. Did you run Champ_save() first?")
        return

    # Combine all role data
    combined = pd.concat(dataframes, ignore_index=True)
    combined = combined.groupby("champion", as_index=False).sum()
    combined["deaths"] = combined["deaths"].replace(0, 1)
    combined["KDA"] = (combined["kills"] + combined["assists"]) / combined["deaths"]
    top20 = combined.sort_values("KDA", ascending=False).head(20)

    plt.figure()
    plt.bar(top20["champion"], top20["KDA"])
    plt.xlabel("Champion")
    plt.ylabel("KDA")
    plt.title("Top 10 Champions Across All Roles")
    plt.tick_params(axis="x", rotation=90) 
    plt.show()
    
def Champ_collective():# This one gets you the different picks based on what side they are on! (Has been swaped out for something else)
    side_pick_rates = "Champ_selected_folder/Pick_rates_different_sides"
    folder = "Champ_selected_folder"

    os.makedirs(folder, exist_ok=True)
    os.makedirs(side_pick_rates, exist_ok=True)

    for role, path in roles.items():
        df = pd.read_csv(path)

        champ_counts = df["champion"].value_counts().reset_index()
        champ_counts.columns = ["champion", "times_chosen"]
        champ_counts.to_csv(os.path.join(folder, f"{role}_counts.csv"), index=False)

        champ_side = (
            df.groupby(["champion", "side"])
            .size()
            .reset_index(name="times_chosen")
        )

        champ_side.to_csv(os.path.join(side_pick_rates, f"{role}_champion_side_counts.csv"), index=False)

def Vissulasation_of_champ_data():
    folder = "Champ_selected_folder"

    fig, axes = plt.subplots(1, len(roles), figsize=(40, 5))

    for ax, (role, path) in zip(axes, roles.items()):
        df = pd.read_csv(os.path.join(folder, f"{role}_counts.csv")) # ROLES!!!
        df = df.sort_values("times_chosen", ascending=False).head(10)# Keep only top 10 champions

        ax.bar(df["champion"], df["times_chosen"]) # lets us store the name of the champs
        ax.set_title(role.capitalize())
        ax.set_xlabel("Champion")
        ax.set_ylabel("Times Picked")
        ax.tick_params(axis="x", rotation=90) 

    plt.tight_layout()
    plt.show()

def Dispaly_winrate_based_on_side():
    pass



def Get_rates_bluevsred_winrate():
    pass


def champion_combos():
    Winrate_path = "/Winrates"
    cleaned_data = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')
    columns_to_check = ['champion', 'result', 'position']  # List of columns to extract

    total_champ_wins = cleaned_data[columns_to_check][cleaned_data['result'] == 1]['champion'].value_counts()
    total_champ_losses = cleaned_data[columns_to_check][cleaned_data['result'] == 0]['champion'].value_counts()
    total_champ_pick = cleaned_data[columns_to_check]['champion'].value_counts()


    for champion in total_champ_wins.index:
        picked = total_champ_pick.get(champion)

        good_wins = total_champ_wins.get(champion, 0)  # Get wins for the champion, default to 0 if not found
        good_losses = total_champ_losses.get(champion, 0)  # Get losses for the champion, default to 0 if not found
        good_win_rate = (good_wins / picked) * 100 if picked > 0 else 0  # Calculate win rate, handle division by zero



        bad_wins = total_champ_wins.get(champion, 0) # Get wins for the champion, default to 0 if not found
        bad_losses = total_champ_losses.get(champion, 0) # Get losses for the champion, default to 0 if not found
        bad_win_rate = (bad_wins / picked) * 100 if picked > 0 else 0  # Calculate win rate, handle division by zero


        print(f"Champion: {champion}, Total Picks: {picked}, Wins: {good_wins}, Losses: {good_losses},  Win Rate: {good_win_rate:.2f}%")
        print("---------------------------------------------------------------------")
        print(f'Champion: {champion}, Total Picks: {picked}, Losses: {bad_losses}, Wins: {bad_wins},  Loss Rate: {100 - bad_win_rate:.2f}%')

def champ_winrates_graph():
    cleaned_data = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')

    total_champ_wins = cleaned_data[cleaned_data['result'] == 1]['champion'].value_counts()
    total_champ_losses = cleaned_data[cleaned_data['result'] == 0]['champion'].value_counts()
    total_champ_pick = cleaned_data['champion'].value_counts()

    data = []

    for champion, picks in total_champ_pick.items():
        wins = total_champ_wins.get(champion, 0)
        losses = total_champ_losses.get(champion, 0)

        if picks > 0:
            winrate = (wins / picks) * 100
            lossrate = (losses / picks) * 100
            data.append((champion, picks, winrate, lossrate))

    df = pd.DataFrame(data, columns=["Champion", "Picks", "WinRate", "LossRate"])

    # Optional filter to remove champions with very few games
    df = df[df["Picks"] >= 10]

    top_win = df.sort_values("WinRate", ascending=False).head(10)
    top_loss = df.sort_values("LossRate", ascending=False).head(10)

    # Highest winrate
    plt.figure()
    plt.bar(top_win["Champion"], top_win["WinRate"])
    plt.title("Top 10 Champions by Win Rate")
    plt.xlabel("Champion")
    plt.ylabel("Win Rate (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Highest lossrate
    plt.figure()
    plt.bar(top_loss["Champion"], top_loss["LossRate"])
    plt.title("Top 10 Champions by Loss Rate")
    plt.xlabel("Champion")
    plt.ylabel("Loss Rate (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
def induvidual_roles():
    cleaned_data = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')

    # Group by position and champion
    role_stats = (
        cleaned_data
        .groupby(['position', 'champion'])
        .agg(
            picks=('result', 'count'),
            wins=('result', 'sum')
        )
        .reset_index()
    )

    # Calculate winrate
    role_stats['winrate'] = (role_stats['wins'] / role_stats['picks']) * 100

    #remove champions with very few games
    role_stats = role_stats[role_stats['picks'] >= 10]

    roles = role_stats['position'].unique()
    for role in roles:
        role_data = role_stats[role_stats['position'] == role]

        top = role_data.sort_values('winrate', ascending=False).head(5)

        plt.figure()
        plt.bar(top['champion'], top['winrate'])
        plt.title(f"Top 5 Champions in {role} by Win Rate")
        plt.xlabel("Champion")
        plt.ylabel("Win Rate (%)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
Vissulasation_of_champ_data()
#Champ_collective()
#Champ_save()
#Dispaly_winrate_based_on_side()
#Get_rates_bluevsred_winrate()
#champion_combos()
#champ_winrates_graph()
#grath_KDA_stats()
#induvidual_roles()

# due to how messy the code got i desided to rewrite it or the win-rate parts ar being written somewhere else