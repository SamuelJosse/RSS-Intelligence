MANUEL D'INSTALLATION / D'UTILISATEUR :

Python est nécessaire pour exécuter le programme.
Afin d'installer toutes les librairies nécessaires, veuillez lancer la commande suivante :
    pip install -r requirements.txt

Pour lancer le programme, il faut exécuter les fichiers python à l'aide des commandes suivantes :
python ArticleScraper.py (attention au temps d'attente, très long à la première exécution)
python dictionaryCreator.py

Ensuite, plusieurs possibilités :
    * Lancer une recherche avec ElasticSearch : python IndexerSearcher.py (saisir un mot-clé pour lancer la recherche)
    * Interagir avec la base de données shelve : python shelve_open.py
    * Utiliser le classifiers pour prédire la catégorie d'un item : lancer classifiers.ipynb avec Jupyter Notebook ou Colab
