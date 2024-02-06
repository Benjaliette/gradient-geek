import pandas as pd
import re
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

def delete_duplicates(df, columns: list):
    """
    This function removes the duplicates from the dataframe.

    Args:
    df: dataframe with the information of the games
    columns: list with the names of the columns to be used

    Returns:
    clean: dataframe without duplicates
    """
    clean = df[df.duplicated(columns).values == False]
    return clean


def nlp_processing(df, serie):
    """
    This function stems and lemmatizes the summary of the games.

    Args:
    df: dataframe with the information of the games
    serie: series with the summary of the games

    Returns:
    df: dataframe with the stemmed and lemmatized summary
    """
    stemmer = PorterStemmer()
    lemmatiser = WordNetLemmatizer()
    stem_lem_series = []

    for index, sentence in serie.items():
        stemmed_words = [stemmer.stem(word) for word in sentence.split()]
        stemmed_sentence = " ".join(stemmed_words)
        lem_words = [
            lemmatiser.lemmatize(word) for word in stemmed_sentence.split()
        ]
        lem_sentence = " ".join(lem_words)
        stem_lem_series.append(lem_sentence)

    df_lemm = pd.DataFrame({"stem_summary": stem_lem_series})
    df = df.join(df_lemm)
    return df


def preprocessing_function(
    dataframe,
    column_names: list,
    column_processed: str
):
    """
    This function preprocesses the dataframe by removing duplicates and
    missing values, and by stemming and lemmatizing the summary of the games.

    Args:
    dataframe: dataframe with the information of the games
    column_names: list with the names of the columns to be used
    column_processed: string with the name of the column to be processed

    Returns:
    dataframe: preprocessed dataframe
    """
    dataframe = dataframe.dropna()
    df_clean = delete_duplicates(dataframe, column_names)
    df_clean = df_clean.reset_index(drop=True)
    df = nlp_processing(df_clean, df_clean[column_processed])
    return df.reset_index(drop=True)

def recommend_by_category(category, df):
    for index, categories in df['Genre'].items():
        if re.search(category, categories) :
            return df[df['Genre'].eq(category)]
    else:
        return {'message': 'Aucun jeu trouvé dans la catégorie spécifiée.'}
