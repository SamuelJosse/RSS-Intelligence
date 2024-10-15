import time
import requests
from bs4 import BeautifulSoup
import textract
import feedparser
import hashlib
from langdetect import detect
import shelve

class ArticleScraper:
    def __init__(self, rss_feeds):
        """
        Initialise la classe ArticleScraper.

        Args:
            rss_feeds (dict): Un dictionnaire de flux RSS avec leurs URL et catégories.
        """
        self.rss_feeds = rss_feeds
        self.article_db = shelve.open('./items/article_db')
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
                        'Catégorie': matched_category
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
        'CNN_world': {
            'url': 'http://rss.cnn.com/rss/edition_world.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_africa': {
            'url': 'http://rss.cnn.com/rss/edition_africa.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_americas': {
            'url': 'http://rss.cnn.com/rss/edition_americas.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_asia': {
            'url': 'http://rss.cnn.com/rss/edition_asia.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_europe': {
            'url': 'http://rss.cnn.com/rss/edition_europe.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_middleeast': {
            'url': 'http://rss.cnn.com/rss/edition_meast.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_us': {
            'url': 'http://rss.cnn.com/rss/edition_us.rss',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'CNN_money': {
            'url': 'http://rss.cnn.com/rss/money_news_international.rss',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'CNN_technology': {
            'url': 'http://rss.cnn.com/rss/edition_technology.rss',
            'categorie': 'SCIENCE/SCIENCE'
        },'CNN_science': {
            'url': 'http://rss.cnn.com/rss/edition_space.rss',
            'categorie': 'SCIENCE/SCIENCE'
        },'CNN_entertainment': {
            'url': 'http://rss.cnn.com/rss/edition_entertainment.rss',
            'categorie': 'ART & CULTURE/ART'
        },'CNN_sport': {
            'url': 'http://rss.cnn.com/rss/edition_sport.rss',
            'categorie': 'SPORT/SPORT'
        },'CNN_football': {
            'url': 'http://rss.cnn.com/rss/edition_football.rss',
            'categorie': 'SPORT/SPORT'
        },'CNN_golf': {
            'url': 'http://rss.cnn.com/rss/edition_golf.rss',
            'categorie': 'SPORT/SPORT'
        },'CNN_motorsport': {
            'url': 'http://rss.cnn.com/rss/edition_motorsport.rss',
            'categorie': 'SPORT/SPORT'
        },'CNN_tennis': {
            'url': 'http://rss.cnn.com/rss/edition_tennis.rss',
            'categorie': 'SPORT/SPORT'
        },'NYTimes_science': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Science.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'NYTimes_environment': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'NYTimes_space': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Space.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'NYTimes_health': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Health.xml',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'NYTimes_wellblog': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Well.xml',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'NYTimes_business': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'NYTimes_economy': {
            'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_unesport': {
            'url': 'https://www.lemonde.fr/sport/rss_full.xml',
            'categorie': 'SPORT/SPORT'
        },'LeMonde_football': {
            'url': 'https://www.lemonde.fr/football/rss_full.xml',
            'categorie': 'SPORT/SPORT'
        },'LeMonde_rugby': {
            'url': 'https://www.lemonde.fr/rugby/rss_full.xml',
            'categorie': 'SPORT/SPORT'
        },'LeMonde_basket': {
            'url': 'https://www.lemonde.fr/basket/rss_full.xml',
            'categorie': 'SPORT/SPORT'
        },'LeMonde_cyclisme': {
            'url': 'https://www.lemonde.fr/cyclisme/rss_full.xml',
            'categorie': 'SPORT/SPORT'
        },'LeMonde_tennis': {
            'url': 'https://www.lemonde.fr/tennis/rss_full.xml',
            'categorie': 'SPORT/SPORT'
        },'LeMonde_uneculture': {
            'url': 'https://www.lemonde.fr/culture/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_cinema': {
            'url': 'https://www.lemonde.fr/cinema/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_musique': {
            'url': 'https://www.lemonde.fr/musiques/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_teleradio': {
            'url': 'https://www.lemonde.fr/televisions-radio/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_livres': {
            'url': 'https://www.lemonde.fr/livres/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_arts': {
            'url': 'https://www.lemonde.fr/arts/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_scene': {
            'url': 'https://www.lemonde.fr/scenes/rss_full.xml',
            'categorie': 'ART & CULTURE/ART'
        },'LeMonde_scene': {
            'url': 'https://www.lemonde.fr/scenes/rss_full.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LeMonde_sciences': {
            'url': 'https://www.lemonde.fr/sciences/rss_full.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LeMonde_espace': {
            'url': 'https://www.lemonde.fr/espace/rss_full.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LeMonde_biologie': {
            'url': 'https://www.lemonde.fr/biologie/rss_full.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LeMonde_physique': {
            'url': 'https://www.lemonde.fr/physique/rss_full.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LeMonde_sante': {
            'url': 'https://www.lemonde.fr/sante/rss_full.xml',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'LeMonde_medecine': {
            'url': 'https://www.lemonde.fr/medecine/rss_full.xml',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'LeMonde_economie': {
            'url': 'https://www.lemonde.fr/economie/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_entreprise': {
            'url': 'https://www.lemonde.fr/entreprises/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_argent': {
            'url': 'https://www.lemonde.fr/argent/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_economiefrancaise': {
            'url': 'https://www.lemonde.fr/economie-francaise/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_industrie': {
            'url': 'https://www.lemonde.fr/industrie/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_emploi': {
            'url': 'https://www.lemonde.fr/emploi/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_immobilier': {
            'url': 'https://www.lemonde.fr/immobilier/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_medias': {
            'url': 'https://www.lemonde.fr/actualite-medias/rss_full.xml',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LeMonde_international': {
            'url': 'https://www.lemonde.fr/international/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_europe': {
            'url': 'https://www.lemonde.fr/europe/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_ameriques': {
            'url': 'https://www.lemonde.fr/ameriques/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_afrique': {
            'url': 'https://www.lemonde.fr/afrique/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_asiepacifique': {
            'url': 'https://www.lemonde.fr/asie-pacifique/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_procheorient': {
            'url': 'https://www.lemonde.fr/proche-orient/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_royaumeuni': {
            'url': 'https://www.lemonde.fr/royaume-uni/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_etatsunis': {
            'url': 'https://www.lemonde.fr/etats-unis/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeMonde_politique': {
            'url': 'https://www.lemonde.fr/politique/rss_full.xml',
            'categorie': 'POLITIQUE-GEOPOLITIQUE/POLITICS-GEOPOLITICS'
        },'LeFigaro_sante': {
            'url': 'https://www.lefigaro.fr/rss/figaro_sante.xml',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'LeFigaro_science': {
            'url': 'https://www.lefigaro.fr/rss/figaro_sciences.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LeDevoir_sante': {
            'url': 'https://www.ledevoir.com/rss/section/societe/sante.xml',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'LeDevoir_science': {
            'url': 'https://www.ledevoir.com/rss/section/societe/science.xml',
            'categorie': 'SCIENCE/SCIENCE'
        },'LaPresse_sante': {
            'url': 'https://www.lapresse.ca/actualites/sante/rss',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'LaPresse_science': {
            'url': 'https://www.lapresse.ca/actualites/sciences/rss',
            'categorie': 'SCIENCE/SCIENCE'
        },'Santepubliquefrance_sante': {
            'url': 'https://www.santepubliquefrance.fr/rss/actualites.xml?1700217194',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'Washingtonpost_business': {
            'url': 'https://feeds.washingtonpost.com/rss/business?itid=lk_inline_manual_37',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        },'LATimes_entertainment': {
            'url': 'https://www.latimes.com/entertainment-arts/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'ART & CULTURE/ART'
        },'LATimes_movies': {
            'url': 'https://www.latimes.com/entertainment-arts/movies/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'ART & CULTURE/ART'
        },'LATimes_music': {
            'url': 'https://www.latimes.com/entertainment-arts/music/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'ART & CULTURE/ART'
        },'LATimes_books': {
            'url': 'https://www.latimes.com/entertainment-arts/books/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'ART & CULTURE/ART'
        },'LATimes_awards': {
            'url': 'https://www.latimes.com/entertainment-arts/awards/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'ART & CULTURE/ART'
        },'LATimes_tv': {
            'url': 'https://www.latimes.com/entertainment-arts/tv/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'ART & CULTURE/ART'
        },'LATimes_lifestyle': {
            'url': 'https://www.latimes.com/lifestyle/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'SANTE-MEDECINE/HEALTH'
        },'LATimes_business': {
            'url': 'https://www.latimes.com/business/rss2.0.xml#nt=0000016c-0bf3-d57d-afed-2fff84fd0000-1col-7030col1',
            'categorie': 'FINANCE-ECONOMIE/FINANCE-ECONOMY'
        }
    }
    '''
        Liste de flux employés (ou non) : 
        'France 24': 'http://www.france24.com/en/timeline/rss',
        'ABC News': 'https://www.abc.net.au/news/feed/2942460/rss.xml',
        'Washington Post': 'http://feeds.washingtonpost.com/rss/world',
        'LA Times': 'http://feeds.latimes.com/latimes/news/nationworld/world',
        'Al Jazeera': 'http://www.aljazeera.com/category/organisation/rss', 
        'Shanghai Daily': 'http://rss.shanghaidaily.com/Portal/mainSite/Handler.ashx?i=7',
        'NY Times': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        'Le Monde': 'https://www.lemonde.fr/rss/une.xml',
        'L\'Essentiel': 'https://partner-feeds.lessentiel.lu/rss/lessentiel-fr',
        'Courrier International': 'http://www.courrierinternational.com/rss/all/rss.xml',
        'La Presse': 'https://www.lapresse.ca/actualites/rss',
        'Libération': 'https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml',
        'L\'Avenir': 'https://www.lavenir.net/arc/outboundfeeds/rss/section/actu/?outputType=xml',
        'Le Devoir': 'https://www.ledevoir.com/rss/manchettes.xml',
        'Le Figaro': 'https://www.lefigaro.fr/rss/figaro_actualites.xml'
    '''
    
    scraper = ArticleScraper(rss_feeds)
    scraper.scrape_articles()    
    scraper.close_database()
