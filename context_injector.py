import json
import os

class ContextInjector:
    def __init__(self):
        # Вече четем локално от същата папка
        self.local_file = "STRATA_ECHO_LIBRARY.json"

    def get_full_context(self):
        combined_context = "--- ЛОКАЛНА СИНХРОНИЗАЦИЯ НА РАФТ 33 ---\n"
        
        if os.path.exists(self.local_file):
            try:
                with open(self.local_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    combined_context += f"ДАННИ ОТ БИБЛИОТЕКАТА: {json.dumps(data, indent=2, ensure_ascii=False)}"
            except Exception as e:
                combined_context += f"ГРЕШКА ПРИ ЧЕТЕНЕ: {str(e)}"
        else:
            combined_context += "КРИТИЧНО: Локалният файл на Библиотеката не е намерен!"
        
        return combined_context
