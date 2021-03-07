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