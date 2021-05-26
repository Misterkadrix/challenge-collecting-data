import pandas as pd
import numpy as np
import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Safari()
website_url =  'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page=1&orderBy=relevance'
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

    for card in house_containers[:3]:  # the loop that will go through each listed house and do the scrapping.
        if len(card.select('.card--result')) == 1:
            # scrapping the property type (The reason I do this outside of the big scrapping loop is because the property type is stated more clearly on the main search page than the individual page.)
            property_type = card.find_all('a', attrs={"class": "card__title-link"})[0].text.strip().replace('\n', '')
            print(property_type)

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


