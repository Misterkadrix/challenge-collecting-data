import pandas as pd
import numpy as np
import re
import requests
import webbrowser
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Safari()
website_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false' \
              '&page=1&orderBy=relevance '
driver.get(website_url)

html = driver.page_source
soup = BeautifulSoup(html)


def scrap_from_page(url: str, list_to_retrieve: list):
    '''This function will return the dict with all scrapped information'''

    # dictionary that will store the scrapped information.
    dict_of_attributes = {}

    # create a beautifulsoup from each of property links
    driver.get(url)
    html_of_page = driver.page_source
    soup_of_page = BeautifulSoup(html_of_page)
    if len(soup_of_page) != 1:
        print(len(soup_of_page))

    # scrapping info from the overview section
    try:
        property_type = soup_of_page.select(".classified__header-primary-info .classified__title")[0].text.replace('\n',
                                                                                                                   '').replace(
            "for sale", "").strip()
        dict_of_attributes['property_type'] = property_type
    except IndexError as e:
        print(e)
        property_type = soup_of_page.select(".classified__header-primary-info .classified__title")
        print(property_type)
        print(url)

    try:
        locality = soup_of_page.select(".classified__information--address-row")[1].text.replace('\n', '').strip()[:4]
        dict_of_attributes['location'] = locality
    except IndexError as e:
        print(e)
        locality = soup_of_page.select(".classified__information--address-row")
        print(locality)
        print(url)

    try:
        price = soup_of_page.select(".classified__price")[0].text
        price = price.split(" ", 1)[0]
        dict_of_attributes['price'] = price
    except IndexError as e:
        print(e)
        price = soup_of_page.select(".classified__price")
        print(price)
        print(url)

    # scrapping info from the interior/exterior and facilities section
    property_attributes = soup_of_page.select(".classified-table__header")

    for attributes in property_attributes:
        attribute_name = attributes.text.strip()  # retrieve only the text and remove all spaces.
        dict_of_attributes[attribute_name] = 0

        # check if attribute name is in the list to retrieve. If yes, find the parent code to brings its value and assign it to attribute value.
        if attribute_name in list_to_retrieve:
            attribute_value = attributes.parent.select(".classified-table__data")[0].text.strip()

            # only retrieve the numerical information, remove the rest.
            if attribute_name in ['Garden surface', 'Terrace surface', 'Living area', 'Surface of the plot']:
                attribute_value = attribute_value.replace("\n", "").replace(" ", "").replace("m²squaremeters", '')

            # assign each property attribute to their value
            dict_of_attributes[attribute_name] = attribute_value

    for attribute in list_of_attributes_to_retrieve:
        # if the attribute information is not found in the website, don't skip it but give the value of 0.
        if attribute not in dict_of_attributes.keys():
            dict_of_attributes[attribute] = 0

    final_dict = {}
    for el in list_to_retrieve:
        if el in list_to_retrieve:
            final_dict[el] = dict_of_attributes[el]
    return final_dict


#START OF THE PROGRAM

# Define what we need to scrap and add them as columns to the data frame
list_of_attributes_to_retrieve = ['Bedrooms', 'property_type', 'location', 'price', 'Living area', 'Kitchen type',
                                  'Furnished', 'How many fireplaces?', 'Garden surface', 'Terrace surface',
                                  'Surface of the plot', 'Number of frontages', 'Swimming pool', 'Building condition']

# initiate dataframe
data_frame = pd.DataFrame(
    columns=list_of_attributes_to_retrieve)  # then the values will be added from the final dictionary.

# defining where the page number is indicated within the website which will help to create the loop for going through each page for scrapping.
total_pages = soup.find_all('span', attrs={"class": "button__label"})[6].text

card_count = 0 #this is to track how many property have been scrapped

for page_number in range(1, int(total_pages) + 1):  # creating a loop that will replace the page number

    # the digit part in the url indicates the page number. so this code will replace the digit with the next number and it will go until 333 - total page number.
    new_url = re.sub('\d', str(page_number), website_url)
    print(f"{card_count} results so far")
    print("New url: ", page_number, new_url)

    # creating beautifulsoup for each advertised house/apartment to scrap.
    driver.get(new_url)
    html = driver.page_source
    soup = BeautifulSoup(html)

    # finding each listed houses' information to scrap further the property type (house,apartement,mansion, etc.)
    house_containers = soup.find_all('li', attrs={"class": "search-results__item"})

    # the loop that will go through each listed house and do the scrapping.
    for card in house_containers:
        if len(card.select('.card--result')) == 1:  # skips the advertisement.

            # check if it's a real estate project.
            # If not, continue scrapping.
            # If yes loop inside. Real estate projects have very different construction within the website.

            is_real_estates = card.find('a', attrs={"class": "card__title-link"}).get('aria-label')

            if 'real estate project' in is_real_estates:
                list_of_real_estate = soup_of_each_property.find_all('a', attrs={"class": "classified__list-item-link"})
                for real_estate in list_of_real_estate:
                    final_dict = scrap_from_page(real_estate.get('href'), list_of_attributes_to_retrieve)
                    data_frame = data_frame.append(final_dict, ignore_index=True)
                    card_count += 1

            else:

                # retrieve the links of each property so the beautifulsoup can be created
                property_link = card.find('a', attrs={"class": "card__title-link"}).get('href')
                final_dict = scrap_from_page(property_link, list_of_attributes_to_retrieve)
                data_frame = data_frame.append(final_dict, ignore_index=True)
                card_count += 1

    print(f"ended after: {card_count} card listed")
    #         #rename the column names to make them easier/cleaner to read.
    #         data_frame.rename({'property_type': 'Property Type', 'location': 'Location', 'price': 'Price', 'Bedrooms': 'Number of bedrooms',
    #                   'area': 'Area'}, axis=1, inplace = True)

    #         #change yes/no answers to binary values as requested for the project.
    #         data_frame['Swimming pool'] = data_frame['Swimming pool'].replace(['No'],'0')  #if it's no assign 0.
    #         data_frame['Furnished'] = data_frame['Furnished'].replace(['No'],'0')
    #         data_frame['Furnished'] = data_frame['Furnished'].replace(['Yes'],'1') #if its furnished 1.

    # data_frame
    data_frame.to_csv("/Users/cerenmorey/Desktop/BeCode/becode_projects/scrapping_project.csv")