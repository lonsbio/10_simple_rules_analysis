#!/usr/bin/env python

""" Gather data and create graphs for Ten Simple Rules analysis

	Search functions based on http://api.plos.org/search-examples/plos_search.py
"""

from bs4 import BeautifulSoup
import requests
import json
from urllib2 import urlopen, quote
from datetime import datetime, timedelta
import re
import matplotlib.pyplot as plt

#API details
my_api_key="<replace with your key>"
searchUrl = 'http://alm.plos.org'
apiUrl = '/api/v3/articles?'

def search(doi):
	'''
		Retrieve JSON data by DOI
	 
		Modified from http://api.plos.org/search-examples/plos_search.py
	'''
	
	query = { 'api_key': my_api_key, 'ids' : quote(doi,""), 'info': 'summary', 'source': 'twitter,crossref' }
    
	url = searchUrl+apiUrl;
	for part in query:
		url += '%s%s=%s' % ('&' if url is not searchUrl+apiUrl else '',part,query[part])
	print 'Making request to',url #TEST
	return json.load(urlopen(url))


def searchextra(doi):
	'''
		Retrieve JSON data by DOI
		
		Modified from http://api.plos.org/search-examples/plos_search.py
	'''
	
	query = { 'api_key': my_api_key, 'ids' : quote(doi,""), 'info': 'detail', 'source': 'counter' }
    
	url = searchUrl+apiUrl;
	for part in query:
		url += '%s%s=%s' % ('&' if url is not searchUrl+apiUrl else '',part,query[part])
	print 'Making request to',url #TEST
	return json.load(urlopen(url))

def plosprint(paper_list):
	'''
	Print details of papers

	'''
	for p in paper_list:
        	print "DOI", p['doi']
        	print "Title:", p['title']
        	print "Authors:", p['authors']
        	print "# Authors:", p['numauthors']
        	print "Philip E. Bourne an author:", p['peb']
        	print "Journal:", p['journal']
        	print "Published:", p['pubdate']
        	print "URI:", p['URI']
        	print "PDF:", p['pdf']
        	print "HTML:", p['html']
        	print "XML:", p['xml']
        	print "Total:", p['total']
        	print "Citations: ", p['citations']
        	print "Views: ", p['views']
        	print "Shares: ", p['shares']
        	print "Bookmarks: ", p['bookmarks']
        	print "URL", p['URL']
        	print "References:", p['references']
        	print "10 Simple Rules references:", p['10simpleref']
        	print "================="
        

# Gather data and produce graphs for the Ten Simple Rules collection
analysis_url = "http://www.ploscollections.org/article/browse/issue/info%3Adoi%2F10.1371%2Fissue.pcol.v03.i01"

# Important note on data. 
# The data in the paper is from June 20th, 2014. The following code will get the latest data from PLoS ALM, however the following plots 
# will replicate the paper. Uncomment the '#Current data' sections and comment out '#June 20th data' sections to get the latest.


r = requests.get(analysis_url)
soup = BeautifulSoup(r.text)
pebcount = 0
pebonlycount = 0
articles = soup.find_all('div',class_='item cf')
allauthors = set()

paper_list = []

for article in articles:
    title =  article.find('a') # get the first link
    author = article.find('div',class_='authors') # print author list
    authors = author.string.split(",")
    peb = False
    pebregex="Philip E\.* Bourne" # Note that both Philip E Bourne and Philip E. Bourne appear
    #clean and count authors
    cleanauthors= []
    for auth in authors:
        clean =  auth.strip()
        allauthors.add(clean)
        cleanauthors.append(clean)
        if(re.search(pebregex,clean)):
            peb=True
            pebcount = pebcount + 1
    if (peb == True and len(authors) == 1): # Philip E. Bourne an author, and only author
        pebonlycount = pebonlycount + 1
    info =  article.find('div',class_='article-info')
    infotext = info.find('p')
    journal = infotext.b.text[:-1] # remove last charcater of : 
    infotail = infotext.text.split(" published ")
    infotailsplit = infotail[1].split(" |")
    pubdate = infotailsplit[0]  
    info = infotailsplit[1]  # take all of the URI info http://en.wikipedia.org/wiki/Info_URI_scheme
    doi = info.split(" info:doi/")[1]
    print doi
    result = search(doi)[0]
    res2 = searchextra(doi)[0]['sources'][0]['metrics']
    paper_url = result[u'url']
    # Sometimes the paper may not be available through the API
    refcount=0
    collectionref=0
    if (paper_url):
        paper = requests.get(paper_url)
        references = BeautifulSoup(paper.text)
        #find the references
        reflist = references.find('ol',class_='references')
        if (reflist):
            refs = reflist.find_all('li')
            # li sometimes repeated, use span to effectively count
            refcount = len(reflist.find_all('span',class_="label"))
            #refcount = len(refs)
            collregex=".*Ten Simple Rules.*" # Articles containing Ten Simple Rules, ignoring case
            for l in refs:
               l = l.text.strip()
               #print l
               if(re.search(collregex,l,re.IGNORECASE)):
                   collectionref = collectionref + 1
        refcountres = str(refcount)
        collectionrefres = str(collectionref)

    else:
        refcountres = "<unable to fetch>"
        collectionrefres = "<unable to fetch>"
    print "==================================================================="
    # within our loop we will collect each paper into a list
    paper = {"title":    title.string.strip(),
             "doi": doi,
            "authors": ', '.join(cleanauthors),
            "numauthors": str(len(authors)),
            "peb": peb,
            "journal":  journal,
            "pubdate": pubdate,
            "URI": info,
            "citations":str(result[u'citations']),
            "views": str(result[u'views']),
            "shares": str(result[u'shares']),
            "bookmarks": str(result[u'bookmarks']),
            "URL": str(paper_url),
            "references": str(refcountres),
            "10simpleref": str(collectionrefres),
            "pdf": str(res2['pdf']),
            "html": str(res2['html']),
            "total": str(res2['total']),
            "xml": str(res2['total']-(res2['pdf']+res2['html']))
         }
    paper_list.append(paper)

# Data values for paper
paper_count_200614 = 37
paper_list_200614 =  paper_list[-paper_count_200614:]

#Setup figures, XKCD style
plt.xkcd()

#Figure 1

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.bar([-0.125, 1.0-0.125], [0, 100], 0.25)
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.set_xticks([0, 1,2])
ax.set_xlim([-0.5, 2.5])
ax.set_ylim([0, 110])
ax.set_xticklabels(['<10 ', '10','>10'])

#June 20th data
ax.set_yticklabels([paper_count_200614])
#Current data
#ax.set_yticklabels([len(paper_list)])


ax.yaxis.set_ticks_position('left')
plt.yticks([100])
plt.tight_layout()
plt.title('Rules in a Ten Simple Rules article')
plt.ylabel('Articles')
plt.xlabel('Rules')
plt.tight_layout()
plt.savefig('figure1.eps')
plt.clf()

#Figure 2

#Current data
#tcount_pie=len(articles)
#pebcount_pie = pebonlycount
#pebcocount_pie =  pebcount-pebonlycount
#othercount_pie = len(articles)-pebcount

#June 20th data
tcount_pie=37
pebcount_pie = 3
pebcocount_pie = 15
othercount_pie = 19

labels = 'Philip E. Bourne\n sole author', 'Philip E. Bourne\n co-author', 'Other authors'
sizes= [pebcount_pie, pebcocount_pie, othercount_pie ]

# Colours for colourblind, from https://github.com/nesanders/colorblind-colormap/blob/master/CBcm.py
CBcdict={
    'Bl':(0,0,0),
    'Or':(.9,.6,0),
    'SB':(.35,.7,.9),
    'bG':(0,.6,.5),
    'Ye':(.95,.9,.25),
    'Bu':(0,.45,.7),
    'Ve':(.8,.4,0),
    'rP':(.8,.6,.7),
}
colors = [CBcdict['SB'],CBcdict['bG'],CBcdict['Or']]
explode = (0.1, 0.1, 0.1)
plt.title('Ten Simple Rules authorship',y=1.20)
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=False, startangle=90,labeldistance=1.18)
plt.axis('equal')
plt.tight_layout()
plt.savefig('figure2.eps')
plt.clf()

#Figure 3

#Current data
#data = [(p['citations'],p['views']) for p in paper_list]
#June 20th data
data = [(p['citations'],p['views']) for p in paper_list_200614]

x,y = zip(*data)
plt.scatter(x,y,alpha=0.5,facecolors='none', edgecolors='black')
plt.axis([-2, 20, -20000, 300000])
plt.xticks()
plt.title('PLOS metrics for Ten Simple Rules',y=1.05)
plt.xlabel('Citations')
plt.ylabel('Views')
plt.tight_layout()
plt.savefig('figure3.eps')
plt.clf()




