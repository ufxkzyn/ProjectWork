from flask import Blueprint, jsonify, render_template, request, Flask
import datetime
import os  # Import the os module to cehck if json file exist or not
import requests  # Import the requests module to make HTTP requests
from bs4 import BeautifulSoup  # Import BeautifulSoup from bs4 to parse HTML
import json  # Import the json module to work with JSON data
import re
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


