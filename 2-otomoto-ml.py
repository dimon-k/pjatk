# coding: utf-8
# ^^ Including the above line for setting up text coding to utf-8,
# it's needed because we use Polish language in our code.

# Before importing any packages visible below, we need to make sure it's installed using 'pip install ...'
from pymongo import MongoClient # MongoDB client for Python - allows to communicate with Mongo directly from Python
# If needed we can use MongoDB Compass desktop app (GUI) for nice data preview
import pandas as pd # needed for creating data sets and data frames
import numpy as np # needed for mathematical functions in Machine Learning
import matplotlib.pyplot as plt # we'll use it for data visualisation when needed to discover data
from sklearn.linear_model import LinearRegression # importing Linear Regression model
from sklearn.model_selection import train_test_split # usefull tool for splitting data into 'train' and 'test' sets
from sklearn.tree import DecisionTreeRegressor # importing Decision Tree Regressor model
from sklearn.neural_network import MLPRegressor # importing MLPRegressor model
from sklearn.ensemble import RandomForestRegressor # importing RandomForestRegressor model
from sklearn.ensemble import ExtraTreesRegressor # importing ExtraTreesRegressor model
from sklearn.ensemble import GradientBoostingRegressor # importing GradientBoostingRegressor model
from sklearn.ensemble import BaggingRegressor # importing BaggingRegressor model


# After all packages are imported we can start by setting up a connection with our Database:
client = MongoClient() # in our case we don't need to provide any additional parameters because Mongo server is running on defaults
db = client.otomoto # connecting to our 'otomoto' database
offers = db.offers # creating 'offers' collection in our 'otomoto' database

# Pulling all the offers from our database, converting to 'list' and then creating a DataFrame
# As a last step, using method 'fillna' filling missing values with zeros (0)
# When importing data, it was thought out to structure data this way, so zeros here are desired values, not compromised
df = pd.DataFrame(list(offers.find())).fillna(0)

# Defining a variable that will hold all column names from our database (123 in total)
# We won't use this variable actually, it's just for our record
columns_list = df.columns.tolist()

# Splitting collumns into three groups (I did split it manually, so all the values are visible):
# 1. Categorical once that needs to be converted onto Integer (14 columns)
columns_list_categorical = ['Marka pojazdu', 'Model pojazdu', 'Kategoria', 'Kolor', 'Kraj pochodzenia', 'Napęd', 'Oferta od', 'Rodzaj paliwa', 'Skrzynia biegów', 'Stan', 'Typ', 'Wersja', 'Miasto', 'Wojewodztwo']
# 2. The once that we want to use for our Machine Learning processes (95 columns)
columns_list_to_be_used = ['Akryl (niemetalizowany)', 'Bezwypadkowy', 'Emisja CO2', 'Faktura VAT', 'Filtr cząstek stałych', 'Leasing', 'Homologacja ciężarowa', 'Kierownica po prawej (Anglik)', 'Liczba drzwi', 'Liczba miejsc', 'Metalik', 'Matowy', 'Moc', 'Możliwość finansowania', 'Perłowy', 'Pierwszy właściciel', 'Pojemność skokowa', 'Przebieg', 'Rok produkcji', 'Serwisowany w ASO', 'Tuning', 'Uszkodzony', 'VAT marża', 'Wyposażenie: ABS', 'Wyposażenie: ASR (kontrola trakcji)', 'Wyposażenie: Alarm', 'Wyposażenie: Alufelgi', 'Wyposażenie: Isofix', 'Wyposażenie: Asystent parkowania', 'Wyposażenie: Asystent pasa ruchu', 'Wyposażenie: Bluetooth', 'Wyposażenie: MP3', 'Wyposażenie: CD', 'Wyposażenie: Centralny zamek', 'Wyposażenie: Czujnik deszczu', 'Wyposażenie: Hak', 'Wyposażenie: Czujnik martwego pola', 'Wyposażenie: Czujnik zmierzchu', 'Wyposażenie: Czujniki parkowania przednie', 'Wyposażenie: Czujniki parkowania tylne', 'Wyposażenie: Dach panoramiczny', 'Wyposażenie: ESP (stabilizacja toru jazdy)', 'Wyposażenie: Elektrochromatyczne lusterka boczne', 'Wyposażenie: Elektrochromatyczne lusterko wsteczne', 'Wyposażenie: Elektryczne szyby przednie', 'Wyposażenie: Elektryczne szyby tylne', 'Wyposażenie: Gniazdo USB', 'Wyposażenie: Elektrycznie ustawiane fotele', 'Wyposażenie: Elektrycznie ustawiane lusterka', 'Wyposażenie: Gniazdo AUX', 'Wyposażenie: Gniazdo SD', 'Wyposażenie: HUD (wyświetlacz przezierny)', 'Wyposażenie: Immobilizer', 'Wyposażenie: Kamera cofania', 'Wyposażenie: Klimatyzacja automatyczna', 'Wyposażenie: Klimatyzacja czterostrefowa', 'Wyposażenie: Klimatyzacja dwustrefowa', 'Wyposażenie: Klimatyzacja manualna', 'Wyposażenie: Komputer pokładowy', 'Wyposażenie: Kurtyny powietrzne', 'Wyposażenie: Nawigacja GPS', 'Wyposażenie: Odtwarzacz DVD', 'Zarejestrowany w Polsce', 'Wyposażenie: Ogranicznik prędkości', 'Wyposażenie: Ogrzewanie postojowe', 'Wyposażenie: Podgrzewana przednia szyba', 'Wyposażenie: Podgrzewane lusterka boczne', 'Wyposażenie: Podgrzewane przednie siedzenia', 'Wyposażenie: Radio fabryczne', 'Wyposażenie: Podgrzewane tylne siedzenia', 'Wyposażenie: Poduszka powietrzna chroniąca kolana', 'Wyposażenie: Tuner TV', 'Wyposażenie: Poduszka powietrzna kierowcy', 'Wyposażenie: Poduszka powietrzna pasażera', 'Wyposażenie: Przyciemniane szyby', 'Wyposażenie: Poduszki boczne przednie', 'Wyposażenie: Poduszki boczne tylne', 'Wyposażenie: Radio niefabryczne', 'Wyposażenie: Regulowane zawieszenie', 'Wyposażenie: Relingi dachowe', 'Wyposażenie: System Start-Stop', 'Wyposażenie: Szyberdach', 'Wyposażenie: Tapicerka skórzana', 'Wyposażenie: Tapicerka welurowa', 'Wyposażenie: Tempomat', 'Wyposażenie: Tempomat aktywny', 'Wyposażenie: Wielofunkcyjna kierownica', 'Wyposażenie: Wspomaganie kierownicy', 'Wyposażenie: Zmieniarka CD', 'Wyposażenie: Łopatki zmiany biegów', 'Wyposażenie: Światła LED', 'Wyposażenie: Światła Xenonowe', 'Wyposażenie: Światła do jazdy dziennej', 'Wyposażenie: Światła przeciwmgielne', 'Zarejestrowany jako zabytek']
# 3. The once that we do not want to use for our Machine Learning processes (13 columns)
# We won't use this variable actually, it's just for our record
columns_list_not_to_be_used = ['_id', 'Data publikacji', 'Liczba pozostałych rat', 'Miesięczna rata', 'Numer rejestracyjny pojazdu', 'VIN', 'Kod Silnika', 'Opis', 'Opłata początkowa', 'Otomoto id', 'Pierwsza rejestracja', 'Url', 'Wartość wykupu']

# Selecting 'label' column - the one that we are going to predict
label = df['Cena']

# Converting our categorical data into Integer
# We need to iterate through all column with categorical data
for column in columns_list_categorical:
    # To make sure all is working correctly, let's decode our strings to utf-8
    column = column.decode('utf-8')
    # To be able to convert categorical data into Integer, first we need to know how many values in each column we have
    # First we peek a desired column from our data frame, then using 'set' method we filter unique values and convert to list
    unique_values = list(set(df[column]))
    # 'mapping' variable will serve as a temporary { key: value } dictionary, for example: { red: 1, blue: 2 }
    mapping = {}
    # To be able to fill our 'mapping' variable we need to iterate through all unique values
    for value in unique_values:
        # Adding { key: value } to our 'mapping' dictionary, where key is our value, and value is value's index
        # As I mentioned in 'otomoto-scraping.py' file, to accomplish this while importing data it could be very difficult,
        # but at this point we can see it's just a few lines of code - very easy
        mapping.update( {value : unique_values.index(value)} )
    # Last but not least, we need to convert our categorical values in data frame
    # This step takes a while!
    df[column] = df[column].replace(mapping)
    # That way ^^ instead of ['red', 'blue', 'green'] values, we'll first get [0,1,2] values - which is just perfect for Machine Learning algorithms

# One last thing that I found while testing first, LinearRegression model,
# Some (0 or 1) columns contain few records with not only zero (0) and one (1) values
# Let's fix it!
df['Akryl (niemetalizowany)'] = df['Akryl (niemetalizowany)'].replace({ u'acrylic': 1 })
df['Matowy'] = df['Matowy'].replace({ u'matt': 1 })
df['Metalik'] = df['Metalik'].replace({ u'metallic': 1 })

# Preparing 'final_columns_list' that we'll use for pulling data from data frame
# To make sure all is working correctly, let's use 'map' method with 'lambda' to decode our strings to utf-8
# For that we should use our predefined variables with column names: 'columns_list_to_be_used' and 'columns_list_categorical'
final_columns_list = map(lambda column: column.decode('utf-8'), columns_list_to_be_used + columns_list_categorical)
# Pulling data from data frame for Machine Learning models using our new, freshly prepared 'final_columns_list' variable
train_data = df[final_columns_list]

# Splitting the data into train and test data using 'train_test_split' method
x_train, x_test, y_train, y_test = train_test_split(train_data, label, test_size=0.1, random_state=2)

# Few Machine Learning models below!

# LinearRegression:
linear_regression = LinearRegression()
linear_regression.fit(x_train, y_train)
lr_score = linear_regression.score(x_test, y_test)
print('LinearRegression score: ' + str(lr_score)) # -> 0.6552409768836058

# MLPRegressor:
mlp_regressor = MLPRegressor()
mlp_regressor.fit(x_train, y_train)
mlpr_score = mlp_regressor.score(x_test, y_test)
print('MLPRegressor score: ' + str(mlpr_score)) # -> 0.8113884821105333

# DecisionTreeRegressor:
decision_tree_regressor = DecisionTreeRegressor()
decision_tree_regressor.fit(x_train, y_train)
dt_score = decision_tree_regressor.score(x_test, y_test)
print('DecisionTreeRegressor score: ' + str(dt_score)) # -> 0.8642185163401331

# GradientBoostingRegressor:
gradient_boosting_regressor = GradientBoostingRegressor()
gradient_boosting_regressor.fit(x_train, y_train)
gb_score = gradient_boosting_regressor.score(x_test, y_test)
print('GradientBoostingRegressor score: ' + str(gb_score)) # -> 0.8978408816999488

# ExtraTreesRegressor:
extra_trees_regressor = ExtraTreesRegressor()
extra_trees_regressor.fit(x_train, y_train)
et_score = extra_trees_regressor.score(x_test, y_test)
print('ExtraTreesRegressor score: ' + str(et_score)) # -> 0.9071302394368891

# BaggingRegressor:
bagging_regressor = BaggingRegressor()
bagging_regressor.fit(x_train, y_train)
b_score = bagging_regressor.score(x_test, y_test)
print('BaggingRegressor score: ' + str(b_score)) # -> 0.9154010467830169

# RandomForestRegressor:
random_forest_regressor = RandomForestRegressor()
random_forest_regressor.fit(x_train, y_train)
rf_score = random_forest_regressor.score(x_test, y_test)
print('RandomForestRegressor score: ' + str(rf_score)) # -> 0.920122663462127

# RandomForestRegressor(max_depth=5, random_state=0, n_estimators=100):
random_forest_regressor = RandomForestRegressor(max_depth=5, random_state=0, n_estimators=100)
random_forest_regressor.fit(x_train, y_train)
rf_score_1 = random_forest_regressor.score(x_test, y_test)
print('RandomForestRegressor(max_depth=5, random_state=0, n_estimators=100) score: ' + str(rf_score_1)) # -> 0.8134829521876554

# RandomForestRegressor(max_depth=200, random_state=100, n_estimators=50):
random_forest_regressor = RandomForestRegressor(max_depth=200, random_state=100, n_estimators=50)
random_forest_regressor.fit(x_train, y_train)
rf_score_2 = random_forest_regressor.score(x_test, y_test)
print('RandomForestRegressor(max_depth=200, random_state=100, n_estimators=50) score: ' + str(rf_score_2)) # -> 0.9329107755184214
