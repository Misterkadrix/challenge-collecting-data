import pandas as pd
import numpy as np
import re
import requests
import webbrowser
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Safari()
website_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page=1&orderBy=relevance'
driver.get(website_url)

html = driver.page_source
soup = BeautifulSoup(html)

# defining where the page number is indicated within the website which will help to create the loop for going through each page for scrapping.
total_pages = soup.find_all('span', attrs={"class": "button__label"})[6].text

for page_number in range(1, int(total_pages) + 1):  # creating a loop that will replace the page number

    # the digit part in the url indicates the page number. so this code will replace the digit with the next number and it will go until 333 - total page number.
    new_url = re.sub('\d', str(page_number), website_url)
    print("New url: ", page_number, new_url)

    # creating beautifulsoup for each advertised house/apartment to scrap.
    driver.get(new_url)

    html = driver.page_source
    soup = BeautifulSoup(html)

    # finding each listed houses' information to scrap further the property type (house,apartement,mansion, etc.)
    house_containers = soup.find_all('li', attrs={"class": "search-results__item"})

    list_of_attributes_to_retrieve = ['property_type', 'location', 'price', 'number_of_rooms', 'area', 'Kitchen type',
                                      'Furnished', 'How many fireplaces?', 'Garden surface', 'Terrace surface',
                                      'Surface of the plot', 'Number of frontages', 'Swimming pool',
                                      'Building condition']

    data_frame = pd.DataFrame(columns=list_of_attributes_to_retrieve)  # then the values will be added from the final dictionary.

    # the loop that will go through each listed house and do the scrapping.
    for card in house_containers[:15]:
        if len(card.select('.card--result')) == 1:  # skips the advertisement.

            # dictionary that will store the scrapped information.
            dict_of_attributes = {}

            # check if it's a real estate project. If not, continue scrapping. If yes don't do anything. Real estate projects have very different construction within the website.
            is_real_estates = card.find('a', attrs={"class": "card__title-link"}).get('aria-label')
            if 'real estate project' not in is_real_estates:

                # scrapping the property type
                property_type = card.find_all('a', attrs={"class": "card__title-link"})[0].text.strip().replace('\n','')
                dict_of_attributes['property_type'] = property_type

                locality = card.find_all('p', attrs={"class": "card__information card--results__information--locality card__information--locality"})[0].text.strip()[:5]
                dict_of_attributes['location'] = locality

                # retrieve the links of each property so the beautifulsoup can be created
                property_link = card.find('a', attrs={"class": "card__title-link"}).get('href')

                # create a beautifulsoup from each of property links
                driver.get(property_link)
                html_of_each_property = driver.page_source
                soup_of_each_property = BeautifulSoup(html_of_each_property)

                # for each property, location, price, number of rooms, and area information are stated at the top of the website and it is the same pattern always.
                # Therefore they can be detected within their class and indexes.

                price = soup_of_each_property.find_all("p", attrs={"class": "classified__price"})[0].text.split(" ")[0].replace('€', '')
                dict_of_attributes['price'] = price

                number_of_rooms = soup_of_each_property.find_all('span', attrs={"class": "overview__text"})[0].text.replace(" ", "")[1]
                dict_of_attributes['number_of_rooms'] = number_of_rooms

                area = soup_of_each_property.find_all('span', attrs={"class": "overview__text"})[2].text.replace(" ","").replace("\n", "")
                area = ''.join(filter(str.isdigit, area))[:-1]  # to retrieve only the digit part without the square(²) sign.
                dict_of_attributes['area'] = area

                # However, some interior and exterior information are optional for each property (e.g. terrace, swimming pool) so we need to create a for loop that will check
                # if that information exists within the website. If yes, retrieve the information. Else, assign it to 0.

                property_attributes = soup_of_each_property.select(".classified-table__header")

                for attributes in property_attributes:
                    attribute_name = attributes.text.strip()  # retrieve only the text and remove all spaces.
                    dict_of_attributes[attribute_name] = 0

                    # check if attribute name is in the list to retrieve. If yes, find the parent code to brings its value and assign it to attribute value.
                    if attribute_name in list_of_attributes_to_retrieve:
                        attribute_value = attributes.parent.select(".classified-table__data")[0].text.strip()

                        # only retrieve the numerical information, remove the rest.
                        if attribute_name == 'Garden surface':
                            attribute_value = attribute_value.replace("\n", "").replace(" ", "").replace("m²squaremeters", '')

                        if attribute_name == 'Terrace surface':
                            attribute_value = attribute_value.replace("\n", "").replace(" ", "").replace("m²squaremeters", '')
                        if attribute_name == 'Surface of the plot':
                            attribute_value = attribute_value.replace("\n", "").replace(" ", "").replace("m²squaremeters", '')

                        # assign each property attribute to their value
                        dict_of_attributes[attribute_name] = attribute_value

                for attribute in list_of_attributes_to_retrieve:
                    # if the attribute information is not found in the website, don't skip it but give the value of 0.
                    if attribute not in dict_of_attributes.keys():
                        dict_of_attributes[attribute] = 0

                final_dict = {}
                for el in list_of_attributes_to_retrieve:
                    if el in list_of_attributes_to_retrieve:
                        final_dict[el] = dict_of_attributes[el]

                # appending the final dictionary values to the data frame as rows.
                data_frame = data_frame.append(final_dict, ignore_index=True)

# rename the column names to make them easier/cleaner to read.
data_frame.rename({'property_type': 'Property Type', 'location': 'Location', 'price': 'Price', 'number_of_rooms': 'Number of Rooms',
     'area': 'Area'}, axis=1, inplace=True)

# change yes/no answers to binary values as requested for the project.
data_frame['Swimming pool'] = data_frame['Swimming pool'].replace(['No'], '0')  # if it's no assign 0.
data_frame['Furnished'] = data_frame['Furnished'].replace(['No'], '0')
data_frame['Furnished'] = data_frame['Furnished'].replace(['Yes'], '1')  # if its furnished 1.

data_frame












