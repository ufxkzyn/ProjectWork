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

bot = pd.read_csv('./Data/positiondata/bot_position_data.csv').filter(items=['goldat10', 'goldat15', 'goldat20', 'goldat25'])
top = pd.read_csv('./Data/positiondata/top_position_data.csv').filter(items=['goldat10', 'goldat15', 'goldat20', 'goldat25'])
mid = pd.read_csv('./Data/positiondata/mid_position_data.csv').filter(items=['goldat10', 'goldat15', 'goldat20', 'goldat25'])
support = pd.read_csv('./Data/positiondata/sup_position_data.csv').filter(items=['goldat10', 'goldat15', 'goldat20', 'goldat25'])
jungle = pd.read_csv('./Data/positiondata/jng_position_data.csv').filter(items=['goldat10', 'goldat15', 'goldat20', 'goldat25'])


bot_stats = bot.describe()
top_stats = top.describe()
mid_stats = mid.describe()
support_stats = support.describe()
jungle_stats = jungle.describe()

""" 
sns.lineplot(data=bot_stats.loc['mean'], label='Bot')
sns.lineplot(data=top_stats.loc['mean'], label='Top')
sns.lineplot(data=mid_stats.loc['mean'], label='Mid')
sns.lineplot(data=support_stats.loc['mean'], label='Support')
sns.lineplot(data=jungle_stats.loc['mean'], label='Jungle')

plt.ylim(0, 15000)
plt.xlim(left = 0)
    
plt.show()

 """

for value in [bot, top, mid, support, jungle]:
    
    sns.lineplot(data=bot_stats[value], label='Bot')
    sns.lineplot(data=top_stats[value], label='Top')
    sns.lineplot(data=mid_stats[value], label='Mid')
    sns.lineplot(data=support_stats[value], label='Support')
    sns.lineplot(data=jungle_stats[value], label='Jungle')

plt.xlim(0, None) # Starts at 0, 'None' keeps the current maximum
plt.ylim(0, None)

plt.show()

