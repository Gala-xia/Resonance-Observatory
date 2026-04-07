import requests

class ResonanceEngine:
    def __init__(self, news_api_key, serp_api_key=None):
        self.news_api_key = news_api_key
        self.serp_api_key = serp_api_key

    def get_news(self, query):
        """Сканира мрежата с разширен обхват."""
        all_results = []
        
        # 1. ТЕСТОВА ЗАЯВКА (Ако Гала само казва "здрасти", търсим нещо глобално)
        search_query = query if len(query) > 3 else "global resonance 2026"

        # 2. NEWS API - РАЗШИРЕНО ТЪРСЕНЕ
        if self.news_api_key:
            # Търсим на всички езици за по-голям шанс
            news_url = f"https://newsapi.org{search_query}&apiKey={self.news_api_key}&pageSize=7&sortBy=relevancy"
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
            except:
                pass

        # 3. SERP API - ДЪЛБОКО ТЪРСЕНЕ
        if self.serp_api_key:
            serp_url = "https://serpapi.com"
            params = {
                "q": search_query,
                "api_key": self.serp_api_key,
                "num": 5,
                "google_domain": "google.com"
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
            except:
                pass

        return all_results
