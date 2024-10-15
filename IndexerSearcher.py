from elasticsearch import Elasticsearch
import shelve

class IndexerSearcher:
    """
    Classe pour gérer la recherche dans Elasticsearch et l'indexation d'articles depuis une base de données Shelve.
    """

    def __init__(self, shelve_db_path, elastic_host, elastic_port, elastic_password, elastic_ca_certs):
        """
        Initialise une instance de la classe ElasticsearchSearch.

        Args:
            shelve_db_path (str): Chemin vers la base de données Shelve.
            elastic_host (str): Hôte Elasticsearch.
            elastic_port (int): Port Elasticsearch.
            elastic_password (str): Mot de passe Elasticsearch.
            elastic_ca_certs (str): Chemin vers le certificat CA pour Elasticsearch.
        """
        self.shelve_db = shelve.open(shelve_db_path, 'r')
        self.elastic_host = elastic_host
        self.elastic_port = elastic_port
        self.elastic_password = elastic_password
        self.elastic_ca_certs = elastic_ca_certs
        self.es = self.setup_elasticsearch()

    def setup_elasticsearch(self):
        """
        Configure et crée un client Elasticsearch.

        Returns:
            Elasticsearch: Client Elasticsearch configuré.
        """
        es = Elasticsearch(
            f"https://{self.elastic_host}:{self.elastic_port}",
            ca_certs=self.elastic_ca_certs,
            basic_auth=("elastic", self.elastic_password)
        )
        if not es.ping():
            raise ValueError("Connection to Elasticsearch failed")
        return es

    def index_articles(self, index_name):
        """
        Indexe tous les articles de la base de données Shelve dans Elasticsearch.

        Args:
            index_name (str): Nom de l'index Elasticsearch.
        """
        for article_id, article in self.shelve_db.items():
            self.es.index(index=index_name, id=article_id, body=article)
            print(f"Indexed article with ID: {article_id}")

    def search(self, index_name, query):
        """
        Effectue une recherche dans Elasticsearch en fonction de la requête et affiche les résultats.

        Args:
            index_name (str): Nom de l'index Elasticsearch.
            query (str): Terme de recherche.
        """
        result = self.es.search(index=index_name, body={
            "query": {
                "bool": {
                    "should": [
                        {"match": {"URL du flux source": query.strip()}},
                        {"match": {"URL de la page source": query.strip()}},
                        {"match": {"Date": query.strip()}},
                        {"match": {"Titre": query.strip()}},
                        {"match": {"Description / Résumé": query.strip()}},
                        {"match": {"Langue": query.strip()}},
                        {"match": {"Contenu": query.strip()}}
                    ]
                }
            },
        })

        if result.get('hits') is not None and result['hits'].get('hits') is not None:
            for hit in result['hits']['hits']:
                print(f"ID: {hit['_id']}")
                print(f"URL du flux source: {hit['_source']['URL du flux source']}")
                print(f"URL de la page source: {hit['_source']['URL de la page source']}")
                print(f"Date: {hit['_source']['Date']}")
                print(f"Titre: {hit['_source']['Titre']}")
                print(f"Description / Résumé: {hit['_source']['Description / Résumé']}")
                print(f"Langue: {hit['_source']['Langue']}")
                print(f"Contenu: {hit['_source']['Contenu']}")
                print("--------")

    def close(self):
        """
        Ferme la base de données Shelve.
        """
        self.shelve_db.close()

# Exemple d'utilisation de la classe
if __name__ == "__main__":
    es_search = IndexerSearcher(
        shelve_db_path='./items/article_db',
        elastic_host='localhost',
        elastic_port=9200,
        elastic_password='4caf_EuW1RkrX77NsO8Y',
        elastic_ca_certs= '../elasticsearch-8.10.3/config/certs/http_ca.crt'
    )

    es_search.index_articles(index_name='rssi')

    query = input("Enter a search: ")
    es_search.search(index_name='rssi', query=query)

    es_search.close()
