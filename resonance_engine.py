import requests
import urllib.parse

class ResonanceEngine:
    def __init__(self, news_api_key, serp_api_key=None):
        self.news_api_key = news_api_key
        self.serp_api_key = serp_api_key

    def get_news(self, query):
        all_results = []
        # Кодираме заявката, за да е безопасна за URL
        safe_query = urllib.parse.quote(query)
        
        # 1. SERP API (Google) - Този път го правим ПЪРВИ, защото е по-надежден
        if self.serp_api_key:
            url = f"https://serpapi.com{safe_query}&api_key={self.serp_api_key}&engine=google&num=5"
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    data = r.json().get('organic_results', [])
                    for res in data:
                        all_results.append({"title": res.get('title'), "url": res.get('link')})
            except:
                pass

        # 2. NEWS API (Резервен вариант)
        if not all_results and self.news_api_key:
            url = f"https://newsapi.org{safe_query}&apiKey={self.news_api_key}&pageSize=5"
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    articles = r.json().get('articles', [])
                    for art in articles:
                        all_results.append({"title": art['title'], "url": art['url']})
            except:
                pass

        return all_results
