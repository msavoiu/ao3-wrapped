from bs4 import BeautifulSoup
from collections import Counter
import requests

# AO3 WRAPPED FUNCTIONS

# Loops through all pages and collects information from HTML.
def getFromSoup(username, url_type, session): # url_type is either 'bookmarks' or 'readings'
    page_counter = 1 
    source = ''
    ships = []
    ratings = []
    fandoms = []

    # Loops through each page and calls specified function to create a list containing desired tags/information.
    while True:
        source = session.get(f'https://archiveofourown.org/users/{username}/{url_type}?page={page_counter}').text
        soup = BeautifulSoup(source, 'lxml')

        # Checking if the page is valid and actually contains works.
        # Initially wanted to check .source_code == 200, but the webpage still exists even if it's empty.
        if soup.find('div', class_='header module') is None:
            break

        # func_call = getFunc(soup)
        # func_call2 = getFunc2(soup)
        # func_call3 = getFunc3(soup)

        # scraped1 += func_call
        # scraped2 += func_call2
        # scraped3 += func_call3

        ships += getShips(soup)
        ratings += getRatings(soup)
        fandoms += getFandoms(soup)

        # Checking if pages are being properly looped through through the terminal. Remove before deployment.
        print("Page:", page_counter)
        page_counter += 1

    results = (ships, ratings, fandoms)

    return results

# RETRIEVAL FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------

# Returns a list of strings of all tagged fandoms.
def getFandoms(soup):
    fandom_headings = soup.find_all('h5', class_='fandoms heading')
    fandom_html = []
    fandom_tags = []

    for h5_tag in fandom_headings:
        fandom_html += h5_tag.find_all('a', class_='tag')

    for a_tag in fandom_html:
        fandom_tags.append(a_tag.text)

    return fandom_tags

# Returns a list of strings of all tagged relationships.
def getShips(soup):
     ship_tags = soup.find_all('li', class_='relationships')

     ships = []
     for tag in ship_tags:
          ships.append(tag.text)

     return ships

# Returns a list of strings containing all age ratings.
def getRatings(soup):
    required_tags = soup.find_all('span', class_='text')

    tag_list = []
    for tag in required_tags:
        tag_list.append(tag.text)

    rating_tags = []
    for tag in tag_list:
            if tag == "Explicit" or tag == "Mature" or tag == "Teen And Up Audiences" or tag == "General Audiences" or tag == "Not Rated":
                rating_tags.append(tag)
    
    return rating_tags

# Returns a list of strings containing all relationship type categories.
def getCategories(soup): # NEEDS FIXING
    required_tags = soup.find_all('span', class_='text')

    tag_list = []
    for tag in required_tags:
        tag_list.append(tag.text)

    category_tags = []
    for tag in tag_list:
            if 'M/M' or 'F/M' or 'F/F' or 'Gen' or 'Multi' in tag:
                category_tags.append(tag)

def getDates(soup):
    date_tags = []
    byline_headings = soup.find_all('h5', class_='byline heading')

    for h5_tag in byline_headings:
        datetime_tag = h5_tag.find_next('p')
        date_tags.append(datetime_tag.text)

    return date_tags

# Returns a list of strings of all tags of a particular type.
# tag_type can be 'relationships', 'characters', or 'freeforms'.
def getFreeformTags(soup):
    tags_html = []
    tags = []

    li_tag_html = soup.find_all('li', class_='freeforms')

    for li_tag in li_tag_html:
        a_tag = li_tag.find('a', class_='tag')
        tags_html.append(a_tag)

    for a_tag in tags_html:
        tags.append(a_tag.text)

    return tags

# SORTING FUNCTIONS ------------------------------------------------------------------------------------------------------------------------------------------------------------
                
# Returns the most commonly occuring item in a list as a dict with a size of 1.
def getMostFreq(list):
    frequency_dict = Counter(list)
    max = 0
    most_freq = {}

    for item, frequency in frequency_dict.items():
        if frequency > max:
             max = frequency
             most_freq.clear()
             most_freq[item] = frequency # this appends stuff instead of replacing what's already in the dict

    return most_freq

''' Returns a key-value pair dictionary containing items and their frequencies in
descending order.'''
def orderByFreq(list):
    frequency_dict = Counter(list)
    ordered_frequency_dict = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True) # From ChatGPT, figure out what all the stuff means later.
    return ordered_frequency_dict
    
# Returns a dict of X items with the highest frequencies.
def getTopDict(list):
    freq_dict = Counter(list)
    ordered_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)

    counter = 0
    top_freq_dict = {}

    for item, freq in ordered_dict:
        if len(list) < 5:
            if counter >= len(list):
                break
        else:
            if counter >= 5:
                break
        top_freq_dict[item] = freq
        counter += 1

    return top_freq_dict

# Prints out items in a list like "1. Item one / 2. Item two / 3. Item three..."
def printTopList(list, statement):
    freq_dict = Counter(list)
    ordered_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
    ordinal_num = 1
    print(statement)
    for item, freq in ordered_dict:
        if len(ordered_dict) < 5:
            if ordinal_num > len(list):
                break
        else:
            if ordinal_num > 5:
                break
        print(f"{ordinal_num}. {item}")
        ordinal_num += 1

''' Same as above but with frequencies included as '(__ works)'. rank_counter is
meant to be getRankCounter()'s return value.'''
def printTopListWithFreq(list, statement):
    freq_dict = Counter(list)
    ordered_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
    ordinal_num = 1
    print(statement)
    for item, freq in ordered_dict:
        if len(ordered_dict) < 5:
            if ordinal_num > len(list):
                break
        else:
            if ordinal_num > 5:
                break
        print(f"{ordinal_num}. {item} ({freq} works)")
        ordinal_num += 1