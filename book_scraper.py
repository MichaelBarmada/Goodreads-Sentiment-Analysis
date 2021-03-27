import time
import bs4
import requests
import pandas as pd
import regex as re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from chromedriver_py import binary_path

# Largely adapted from the following...
"""
Copyright (C) 2021 by Maria Antoniak: https://github.com/maria-antoniak/goodreads-scraper
Licensed under GPL v3.0: https://github.com/maria-antoniak/goodreads-scraper/blob/d9913023e956c2ff0bafad9220375a887bd4bc43/LICENSE
Accessed on 22 March 2021.
"""
# ...combining elements of both get_reviews.py and get_books.py

# Goodreads reviews are, for some reason, labeled in html as such...
score_dict = {'it was amazing': 5,
          'really liked it': 4,
          'liked it': 3,
          'it was ok': 2,
          'did not like it': 1,
          '': None}

safety = 120 # How many review would you like to scrape per book?
cap = int(safety/5) # Max reviews per score-level

compiled_list = []

# A book's page lists only the top 30 reviews. Upon request, the next 30 reviews are retrieved
# asynchronously. In order to deal with these Ajax requests, we need a driver to interact with
# the browser for us.
driver = webdriver.Chrome(executable_path=binary_path)

def compile_reviews(response):
# Here we actually scrape our reviews. Instead of going page-by-page like before, we now use
# GoodRead's filter system to look at the top reviews from each score-level.

    star_counts = {1: 0,
                   2: 0,
                   3: 0,
                   4: 0,
                   5: 0}

    def get_book_data(soup):
    # Retrieves overview data for a given book, including title, year of publication, and
    # associated genre tags (as determined by users).
        genres = []
        title = soup.find(id='bookTitle').text.strip()    
        try:
            pub_data = soup.find('nobr', {'class':'greyText'}).string
        except (NoSuchElementException, AttributeError): 
            pub_data = soup.find('div', {'id':'details'}).find_all('div', {'class':'row'})[1].string
        year = re.search('([0-9]{4})', pub_data).group(1)
        if len(soup.find_all('a', {'class': 'actionLinkLite bookPageGenreLink'})) >0:
            for g in soup.find_all('a', {'class': 'actionLinkLite bookPageGenreLink'}):
                genres.append(g.text)   
        return title, year, genres

    def get_text(review):
    # Retrieves the text of the current review. Returns an empty string if there is none.
        display_text = ''
        full_text = ''
        if len(review.find_all('span', {'class': 'readable'})) > 0:
            for child in review.find_all('span', {'class': 'readable'})[0].children:
                if child.name == 'span' and 'style' not in child:
                    display_text = child.text
                if child.name == 'span' and child.get('style') and child['style'] == 'display:none':
                    full_text = child.text
        if full_text:
            return full_text
        return display_text

    def get_score(review):
    # Retrieves each review's score out of five stars.
        if len(review.find_all('span', {'class': 'staticStars'})) > 0:
            rating = review.find_all('span', {'class': 'staticStars'})[0]['title']
            return score_dict[rating]
        return ''

    def get_likes(review):
    # Finds no. of likes for each review.
        if len(review.find_all('span', {'class': 'likesCount'})) > 0:
            likes = review.find_all('span', {'class': 'likesCount'})[0].text
            return likes
        return ''

    def get_date(review):
    # Finds when each review was published.
        if len(review.find_all('a', {'class': 'reviewDate createdAt right'})) > 0:
            return review.find_all('a', {'class': 'reviewDate createdAt right'})[0].text
        return ''

    def get_shelves(review):
    # For each review, finds all 'shelves' in which the reviewer has placed said book.
        shelves = []       
        if review.find('div', {'class': 'uitext greyText bookshelves'}):
            _shelves_review = review.find('div', {'class': 'uitext greyText bookshelves'})
            for _shelf_review in _shelves_review.find_all('a'):
                shelves.append(_shelf_review.text)
        return shelves

    def scrape_current_page(soup, page):
    # Scrapes review data from current "page" and appends them to compiled_list along with book data.
        review_list = soup.find_all('div', {'class': 'review'})
        if page: print(f'Found {len(review_list)} total {page}-star reviews.')
        for review in review_list:
            score = get_score(review)
            text = get_text(review)
            likes = get_likes(review)
            date = get_date(review)
            shelves = get_shelves(review)
            if score in star_counts and star_counts[score] < cap and text != '':
                star_counts[score] += 1 
                compiled_list.append({'Title':title,
                                     'Year':year,
                                     'Genres':genres,
                                     'Rating':score,
                                     'Likes':likes,
                                     'Date':date,
                                     'Shelves':shelves,
                                     'Text':text})
        return

    driver.get(response.url)
    soup = bs(driver.page_source, 'lxml')
    title, year, genres = get_book_data(soup)
    print(f'Compiling review data for {title}...')
    print('Scraping first page...`')
    scrape_current_page(soup, False)
    for k in star_counts.keys():
        print('\t',k,'star:\t',star_counts[k])
    score_counter = 1
    while score_counter <= 5 and sum(star_counts.values()) < safety:
        try:
            filters = driver.find_element_by_link_text('More filters')
            ActionChains(driver).move_to_element(filters).perform()
            if score_counter == 1:
                driver.find_element_by_partial_link_text('1 star').click()
            else:
                driver.find_element_by_partial_link_text((str(score_counter)+' stars ')).click()
            time.sleep(3) # Page needs to load.
            soup = bs(driver.page_source, 'lxml')
            current_filter = soup.find('div', {'class':'reviewSearchResults__count'})
            if current_filter is None or str(score_counter) not in current_filter.b.string: # Make sure new data has actually loaded
                buffer = 3
                while buffer < 7:
                    print('Buffering...')
                    time.sleep(buffer)
                    soup = bs(driver.page_source, 'lxml')
                    current_filter = soup.find('div', {'class':'reviewSearchResults__count'})
                    if current_filter is None or str(score_counter) not in current_filter.b.string:
                        buffer += 1
                        continue
                    else:
                        break
                if buffer == 7:
                    print("Clearing filters and trying again...")
                    driver.find_element_by_id('clearFilterbutton').click()
                    time.sleep(3)
                    continue
            scrape_current_page(soup, score_counter)
            print(f"Successfully scraped {star_counts[score_counter]} reviews!")
            for k in star_counts.keys():
                print('\t',k,'star:\t',star_counts[k])
            score_counter+= 1
            continue
        except NoSuchElementException:
            print('NoSuchElementException (likely a pop-up). Refreshing page. Standby...')
            driver.get(response.url)
            continue
        except ElementNotInteractableException:
            print('ElementNotInteractableException. Cooling down 30 secs and refreshing page. Standby...')
            for i in len(30):
                time.sleep(1)
                print(str(i+1)+'...')
            driver.get(response.url)
            continue
    print(f"All done for {title}! Here's a preview of your DataFrame...\n")
    update_df = pd.DataFrame(compiled_list)
    print(update_df.info())
    print(update_df.Title.value_counts())    
    return

def find_links(response):
    base_url = 'https://www.goodreads.com'
    url_parsed = requests.get(response)
    soup = bs(url_parsed.text, 'lxml')
    link_list = [link['href'] for link in soup.find_all('a', {'class':'bookTitle'}) if not re.search(r'\#[^1]\d?\)', link.text)] # We only want the first book in a series
    for link in link_list[21:]:
        print(base_url+link)
        compile_reviews(requests.get(base_url+link))
        backup_df = pd.DataFrame(compiled_list)
        backup_df.to_csv('data/backup_df.csv', index= False)
        time.sleep(10) # To avoid overloading Goodread's servers

def main():
    start_urls = ['https://www.goodreads.com/shelf/show/fantasy']
    for url in start_urls:
        find_links(url)
    driver.quit()
    print('Putting together your dataframe...')
    compiled_df = pd.DataFrame(compiled_list)
    print('Ta-Da!\n')
    print(compiled_df.info(verbose = True))
    print()
    print(compiled_df.head())
    print(compiled_df.tail())

    compiled_df.to_csv('data/compiled_df.csv', index = False)

if __name__ == '__main__':
    main()