import pandas as pd
from sklearn.neighbors import NearestNeighbors
import joblib
import requests
import zipfile
import io
import os

def creating_data():
    print("Hi!")
    # Get current working directory
    current_dir = os.getcwd()
    if not(os.path.exists(current_dir + "/Data")):
        os.mkdir(current_dir + "/Data")
    print(current_dir)

    # Check if the data is already downloaded
    if (not(os.path.exists(current_dir + "/Data/Cleaned_Data.csv"))):
        if (not(os.path.exists(current_dir + "/Books/BX-Books.csv"))) or (
            not(os.path.exists(current_dir + "/Books/BX-Book-Ratings.csv"))):
            zip_file = requests.get("http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip")
            zip_file = zipfile.ZipFile(io.BytesIO(zip_file.content))
            zip_file.extractall(current_dir + "/Books/")

        books_filename = 'Books/BX-Books.csv'
        ratings_filename = 'Books/BX-Book-Ratings.csv'

        df_books = pd.read_csv(
            books_filename,
            encoding = "ISO-8859-1",
            sep=";",
            header=0,
            names=['isbn', 'title', 'author'],
            usecols=['isbn', 'title', 'author'],
            dtype={'isbn': 'str', 'title': 'str', 'author': 'str'})

        df_ratings = pd.read_csv(
            ratings_filename,
            encoding = "ISO-8859-1",
            sep=";",
            header=0,
            names=['user', 'isbn', 'rating'],
            usecols=['user', 'isbn', 'rating'],
            dtype={'user': 'int32', 'isbn': 'str', 'rating': 'float32'})

        df_ratings = df_ratings[(df_ratings.groupby('isbn')['isbn'].transform('size') >= 100) & (
                                df_ratings.groupby('user')['user'].transform('size') >= 200)]
        df = pd.merge(right=df_ratings, left = df_books, on='isbn')
        df.drop_duplicates(subset=['title', 'user'], inplace=True)
        piv = df.pivot(index='title', columns='user', values='rating')
        piv.fillna(0, inplace=True)

        piv.to_csv('Data/Cleaned_Data.csv')
    else:
        piv = pd.read_csv('Data/Cleaned_Data.csv', index_col=0)
    X = piv.values
    neigh = NearestNeighbors(metric='cosine', algorithm='brute').fit(X)
    
    KNN_model = joblib.dump(neigh, 'Data/KNN_model.pkl')

if __name__ == "__main__":
    creating_data()