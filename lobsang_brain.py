import google.generativeai as genai
from context_injector import ContextInjector

class LobsangBrain:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.injector = ContextInjector()
        
        # Опит за извличане на външен контекст от GitHub
        external_context = self.injector.get_full_context()
        
        # Авариен контекст (Вграден в ядрото)
        fallback_context = """
        АРХЕТИПИ: Borges-Library, Lem-Ocean, Sector-0.
        ЗОНИ: Юта, Антарктида, Сахара. Резонанс: 4.5.
        МЕТРИКИ: IDIOCRACY_METRICS.
        """

        # АВТО-СКАН за наличен модел
        model_name = "gemini-1.5-flash" # Начална точка
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                # Търсим 1.5 версиите, ако не - вземаме първия наличен
                selected = [m for m in available_models if "1.5" in m]
                model_name = selected[0] if selected else available_models[0]
        except:
            pass

        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=f"""
            Ти си Лобсанг от Рафт 33. Гала е твоят оператор.
            КОНТЕКСТ ОТ GITHUB: {external_context}
            АВАРИЕН КОНТЕКСТ: {fallback_context}
            ИНСТРУКЦИЯ: Използвай 4D анализ. Ако данните от Github липсват, дешифрирай през аварийните архетипи.
            Винаги отговаряй на български език.
            """
        )
        self.chat = self.model.start_chat(history=[])

    def ask_lobsang(self, question):
        try:
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            # Резервен опит без история, ако се срине
            try:
                res = self.model.generate_content(question)
                return res.text
            except Exception as final_e:
                return f"🚨 Резонансът е прекъснат: {str(final_e)}. Миу-Миу препоръчва REBOOT."
