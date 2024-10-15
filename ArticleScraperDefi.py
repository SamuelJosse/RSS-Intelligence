import time
import requests
from bs4 import BeautifulSoup
import textract
import feedparser
import hashlib
from langdetect import detect
import shelve

class ArticleScraperDefi:
    def __init__(self, rss_feeds):
        """
        Initialise la classe ArticleScraperDefi.

        Args:
            rss_feeds (dict): Un dictionnaire de flux RSS avec leurs URL et catégories.
        """
        self.rss_feeds = rss_feeds
        self.article_db = shelve.open('./items/defi_db')
        self.articles_par_categorie = {}

    def generate_unique_id(self, title, url, description):
        """
        Génère un identifiant unique pour un article en se basant sur son titre, son URL et sa description.

        Args:
            title (str): Le titre de l'article.
            url (str): L'URL de l'article.
            description (str): La description ou le résumé de l'article.

        Returns:
            str: Un identifiant unique pour l'article.
        """
        data = title + url + description
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode('utf-8'))
        return md5_hash.hexdigest()

    def extract_text_from_url(self, url):
        """
        Extrait le contenu textuel à partir d'une URL donnée.

        Args:
            url (str): L'URL de la page web.

        Returns:
            str: Le contenu textuel extrait de l'URL.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                extracted_text = " ".join([p.get_text().replace('\n', ' ').replace('\t', ' ') for p in soup.find_all("p")])
                return extracted_text
            else:
                print("La demande a échoué avec le code d'état :", response.status_code)
        except requests.exceptions.ConnectionError as e:
            print("Erreur de connexion :", e)
        except requests.exceptions.RequestException as e:
            print("Erreur de requête :", e)
        except Exception as e:
            print("Une erreur s'est produite :", e)
        return ""

    def scrape_articles(self):
        """
        Parcours les flux RSS spécifiés et extrait les articles, les stockant dans la base de données.

        Cette méthode parcourt les flux RSS spécifiés dans la liste `rss_feeds`, télécharge les articles, et les stocke dans
        la base de données. Les articles sont associés à leurs catégories respectives. Si un article a déjà été enregistré dans
        la base de données, il n'est pas ajouté à nouveau.

        Returns:
            None
        """
        for feed_name, feed_info in self.rss_feeds.items():
            d = feedparser.parse(feed_info['url'])
            for post in d.entries:
                matched_category = feed_info['categorie']
                
                title_normalized = post.title.lower()
                title_language = ''
                if len(title_normalized) >= 3:
                    title_language = detect(title_normalized)
                # Ajout de la validation de la langue ici
                accepted_languages = ['fr', 'en']
                if title_language not in accepted_languages:
                    print(f"L'article n'est pas ajouté car la langue n'est pas acceptée. Langue détectée : {title_language}")
                    continue  # Passe à l'article suivant
                    
                description_normalized = post.summary.lower() if 'summary' in post else ''
                article_id = self.generate_unique_id(post.title, post.link if 'link' in post else '', description_normalized)
                if article_id not in self.article_db:
                    extracted_text = ""
                    if 'link' in post and 'content' not in post:
                        extracted_text = self.extract_text_from_url(post.link)
                    self.articles_par_categorie.setdefault(matched_category, []).append({
                        'URL du flux source': feed_info['url'],
                        'URL de la page source': post.link if 'link' in post else '',
                        'Date': post.published if 'published' in post else '',
                        'Titre': title_normalized,
                        'Description / Résumé': description_normalized,
                        'Langue': title_language if len(title_normalized) >= 3 else '',
                        'Contenu': extracted_text,
                        'Catégorie': matched_category,
                        'Catégorie prédite': '',
                        'Probabilités': []
                    })
                    self.article_db[article_id] = self.articles_par_categorie[matched_category][-1]
                    print("Item stocké en base de données")
                else:
                    print("L'article est déjà présent en base de données, il ne sera pas ajouté.")

        
    def close_database(self):
        """
        Ferme la base de données utilisée pour stocker les articles.

        Cette méthode ferme la base de données shelve utilisée pour stocker les articles collectés à partir des flux RSS.
        Assurez-vous d'appeler cette méthode une fois que vous avez terminé d'utiliser la base de données.

        Returns:
            None
        """
        self.article_db.close()
    

# Exemple d'utilisation du ArticleScraper sur un flux RSS
if __name__ == "__main__":

    rss_feeds = {
        'Anglais': {
            'url': './benchmark/benchmark_en.xml',
            'categorie': '?'
        },'Français': {
            'url': './benchmark/benchmark_fr.xml',
            'categorie': '?'
        }
    }
    
    scraper = ArticleScraperDefi(rss_feeds)
    scraper.scrape_articles()    
    scraper.close_database()
