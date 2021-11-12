import requests
import validators
import sys
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import wget
from urllib.request import urlopen
import urllib.request 

def check_validity(my_url):
    try:
        urlopen(my_url)
        print("Valid URL")
    except IOError:
        print ("Invalid URL")
        sys.exit()


def get_pdfs(my_url):
    links = []
    html = urlopen(my_url).read()
    html_page = bs(html, features="lxml") 
    og_url = html_page.find("meta",  property = "og:url")
    base = urlparse(my_url)
    print("base",base)
    for link in html_page.find_all('a'):
        current_link = link.get('href')
        if current_link != None and current_link.endswith('pdf'):
            if og_url:
                print("currentLink",current_link)
                links.append(og_url["content"] + current_link)
            else:
                links.append(base.scheme + "://" + base.netloc + current_link)

    for link in links:
        try: 
            print(link)
            # wget.download(link)
        except:
            print(" \n \n Unable to Download A File \n")
    print('\n')

def get_order_code(my_url):
    links = []
    html = urlopen(my_url).read()
    html_page = bs(html, features="lxml") 
    og_url = html_page.find("meta",  property = "og:url")
    base = urlparse(my_url)
    print("base",base)
    for finding in html_page.find_all('tr'):
        data_order_code = finding.get('data-order-code')
        if data_order_code != None :
            print(data_order_code)

def get_table(my_url):
    links = []
    html = urlopen(my_url).read()
    html_page = bs(html, features="lxml") 
    og_url = html_page.find("meta",  property = "og:url")
    base = urlparse(my_url)
    print("base",base)
    for finding in html_page.find_all('th'):
        headerclass = finding.get('class')
        sortable = finding.get("sortable")
        data = finding.get_text() # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all
        if headerclass != None and sortable != None:
            if headerclass[0] == "productTable__table--sticky-head__moving" and sortable == "true":
                print(data)

    for finding in html_page.find_all('td'):
        data_unit = finding.get('data-unit')
        data_mobile_visible_index = finding.get('data-mobile-visible-index')
        data = finding.string # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all
        if data_unit != None and data_mobile_visible_index!= None :
            print(data_mobile_visible_index, data, data_unit)


def main():
    # print("Enter Link: ")
    # my_url = input()
    my_url = "https://www.we-online.com/katalog/de/WE-TOF"
    check_validity(my_url)
    # get_pdfs(my_url)
    # get_order_code(my_url)
    get_table(my_url)

main()

