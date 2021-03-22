import time
import bs4
import pandas as pd
import regex as re
import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from chromedriver_py import binary_path

safety = 150 # How many review would you like to scrape per book?

# Goodreads reviews are, for some reason, labeled in html as such...
score_dict = {'it was amazing': 5,
              'really liked it': 4,
              'liked it': 3,
              'it was ok': 2,
              'did not like it': 1,
              '': None}

# A book's page lists only the top 30 reviews. Upon request, the next 30 reviews are retrieved
# asynchronously. In order to deal with these Ajax requests, a driver is necessary.
driver = webdriver.Chrome(executable_path=binary_path)

compiled_list = []

class GR_Spider(scrapy.Spider):
    name = 'gr_spider'

    def start_requests(self):
        # Looking at two books for now.
        start_urls = ['https://www.goodreads.com/book/show/7235533-the-way-of-kings', 'https://www.goodreads.com/book/show/44767458-dune']
        
        for url in start_urls:
            yield scrapy.Request(url = url, callback = self.compile_reviews)
        
        
    def compile_reviews(self, response):
    # Groups review text with associated score and book title.
        print('Compiling review data...')

        star_counts = {1: 0,
                       2: 0,
                       3: 0,
                       4: 0,
                       5: 0}

        def get_book_data(soup):
        # Retrieves overview data for a given book, including title, year of publication, and
        # associated genre tags (as determined by users).
            title = ''
            year = ''
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

        def scrape_current_page(page):
        # Scrapes review data from current "page" and appends them to compiled_list along with book data.
            soup = bs(driver.page_source, 'lxml')
            review_list = soup.find_all('div', {'class': 'review'})
            print(f'Found {len(review_list)} total {page}-star reviews.')
            for review in review_list:
                cap = int(safety/5) # Max reviews per score-level
                score = get_score(review)
                text = get_text(review)
                likes = get_likes(review)
                date = get_date(review)
                shelves = get_shelves(review)
                total_reviews = sum(star_counts.values())
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

        # Now we get to scraping our reviews. Instead of going page-by-page like before, we now use
        # GoodRead's filter system to look at the top reviews from each score-level.
        driver.get(response.url)
        soup = bs(response.text, 'lxml')
        
        title, year, genres = get_book_data(soup)
        
        page_counter = 1
        while page_counter <= 5:
            buffer = 3
            try:
                if sum(star_counts.values()) >= safety: break # Just to be safe...
                filters = driver.find_element_by_link_text('More filters')
                ActionChains(driver).move_to_element(filters).perform()
                if page_counter == 1:
                    driver.find_element_by_partial_link_text('1 star').click()
                else:
                    driver.find_element_by_partial_link_text((str(page_counter)+' stars ')).click()
                time.sleep(buffer) # Page needs to load.
                scrape_current_page(page_counter)
                print(f"Successfully scraped {star_counts[page_counter]} reviews!")
                try: driver.find_element_by_id('clearFilterbutton').click()
                except NoSuchElementException:
                    print("Error: Slow internet. Let's try that again...")
                    if buffer < 10: buffer += 1
                    continue
                time.sleep(buffer)
                page_counter += 1
            except NoSuchElementException:
                print('NoSuchElementException (likely a pop-up). Refreshing page. Standby...')
                driver.get(response.url)
                continue

        return

def main():
    process = CrawlerProcess()
    process.crawl(GR_Spider)
    process.start()

    print('Putting together your dataframe...')
    compiled_df = pd.DataFrame(compiled_list)

    print('Ta-Da!')
    print()
    print(compiled_df.info(verbose = True))
    print()
    print(compiled_df.head())
    print(compiled_df.tail())

    compiled_df.to_csv(r'data/compiled_df.csv', index = False)

if __name__ == '__main__':
    main()
            

