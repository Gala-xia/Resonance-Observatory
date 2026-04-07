import streamlit as st
import requests

class ResonanceEngine:
    def __init__(self, news_api_key, serp_api_key=None):
        self.news_api_key = news_api_key
        self.serp_api_key = serp_api_key

    def get_news(self, query):
        """Сканира News API и Serp API за 4D съответствия."""
        all_results = []
        
        # 1. СКАНИРАНЕ ЧРЕЗ NEWS API
        if self.news_api_key:
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
            except:
                pass

        # 2. СКАНИРАНЕ ЧРЕЗ SERP API
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
            except:
                pass

        return all_results

    def analyze_resonance(self, text):
        """Опростен анализ на резонанса без Spacy."""
        # Просто разделяне на думи като временна мярка
        return text.split()[:10] 
