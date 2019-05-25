# ToposAssignment
Topos Intern Assignment
Version Python3.7 required
Run the main.py file and it will generate Final.csv.

The data has been generated from https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population. The table containing the cities has been gathered and additionally, for each of the cities, the link to the FIPS Code website can be found which has additional demographic details of the city. The table found there is not scrapable with general BeautifulSoup. And also included an extra column for summary, which summarizes the contents of the wikipedia page of the corresponding city using nltk. It tokenizes the words and removes stop words and assigns a score to each sentence based on the term frequencies. The top 10 sentences are included for the summary. This is an extractive approach for text summarization. However, an abstractive approach can be used using neural networks for the same.
