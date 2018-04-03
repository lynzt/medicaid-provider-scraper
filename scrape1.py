from bs4 import BeautifulSoup
import requests
import json
import sys
import re
import os

s = requests.Session()

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_dotnet_viewstate(soup):
    view_state = soup.select("#__VIEWSTATE")[0]['value']
    event_validation = soup.select("#__EVENTVALIDATION")[0]['value']
    view_state_generator = soup.select("#__VIEWSTATEGENERATOR")[0]['value']

    form_data = {
        '__EVENTVALIDATION': event_validation,
        '__VIEWSTATE': view_state,
        '__VIEWSTATEGENERATOR': view_state_generator,
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': ''
    }
    return (form_data)

def lower_and_underscore(string):
    return (string.lower()).replace(' ', '_')

def replace_forward_slash(string):
    return string.replace('/', '-')

def get_provider_types(soup):
    ddl_categories = soup.findAll('option')
    categories = list(map(lambda x: {'id': x['value'], 'name': replace_forward_slash(x.text)}, ddl_categories))
    return list(filter(lambda x: x['id'] != '', categories))

def get_provider_subtypes(soup):
    select_subcategories = soup.find('select', {'id': 'ddlSubCategory'})
    ddl_subcategories = select_subcategories.findAll('option')
    return list(map(lambda x: {'id': x['value'], 'name': replace_forward_slash(x.text)}, ddl_subcategories))

def hit_main_directory_page():
    url = 'http://mhcpproviderdirectory.dhs.state.mn.us/'
    r =  s.get(url)

    return BeautifulSoup(r.text, "html.parser")


def hit_provider_type_page(soup, type_id):
    url = 'http://mhcpproviderdirectory.dhs.state.mn.us/index.aspx'

    form_data = get_dotnet_viewstate(soup)
    form_data['ddlCategory'] = type_id
    form_data['btnSearch'] = 'Next'

    r = s.post(url, data=form_data)
    return BeautifulSoup(r.text, "html.parser")

def hit_provider_subtype_page(soup, type_id, subtype_id):
    url = 'http://mhcpproviderdirectory.dhs.state.mn.us/search.aspx'

    form_data = get_dotnet_viewstate(soup)
    form_data['ddlCategory'] = type_id
    form_data['ddlSubCategory'] = subtype_id
    form_data['txtProvider'] = ''
    form_data['txtAddress'] = ''
    form_data['txtCity'] = ''
    form_data['ddlState'] = 'MN'
    form_data['ddlCounty'] = ''
    form_data['txtZip'] = ''
    form_data['btnSearch'] = 'Search'

    r = s.post(url, data=form_data)
    return BeautifulSoup(r.text, "html.parser")

def parse_provider_data(soup, type, subtype):
    for br in soup.find_all("br"):
        br.replace_with("\n")
    nbr_results = soup.find('span', {'id': 'lblNbrProviders'})
    table = nbr_results.parent.parent
    tds = table.findAll('td')

    directory = 'provider_files/{}'.format(type['name'])
    # file = '{}/{}::{}::{}.txt'.format(directory, subtype['name'], type['id'], subtype['id'])
    file = '{}/{}.txt'.format(directory, subtype['name'])
    ensure_dir(directory)
    file = open(file, 'w')
    file.write(tds[3].text)

def main():
    main_soup = hit_main_directory_page()
    types =  get_provider_types(main_soup)
    counter = 0
    types = list(filter(lambda x: x['name'] > 'D', types))
    # types = list(filter(lambda x: x['id'] == '101', types))

    for type in types:
        counter+=1
        type_soup = hit_provider_type_page(main_soup, type['id'])
        subtypes =  get_provider_subtypes(type_soup)
        for subtype in subtypes:
            subtype_soup = hit_provider_subtype_page(type_soup, type['id'], subtype['id'])
            print ('{} | {}'.format(type['name'], subtype['name']))
            parse_provider_data(subtype_soup, type, subtype)

        # if counter > 3:
        #     break




if __name__ == '__main__':
    main()
