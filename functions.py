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

        # Check if the page has content
        if soup.find('div', class_='header module') is None:
            break

        # Check if page has any works saved during the current year
        all_dates = []
        if url_type == 'bookmarks':
            for div in soup.find_all('div', class_='user module group'):
                all_dates.append(div.find('p', class_='datetime').text)
        elif url_type == 'readings':
            for h4 in soup.find_all('h4', class_='viewed heading'):
                all_dates.append(h4.text)

        if not any(year in date for date in all_dates):
            break

        blurbs = soup.find_all('li', role='article')

        # Remove deleted and mystery works
        index = 0
        deletion_indices = []

        for blurb in blurbs:
            if url_type == 'bookmarks':
                if (year not in blurb.find('div', class_='user module group').find('p', class_='datetime').text or
                    'This has been deleted, sorry!' in blurb.text or
                    'Mystery Work' in blurb.text):
                    deletion_indices.append(index)
            elif url_type == 'readings':
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
            elif url_type == 'readings':
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

        # Checks if the page has any content
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
            elif url_type == 'readings':
                if ('Deleted work,' in blurb.text or
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
            elif url_type == 'readings':
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
    wordcloud = WordCloud(width=1920, height=1080,
                          background_color='white',
                          max_words=30,
                          color_func=lambda *args, **kwargs: (156,20,24),
                          font_path='static/fonts/LucidaGrande.ttf').generate_from_frequencies(Counter(tags))

    # Display the word cloud
    plt.figure(figsize=(16, 9))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Remove axes

    plt.savefig('static/images/wordcloud.png',
                bbox_inches='tight')
    print("Word cloud saved to 'static/images/wordcloud.png'")
