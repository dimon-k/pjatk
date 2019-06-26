# coding: utf-8
# ^^ Including the above line for setting up text coding to utf-8,
# it's needed because we use Polish language in our code.

# Before importing any packages visible below, we need to make sure it's installed using 'pip install ...'
import requests # will be used for making http requests from our scraper
import time # to make sure we are not banned by otomoto server, we'll be using 'sleep' method between each request
from bs4 import BeautifulSoup # html parser package
from pymongo import MongoClient # MongoDB client for Python - allows to communicate with Mongo directly from Python
# If needed we can use MongoDB Compass desktop app (GUI) for nice data preview


# After all packages are imported we can start by setting up a connection with our Database:
client = MongoClient() # in our case we don't need to provide any additional parameters because Mongo server is running on defaults
db = client.otomoto # connecting to our 'otomoto' database
offers = db.offers # creating 'offers' collection in our 'otomoto' database

# Our 'Base' url contains only sorting 'by newest' offers and has a prepared 'page' param which will be fed in our 'for' loop
url = 'https://www.otomoto.pl/osobowe/?search%5Border%5D=created_at_first%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D=&page='

# Some items on offer details page are clickable, so they have a little bit different DOM structure, we need to distinguish it, to make it working
link_items_as_href = ['Oferta od', 'Kategoria', 'Marka pojazdu', 'Model pojazdu', 'Rodzaj paliwa', 'Napęd', 'Typ', 'Kolor',
                      'Metalik', 'Perłowy', 'VAT marża', 'Kraj pochodzenia', 'Pierwszy właściciel', 'Serwisowany w ASO', 'Stan',
                      'Wersja', 'Skrzynia biegów', 'Bezwypadkowy', 'Akryl (niemetalizowany)', 'Faktura VAT', 'Zarejestrowany w Polsce',
                      'Używane', 'Filtr cząstek stałych', 'Kod Silnika', 'Możliwość finansowania', 'Leasing', 'Uszkodzony', 'Tuning',
                      'Matowy', 'Homologacja ciężarowa', 'Zarejestrowany jako zabytek', 'Kierownica po prawej (Anglik)']
# Some item are out of the box ready to be converted to Integers, so also distinguishing it
convert_to_int = ['Liczba drzwi', 'Liczba miejsc', 'Rok produkcji']

# 'pages' variable takes the amount of pages we want to go through - each page has 32 offers
pages = 3114
# 'count' variable is just a helper which shows us how many records we have already downloaded
count = 0

# We start by creating a loop which will go through a range of pages
for page in range(1, pages):
    # Using a 'requests' library we get a response of a page with 32 offers
    # Prior to the request, of course, we should concatenate our 'url' and a 'page' number
    response = requests.get(url + str(page))

    # Using 'BeautifulSoup' library we parse our response and make it ready to be worked with
    soup = BeautifulSoup(response.text, 'html.parser')

    # At this step we are looking for all 'contents' / offers on a list page
    # Each offer has basic information like: mini photo, price, short description, some parameters and location
    contents = soup.findAll('div', class_='offer-item__content')

    # Then we go through each 'content' / offer
    for content in contents:
        # Creating an empty dictionary which will temporarly hold data before saving it to MongoDB database
        db_record = {}
        
        # Being on the list page, first thing we are interested in, is an url which will lead us to the offer's details page
        link = content.find('a', class_='offer-title__link')
        # Assigning a link of an offer to 'link_url' variable since we'll be using it several times in the code
        link_url = link.get('href')
        # Similarly to the previuos one, making a request and getting data for offer's details page
        link_response = requests.get(link_url)
        # In my code I use 'print' method very often, it helps tracking and easily debugging when something goes wrong
        # Printing offer's details url
        print(link_url)

        # Similarly to the previuos one, parsing our response
        link_soup = BeautifulSoup(link_response.text, 'html.parser')
        # In our parsed offer's details page looking for 'date' and 'otomoto id' items
        link_date_and_id = link_soup.find('div', class_='offer-content__rwd-metabar').findAll('span', class_='offer-meta__value')
        # There are only two elements with 'offer-content__rwd-metabar' class
        # After inspecting the page, we know that 'otomoto id' is stored under second element
        # There were no other way to pull this data since it didn't have any unique id
        link_id = link_date_and_id[1].string.strip()
        # Printing 'otomoto id'
        print(link_id)

        # It's a good approach to check whether a particular offer was already downloaded, if so, we don't want to have any duplications
        # Some times this situation can take place because while we scrape pages, people add offers, so they'll move accross pages
        # It's also a good approach to make this check as early, as possible - so we don't waste our time on data modifications which won't be saved anyways
        if (offers.find_one({'otomoto_id': link_id})):
            # Printing a message that a record was not saved in the database because the same one was already there
            print('DID NOT save!')
            # By calling 'continue' we skip the rest of the code and going to the next offer in our 'for loop' 
            continue

        # Once we make sure an offer is not yet in our database, we can prepare the rest of the data of this offer
        # Pulling a date when an offer was added to Otomoto
        link_date = link_date_and_id[0].string.strip()
        # Printing 'Data publikacji' date
        print(link_date)

        # Looking for 'location' items which contains both, 'state' (województwo) and 'city' (miasto)
        # Since the format is as followed: 'Warszawa (Mazowieckie)' - the best way is to just split by '('
        location = content.find('span', class_='offer-item__location').h4.text.split('(')
        # First element is 'city' (miasto), removing side spaces
        city = location[0].strip()
        # Second element is 'state' (województwo), removing ')' and side spaces
        state = location[1].replace(')', '').strip()
        # Printing 'city' (miasto)
        print(city)
        # Printing 'state' (województwo)
        print(state)
        
        # Looking for 'price' and making basic modifications
        # Removing 'PLN' substring, spaces and new lines
        price = content.find('span', class_='offer-price__number').text.replace('PLN', '').replace(' ', '').replace('\n', '')
        # Printing 'price' (cena)
        print(price)

        # Not often, but some prices are given in other currencies that PLN
        # In case when 'price' is in 'EUR' we want to...
        if ('EUR' in price):
            # ... we want to remove 'EUR' in string as well as replace comas with dots, convert to Float, calculate PLN and then convert to Integer
            price = int(float(price.replace('EUR', '').replace(',', '.'))*4.27)
        # In case when 'price' is in 'USD' we want to...
        elif ('USD' in price):
            # ... we want to remove 'USD' in string as well as replace comas with dots, convert to Float, calculate PLN and then convert to Integer
            price = int(float(price.replace('USD', '').replace(',', '.'))*3.74)
        else:
            # In any other cases, since we already know we deal with PLN, we just want to replace comas with dots and save as is
            price = int(float(price.replace(',', '.')))
        
        # Looking for all basic information items on offer's details page
        # Such us Year, Make, Model and so on
        link_items = link_soup.findAll('li', class_='offer-params__item')
        
        # Iterating through all the basic informations on offer's details page
        for link_item in link_items:
            # For each item we want to pull 'key', which can be for example 'Year' or 'Make'
            key = link_item.span.string.strip()
            # And for each 'key' we also want to have value itself, which can be '2010' or 'Audi' respectively
            value = link_item.div
            # Printing 'key' of the current iteration of items
            print(key)
 
            # At this step we want to check if current 'value' of an 'item' is a string, or a link - for both we needed to have different flows
            # Also coding is not working by default, we cannot compare simple strings with unicode text, so it's better to encode manually
            # We are doing this comparison by checking in pre defined 'link_items_as_href' variable which contains all known links in items
            if (key.encode('utf-8') in link_items_as_href):
                # Printing  'value' of the current iteration of items
                print(value.a.string.encode('utf-8').strip())
                # Items that has 'values' as 'Yes' ('Tak' in polish) we want to convert right away and store in our database as just 1 (one)
                if (value.a.string.encode('utf-8').strip() == 'Tak'):
                    # Adding 'key' and 'value' (as 1) pair to our previously defined 'db_record' variable
                    db_record.update( {key.encode('utf-8') : 1} )
                else:
                    # If 'value' is not 'Tak', we want to store real value
                    # Prior to adding to our 'db_record' variable, you can see many times we always 'encode' strings and if needed 'strip' all the spaces
                    db_record.update( {key.encode('utf-8') : value.a.string.encode('utf-8').strip()} )
            else:
                # If our item is not link, we have a different flow for that
                # Printing 'value' of the current iteration of items
                print(value.string.encode('utf-8').strip())
                # In this flow, different 'keys' has also different flows
                # In case when the 'key' is 'Przebieg' we want to...
                if (key.encode('utf-8') == 'Przebieg'):
                    # ... we want to encode, remove 'km' in string as well as all the spaces and new lines, at the end we convert to Integer
                    db_record.update( {key.encode('utf-8') : int(value.string.encode('utf-8').replace('km', '').replace(' ', '').replace('\n', ''))} )
                # In case when the 'key' is 'Pojemność skokowa' we want to...
                elif (key.encode('utf-8') == 'Pojemność skokowa'):
                    # ... we want to encode, remove 'cm3' in string as well as all the spaces and new lines, at the end we convert to Integer
                    db_record.update( {key.encode('utf-8') : int(value.string.encode('utf-8').replace('cm3', '').replace(' ', '').replace('\n', ''))} )
                # In case when the 'key' is 'Moc' we want to...
                elif (key.encode('utf-8') == 'Moc'):
                    # ... we want to encode, remove 'KM' in string as well as all the spaces and new lines, at the end we convert to Integer
                    db_record.update( {key.encode('utf-8') : int(value.string.encode('utf-8').replace('KM', '').replace(' ', '').replace('\n', ''))} )
                # In case when the 'key' is 'Emisja CO2' we want to...
                elif (key.encode('utf-8') == 'Emisja CO2'):
                    # ... we want to encode, remove 'g/km' in string as well as all the spaces and new lines, at the end we convert to Integer
                    db_record.update( {key.encode('utf-8') : int(value.string.encode('utf-8').replace('g/km', '').replace(' ', '').replace('\n', ''))} )
                # In case when the 'key' is just a number (we predefined this values in 'convert_to_int' variable) we want to...
                elif (key.encode('utf-8') in convert_to_int):
                    # ... we want to encode, remove all the side spaces and convert to Integer
                    db_record.update( {key.encode('utf-8') : int(value.string.encode('utf-8').strip())} )
                else:
                    # In any other cases we just want to remove all the side spaces and save as is
                    db_record.update( {key.encode('utf-8') : value.string.encode('utf-8').strip()} )

        # In our parsed offer's details page looking for 'feature' items
        # These items are what a car is equipped with, such as ' Anti Blockier System', 'CD changer' or 'Air Conditioning'
        features = link_soup.find('div', class_='offer-features')
        # If no features provided, parser crashes, so we want to protect ourselves from such eventualities by including the below 'if' statement
        if (features != None):
            # Looking for all 'list' items in our features
            features = features.findAll('li', class_='offer-features__item')
            # Iterating through all found features
            for feature in features:
                # Concatenating 'Wyposażenie: ' word and 'feature' itself
                # 'Wyposażenie: ' word will help us to distinguish these items from others base features such as 'year', 'make' and so on
                feature = 'Wyposażenie: ' + feature.text.encode('utf-8').strip()
                # Printing full 'feature' message that will be stored in the database
                print(feature)
                # Adding our 'feature' to our previously defined 'db_record' variable
                # Similarly to the 'link_items' few lines above, with a simple value 1 (one)
                db_record.update( {feature : 1} )
        
        # Last but not least looking for full description
        # Full descriptions could be a good dataset for Data Mining project
        description = link_soup.find('div', class_='offer-description').div.text.strip()
        # Printing full description
        print(description)

        # At the end, before saving to the database our previously defined and updated along the way 'db_record' variable
        # We want to print a link to the offer to make sure if something brakes, we can debug
        print(link_url)

        # Finally adding the rest of general information to our 'db_record' variable
        db_record.update({'Otomoto id': link_id,
                          'Data publikacji': link_date,
                          'Cena': price,
                          'Miasto': city,
                          'Wojewodztwo': state,
                          'Url': link_url,
                          'Opis': description })
        # Saving to the MongoDB database
        offers.insert_one(db_record)
        # Printing a message that a record was saved successfully
        print('saved!')

        # Since one iteration is almost complete here, incrementing our 'count' helper by 1
        count += 1
        # Printing current 'count' number so we could see how many records were already saved to the database
        print(count)
        # This line is not necessary, but recommended to use so Otomoto server does not ban us
        # Adding half a second of break before making another request and starting new iteration
        time.sleep(0.5)

# Printing a message that all iterations, through all the pages we wanted to go through (stored in 'pages' variable) are DONE!
print('!!!!END!!!!')
