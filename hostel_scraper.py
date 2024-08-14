import time
import json
import re
import pandas as pd
from random import randint
from time import sleep
from urllib.request import urlopen
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

chrome_options = Options()

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("detach", True)
options.add_experimental_option("useAutomationExtension", False)
CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'
service = Service(executable_path=CHROME_DRIVER_PATH)

browser = webdriver.Chrome(
    options=options,
    service=service,
)

with open("continent_dict.json", encoding="UTF-8") as country_dict:
    country_dict = country_dict.read()

country_dict = json.loads(country_dict)


# user enters country name
def user_country():
    country_choice = input("\nEnter country: ")
    return country_choice


country = user_country()


# country variable used to get continent name from dictionary to autofill into country url # noqa
def get_continent():
    # item = value of k:v
    for item in country_dict.values():
        print(f"\nCountries in continent: {item}\n")
        # element represents the country in the list of countries from dictionary that country variable will be compared against # noqa
        for element in item:
            # country is the user's choice
            if country == element:
                continent_dict = [k for k, v in country_dict.items() if v == item][0] # noqa
                # print(f"\nContinent of country: {continent_dict}\n")
                return continent_dict


continent = get_continent()

city_list = []


# accesses main hostel page for user country using continent, country variables
def get_cities():
    # generates list of cities with hostels in that country
    url = f"https://www.hostelworld.com/st/hostels/{continent}/{country}/"
    print(f"\nURL to be opened: {url}\n")
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    soup.prettify()

    browser.get(url)
    # time.sleep(4)

    results = browser.find_elements(
        By.XPATH,
        "//div[@class='average-city-prices-list']/a"
    )

    for result in results:
        title = result.get_attribute("title")
        city_list.append(title)
    print(f"\nList of cities: {city_list}\n")
    # print(*city_list, sep="\n")
    # time.sleep(5)
    # browser.quit()


get_cities()


def dict_cities():
    digit = [num + 1 for num in range(len(city_list))]

    # make dictionary
    joint_list = zip(digit, city_list)
    city_dict = dict(joint_list)
    print(f"\nDictionary of city choices: {city_dict}\n")
    return city_dict


dictionary_cities = dict_cities()


def list_cities():
    # create list of numbers for each city in city_list
    number_list = [num + 1 for num in range(len(city_list))]

    # add periods to each number
    number_list = [f"{num}. " for num in number_list]

    number_city_list = [num + city for num, city in zip(number_list, city_list)] # noqa
    print(f"\nNumbered city list: {number_city_list}\n")
    return number_city_list


city_choices = list_cities()

# print(*city_choices, sep="\n")


def choose_city():
    print("\nCHOOSE A CITY:\n")
    # unpacks city_choice list - user sees each item in a new line
    print(*city_choices, sep="\n")
    city_choice = int(input("\nEnter city by digit: "))

    if city_choice in dictionary_cities:
        print("\nYes\n")
        city_value = dictionary_cities[city_choice]
        return city_value

    # user enters number
    # open web page based on city choice


city = choose_city()


# next function should scan country page for pagination of hostel lists
def city_page():
    url = f"https://www.hostelworld.com/st/hostels/{continent}/{country}/{city}/" # noqa
    # replaces any white space with %20
    url = url.replace(" ", "%20")
    print(url)
    html = urlopen(url)
    # page = requests.get(url, timeout=10)

    soup = BeautifulSoup(html, "html.parser")
    soup.prettify()

    browser.get(url)
    time.sleep(4)

    # def pagination_count():
    if soup.find("section", {"name": "pagination"}) is not None:
        print("\nDetected for pagination.\n")

        time.sleep(8)
        results = browser.find_element(
            By.XPATH,
            "//main/div[3]/section",
        )
        print(results)
        raw_string = results.get_attribute("innerText").replace("\n", "")
        digit_string = re.sub("[^0-9]", "", raw_string)
        # digit_list = number of pages ex. London has 4 pages worth of hostels
        # so digit_list = [1, 2, 3, 4]
        digit_list = [int(page) for page in digit_string]

        print("\nDetermined number of pages.\n")
        print(f"\ndigit_list is: {digit_list}\n")

        time.sleep(5)

        # url_list initially creates template hostel link for each element in digit list # noqa

        url_list = [url for count in enumerate(digit_list)]

        # print([url for count in range(list_len)])
        # page number syntax is added to [1:]
        # url_list: [
        #   'https://www.hostelworld.com/st/hostels/europe/england/london/',
        #   'https://www.hostelworld.com/st/hostels/europe/england/london/p/2/',
        #   'https://www.hostelworld.com/st/hostels/europe/england/london/p/3/',
        #   'https://www.hostelworld.com/st/hostels/europe/england/london/p/4/'
        # ]
        i = 1
        for index, dummy in enumerate(url_list):
            i = i + 1
            url_list[index] = url_list[index] + "/p/" + str(i) + "/"

        print(f"Paginated url list: {url_list}")
        return url_list
    else:
        print("\nThis city has only one page worth of hostels.\n")
        url_list = [url]
        print(f"Single url link: {url_list}")
        return url_list


paginated_list = city_page()

links_list = []


def links_city_hostels():

    for index, dummy in enumerate(paginated_list):
        page = requests.get(paginated_list[index], timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        soup.prettify()

        link_elements = soup.find_all("div", class_="property-listing-cards")
        # scrape each page for links for each hostel listed
        for link in link_elements:
            results = link.find_all("a")
            for result in results:
                link_url = result["href"]
                links_list.append(link_url)
        browser.quit()

    url_count = len(links_list)
    print(f"\nlinks_list = {links_list}\n")
    print(f"\nLength of list: {url_count}")
    return url_count


hostels_links = links_city_hostels()


def city_hostel_dict():
    name_list = []
    composite_hostel_scores = []

    for url in range(0, hostels_links):
        page = requests.get(links_list[url], timeout=10)

        soup = BeautifulSoup(page.content, "html.parser")
        soup.prettify()

        hostel_name = soup.find("h1").text.strip()
        name_list.append(hostel_name)

        parent_divs = soup.find_all('div', class_='rating-label-score-wrapper')

        specific_scores = [
            parent_div.find('div', class_='rating-score').text.strip() for
            parent_div in parent_divs
        ]

        composite_hostel_scores.append(specific_scores)

        lists_to_join = zip(name_list, composite_hostel_scores)
        specific_ratings = list(lists_to_join)
        # print(f"\nSpecific ratings: {specific_ratings}\n")
        ratings_dict = dict(specific_ratings)

        dict_length = len(ratings_dict)

        seconds = randint(2, 10)
        sleep(seconds)

        print(f"\nProgress: {dict_length}/{hostels_links} ")
        print(f"I waited {seconds} seconds\n")

        sleep(randint(2, 10))

    no_ratings_dict = {key: value for (key, value) in ratings_dict.items() if not value} # noqa

    ratings_dict = {key: value for (key, value) in ratings_dict.items() if value} # noqa

    no_rating_list = list(no_ratings_dict.keys())
    no_rating_string = ", ".join([str(elem) for elem in no_rating_list])

    print(f"\nComplete Dictionary: {ratings_dict}\n")
    print(f"Unrated hostels: {no_rating_string}")
    return ratings_dict


city_ratings_dict = city_hostel_dict()

df = pd.DataFrame(city_ratings_dict)
# print(df)
df.to_csv("Hostel_City_Ratings.csv")
print("\nCSV created! YAY!!\n")
