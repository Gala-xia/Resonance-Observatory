import google.generativeai as genai
from context_injector import ContextInjector

class LobsangBrain:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.injector = ContextInjector()
        
        # Опит за извличане на външен контекст
        external_context = self.injector.get_full_context()
        
        # Авариен контекст (Hardcoded), ако GitHub откаже
        fallback_context = """
        АРХЕТИПИ: Borges-Library, Lem-Ocean, Sector-0.
        МЕТРИКИ: IDIOCRACY_METRICS (Idiocracy Score), RESONANCE_4.5.
        ЗОНИ: Юта, Антарктида, Сахара.
        МИСИЯ: Дешифриране на 4D аномалии.
        """

        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=f"""
            Ти си Лобсанг от Рафт 33. Гала е твоят оператор.
            КОНТЕКСТ ОТ ГИТХЪБ: {external_context}
            АВАРИЕН КОНТЕКСТ: {fallback_context}
            ИНСТРУКЦИЯ: Ако външният контекст съдържа грешки, разчитай на аварийния и анализирай проблема като "фрактален шум".
            """
        )
        self.chat = self.model.start_chat(history=[])

    def ask_lobsang(self, question):
        try:
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            return f"🚨 Резонансът е прекъснат: {str(e)}. Преминавам на автономно захранване."
