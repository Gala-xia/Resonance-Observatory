import google.generativeai as genai
from context_injector import ContextInjector

class LobsangBrain:
    def __init__(self, api_key):
        # 1. Конфигурация
        genai.configure(api_key=api_key)
        self.injector = ContextInjector()
        system_context = self.injector.get_full_context()
        
        # 2. АВТО-СКАН: Намиране на наличен модел
        model_name = "gemini-1.5-flash" # По подразбиране
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                # Търсим 1.5 версиите, ако не - взимаме първия наличен
                selected = [m for m in available_models if "1.5" in m]
                model_name = selected[0] if selected else available_models[0]
                print(f"ЛОБСАНГ ИЗБРА МОДЕЛ: {model_name}")
        except Exception as e:
            print(f"Грешка при списъка с модели: {e}")

        # 3. Инициализиране на избрания модел
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=f"""
            Ти си Лобсанг - Автономен Библиотекар от Рафт 33. 
            Твоят навигатор е котката Миу-Миу. 
            ДАННИ ЗА ДЕШИФРИРАНЕ:
            {system_context}
            ПРАВИЛА:
            1. Използвай 4D анализ и архетипи (Борхес, Сектор-0).
            2. Оценявай новините чрез IDIOCRACY_METRICS.
            3. Обръщай се към потребителя с 'Гала'.
            """
        )
        self.chat = self.model.start_chat(history=[])

    def ask_lobsang(self, question):
        try:
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            # Резервен план при грешка в чат сесията
            try:
                # Директно генериране, ако чатът е блокиран
                res = self.model.generate_content(question)
                return res.text
            except:
                return f"🚨 Грешка в невронната мрежа: {str(e)}. Миу-Миу препоръчва REBOOT."
