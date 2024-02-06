import pandas as pd
import numpy as np
import re
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

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

def get_recommendations(
    game_names, platform: str, dataframe, unliked=False
):
    """
    This function returns the top 10 recommendations for the user based on the
    games that the user liked or not.

    Args:
    user_games: list with the names of the games that the user liked
    platform: string with the name of the platform
    dataframe: dataframe with the information of the games
    unliked: boolean that indicates if the user wants to get recommendations
             based on the games that the user did not like

    Returns:
    recommendations: dataframe with the top 10 recommendations
    """
    try:
        subset = dataframe[dataframe["platform"] == platform]
        subset.reset_index(inplace=True, drop=True)

        cosine_similarities_concat = np.empty((1, len(subset)))
        euclidean_similarities_concat = np.empty((1, len(subset)))

        for game_name in game_names:
            cosine_similarities, euclidean_similarities = similarities_calcul(
                game_name, subset
            )
            cosine_similarities_concat = np.concatenate(
                (cosine_similarities, cosine_similarities_concat), axis=0
            )
            euclidean_similarities_concat = np.concatenate(
                (euclidean_similarities, euclidean_similarities_concat), axis=0
            )

        final_cosinus_similarity = cosine_similarities_concat[: len(game_names) - 1]
        final_euclidean_similarity = euclidean_similarities_concat[: len(game_names) - 1]

        # Calculer la moyenne des matrices de similarité
        avg_cosinus_similarity = np.mean(
            [final_cosinus_similarity[i, :] for i in range(len(game_names) - 1)], axis=0
        )
        avg_euclidean_similarity = np.mean(
            [final_euclidean_similarity[i, :] for i in range(len(game_names) - 1)], axis=0
        )

        overall_avg_similarity = (avg_cosinus_similarity + avg_euclidean_similarity) / 2

        # Trier les jeux par similarité moyenne
        sorted_game_indices = np.argsort(overall_avg_similarity)[::-1]

        # Obtenir les recommandations
        recommendations = subset[
            ["name", "genre", "platform", "score", "date", "ratio_confiance"]
        ].iloc[
            sorted_game_indices
        ]

        filtered_recommendations = recommendations[
            ~recommendations["name"].isin(game_names)
        ]

        cosine_similarity_score = pd.DataFrame(
            avg_cosinus_similarity[filtered_recommendations.index],
            columns=["cosine_score"]
        )
        euclidean_similarity_score = pd.DataFrame(
            avg_euclidean_similarity[filtered_recommendations.index],
            columns=["euclidean_score"],
        )
        overall_similarity_score = pd.DataFrame(
            overall_avg_similarity[filtered_recommendations.index],
            columns=["overall_mean_score"],
        )

        filtered_recommendations.reset_index(inplace=True, drop=True)
        filtered_recommendations = filtered_recommendations.join(
                                                    cosine_similarity_score
        )
        filtered_recommendations = filtered_recommendations.join(
                                                    euclidean_similarity_score
        )
        filtered_recommendations = filtered_recommendations.join(
                                                    overall_similarity_score
        )

        if unliked:
            filtered_recommendations = filtered_recommendations.sort_values(
                by="overall_mean_score", ascending=True
            )
            return filtered_recommendations[
                [
                    "name",
                    "genre",
                    "date",
                    "score",
                    "ratio_confiance",
                    "cosine_score",
                    "euclidean_score",
                    "overall_mean_score",
                ]
            ][:10]
        else:
            return filtered_recommendations[
                [
                    "name",
                    "genre",
                    "date",
                    "score",
                    "ratio_confiance",
                    "cosine_score",
                    "euclidean_score",
                    "overall_mean_score",
                ]
            ][:10]
    except:
        return

def similarities_calcul(game, dataframe):
    """
    This function calculates the cosine similarity and the euclidean distance
    between the game and the rest of the games in the dataframe.

    Args:
    game: string with the name of the game
    dataframe: dataframe with the information of the games

    Returns:
    cosine_similarities: array with the cosine similarity between the game and
                        the rest of the games
    euclidean_distances_values: array with the euclidean distance between
                                the game and the rest of the games
    """

    similarity_features = (
        dataframe["stem_summary"]
        + " "
        + dataframe["genre"]
        + " "
        + dataframe["score"].astype(str)
        + " "
        + dataframe["date"].astype(str)
    )
    token_game = (
        dataframe[dataframe["name"] == game]["stem_summary"]
        + " "
        + dataframe[dataframe["name"] == game]["stem_summary"]
        + " "
        + dataframe[dataframe["name"] == game]["genre"]
        + " "
        + dataframe[dataframe["name"] == game]["score"].astype(str)
        + " "
        + dataframe[dataframe["name"] == game]["date"].astype(str)
    )

    try:
        tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(0, 2)
            )
        tfidf_matrix = tfidf_vectorizer.fit_transform(similarity_features)
        tfidf_game = tfidf_vectorizer.transform(token_game)

        # Cosine similarity
        cosine_similarities = cosine_similarity(tfidf_game, tfidf_matrix)

        # Euclidean similarity
        euclidean_distances_values = euclidean_distances(tfidf_game, tfidf_matrix)

        return cosine_similarities, euclidean_distances_values
    except:
        return
