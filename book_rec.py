# import
import pandas as pd
import numpy as np
import sqlite3

"""
Script with book recommendation function

Firstly we need to load the data from the database
"""
conn = sqlite3.connect("books.db")

ratings = pd.read_sql_query("SELECT * FROM ratings;", conn)
books = pd.read_sql_query("SELECT * FROM books;", conn)
BooksList = pd.read_sql_query("SELECT * FROM FrontendBookList;", conn)
conn.close()


def get_options() -> dict:
    """
    Returns dict with unique books list which should be shown in the selector in the frontend

    :returns: Dict containing book-titles which will be shown in the selector on main page
    """
    return BooksList.to_dict(orient="records")


def book_recommendation_engine(isbn: str):
    """
    The function which will create books recommendations based on user reviews
    :param isbn: ISNB of the book we want the recommendation for
    :return: Dataframe of recommended books consisting 3 atributes: Book-Title (Object), Book-Author (Object)
    and Image-URL-L (image of the book)
    """

    dataset = pd.merge(ratings, books, on=['ISBN'])
    dataset_lowercase = dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
    books_lowercase = books.drop("Image-URL-L", axis=1).apply(lambda x: x.str.lower() if (x.dtype == 'object') else x)
    books_lowercase["Image-URL-L"] = books["Image-URL-L"]
    # Finding book name according to ISBN
    SelectedBook = books_lowercase[books_lowercase['ISBN'] == str(isbn).lower()]
    Book_name = SelectedBook["Book-Title"].tolist()[0]
    Book_author = SelectedBook["Book-Author"].str.split().str[-1].tolist()[0]
    # Here we get Users who rated our selected book
    selected_book_readers = dataset_lowercase['User-ID'][(dataset_lowercase['Book-Title'] == Book_name) &
                                                         (dataset_lowercase['Book-Author'].str.contains(Book_author))]
    selected_book_readers = selected_book_readers.tolist()
    selected_book_readers = np.unique(selected_book_readers)

    # final dataset
    # Here are only rows with Users that made the review toward selected book
    books_of_author_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(selected_book_readers))]

    # Number of ratings per other books in dataset
    # We are calculation how many reviews books got
    number_of_rating_per_book = books_of_author_readers.groupby(['Book-Title']).agg('count').reset_index()

    # select only books which have actually higher number of ratings than threshold

    books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]
    books_to_compare = books_to_compare.tolist()

    ratings_data_raw = books_of_author_readers[['User-ID', 'Book-Rating', 'Book-Title']][books_of_author_readers['Book-Title'].isin(books_to_compare)]

    # group by User and Book and compute mean

    ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

    # reset index to see User-ID in every row
    ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

    dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

    LoR_list = Book_name

    result_list = []
    worst_list = []

    #Take out the Lord of the Rings selected book from correlation dataframe
    dataset_of_other_books = dataset_for_corr.copy(deep=False)

    dataset_of_other_books.drop([LoR_list], axis=1, inplace=True)

    # empty lists
    book_titles = []
    correlations = []
    avgrating = []
    # corr computation
    for book_title in list(dataset_of_other_books.columns.values):
        book_titles.append(book_title)
        correlations.append(dataset_for_corr[LoR_list].corr(dataset_of_other_books[book_title]))
        tab = (ratings_data_raw[ratings_data_raw['Book-Title'] == book_title].groupby(ratings_data_raw['Book-Title']).mean("Book-Rating"))

        avgrating.append(tab['Book-Rating'].min())

    # final dataframe of all correlation of each book
    corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
    corr_fellowship.sort_values('corr', ascending=False).head(10)

    # top 10 books with highest corr
    result_list.append(corr_fellowship.sort_values('corr', ascending=False).head(10))

    corr_fellowship = corr_fellowship[["book", "corr"]]

    # Creating the final dataframe which will be shown in frontend
    final_dataset = pd.merge(corr_fellowship, books_lowercase,how="left",left_on="book",right_on="Book-Title")
    final_dataset = final_dataset.drop_duplicates(subset=["book"])
    final_dataset = final_dataset.sort_values('corr', ascending=False).head(10)
    final_dataset[["book", "Book-Author"]] = final_dataset[["book","Book-Author"]].apply(lambda x: x.str.upper())
    final_dataset = final_dataset[["book", "Book-Author", "Image-URL-L"]]

    return final_dataset


