import requests
import validators
import sys
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import wget
from urllib.request import urlopen
import urllib.request
import json

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
    return links
    for link in links:
        try: 
            print(link)
            # wget.download(link)
        except:
            print(" \n \n Unable to Download A File \n")
    print('\n')

def get_categories(my_url):
    links = []
    html = urlopen(my_url).read()
    html_page = bs(html, features="lxml") 
    og_url = html_page.find("meta",  property = "og:url")
    base = urlparse(my_url)
    print("base",base)
    for link in html_page.find_all('a'):
        current_link = link.get('href')
        myclass = link.get('class')
        if myclass != None:
            # print(myclass)
            if current_link != None and "js-force-parametric-search" in myclass:
                if og_url:
                    print("currentLink",current_link)
                    links.append(og_url["content"] + current_link)
                else:
                    links.append(base.scheme + "://" + base.netloc + current_link)
    return links
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
    # download_links_list = get_pdfs(my_url)
    links , table_header_list , table_value_list, pdf_dlink_list = [] , [] , [], []
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
            for links in finding.find_all('a'):
                dlink = links.get('href')
                if dlink.endswith("pdf"):
                    pdf_dlink_list.append(f"{base.scheme}://{base.netloc}{dlink}")
            continue

        data_unit = finding.get('data-unit')
        data_mobile_visible_index = finding.get('data-mobile-visible-index')
        data = finding.string # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all
        if data_unit != None and data_mobile_visible_index!= None :
            # strip whitespace
            data = data.strip()

            # convert to digit
            data_mobile_visible_index = int(data_mobile_visible_index)
            if isfloat(data.replace(" ","")): data=float(data.replace(" ",""))

            # add all table values to data_dict
            if (data_mobile_visible_index <= len(table_header_list)):
                data_dict[table_header_list[data_mobile_visible_index-1]] = data

            # if header list is reached then build table dict as MPN : data_dict 
            if len(table_header_list) == data_mobile_visible_index:
                # add pdf link to dict and clear dict after that
                data_dict["pdf_links"] = pdf_dlink_list
                pdf_dlink_list = []

                # add data_dict to table_dict
                table_dict[data_order_code_list[index]] = data_dict
                
                index += 1
                data_dict = {}

    return table_dict
def unite_nested_dict(A, B) -> dict:
    return {k: dict(A.get(k, {}), **B.get(k, {})) for k in A.keys() | B.keys()} #https://stackoverflow.com/a/29241297

def main():
    my_url = "https://www.we-online.com/katalog/en/pbs/emc_components/ferrites_for_cable_assembly"
    we_online_dict = {}
    filename = "we_online_dict.json"

    for category_link in get_categories(my_url):
        table = get_table(category_link)
        category = category_link.split("/")[-1]
        we_online_dict[category] = {}
        we_online_dict[category]["category_link"] = category_link
        we_online_dict[category]["mpn_table"] = table
        we_online_dict = dict(sorted(we_online_dict.items()))
        for key in we_online_dict.keys():
            we_online_dict[key]["mpn_table"] = dict(sorted(we_online_dict[key]["mpn_table"].items()))

    try:
        with open(filename, "r") as jsonFile:
            openjson = json.load(jsonFile)
            we_online_dict = unite_nested_dict(openjson, we_online_dict)
            print(f"existing {filename} found -> will be united with new dictionary")
            we_online_dict = dict(sorted(we_online_dict.items()))
            for key in we_online_dict.keys():
                we_online_dict[key]["mpn_table"] = dict(sorted(we_online_dict[key]["mpn_table"].items()))
    except IOError:
        print(f"no existing {filename} found for unite")

    with open(filename, 'w') as fp:
        json.dump(we_online_dict, fp, indent=4)
    

main()

