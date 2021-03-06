import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import bs4
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd
from chromedriver_py import binary_path
import time

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
        start_urls = ['https://www.goodreads.com/book/show/7235533-the-way-of-kings','https://www.goodreads.com/book/show/44767458-dune']
        
        for url in start_urls:
            yield scrapy.Request(url = url, callback = self.compile_reviews)

            
    def compile_reviews(self, response):
    # Groups review text with associated score and book title.
        print('Compiling review data...')

        driver.get(response.url)
        
        url_parsed = bs(response.text, 'lxml')

        book_title = url_parsed.find(id='bookTitle').text.strip()

        star_counts = {1: 0,
                       2: 0,
                       3: 0,
                       4: 0,
                       5: 0}

        def scrape_current_page(driver, soup):
        # Scrapes review data from current "page" and appends them to compiled_list.
            if driver:
                source = driver.page_source
                soup = bs(source, 'lxml')
            review_list = soup.find_all('div', {'class': 'review'})
            for review in review_list:
                score = get_score(review)
                text = get_text(review)
                total_reviews = sum(star_counts.values())
                if total_reviews < 50:
                    if score in star_counts and star_counts[score] <= 10 and text != '':
                        star_counts[score] += 1 
                        compiled_list.append({'book_title':book_title,
                                            'rating':score,
                                            'text':text})
                else:
                    return
            return
        
        def get_text(review):
        # Retrieves the text of a given review. Returns an empty string if there is none.
            text = ''
            if len(review.find_all('span', {'class': 'readable'})) > 0:
                for child in review.find_all('span', {'class': 'readable'})[0].children:
                    if child.name == 'span' and child.get('style') and child['style'] == 'display:none':
                        text = child.text
            return text

        def get_score(review):
        # Retrieves each review's score out of five stars.
            if len(review.find_all('span', {'class': 'staticStars'})) > 0:
                rating = review.find_all('span', {'class': 'staticStars'})[0]['title']
                return score_dict[rating]
            return ''

        # Here we scrape our first page
        scrape_current_page(False, url_parsed)
        print('Scraped page 1')

        # Goodreads only links to 10 'pages' of reviews. This loops through them until star_counts is full
        # or until we reach page 10.
        page_counter = 2
        while page_counter <=10:
            if sum(star_counts.values()) < 50:
                if driver.find_element_by_link_text(str(page_counter)):
                        driver.find_element_by_link_text(str(page_counter)).click()
                        time.sleep(3) # Page needs to load.
                        scrape_current_page(driver, url_parsed)
                        print(f"Scraped page {page_counter}")
                        page_counter += 1
            else:
                break
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
            

