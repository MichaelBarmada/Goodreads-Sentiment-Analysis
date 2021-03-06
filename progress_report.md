# Progress Report
---
## February
- 18th: Project began, repository created, sources considered.
- 28th: Approach finalised: scraping GoodReads rather than Google Books API.

## March
- 3rd: Preliminary scraper added. Looks at one book and collects both text and scores from the 30 highest-rated reviews.
- 6th: Scraper updated to retrieve 10 reviews for each score level, resulting in a total of 50 scores per book. The data has been included in a new file called compiled_df.csv. For now, this is only looking at 2 books. The next step will be expanding the no. of books and (potentially) finding a more efficient way of gathering reviews for each score-level. 