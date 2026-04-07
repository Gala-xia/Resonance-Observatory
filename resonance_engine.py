import requests

class ResonanceEngine:
    def __init__(self, news_api_key, serp_api_key=None):
        self.news_api_key = news_api_key
        self.serp_api_key = serp_api_key
        # Добавяме хедър, за да не ни блокират
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def get_news(self, query):
        all_results = []
        
        # 1. NEWS API (С добавени хедъри)
        if self.news_api_key:
            news_url = f"https://newsapi.org{query}&apiKey={self.news_api_key}&pageSize=5"
            try:
                r = requests.get(news_url, headers=self.headers, timeout=10)
                if r.status_code == 200:
                    articles = r.json().get('articles', [])
                    for art in articles:
                        all_results.append({"title": art['title'], "url": art['url']})
            except:
                pass

        # 2. SERP API (Ако NewsAPI е празно, това трябва да ни спаси)
        if not all_results and self.serp_api_key:
            serp_url = "https://serpapi.com"
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "num": 5
            }
            try:
                r = requests.get(serp_url, params=params, timeout=10)
                if r.status_code == 200:
                    results = r.json().get('organic_results', [])
                    for res in results:
                        all_results.append({"title": res.get('title'), "url": res.get('link')})
            except:
                pass

        return all_results
