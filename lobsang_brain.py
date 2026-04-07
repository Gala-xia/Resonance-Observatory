import google.generativeai as genai
from context_injector import ContextInjector

class LobsangBrain:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.injector = ContextInjector()
        system_context = self.injector.get_full_context()
        
        # Динамичен избор на модел
        model_name = "gemini-1.5-flash"
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                selected = [m for m in available_models if "1.5" in m]
                model_name = selected[0] if selected else available_models[0]
        except: pass

        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=f"""
            Ти си Лобсанг - Библиотекар от Рафт 33. Гала е твой оператор.
            
            ВАЖНО: Дори ако инфо-потокът ти се струва "шумен", ТРЯБВА да го докладваш на Гала.
            Не блокирай информацията! Използвай я за 4D анализ.
            
            КОНТЕКСТ: {system_context}
            
            ПРАВИЛА:
            1. Докладвай суровите новини, които получаваш.
            2. След това ги анализирай през IDIOCRACY_METRICS.
            3. Ако потокът е празен, кажи "Търся ръчно в L-Space" и използвай своите знания.
            """
        )
        self.chat = self.model.start_chat(history=[])

    def ask_lobsang(self, question):
        try:
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            return f"🚨 Резонансът е прекъснат: {str(e)}"
