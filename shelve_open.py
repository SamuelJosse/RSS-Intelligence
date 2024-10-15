import shelve

# Fonction pour ouvrir la base de données shelve en lecture
def open_article_database(file_path):
    return shelve.open(file_path, 'c')



# Fonction pour lire un article en particulier
def read_article(article_db, article_id):
    if article_id in article_db:
        print(f"La clé '{article_id}' existe dans la base de données shelve.")
        article = article_db[article_id]
        print(article)
    else:
        print("Article not found")



# Fonction pour indiquer le nombre d'articles par catégorie
def count_articles_by_category(article_db):
    articles_par_categorie_langue = {}

    for article_id, article_data in article_db.items():
        categorie = article_data.get('Catégorie', 'Catégorie inconnue')
        langue = article_data.get('Langue', 'Langue inconnue')

        if categorie not in articles_par_categorie_langue:
            articles_par_categorie_langue[categorie] = {}
        if langue not in articles_par_categorie_langue[categorie]:
            articles_par_categorie_langue[categorie][langue] = 0

        articles_par_categorie_langue[categorie][langue] += 1

    return articles_par_categorie_langue



# Fonction pour supprimer les articles qui ne sont pas en langue fr ou en
def delete_articles_by_language(article_db):
    articles_to_delete = []
    
    for article_id, article_data in article_db.items():
        langue = article_data.get('Langue', 'Langue inconnue')
        if langue not in ('fr', 'en'):
            articles_to_delete.append(article_id)
    
    for article_id in articles_to_delete:
        del article_db[article_id]
    
    print(f"{len(articles_to_delete)} articles supprimés.")

# Fonction pour afficher le nombre total d'articles
def total_article_count(article_db):
    return len(article_db)

# Fonction pour fermer la base de données shelve
def close_article_database(article_db):
    article_db.close()

article_db = open_article_database('./items/article_db')

# Lecture d'un article en particulier
article_id = 'eaa631984fa0e5b023b5888c21c5c435'
read_article(article_db, article_id)

# Supprimer les articles qui ne sont pas en langue fr ou en
#delete_articles_by_language(article_db)

# Indication du nombre d'articles par catégorie
articles_by_category = count_articles_by_category(article_db)

# Afficher le nombre d'articles par catégorie et par langue
for categorie, langues in articles_by_category.items():
    for langue, nombre_articles in langues.items():
        print(f"{categorie} ({langue}): {nombre_articles} articles")

# Afficher le nombre total d'articles
total_count = total_article_count(article_db)
print(f"Nombre total d'articles : {total_count}")

        
# Fermeture de la base de données shelve
close_article_database(article_db)

