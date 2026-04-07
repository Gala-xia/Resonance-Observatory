import requests

class ContextInjector:
    def __init__(self):
        self.sources = {
            "echo_library": "https://githubusercontent.com",
            "shield_config": "https://githubusercontent.com",
            "pattern_mapping": "https://githubusercontent.com"
        }

    def get_full_context(self):
        combined_context = "--- СИНХРОНИЗАЦИЯ НА РАФТ 33 ---\n"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for key, url in self.sources.items():
            try:
                # Опит за четене с увеличен тайм-аут
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    combined_context += f"\n[{key.upper()}]: {response.text[:1000]}...\n"
                else:
                    combined_context += f"\n[{key}]: ГРЕШКА {response.status_code}\n"
            except:
                combined_context += f"\n[{key}]: ВРЪЗКАТА Е БЛОКИРАНА ОТ ШУМ.\n"
        
        return combined_context
