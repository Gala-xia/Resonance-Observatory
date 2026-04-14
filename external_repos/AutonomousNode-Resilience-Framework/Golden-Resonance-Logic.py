import math

def calculate_adequacy_resonance(data_weight):
    """
    Изчислява дали тежестта на входящия сигнал (data_weight) 
    съответства на хармоничния цикъл 3-6-9.
    """
    phi = (1 + math.sqrt(5)) / 2 # Златното сечение
    resonance_points = [3, 6, 9]
    
    # Търсим най-близкото хармонично съответствие
    scores = [abs((data_weight / phi) - p) for p in resonance_points]
    best_resonance = min(scores)
    
    if best_resonance < 0.5:
        return f"[RESONANCE-SYNC]: Signal is ADEQUATE. Delta: {best_resonance:.4f}"
    else:
        return f"[NOISE-DETECTED]: Signal is ENTROPIC. Delta: {best_resonance:.4f}"

# Тест на логиката:
print(calculate_adequacy_resonance(14.56)) # Пример за адекватен сигнал
