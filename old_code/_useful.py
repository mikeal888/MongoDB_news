import requests
import bs4 as bs

def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    stocks = {}
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text[:-1]
        name = row.findAll('td')[1].text
        stocks[name] = ticker
        
    return stocks
