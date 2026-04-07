import streamlit as st
import requests

class ResonanceEngine:
    def __init__(self, news_api_key, serp_api_key=None):
        self.news_api_key = news_api_key
        self.serp_api_key = serp_api_key

    def get_news(self, query):
        """Сканира мрежата и връща данни или съобщение за грешка."""
        all_results = []
        
        # 1. NEWS API SCAN
        if self.news_api_key:
            # Търсим само заглавия за по-голяма скорост и чистота
            news_url = f"https://newsapi.org{query}&apiKey={self.news_api_key}&pageSize=5&language=en"
            try:
                r = requests.get(news_url, timeout=10)
                if r.status_code == 200:
                    articles = r.json().get('articles', [])
                    for art in articles:
                        all_results.append({
                            "title": art['title'],
                            "url": art['url'],
                            "source": "NewsAPI"
                        })
                else:
                    print(f"NewsAPI Error: {r.status_code}")
            except Exception as e:
                print(f"NewsAPI Exception: {e}")

        # 2. SERP API SCAN (Ако е наличен)
        if self.serp_api_key:
            serp_url = "https://serpapi.com"
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "num": 5
            }
            try:
                r = requests.get(serp_url, params=params, timeout=10)
                if r.status_code == 200:
                    search_results = r.json().get('organic_results', [])
                    for res in search_results:
                        all_results.append({
                            "title": res.get('title'),
                            "url": res.get('link'),
                            "source": "SerpAPI"
                        })
            except Exception as e:
                print(f"SerpAPI Exception: {e}")

        return all_results
