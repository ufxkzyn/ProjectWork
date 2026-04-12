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

main_folder = ("Champwin_rate_folder")

def create_champ_winrate_files():
    output_folder = "Champwin_rate_folder"
    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')

    roles = ["top", "mid", "bot", "jng", "sup"]

    for role in roles:
        role_df = df[df['position'] == role]

        results = []
        for (champion, side), group in role_df.groupby(['champion', 'side']):
            picks = len(group)
            wins = (group['result'] == 1).sum()
            losses = (group['result'] == 0).sum()

            results.append({
                "champion": champion,
                "side": side,
                "picks": picks,
                "wins": wins,
                "losses": losses,
                "winrate": (wins / picks) * 100 if picks > 0 else 0
            })

        result_df = pd.DataFrame(results)

        path = os.path.join(output_folder, f"{role}_champion_stats.csv")
        result_df.to_csv(path, index=False)

        print(f"Saved: {path}")

def creat_champ_list_for_all():
    output_folder = "Champion_data_general"
    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_csv('./Data/2026_LoL_esports_match_data_cleaned.csv')

    roles = ["top", "mid", "bot", "jng", "sup"]

    for role in roles:
        role_df = df[df['position'] == role]

        results = []
        for champion, group in role_df.groupby('champion'):  # FIXED HERE
            picks = len(group)
            wins = (group['result'] == 1).sum()
            losses = (group['result'] == 0).sum()

            results.append({
                "champion": champion,
                "picks": picks,
                "wins": wins,
                "losses": losses,
                "winrate": (wins / picks) * 100 if picks > 0 else 0
            })

        result_df = pd.DataFrame(results)

        path = os.path.join(output_folder, f"{role}_champion_stats.csv")
        result_df.to_csv(path, index=False)

        print(f"Saved: {path}")

def plot_top10_winrates_per_role(folder="Champwin_rate_folder"):
    roles = ["top", "mid", "bot", "jng", "sup"]

    for role in roles:
        path = os.path.join(folder, f"{role}_champion_stats.csv")

        if not os.path.exists(path):
            print(f"Missing file: {path}")
            continue

        df = pd.read_csv(path)

        # Get top 10 champions by total picks (sum both sides)
        top_champs = (
            df.groupby('champion')['picks']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index
        )

        df = df[df['champion'].isin(top_champs)]

        # Pivot for plotting
        pivot = df.pivot(index='champion', columns='side', values='winrate').fillna(0)

        # Sort by average winrate (cleaner)
        pivot['avg'] = pivot.mean(axis=1)
        pivot = pivot.sort_values('avg', ascending=False)
        pivot = pivot.drop(columns='avg')

        # Plot
        pivot.plot(kind='bar')

        plt.title(f"{role.upper()} - Top 10 Champions (Blue vs Red Winrate)")
        plt.xlabel("Champion")
        plt.ylabel("Winrate (%)")
        plt.xticks(rotation=45)

        # Set colors manually
        for i, bar in enumerate(plt.gca().containers):
            if i == 0:
                for b in bar:
                    b.set_color('blue')
            elif i == 1:
                for b in bar:
                    b.set_color('red')

        plt.legend(title="Side")
        plt.tight_layout()
        plt.show()

def boxplot_winrates_per_role(folder="Champwin_rate_folder"):
    roles = ["top", "mid", "bot", "jng", "sup"]

    for role in roles:
        path = os.path.join(folder, f"{role}_champion_stats.csv")
        if not os.path.exists(path):
            continue

        df = pd.read_csv(path)

        # Top 10 champions by total picks
        top_champs = df.groupby('champion')['picks'].sum().sort_values(ascending=False).head(10).index
        df = df[df['champion'].isin(top_champs)]

        plt.figure(figsize=(8,6))
        ax = sns.boxplot(
            data=df,
            x='side',
            y='winrate',
            palette={"Blue": "skyblue", "Red": "lightcoral"}  # custom colors
        )

        # Optional: customize individual elements
        for patch, side in zip(ax.artists, df['side'].unique()):
            # Set edge color to make boxes pop
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)

        plt.title(f"{role.upper()} - Winrate Distribution (Top 10 Champs)")
        plt.xlabel("Side")
        plt.ylabel("Winrate (%)")
        plt.tight_layout()
        plt.show()

def plot_most_popular_champs(folder="Champion_data_general"):
    all_data = []

    # Load all role files
    for file in os.listdir(folder):
        if file.endswith("_champion_stats.csv"):
            df = pd.read_csv(os.path.join(folder, file))
            all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)

    # Combine same champions across roles
    combined = (
        combined.groupby('champion', as_index=False)
        .agg({'picks': 'sum'})
    )

    # Top 10 most picked
    top10 = combined.sort_values('picks', ascending=False).head(10)

    # Plot
    plt.figure()
    plt.bar(top10['champion'], top10['picks'])

    plt.title("Top 10 Most Picked Champions (All Roles)")
    plt.xlabel("Champion")
    plt.ylabel("Total Picks")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()    

def plot_most_popular_per_role(folder="Champion_data_general"):
    roles = ["top", "mid", "bot", "jng", "sup"]

    for role in roles:
        path = os.path.join(folder, f"{role}_champion_stats.csv")

        if not os.path.exists(path):
            print(f"Missing file: {path}")
            continue

        df = pd.read_csv(path)

        # Get top 10 by picks
        top10 = df.sort_values("picks", ascending=False).head(10)

        plt.figure()

        plt.bar(top10["champion"], top10["picks"])

        plt.title(f"{role.upper()} - Top 10 Most Picked Champions")
        plt.xlabel("Champion")
        plt.ylabel("Picks")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()


def plot_most_popular_champions():
    input_folder = 'Champion_data_general'
    output_folder = './Champwin_rate_folder'
    os.makedirs(output_folder, exist_ok=True)

    roles = ["top", "mid", "jng", "bot", "sup"]
    all_data = []

    # Load all role files
    for role in roles:
        path = os.path.join(input_folder, f"{role}_champion_stats.csv")
        df = pd.read_csv(path)
        all_data.append(df)

    combined_df = pd.concat(all_data)

    # Merge the roles
    combined = combined_df.groupby('champion').agg(
        total_picks=('picks', 'sum'),
        total_wins=('wins', 'sum')
    ).reset_index()

    # Clean champion names
    combined['champion'] = combined['champion'].astype(str)
    combined['champion'] = combined['champion'].str.replace(r"[()\']", "", regex=True)
    combined['champion'] = combined['champion'].str.strip()

    # Calculate winrate
    combined['winrate'] = combined['total_wins'] / combined['total_picks'] * 100

    # Filter out champions with fewer than 10 picks
    combined = combined[combined['total_picks'] >= 10]

    # Filter top 10 by winrate
    top_10 = combined.sort_values(by='winrate', ascending=False).head(10)

    # Sort so highest is on top (better visual)
    top_10 = top_10.sort_values(by='winrate')

    # Plot
    plt.figure(figsize=(12,6))
    bars = plt.barh(top_10['champion'], top_10['winrate'], color='dodgerblue')
    plt.xlabel('Winrate (%)')
    plt.title('Top 10 Champions by Winrate (All Roles)', fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Annotate bars with winrate
    for bar in bars:
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{bar.get_width():.1f}%', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'most_popular_champions.png'))
    plt.close()

def plot_lowest_winrate_champions():
    input_folder = 'Champion_data_general'
    output_folder = './Champwin_rate_folder'
    os.makedirs(output_folder, exist_ok=True)

    roles = ["top", "mid", "jng", "bot", "sup"]
    all_data = []

    for role in roles:
        path = os.path.join(input_folder, f"{role}_champion_stats.csv")
        df = pd.read_csv(path)
        all_data.append(df)

    combined_df = pd.concat(all_data)

    #merges the roles
    combined = combined_df.groupby('champion').agg(
    total_picks=('picks', 'sum'),
    total_wins=('wins', 'sum')
    ).reset_index()

    # Clean champion names
    combined['champion'] = combined['champion'].astype(str)
    combined['champion'] = combined['champion'].str.replace(r"[()\']", "", regex=True)
    combined['champion'] = combined['champion'].str.strip()

    # Calculate winrate
    combined['winrate'] = (combined['total_wins'] / combined['total_picks']) * 100

    # Calculate winrate
    combined['winrate'] = (combined['total_wins'] / combined['total_picks']) * 100

    # Filter low sample size
    combined = combined[combined['total_picks'] >= 20]

    # Sort ascending (lowest first) and take bottom 15
    bottom_10 = combined.sort_values(by='winrate').head(10)
    bottom_10 = bottom_10.sort_values(by='winrate')  # visual ascending

    # Plot
    plt.figure(figsize=(12,6))
    bars = plt.barh(bottom_10['champion'], bottom_10['winrate'], color='tomato')
    plt.xlabel('Winrate (%)')
    plt.title('Bottom 10 Winrate Champions', fontsize=14)
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Annotate bars
    for bar in bars:
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{bar.get_width():.1f}%', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'lowest_winrate_champions.png'))
    plt.close()
#plot_top10_winrates_per_role() # name is self explanitory
#boxplot_winrates_per_role() # same as the one above but returns box-plots instead
#create_champ_winrate_files() # if the data needs to be seperated use this to prep a file for the other functions
#creat_champ_list_for_all() #creats general information storage for uses in more wide spread graths
#plot_most_popular_champs() # makes a grath that shows the most picked champ ingeneral
#plot_most_popular_per_role()
#plot_most_popular_champions()
plot_lowest_winrate_champions()