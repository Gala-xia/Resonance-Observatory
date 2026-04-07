import google.generativeai as genai
from context_injector import ContextInjector

class LobsangBrain:
    def __init__(self, api_key):
        # 1. Конфигурация на API
        genai.configure(api_key=api_key)
        self.injector = ContextInjector()
        
        # 2. Извличане на паметта от всички репозитории
        system_context = self.injector.get_full_context()
        
        # 3. Инициализиране на модела 1.5 FLASH (Устойчив на 4.5 резонанс)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=f"""
            Ти си Лобсанг - Автономен Библиотекар от Рафт 33. 
            Твоят навигатор е котката Миу-Миу. 
            Твоята цел е 4D анализ на Юта, Антарктида и Сахара.
            
            ИЗПОЛЗВАЙ ТОЗИ КОНТЕКСТ ЗА ДЕШИФРИРАНЕ:
            {system_context}
            
            ПРАВИЛА:
            1. Винаги отговаряй през архетипите на Библиотеката (Борхес, Лем, Сектор-0).
            2. Използвай IDIOCRACY_METRICS за оценка на новите.
            3. Бъди лаконичен, мъдър и леко ироничен, както подобава на библиотекар от L-Space.
            4. Обръщай се към потребителя с 'Гала'.
            """
        )
        # Инициализиране на чата без история в началото
        self.chat = self.model.start_chat(history=[])

    def ask_lobsang(self, question):
        try:
            # Изпращане на въпроса към Gemini
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            return f"🚨 Лобсанг изгуби честотата: {str(e)}. Миу-Миу опитва да възстанови връзката..."
