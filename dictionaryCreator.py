import shelve
import snowballstemmer
from stop_words import get_stop_words
import re
from sklearn.feature_extraction.text import CountVectorizer
import joblib
from collections import Counter

def separate_articles_by_language(article_db):
    article_db_french = {}
    article_db_english = {}

    # Sépare les articles par langue
    for article_id, article in article_db.items():
        language = article.get('Langue', '').lower()
        if language == 'fr':
            article_db_french[article_id] = article
        elif language == 'en':
            article_db_english[article_id] = article

    return article_db_french, article_db_english
        
def process_articles(article_db, stopwords, stemmer):
    all_processed_texts = []

    # Traite les articles
    for article_id, article in article_db.items():
        title = article.get('Titre', '')
        description = article.get('Description / Résumé', '')
        content = article.get('Contenu', '')

        # Combine les valeurs et imprime
        combined_text = f"{title} {description} {content}"

        # Supprime la ponctuation, met en minuscules et supprime les chiffres
        text_without_punctuation = re.sub(r'[^\w\s]', '', combined_text)
        text_lower = text_without_punctuation.lower()
        text_without_numbers = re.sub(r'\d+', '', text_lower)

        # Tokenize le texte et effectue le stemming
        words = text_without_numbers.split()
        filtered_words = [word for word in words if word.lower() not in stopwords]
        stemmed_words = [stemmer.stemWord(word) for word in filtered_words]

        # Combine les mots stemmés en une chaîne pour CountVectorizer
        processed_text = ' '.join(stemmed_words)

        # Ajoute le texte traité à la liste
        all_processed_texts.append(processed_text)

    return all_processed_texts

def save_and_load_data(vectorizer, sparse_matrix, filename_feature, filename_matrix):
    # Sauvegarde les noms de caractéristiques et la matrice creuse dans deux fichiers
    joblib.dump(vectorizer.get_feature_names_out(), filename_feature)
    joblib.dump(sparse_matrix, filename_matrix)

    # Charge les noms de caractéristiques et la matrice creuse en mémoire
    loaded_feature_names = joblib.load(filename_feature)
    loaded_sparse_matrix = joblib.load(filename_matrix)

    return loaded_feature_names, loaded_sparse_matrix

def calculate_word_occurrences(feature_names, sparse_matrix):
    total_word_occurrences = Counter()
    for row in sparse_matrix:
        total_word_occurrences += Counter({feature: count for feature, count in zip(feature_names, row.toarray()[0])})

    return total_word_occurrences

def display_word_occurrences(word_occurrences):
    # Affiche le nombre total d'occurrences de chaque mot avec plus de 100 occurrences, trié par nombre en ordre décroissant
    print("\nTotal des occurrences de mots dans tous les articles (avec plus de 100 occurrences), trié par nombre:")

    # Trie le dictionnaire total_word_occurrences par nombre en ordre décroissant
    sorted_word_occurrences = sorted(word_occurrences.items(), key=lambda x: x[1], reverse=False)

    # Affiche les résultats triés
    for word, count in sorted_word_occurrences:
        print(f"{word}: {count}")


# Définition des langues
lang_french = "french"
lang_english = "english"

# Stemmers et stop words Snowball
stemmer_french = snowballstemmer.stemmer(lang_french)
stopwords_french = get_stop_words(lang_french)

stemmer_english = snowballstemmer.stemmer(lang_english)
stopwords_english = get_stop_words(lang_english)

# Ouvre le fichier shelve en lecture
article_db = shelve.open('./items/defi_db', 'r')

# Sépare les articles par langue
article_db_french, article_db_english = separate_articles_by_language(article_db)

# Ferme le fichier shelve une fois terminé
article_db.close()

# Traite les articles français
all_processed_texts_french = process_articles(article_db_french, stopwords_french, stemmer_french)

# Traite les articles anglais
all_processed_texts_english = process_articles(article_db_english, stopwords_english, stemmer_english)

# Utilise CountVectorizer directement sur les textes traités pour chaque langue
vectorizer_french = CountVectorizer(stop_words=stopwords_french)
all_sparse_matrix_french = vectorizer_french.fit_transform(all_processed_texts_french)

vectorizer_english = CountVectorizer(stop_words=stopwords_english)
all_sparse_matrix_english = vectorizer_english.fit_transform(all_processed_texts_english)

# Sauvegarde et charge les données pour le français
loaded_feature_names_french, loaded_sparse_matrix_french = save_and_load_data(
    vectorizer_french, all_sparse_matrix_french, 'dico/feature_names_french.joblib', 'dico/sparse_matrix_french.joblib'
)

# Sauvegarde et charge les données pour l'anglais
loaded_feature_names_english, loaded_sparse_matrix_english = save_and_load_data(
    vectorizer_english, all_sparse_matrix_english, 'dico/feature_names_english.joblib', 'dico/sparse_matrix_english.joblib'
)

# Calcule les occurrences de mots pour le français
total_word_occurrences_french = calculate_word_occurrences(loaded_feature_names_french, loaded_sparse_matrix_french)
print("\nTotal des occurrences de mots dans tous les articles français:")
display_word_occurrences(total_word_occurrences_french)

# Calcule les occurrences de mots pour l'anglais
total_word_occurrences_english = calculate_word_occurrences(loaded_feature_names_english, loaded_sparse_matrix_english)
print("\nTotal des occurrences de mots dans tous les articles anglais:")
display_word_occurrences(total_word_occurrences_english)
