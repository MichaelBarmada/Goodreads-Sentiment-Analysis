# Progress Report

## February
- 18th: Project began, repository created, sources considered.
- 28th: Approach finalised: scraping GoodReads rather than Google Books API.

## March
- 3rd: Preliminary scraper added. Looks at one book and collects both text and scores from the 30 highest-rated reviews.

## 1st Progress Report (6th March) 
- I updated book_scraper.py to retrieve 10 reviews for each score level, resulting in a total of 50 scores per book. The data has been included in a new file called compiled_df.csv. For now, this is only looking at 2 books. The next step will be expanding the no. of books and (potentially) finding a more efficient way of gathering reviews for each score-level.
- The jupyter notebook (analysis.ipynb) covers data clean-up and analysis, including tokenization and ttr. Eventually, this will also be where sentiment analysis is conducted on the final collection of review data. 
- In terms of sharing, I have not yet decided the extent to which I will make my data available. I would like to make the data openly available in the github repository as none of the reviews are accompanied by the user's ID, and they are, ultimately, publically available reviews. However, the content of the reviews themselves might be a little too-easily identifiable. For now, there is a small sample of data in compiled_df.csv and a few snippets in the jupyter notebook, but that is all.

## 2nd Progress Report (23 March)
- A license has been added to my code. I decided to use the GNU General Public License v3.0, largely because I borrowed code that was, itself, distributed under this license and it stipulates that reproductions/ adaptations of code with this license must carry it as well.
- I have massively overhauled book_scraper.py so that it now includes data such as year of (first) publication, genre tags, and the number of likes for each review. 
I also removed the spider elements, seeing as it doesn't actually do any crawling and most of the interactions are handled by the driver. I also altered the code so that, instead of looping through the most-liked reviews to find enough from each score level, it uses goodread's review filters. Not only does this make it significantly easier to find 1- and 2- star reviews (as most of these reviews are overwhelmingly positive), but it also means that I can scrape significantly more data. Applying each filter displays the ~30 most-liked reviews from that score level, making it easy to scrape all 30 at once. Now instead of 50 reviews per-book I can scrape up to 150 in a fraction of the time!
- I have therefore expanded my data from 2 books and ~100 reviews to 20 books and ~ 2,400 reviews, and I can easily get more if need-be.
- In the next few days, I will be focusing on updating my jupyter notebook analysis and will start digging more deeply into the data I have. 
