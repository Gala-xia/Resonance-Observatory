import requests
import json

class ContextInjector:
    def __init__(self):
        # RAW линкове към твоите ключови файлове
        self.sources = {
            "echo_library": "https://githubusercontent.com",
            "shield_config": "https://githubusercontent.com",
            "pattern_mapping": "https://githubusercontent.com"
        }

    def get_full_context(self):
        combined_context = "--- СИСТЕМЕН КОНТЕКСТ (L-SPACE) ---\n"
        for key, url in self.sources.items():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    combined_context += f"\n[{key.upper()}]:\n{response.text}\n"
            except:
                combined_context += f"\n[ГРЕШКА]: Неуспешно извличане на {key}\n"
        return combined_context
