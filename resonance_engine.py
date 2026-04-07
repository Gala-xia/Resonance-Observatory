import streamlit as st
import requests
import spacy
import os

# СИГУРНО ЗАРЕЖДАНЕ НА ЕЗИКОВИЯ МОДЕЛ
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Автоматично изтегляне, ако липсва в средата на Streamlit
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class ResonanceEngine:
    def __init__(self, news_api_key, serp_api_key=None):
        self.news_api_key = news_api_key
        self.serp_api_key = serp_api_key
        self.nlp = nlp

    def get_news(self, query):
        """Сканира News API и Serp API за 4D съответствия."""
        all_results = []
        
        # 1. СКАНИРАНЕ ЧРЕЗ NEWS API (Официален поток)
        news_url = f"https://newsapi.org{query}&apiKey={self.news_api_key}&pageSize=5"
        try:
            r = requests.get(news_url)
            if r.status_code == 200:
                articles = r.json().get('articles', [])
                for art in articles:
                    all_results.append({
                        "title": art['title'],
                        "url": art['url'],
                        "source": "NewsAPI"
                    })
        except Exception as e:
            print(f"Грешка в NewsAPI: {e}")

        # 2. СКАНИРАНЕ ЧРЕЗ SERP API (Дълбоко търсене / Dorking)
        if self.serp_api_key:
            serp_url = "https://serpapi.com"
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "num": 5
            }
            try:
                r = requests.get(serp_url, params=params)
                if r.status_code == 200:
                    search_results = r.json().get('organic_results', [])
                    for res in search_results:
                        all_results.append({
                            "title": res.get('title'),
                            "url": res.get('link'),
                            "source": "SerpAPI"
                        })
            except Exception as e:
                print(f"Грешка в SerpAPI: {e}")

        return all_results

    def analyze_resonance(self, text):
        """Анализира текста за ключови архетипи (4D филтър)."""
        doc = self.nlp(text)
        # Тук можем да добавим специфично извличане на обекти в бъдеще
        entities = [ent.text for ent in doc.ents]
        return entities
