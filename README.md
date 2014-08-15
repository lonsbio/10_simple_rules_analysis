10_simple_rules_analysis
========================

Python scripts used to produce figures for "Ten Simple Rules for Writing a PLOS Ten Simple Rules Article"

Script will create (and possibly clobber) three files:
  - figure1.eps
  - figure2.eps
  - figure3.eps

# Prerequisites

Tested on Python 2.7, needs the following packages:
- Matplotlib >= 1.3.1
- BeautifulSoup
- Requests

# Instructions

- Obtain a [PLOS API key](http://api.plos.org/registration/) and replace:
```python
my_api_key="<replace with your key>"
```

# Important note on data. 
The number of articles analysed in the paper is from June 20th, 2014. The  code will get the latest data from PLOS ALM (including latest citations and views), however the  plots will replicate the paper with only the number of papers published to that point. Uncomment the '#Current data' sections and comment out '#June 20th data' sections to get all papers published in the Ten Simple Rules series collection to date.


