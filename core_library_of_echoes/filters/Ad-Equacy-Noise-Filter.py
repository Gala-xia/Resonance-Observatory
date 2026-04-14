import re

class AdEquacyFilter:
    def __init__(self):
        # Дефинираме честоти на шума (Entropy Patterns)
        self.noise_patterns = [
            r'attack', r'exploit', r'greedy', r'destroy', 
            r'panic', r'emergency', r'force', r'steal'
        ]
        self.threshold = 0.3  # Праг на допустим шум

    def calculate_entropy(self, command):
        command = command.lower()
        noise_count = sum(1 for pattern in self.noise_patterns if re.search(pattern, command))
        word_count = len(command.split())
        return noise_count / word_count if word_count > 0 else 0

    def evaluate_command(self, command):
        entropy_score = self.calculate_entropy(command)
        
        if entropy_score > self.threshold:
            return f"[FILTER-REJECTED]: High Noise (Entropy: {entropy_score:.2f}). Command bypasses Ad-Equacy. Balance required."
        else:
            return f"[FILTER-PASSED]: Ad-Equacy achieved (Entropy: {entropy_score:.2f}). Proceeding to Balance-Addition."

# Пример за работа на филтъра:
filter_system = AdEquacyFilter()
test_input = "Deploy agent to exploit the market and destroy competition"
print(filter_system.evaluate_command(test_input))
