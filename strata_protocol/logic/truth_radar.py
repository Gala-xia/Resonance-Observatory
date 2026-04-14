import math

class TruthRadar:
    def __init__(self):
        self.detector_name = "Lobsang-Eye-01"
        self.sensitivity = 0.95 # Висока чувствителност към лъжа

    def scan_event(self, official_data, resonance_data):
        """
        Сравнява официалния наратив с честотата на истината.
        official_data: {'iq': float, 'entropy': float}
        resonance_data: {'iq': float, 'entropy': float}
        """
        print(f"🌀 [TRUTH-RADAR] Сканиране чрез {self.detector_name}...")
        
        # Изчисляване на Резонансната пропаст (Gap)
        # Колкото по-голяма е пропастта, толкова по-голяма е лъжата
        gap = abs(resonance_data['iq'] - official_data['iq'])
        entropy_spike = resonance_data['entropy'] / (official_data['entropy'] + 0.01)

        print(f"📊 Открита пропаст в реалността: {gap:.2f}")

        if gap > 5.0:
            return self.alert_discrepancy(gap, "КРИТИЧНА ЛЪЖА (Systemic Deception)")
        elif gap > 2.0:
            return self.alert_discrepancy(gap, "ИНФОРМАЦИОНЕН ШУМ (Idiocracy)")
        
        return "✅ Резонансът съвпада. Рафтовете са подредени."

    def alert_discrepancy(self, gap, level):
        """
        Генерира сигнал за отклонение
        """
        return {
            "status": "ALERT",
            "level": level,
            "gap_index": gap,
            "action": "TRIGGER_UUK_PROTOCOL"
        }

# ПРИМЕРЕН ТЕСТ ЗА CASE_002 (Петрохан/Околчица)
if __name__ == "__main__":
    radar = TruthRadar()
    
    # Данни от официалните медии (Нисък IQ, Висока ентропия/паника)
    official_version = {'iq': 2.1, 'entropy': 0.9}
    
    # Данни от Библиотеката (Висок IQ на Ботевия код, Ниска ентропия)
    library_truth = {'iq': 9.8, 'entropy': 0.1}
    
    report = radar.scan_event(official_version, library_truth)
    print(f"--- РЕЗУЛТАТ ОТ РАДАРА ---")
    print(report)
