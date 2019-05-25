#!/usr/bin/env python
# coding: utf-8

import os
import requests
import re
import nltk
import heapq  
import pandas as pd
import csv
import numpy as np
from bs4 import BeautifulSoup

'''
This function builds a csv file with only the wikipedia top cities table and returns the wikipedia page links for each city in a list format.
It uses functions writeheaders and writeData to build the csv file.
'''
def buildCSV():
    website_url = requests.get('https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population').text
    soup = BeautifulSoup(website_url,'lxml')
    mytable = soup.find('table',{'class':'wikitable sortable'})
    rows = mytable.findAll('tr')
    import re
    links = []
    for row in rows[1:]:
        links.append('https://en.wikipedia.org' + str(row.find('a',attrs={'href': re.compile("wiki/")}).get('href')))
    headers = rows[0].findAll('th')
    f = open('abc.csv',"w",encoding='utf-8-sig')
    writeheaders(headers,f)
    writeData(rows,f)
    f.close()
    return links

'''
This writes all the headers for the csv file that we generate. It only includes the data scraped from the top cities table. 
However, the data is preprocessed and the encoding is utf-8-sig.
'''


def writeheaders(headers,f):
    heads = []
    for h in headers:
        txt = str(h.get_text().strip().split('[')[0])
        txt = txt.title().replace(' ','')
        if txt[:4] == '2016':
            txt1 = txt + 'Mi'
            txt2 = txt + 'Km'
            heads.append(txt1)
            heads.append(txt2)
            continue
        heads.append(txt)
    heads[-1] = 'latitude'
    heads.append('longitude')
    headerstr = ','.join(heads) + '\n'
    f.write(headerstr)
'''
This writes all the data i.e. all the cities and their respective data mentioned in the table.
'''

def writeData(rows,f):
    from unicodedata import normalize
    for r in rows[1:]:
        txt = str(r.text)
        txtlist = str(txt.replace('\n\n','\n')).strip().split('\n')
        for i in range(len(txtlist)):
            txtlist[i] = txtlist[i].replace(',','')
            txtlist[i] =normalize('NFKD', txtlist[i])
            txtlist[i] = txtlist[i].strip()
            txtlist[i] = txtlist[i].split('[')[0]
        lat = (txtlist[-1].split()[0]).replace("′","")
        lat = lat.replace("°","")[:-1]
        long = (txtlist[-1].split()[1]).replace("′","")
        long = long.replace("°","")[:-2]
        txtlist[-1] = lat
        txtlist.append(long)
        writestr = (','.join(txtlist)) + '\n'
        f.write(writestr)


'''
This function adds all the additional data i.e. Links for FIPS pages and also the summary for the wikipedia page for that city.
'''


def addFIPSandSummary(data, links):
    fips = []
    summ = []
    for l in links:
        summ.append(generateSummary(l))
        flag = 0
        link = requests.get(l).text
        soup = BeautifulSoup(link,'lxml')
        tb = soup.find('table',{'class':'infobox geography vcard'})
        rows = tb.findAll('tr')
        for row in rows:
            if str(row.text)[:4] == 'FIPS':
                td = row.find('td')
                text = str(td.text).replace('-','').split('[')[0][:7]
                fips.append('https://factfinder.census.gov/bkmk/table/1.0/en/DEC/10_DP/DPDP1/1600000US'+text)
                flag = 1
        if flag == 0:
            fips.append(np.nan)
    data['FIPS Code'] = fips
    data['summary'] = summ
    return data

'''
This function generates a summary for the wikipedia page given a link. It uses all the 'p' elements in the page. 
Input is the link for the page. It is a naive extractive approach for text summarization based on term frequencies. 
'''
def generateSummary(l):
    link = requests.get(l).text
    soup = BeautifulSoup(link,'lxml')
    pg = soup.findAll('p')
    text = ""
    for p in pg:
        text += str(p.text)
    text = re.sub(r'\[[0-9]*\]', ' ', text)  
    text = re.sub(r'\s+', ' ', text)  
    ftext = re.sub('[^a-zA-Z]', ' ', text )  
    ftext = re.sub(r'\s+', ' ', ftext)  

    sentence_list = nltk.sent_tokenize(text)  

    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}  
    for word in nltk.word_tokenize(ftext):  
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())
    word_frequencies.values()
    for word in word_frequencies.keys():  
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    sentence_scores = {}  
    for sent in sentence_list:  
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(10, sentence_scores, key=sentence_scores.get)
    summary = ''.join(summary_sentences)
    summary.replace(',','')
    return summary
    
'''
The main function. Generates a final csv. Takes some time to run. About 5 minutes. 
'''

def main():
    links = buildCSV()
    data = pd.read_csv('abc.csv', encoding = 'utf-8')
    os.remove('abc.csv')
    data = data.set_index('2018Rank')
    data = addFIPSandSummary(data, links)
    data.to_csv('Final.csv')

main()
