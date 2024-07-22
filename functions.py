from bs4 import BeautifulSoup
from collections import Counter
from datetime import date
import matplotlib.pyplot as plt
from wordcloud import WordCloud

class Fanfiction:
    def __init__(self, link, title, author, fandoms, rating, categories, relationships,
                 characters, freeforms, wordcount, access_date):
        self.link = f'archiveofourown.org{link}'
        self.title = title
        self.author = author
        self.fandoms = fandoms
        self.rating = rating
        self.categories = categories
        self.relationships = relationships
        self.characters = characters
        self.freeforms = freeforms
        self.wordcount = wordcount
        self.access_date = access_date

def scrapeFanficsByYear(username, url_type, session):
    year = str(date.today().year)
    print('The year is', year)
    counter = 1
    source = ''
    fanfics = []

    while True:
        source = session.get(f'https://archiveofourown.org/users/{username}/{url_type}?page={counter}').content
        soup = BeautifulSoup(source, 'lxml')

        # Checks if the page has content
        if soup.find('div', class_='header module') is None:
            break

        blurbs = soup.find_all('li', role='article')

        # Removing deleted and mystery works
        index = 0
        deletion_indices = []

        for blurb in blurbs:
            if url_type == 'bookmarks':
                if (year not in blurb.find('div', class_='user module group').find('p', class_='datetime').text or
                    'This has been deleted, sorry!' in blurb.text or
                    'Mystery Work' in blurb.text):
                    deletion_indices.append(index)
            if url_type == 'readings':
                if (year not in blurb.find('div', class_='user module group').find('h4', class_='viewed heading').text or
                    'This has been deleted, sorry!' in blurb.text or
                    'Mystery' in blurb.text):
                    deletion_indices.append(index)
            index += 1

        # Items need to be deleted in reverse order so as not to throw off
        # subsequent indices
        for index in sorted(deletion_indices, reverse=True):
            del blurbs[index]

        # Prints title for command-line testing
        for blurb in blurbs:
            # ↓ link provided as relative path
            link = blurb.find('h4', class_='heading').find('a').get('href')
            # print(link)

            title = blurb.find('div', class_='header module').find('a').text
            # print(title)

            if blurb.find('a', rel='author') is None:
                author = 'Anonymous'
            else:
                author = blurb.find('a', rel='author').text
            # print(author)

            fandoms = blurb.find('h5', class_='fandoms heading').find_all('a', class_='tag')
            for index, fandom in enumerate(fandoms):
                fandoms[index] = fandom.text
                # print(fandoms)

            required_tags = blurb.find('ul', class_='required-tags')
            rating = required_tags.find('span', class_='text').text
            # print(rating)
            
            for span in required_tags.find_all('span'):
                if 'category' in span.get('class'):
                    categories = [category.strip() for category in span.text.split(',')]
            # print(categories)
            
            relationships = []
            for tag in blurb.find_all('li', class_='relationships'):
                relationships.append(tag.text)
            # print(relationships)

            characters = []
            for tag in blurb.find_all('li', class_='characters'):
                characters.append(tag.text)
            # print(characters)

            freeforms = []
            for tag in blurb.find_all('li', class_='freeforms'):
                freeforms.append(tag.text)
            # print(freeforms)

            wordcount = int(blurb.find('dd', class_='words').text.replace(',', ''))
            # print(wordcount)

            date_text = blurb.find('div', class_='user module group')
            if url_type == 'bookmarks':
                date_text = date_text.find('p', class_='datetime').text
                access_date = tuple(date_text.split())
            if url_type == 'readings':
                date_text = date_text.find('h4', class_='viewed heading').text
                access_date = tuple(date_text[14:26].split())
            # print(access_date)

            fanfic_object = Fanfiction(link, title, author, fandoms, rating,
                                    categories, relationships, characters,
                                    freeforms, wordcount, access_date)

            fanfics.append(fanfic_object)

        print("Page:", counter) # for debugging
        counter += 1

    return fanfics

def scrapeAllFanfics(username, url_type, session):
    counter = 1
    source = ''
    fanfics = []

    while True:
        source = session.get(f'https://archiveofourown.org/users/{username}/{url_type}?page={counter}').content
        soup = BeautifulSoup(source, 'lxml')

        # Checks if the page has content
        if soup.find('div', class_='header module') is None:
            break

        blurbs = soup.find_all('li', role='article')

        # Removing deleted and mystery works
        index = 0
        deletion_indices = []

        for blurb in blurbs:
            if url_type == 'bookmarks':
                if ('This has been deleted, sorry!' in blurb.text or
                    'Mystery Work' in blurb.text):
                    deletion_indices.append(index)
            if url_type == 'readings':
                if ('This has been deleted, sorry!' in blurb.text or
                    'Mystery' in blurb.text):
                    deletion_indices.append(index)
            index += 1

        # Items need to be deleted in reverse order so as not to throw off
        # subsequent indices
        for index in sorted(deletion_indices, reverse=True):
            del blurbs[index]

        # Prints title for command-line testing
        for blurb in blurbs:
            # ↓ link provided as relative path
            link = blurb.find('h4', class_='heading').find('a').get('href')
            # print(link)

            title = blurb.find('div', class_='header module').find('a').text
            # print(title)

            if blurb.find('a', rel='author') is None:
                author = 'Anonymous'
            else:
                author = blurb.find('a', rel='author').text
            # print(author)

            fandoms = blurb.find('h5', class_='fandoms heading').find_all('a', class_='tag')
            for index, fandom in enumerate(fandoms):
                fandoms[index] = fandom.text
            # print(fandoms)

            required_tags = blurb.find('ul', class_='required-tags')
            rating = required_tags.find('span', class_='text').text
            # print(rating)
            
            for span in required_tags.find_all('span'):
                if 'category' in span.get('class'):
                    categories = [category.strip() for category in span.text.split(',')]
            # print(categories)
            
            relationships = []
            for tag in blurb.find_all('li', class_='relationships'):
                relationships.append(tag.text)
            # print(relationships)

            characters = []
            for tag in blurb.find_all('li', class_='characters'):
                characters.append(tag.text)
            # print(characters)

            freeforms = []
            for tag in blurb.find_all('li', class_='freeforms'):
                freeforms.append(tag.text)
            # print(freeforms)

            wordcount = int(blurb.find('dd', class_='words').text.replace(',', ''))
            # print(wordcount)

            date_text = blurb.find('div', class_='user module group')
            if url_type == 'bookmarks':
                date_text = date_text.find('p', class_='datetime').text
                access_date = tuple(date_text.split())
            if url_type == 'readings':
                date_text = date_text.find('h4', class_='viewed heading').text
                access_date = tuple(date_text[14:26].split())
            # print(access_date)

            fanfic_object = Fanfiction(link, title, author, fandoms, rating,
                                    categories, relationships, characters,
                                    freeforms, wordcount, access_date)

            fanfics.append(fanfic_object)

        print("Page:", counter) # for debugging
        counter += 1
    return fanfics

def sortedFrequencyList(mylist):
    return sorted(Counter(mylist).items(), key=lambda x: x[1], reverse=True)

def frequenciesToPercents(mylist):
    frequencies = sortedFrequencyList(mylist)
    total_frequency = sum(frequency for item, frequency in frequencies)

    percent_frequencies = []
    for item, frequency in frequencies:
        percent = round((frequency / total_frequency) * 100, 1) # whole number % rounded one decimal
        percent_frequencies.append((item, percent))
    
    return percent_frequencies

def generateWordcloud(tags):
    wordcloud = WordCloud(width=1920, height=1920,
                          background_color='white',
                          max_words=50,
                          color_func=lambda *args, **kwargs: (156,20,24),
                          font_path='static/fonts/LucidaGrande.ttf').generate_from_frequencies(Counter(tags))

    # Display the word cloud
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Remove axes

    plt.savefig('static/images/wordcloud.png')
    print("Word cloud saved to 'static/images/wordcloud.png'")

# # Loops through all pages and collects information from HTML.
# def getFromSoup(username, url_type, session): # url_type = 'bookmarks' or 'readings'
#     page_counter = 1 
#     source = ''
#     ships = []
#     ratings = []
#     fandoms = []

#     # Loops through each page and calls specified function to create a list containing desired tags/information.
#     while True:
#         source = session.get(f'https://archiveofourown.org/users/{username}/{url_type}?page={page_counter}').text
#         soup = BeautifulSoup(source, 'lxml')

#         # Checking if the page is valid and actually contains works.
#         # Initially wanted to check .source_code == 200, but the webpage still exists even if it's empty.
#         if soup.find('div', class_='header module') is None:
#             break

#         # func_call = getFunc(soup)
#         # func_call2 = getFunc2(soup)
#         # func_call3 = getFunc3(soup)

#         # scraped1 += func_call
#         # scraped2 += func_call2
#         # scraped3 += func_call3

#         ships += getShips(soup)
#         ratings += getRatings(soup)
#         fandoms += getFandoms(soup)

#         # Checking if pages are being properly looped through through the terminal. Remove before deployment.
#         print("Page:", page_counter)
#         page_counter += 1

#     results = (ships, ratings, fandoms)

#     return results

# RETRIEVAL FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------

# # Returns a list of strings of all tagged fandoms.
# def getFandoms(soup):
#     fandom_headings = soup.find_all('h5', class_='fandoms heading')
#     fandom_html = []
#     fandom_tags = []

#     for h5_tag in fandom_headings:
#         fandom_html += h5_tag.find_all('a', class_='tag')

#     for a_tag in fandom_html:
#         fandom_tags.append(a_tag.text)

#     return fandom_tags

# # Returns a list of strings of all tagged relationships.
# def getShips(soup):
#      ship_tags = soup.find_all('li', class_='relationships')

#      ships = []
#      for tag in ship_tags:
#           ships.append(tag.text)

#      return ships

# # Returns a list of strings containing all age ratings.
# def getRatings(soup):
#     required_tags = soup.find_all('span', class_='text')

#     tag_list = []
#     for tag in required_tags:
#         tag_list.append(tag.text)

#     rating_tags = []
#     for tag in tag_list:
#             if tag == "Explicit" or tag == "Mature" or tag == "Teen And Up Audiences" or tag == "General Audiences" or tag == "Not Rated":
#                 rating_tags.append(tag)
    
#     return rating_tags

# # Returns a list of strings containing all relationship type categories.
# def getCategories(soup): # NEEDS FIXING
#     required_tags = soup.find_all('span', class_='text')

#     tag_list = []
#     for tag in required_tags:
#         tag_list.append(tag.text)

#     category_tags = []
#     for tag in tag_list:
#             if 'M/M' or 'F/M' or 'F/F' or 'Gen' or 'Multi' in tag:
#                 category_tags.append(tag)

# def getDates(soup):
#     date_tags = []
#     byline_headings = soup.find_all('h5', class_='byline heading')

#     for h5_tag in byline_headings:
#         datetime_tag = h5_tag.find_next('p')
#         date_tags.append(datetime_tag.text)

#     return date_tags

# # Returns a list of strings of all tags of a particular type.
# # tag_type can be 'relationships', 'characters', or 'freeforms'.
# def getFreeformTags(soup):
#     tags_html = []
#     tags = []

#     li_tag_html = soup.find_all('li', class_='freeforms')

#     for li_tag in li_tag_html:
#         a_tag = li_tag.find('a', class_='tag')
#         tags_html.append(a_tag)

#     for a_tag in tags_html:
#         tags.append(a_tag.text)

#     return tags

# # SORTING FUNCTIONS ------------------------------------------------------------------------------------------------------------------------------------------------------------
                
# # Returns the most commonly occuring item in a list as a dict with a size of 1.
# def getMostFreq(list):
#     frequency_dict = Counter(list)
#     max = 0
#     most_freq = {}

#     for item, frequency in frequency_dict.items():
#         if frequency > max:
#              max = frequency
#              most_freq.clear()
#              most_freq[item] = frequency # this appends stuff instead of replacing what's already in the dict

#     return most_freq

# ''' Returns a key-value pair dictionary containing items and their frequencies in
# descending order.'''
# def orderByFreq(list):
#     frequency_dict = Counter(list)
#     ordered_frequency_dict = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True) # From ChatGPT, figure out what all the stuff means later.
#     return ordered_frequency_dict
    
# # Returns a dict of X items with the highest frequencies.
# def getTopDict(list):
#     freq_dict = Counter(list)
#     ordered_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)

#     counter = 0
#     top_freq_dict = {}

#     for item, freq in ordered_dict:
#         if len(list) < 5:
#             if counter >= len(list):
#                 break
#         else:
#             if counter >= 5:
#                 break
#         top_freq_dict[item] = freq
#         counter += 1

#     return top_freq_dict

# # Prints out items in a list like "1. Item one / 2. Item two / 3. Item three..."
# def printTopList(list, statement):
#     freq_dict = Counter(list)
#     ordered_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
#     ordinal_num = 1
#     print(statement)
#     for item, freq in ordered_dict:
#         if len(ordered_dict) < 5:
#             if ordinal_num > len(list):
#                 break
#         else:
#             if ordinal_num > 5:
#                 break
#         print(f"{ordinal_num}. {item}")
#         ordinal_num += 1

# ''' Same as above but with frequencies included as '(__ works)'. rank_counter is
# meant to be getRankCounter()'s return value.'''
# def printTopListWithFreq(list, statement):
#     freq_dict = Counter(list)
#     ordered_dict = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
    
#     ordinal_num = 1
#     print(statement)
#     for item, freq in ordered_dict:
#         if len(ordered_dict) < 5:
#             if ordinal_num > len(list):
#                 break
#         else:
#             if ordinal_num > 5:
#                 break
#         print(f"{ordinal_num}. {item} ({freq} works)")
#         ordinal_num += 1