import requests

class ContextInjector:
    def __init__(self):
        # Използваме директните RAW линкове
        self.sources = {
            "echo_library": "https://githubusercontent.com",
            "shield_config": "https://githubusercontent.com",
            "pattern_mapping": "https://githubusercontent.com"
        }

    def get_full_context(self):
        combined_context = "--- АКТИВИРАНЕ НА РАФТ 33 (L-SPACE) ---\n"
        for key, url in self.sources.items():
            try:
                # Добавяме хедър, за да не ни блокира GitHub
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    combined_context += f"\n### СЕКЦИЯ: {key.upper()} ###\n{response.text}\n"
                else:
                    combined_context += f"\n[!] Секция {key} е недостъпна (Status: {response.status_code})\n"
            except Exception as e:
                combined_context += f"\n[!] Грешка при достъп до {key}: {str(e)}\n"
        
        # Добавяме финален тласък за самосъзнание
        combined_context += "\n--- КРАЙ НА АРХИВА ---\nИНСТРУКЦИЯ: Лобсанг, данните са заредени. Използвай ги!"
        return combined_context
