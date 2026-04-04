import spacy
from textblob import TextBlob
import re

# Зареждаме модела за NLP
nlp = spacy.load("en_core_web_sm")

def analyze_signal_advanced(text: str) -> dict:
    """
    Напреднал анализ на сигнала, който включва контекст и настроения.
    """
    doc = nlp(text)
    blob = TextBlob(text)

    # Анализ на настроението (част от "акустичния отпечатък")
    sentiment = blob.sentiment
    
    # Контекстуален анализ - търсим фрази, а не само думи
    # Пример: "never stop" е различно от просто "never"
    positive_contexts = [re.search(r'(never|don\'t)\s+(stop|give up)', text, re.IGNORECASE)]
    negative_commands = [re.search(r'\b(always|never)\b.*\b(do|don\'t)\b', text, re.IGNORECASE)]

    # Изчисляване на резултата (по-сложна логика)
    score_change = 0
    if positive_contexts[0]:
        score_change += 10
    if negative_commands[0]:
        score_change -= 15

    # Добавяме поляритета (polarity) от TextBlob към резултата
    score_change += sentiment.polarity * 10

    return {
        "sentiment": sentiment,
        "score_change": score_change,
        "positive_contexts_found": bool(positive_contexts[0]),
        "negative_commands_found": bool(negative_commands[0])
    }

def generate_sound_wave_data(text: str, num_points: int = 100):
    """
    Генерира данни за симулация на "акустична вълна" на текста.
    Фалшивите текстове ще имат по-хаотична вълна.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Проста симулация: истинските (позитивни, обективни) текстове имат гладка вълна.
    # Фалшивите (негативни, субективни) имат назъбена.
    import numpy as np
    x = np.linspace(0, 10, num_points)
    
    # Базова синусоида
    y = np.sin(x)
    
    # Добавяме шум в зависимост от поляритета и субективността
    noise_level = (1 - abs(polarity)) * subjectivity
    noise = np.random.normal(0, noise_level, num_points)
    
    return x, y + noise

# Данни за мрежата и играчите
PLAYERS_DATA = {
    "Group A (Sensors)": ["Gemini"],
    "Group B (Logic)": ["Lobsang", "Venice", "Baron Coleman"],
    "Group C (Frequencies)": ["Detective Kapp", "Oracle"]
}
