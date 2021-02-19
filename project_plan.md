# Project Plan
## Goodreads Reviews Sentiment Analysis
---
## Summary
How do book reviews vary by rating? Does vocabulary change? Does pronoun usage? Length? Inspired by the 100 years of Science Fiction project by Bethanie Maples, Srini Kadamati, and Eric Berlow, this project will use scraped data from Goodreads reviews to organize books from the fantasy genre by keyword and gather some of the most-liked reviews from each rating (out of five stars).

## Data
Data will involve raw text of reviews grouped by book and by rating. Keywords will also have to be extracted from such reviews and applied to each book for analysis. I (tentatively) plan to use the 20 most-liked reviews from each rating (on a scale of 1 - 5 stars), resulting in 100 reviews per book. One issue will be finding a good metric for choosing books and fine-tuning the number of books to keep the dataset at a reasonable size. It will also be difficult to seperate Fantasy from SciFi as the two genres overlap significantly. I may just end up looking at both.

## Analysis
I will aim to sort reviews by keyword to see what (if any) elements result in more positive or negative reviews. The most interesting analysis will be looking at middle-grade reviews (2.5 - 3.5 stars) to see what percentage of them are positive, what percentage are negative, and what percentage are mixed. This will first require a classifier to be trained on a certain portion of the dataset. Using one-star and five-star reviews may work for this, as they can reasonably be said to correspond to negative and positive opinions respectively. It will also be interesting to see at what point on the grading scale reviews shift from overall-positive to overall-negative.

## Presentation
It will likely include graphs of some variety. Word clouds will also be present if at all possible. 