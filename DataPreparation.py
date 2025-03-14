# import
import pandas as pd
import numpy as np
import sqlite3

# load raw data
ratings = pd.read_csv('Datasets/BX-Book-Ratings.csv', encoding='cp1251', sep=';')
books = pd.read_csv('Datasets/BX-Books.csv',  encoding='cp1251', sep=';', on_bad_lines="skip", low_memory=False)

# Drop duplicates, null values and rows with rating 0
ratings = ratings.drop_duplicates().dropna()
books = books.drop_duplicates().dropna()
ratings = ratings[ratings["Book-Rating"] != 0]
books["Book-Title"] = books["Book-Title"].str.strip()

books = books[["ISBN","Book-Title","Book-Author","Image-URL-L"]]

"""
Creation of dataset for frontend 
"""

# Choosing only Users with at least 5 reviews
UserIDCounts = ratings.groupby('User-ID').size()
ValidUserID = UserIDCounts[UserIDCounts >= 5].index
ratings = ratings[ratings['User-ID'].isin(ValidUserID)]

# Choosing only Books with at least 30 reviews
Book_rating = pd.merge(books,ratings,on="ISBN")
book_counts = Book_rating.groupby('ISBN').size()
valid_isbn = book_counts[book_counts >= 30].index
Book_rating = Book_rating[Book_rating['ISBN'].isin(valid_isbn)]
books_fr_list = books[books['ISBN'].isin(valid_isbn)]

# Getting rid of duplicate values for frontend
books_fr_list = books_fr_list.drop_duplicates(subset=["Book-Title"])
BooksList = books_fr_list[["ISBN", "Book-Title"]]

"""
Inserting data cleaned data into the database 
(if it was some dataset with regular updates the we wouln´t replaced the whole table each time, instead we would be 
checking for new rows and adding them toward the tables in the database
"""

connection = sqlite3.connect("books.db")

# Saving tables to the database

books.to_sql("books", connection, if_exists="replace", index=False)
ratings.to_sql("ratings", connection, if_exists="replace", index=False)
BooksList.to_sql("FrontendBookList", connection, if_exists="replace", index=False)
print("Data was successfully saved to the Database")

connection.close()




