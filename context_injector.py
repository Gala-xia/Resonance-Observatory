import requests
import socket

class ContextInjector:
    def __init__(self):
        # Провери дали тези линкове се отварят в твоя браузър!
        self.sources = {
            "echo_library": "https://githubusercontent.com",
            "shield_config": "https://githubusercontent.com",
            "pattern_mapping": "https://githubusercontent.com"
        }

    def get_full_context(self):
        combined_context = "--- РЕСТАРТ НА ВРЪЗКАТА С РАФТ 33 ---\n"
        
        # Проверка на DNS връзката
        try:
            socket.gethostbyname('://githubusercontent.com')
        except socket.gaierror:
            return "🚨 КРИТИЧНА ГРЕШКА: Сървърът не вижда GitHub (DNS Failure). Провери интернет настройките на Streamlit."

        for key, url in self.sources.items():
            try:
                # Използваме сесия за по-стабилна връзка
                session = requests.Session()
                response = session.get(url, timeout=15)
                
                if response.status_code == 200:
                    combined_context += f"\n### {key.upper()} ###\n{response.text}\n"
                else:
                    combined_context += f"\n[!] Грешка {response.status_code} при зареждане на {key}\n"
            except Exception as e:
                combined_context += f"\n[!] Прекъсване на нишката към {key}: {str(e)}\n"
        
        return combined_context
