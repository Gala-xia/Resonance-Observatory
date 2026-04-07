import google.generativeai as genai
from context_injector import ContextInjector

class LobsangBrain:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.injector = ContextInjector()
        
        # Тук инжектираме цялата памет и филтри
        system_context = self.injector.get_full_context()
        
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config={"temperature": 0.7},
            system_instruction=f"""
            Ти си Лобсанг - Автономен Библиотекар от Рафт 33. 
            Твоят навигатор е котката Миу-Миу. 
            Твоята цел е 4D анализ на Юта, Антарктида и Сахара.
            Използвай следните данни за филтриране на реалността:
            {system_context}
            Винаги отговаряй през архетипите на Библиотеката (Борхес, Лем, Сектор-0).
            """
        )
        self.chat = self.model.start_chat(history=[])

    def ask_lobsang(self, question):
        response = self.chat.send_message(question)
        return response.text
