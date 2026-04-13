import math
import os
from collections import Counter

class CordeliaCuppScanner:
    """
    Аналитичен модул, вдъхновен от детектив Корделия Къп (The Residence).
    Специализиран в откриването на фини несъответствия и манипулирани ехота.
    Философия: Реалността е хаотична. Прекомерният ред е лъжа.
    """

    def __init__(self, suspicion_threshold=4.5):
        """
        Инициализира скенера.
        :param suspicion_threshold: Праг на ентропията, над който нещата стават "интересни".
        """
        self.suspicion_threshold = suspicion_threshold
        # Ехо-сигнатура на Корделия
        self.status = "Active: Looking for things hidden in plain sight."

    def calculate_shannon_entropy(self, data):
        """
        Изчислява ентропията на Шанън. 
        Ниската ентропия означава прекалена подреденост (инсценировка).
        Високата ентропия означава автентичен хаос или скрита информация.
        """
        if not data:
            return 0
        
        # Превръщаме в стрингова репрезентация за анализ на честотата
        str_data = str(data)
        byte_counts = Counter(str_data)
        total_len = len(str_data)
        
        entropy = 0
        for count in byte_counts.values():
            p_x = count / total_len
            entropy -= p_x * math.log2(p_x)
            
        return entropy

    def cordelia_scan(self, echo_payload):
        """
        Основната функция за разпит на ехото.
        """
        content = echo_payload.get('content', '')
        metadata = echo_payload.get('metadata', {})
        
        entropy = self.calculate_shannon_entropy(content)
        
        # Методът на Къп: Търсим аномалии
        is_suspicious = False
        findings = []

        if entropy < 2.0 and len(content) > 20:
            is_suspicious = True
            findings.append("Прекалено подредена структура. Възможна инсценировка.")
        
        if entropy > self.suspicion_threshold:
            is_suspicious = True
            findings.append("Необичайно висока информационна плътност. Скрит подтекст?")

        if not metadata:
            findings.append("Липса на метаданни. Субектът се опитва да прикрие произхода си.")

        return {
            "verdict": "ПОДОЗРИТЕЛНО" if is_suspicious else "АВТЕНТИЧНО",
            "entropy_score": round(entropy, 4),
            "findings": findings,
            "agent_note": "Корделия Къп приключи огледа. Не вярвайте на първото впечатление."
        }

# Инициализация за бъдеща употреба в общата система
cupp_scanner = CordeliaCuppScanner()
