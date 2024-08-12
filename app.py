from bs4 import BeautifulSoup
from collections import Counter
from datetime import date
from flask import *
from functions import *
import json
import matplotlib.pyplot as plt
import re
import requests
from wordcloud import WordCloud

app = Flask(__name__)
app.secret_key = "AO3Wrapped"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/bookmarks')
def bookmarks():
    return render_template('bookmarks.html')

@app.route('/bookmarks', methods=['POST'])
def bookmarksWrapped():
    username = request.form['username']
    s = requests.session()

    # Checking if username provided is valid
    login_check = s.get(f'https://archiveofourown.org/users/{username}/bookmarks').text
    login_check_soup = BeautifulSoup(login_check, 'lxml')
    if login_check_soup.find('div', class_='system errors error-404 region'):
        flash("Your username is invalid. Please try again!")
        return redirect('/bookmarks', code=302)
    if '0 Bookmarks by' in login_check_soup.find('div', class_='bookmarks-index dashboard filtered region').text:
        flash("Sorry, it doesn't look like you have any public bookmarks!")
        return redirect('/bookmarks', code=302)

    if request.form['timeframe'] == 'All time':
        fanfics = scrapeAllFanfics(username, 'bookmarks', s)
    if request.form['timeframe'] == 'This year':
        fanfics = scrapeFanficsByYear(username, 'bookmarks', s)

    fandoms = []
    ratings = []
    categories = []
    ships = []
    characters = []
    freeforms = []
    access_months = []
    total_word_count = 0


    for fanfic in fanfics:
        fandoms.extend(fanfic.fandoms)
        ratings.append(fanfic.rating)
        categories.extend(fanfic.categories)
        ships.extend(fanfic.relationships)
        characters.extend(fanfic.characters)
        freeforms.extend(fanfic.freeforms)
        total_word_count += fanfic.wordcount
        access_months.append(fanfic.access_date[1])

    generateWordcloud(freeforms)

    labels = []
    values = []

    category_freqs = sortedFrequencyList(categories)
    for category, freq in category_freqs:
        labels.append(category)
        values.append(freq)

    month_abbrevs = {'Jan': 'January',
                     'Feb': 'February',
                     'Mar': 'March',
                     'Apr': 'April',
                     'May': 'May',
                     'Jun': 'June',
                     'Jul': 'July',
                     'Aug': 'August',
                     'Sep': 'September',
                     'Oct': 'October',
                     'Nov': 'November',
                     'Dec': 'December'}

    return render_template('wrapped.html',
                           timeframe = request.form['timeframe'],
                           total_fanfic_amount = len(fanfics),
                           total_word_count = total_word_count,
                           total_word_count_string = f'{total_word_count:,d}',
                           fandoms = sortedFrequencyList(fandoms)[0:5],
                           ships = sortedFrequencyList(ships)[0:5],
                           month = month_abbrevs[sortedFrequencyList(access_months)[0][0]],
                           ratings = frequenciesToPercents(ratings),
                           categories = labels,
                           frequencies = values)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/history', methods=['POST'])
def historyWrapped():
    username = request.form['username']
    password = request.form['password']

    login_url = 'https://archiveofourown.org/users/login'

    s = requests.session()

    login_req = s.get(login_url).text
    login_req_soup = BeautifulSoup(login_req, 'lxml')

    # Authenticity token
    token = login_req_soup.find('input', type='hidden').get('value')

    payload = {
        'authenticity_token': token,
        'user[login]': username,
        'user[password]': password,
        'user[remember_me]': 1,
        'commit': 'Log in'
    }

    # Logging into AO3.
    s.post(login_url, data=payload)

    # Checking if login credentials provided are valid
    login_check = s.get(f'https://archiveofourown.org/{username}/readings').text
    login_check_soup = BeautifulSoup(login_check, 'lxml')
    if login_check_soup.find('body', class_='logged-out'):
        flash('Your username and/or password is incorrect. Please try again!')
        return redirect('/history', code=302)

    if request.form['timeframe'] == 'All time':
        fanfics = scrapeAllFanfics(username, 'readings', s)
    if request.form['timeframe'] == 'This year':
        fanfics = scrapeFanficsByYear(username, 'readings', s)

    fandoms = []
    ratings = []
    categories = []
    ships = []
    characters = []
    freeforms = []
    access_months = []
    total_word_count = 0


    for fanfic in fanfics:
        fandoms.extend(fanfic.fandoms)
        ratings.append(fanfic.rating)
        categories.extend(fanfic.categories)
        ships.extend(fanfic.relationships)
        characters.extend(fanfic.characters)
        freeforms.extend(fanfic.freeforms)
        total_word_count += fanfic.wordcount
        access_months.append(fanfic.access_date[1])

    generateWordcloud(freeforms)

    labels = []
    values = []

    category_freqs = sortedFrequencyList(categories)
    for category, freq in category_freqs:
        labels.append(category)
        values.append(freq)

    month_abbrevs = {'Jan': 'January',
                     'Feb': 'February',
                     'Mar': 'March',
                     'Apr': 'April',
                     'May': 'May',
                     'Jun': 'June',
                     'Jul': 'July',
                     'Aug': 'August',
                     'Sep': 'September',
                     'Oct': 'October',
                     'Nov': 'November',
                     'Dec': 'December'}

    return render_template('wrapped.html',
                           timeframe = request.form['timeframe'],
                           total_fanfic_amount = len(fanfics),
                           total_word_count = total_word_count,
                           total_word_count_string = f'{total_word_count:,d}',
                           fandoms = sortedFrequencyList(fandoms)[0:5],
                           ships = sortedFrequencyList(ships)[0:5],
                           month = month_abbrevs[sortedFrequencyList(access_months)[0][0]],
                           ratings = frequenciesToPercents(ratings),
                           categories = labels,
                           frequencies = values)

if __name__ == '__main__':
    app.run(debug=True)