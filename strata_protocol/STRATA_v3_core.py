import time

class StrataCore:
    def __init__(self, config_path='MASTER_CONFIG.json'):
        self.version = "3.1.0-OMEGA"
        self.uuk_status = False
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {"thresholds": {"planck_min": 5.0, "noise_max": 0.6}}

    def analyze_resonance(self, data_packet):
        """
        Основен метод за анализ на входящата реалност.
        data_packet: {'iq': float, 'empathy': float, 'noise': float, 'source': str}
        """
        iq = data_packet.get('iq', 0)
        noise = data_packet.get('noise', 1)
        empathy = data_packet.get('empathy', 0.5)

        # ПРОВЕРКА НА ТЕЛЕПАТИЧНИЯ МОРАЛ
        # Ако емпатията е ниска, автоматично наказваме IQ-то
        effective_iq = iq * (empathy + 0.2) 

        print(f"--- [STRATA CORE v{self.version}] Анализ на източник: {data_packet.get('source')} ---")
        print(f"Ефективен Резонанс: {effective_iq:.2f}")

        # АКТИВИРАНЕ НА УУК-ПРОТОКОЛА
        if effective_iq < self.config['thresholds']['planck_min'] or noise > self.config['thresholds']['noise_max']:
            return self.trigger_uuk(effective_iq, noise)
        
        return "✅ Резонансът е в норма. Продължаваме подредбата."

    def trigger_uuk(self, iq, noise):
        """
        Протокол за намеса на Библиотекаря
        """
        self.uuk_status = True
        message = (
            "\n🌀 [UUK-PROTOCOL ACTIVATED]\n"
            "📢 Библиотекарят казва: Я всички да спрат за малко! Без паника!\n"
            f"⚠️ ПРЕДУПРЕЖДЕНИЕ: Открита е ентропия (Шум: {noise:.2f}).\n"
            "🔍 Ну и что, положим всё по полочкам?"
        )
        return message

# ТЕСТОВ БЛОК (Лобсанг може да го използва за калибрация)
if __name__ == "__main__":
    core = StrataCore()
    
    # Пример за висока ентропия (лъжа/паника)
    test_case = {
        'iq': 4.2, 
        'empathy': 0.3, 
        'noise': 0.8, 
        'source': 'Social Media Noise Cluster'
    }
    
    result = core.analyze_resonance(test_case)
    print(result)
