import pandas as pd
import numpy as np
import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Safari()
<<<<<<< Updated upstream
website_url =  'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page=1&orderBy=relevance'
=======
driver.execute_cpd_cmd('Network.setUserAgentOverride', {'user agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'}
website_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false' \
              '&page=1&orderBy=relevance '
>>>>>>> Stashed changes
driver.get(website_url)

html = driver.page_source
soup = BeautifulSoup(html, features = "html.parser")

import webbrowser
import re

# defining where the page number is indicated within the website which will help to create the loop for going through each page for scrapping.
total_pages = soup.find_all('span', attrs={"class": "button__label"})[6].text
total_pages = 1

for page_number in range(1, total_pages + 1):  # creating a loop that will replace the page number
    # the digit part in the url indicates the page number. so this code will replace the digit with the next number and it will go until 333 - total page number.
    new_url = re.sub('\d', str(page_number), website_url)
    print("New url: ", page_number, new_url)

    driver.get(new_url)

    html = driver.page_source
    soup = BeautifulSoup(html, features= "html.parser")

    # finding each listed houses' information to scrap further the property type (house,apartment,mansion, etc.)
    house_containers = soup.find_all('li', attrs={"class": "search-results__item"})

<<<<<<< Updated upstream
    for card in house_containers[:3]:  # the loop that will go through each listed house and do the scrapping.
        if len(card.select('.card--result')) == 1:
            # scrapping the property type (The reason I do this outside of the big scrapping loop is because the property type is stated more clearly on the main search page than the individual page.)
            property_type = card.find_all('a', attrs={"class": "card__title-link"})[0].text.strip().replace('\n', '')
            print(property_type)
=======
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

<<<<<<< Updated upstream
                # scrapping the property type
                property_type = card.find_all('a', attrs={"class": "card__title-link"})[0].text.strip().replace('\n',
                                                                                                                '')
                dict_of_attributes['property_type'] = property_type
=======
            if 'real estate project' in is_real_estates:
                list_of_real_estate = card.find_all('a', attrs={"class": "classified__list-item-link"})
                for real_estate in list_of_real_estate:
                    final_dict = scrap_from_page(real_estate.get('href'), list_of_attributes_to_retrieve)
                    data_frame = data_frame.append(final_dict, ignore_index=True)
                    card_count += 1

            else:
>>>>>>> Stashed changes

                # retrieve the links of each property so the beautifulsoup can be created
                property_link = card.find('a', attrs={"class": "card__title-link"}).get('href')

                # create a beautifulsoup from each of property links
                driver.get(property_link)
                html_of_each_property = driver.page_source
                soup_of_each_property = BeautifulSoup(html_of_each_property)

                # for each property, location, price, number of rooms, and area information are stated at the top of the website and it is the same pattern always.
                # Therefore they can be detected within their class and indexes.
                locality = soup_of_each_property.select(".classified__information--address-row")[1].text.replace(" ","").replace('\n', '')
                dict_of_attributes['location'] = locality

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






>>>>>>> Stashed changes

            # Retrieve the links to each property
            property_link = card.find('a', attrs={"class": "card__title-link"}).get('href')
            print("Property link: ", property_link)

            # create a BeautifulSoup from each of property links
            driver.get(property_link)
            html_of_each_property = driver.page_source
            soup_of_each_property = BeautifulSoup(html_of_each_property, features= "html.parser")

            locality = soup_of_each_property.select(".classified__information--address-row")[1].text
            locality = ''.join(filter(str.isdigit, locality))  # only output will be the postal code digit.
            print(locality)

            # sub_type_of_property = I might skip this because it is already stated in the property_type if its a house,mansion,villa etc.

            price = soup_of_each_property.find_all("p", attrs={"class": "classified__price"})[0].text.split(" ")[0]
            print(price)

<<<<<<< Updated upstream
            
=======
    # data_frame
    data_frame.to_csv("/Users/Pauwel/Desktop/BeCode/becode_projects/scrapping_project.csv")
>>>>>>> Stashed changes
