import requests
import validators
import sys
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import wget
from urllib.request import urlopen
import urllib.request 

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

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
    links, data_order_code_list = [] , []
    html = urlopen(my_url).read()
    html_page = bs(html, features="lxml") 
    og_url = html_page.find("meta",  property = "og:url")
    base = urlparse(my_url)
    print("base",base)
    for finding in html_page.find_all('tr'):
        data_order_code = finding.get('data-order-code')
        if data_order_code != None :
            # print(data_order_code)
            data_order_code_list.append(data_order_code)
    return(data_order_code_list)

def get_table(my_url):
    check_validity(my_url)
    data_dict, table_dict = {} , {}
    data_order_code_list = get_order_code(my_url)
    links , table_header_list , table_value_list = [] , [] , []
    html = urlopen(my_url).read()
    html_page = bs(html, features="lxml") 
    og_url = html_page.find("meta",  property = "og:url")
    base = urlparse(my_url)
    print("base",base)

    # Search Table header in WE
    for finding in html_page.find_all('th'):
        headerclass = finding.get('class')
        sortable = finding.get("sortable")
        table_header = finding.get_text() # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all
        if headerclass != None and sortable != None:
            if headerclass[0] == "productTable__table--sticky-head__moving" and sortable == "true":
                if table_header in table_header_list: break
                else: table_header_list.append(table_header)

    # Search Table values in WE
    index = 0
    for finding in html_page.find_all('td'):
        # get downloadpath for pdf
        if finding.get("class")[0] == "datasheet":
            dlink = finding.find_all('a')[0].get('href')
            continue

        data_unit = finding.get('data-unit')
        data_mobile_visible_index = finding.get('data-mobile-visible-index')
        data = finding.string # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all
        if data_unit != None and data_mobile_visible_index!= None :
            # convert to digit
            data_mobile_visible_index = int(data_mobile_visible_index)
            if isfloat(data.replace(" ","")): data=float(data.replace(" ",""))

            # add all table values to data_dict
            if (data_mobile_visible_index <= len(table_header_list)):
                data_dict[table_header_list[data_mobile_visible_index-1]] = data

            # if header list is reached then build table dict as MPN : data_dict 
            if len(table_header_list) == data_mobile_visible_index:
                # creates download link
                data_dict["pdf_link"] = f"{base.scheme}://{base.netloc}{dlink}"
                table_dict[data_order_code_list[index]] = data_dict
                
                index += 1
                data_dict = {}

    return table_dict
def main():
    # print("Enter Link: ")
    # my_url = input()
    my_url = "https://www.we-online.com/katalog/de/WE-TOF"
    table = get_table(my_url)
    print(table)

main()

