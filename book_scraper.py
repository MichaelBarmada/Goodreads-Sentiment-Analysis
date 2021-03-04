import scrapy
import requests
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd

def get_text(review):
    # Retrieves the full text from the front-page reviews for a book.
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
        return rating
    return ''

def compile_reviews(url):
    # Groups review text with associated score and book title.
    print('Compiling review data...')
    review_data = []
    
    url_list = requests.get(url)
    url_list = bs(url_list.text, 'lxml')

    book_title = url_list.find(id='bookTitle').text.strip()

    review_list = url_list.find_all('div', {'class': 'review'})

    for review in review_list:
        review_data.append({'book_title':book_title,
                            'rating':get_score(review),
                            'text':get_text(review)})

    print('Compiliation complete!')
    print()
    return review_data

def main():
    # For now, we're just looking at one. This will be expanded later on.
    url = 'https://www.goodreads.com/book/show/7235533-the-way-of-kings'

    compiled_list = compile_reviews(url)

    print('Putting together your dataframe...')
    compiled_df = pd.DataFrame(compiled_list)

    print('Ta-Da!')
    print(compiled_df.info(verbose = True))

if __name__ == '__main__':
    main()
