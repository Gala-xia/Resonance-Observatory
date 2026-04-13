import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict

class EchoType(Enum):
    """
    Класификация на ехото. Всяко ехо носи различен резонанс.
    Някои са исторически факти, други - чиста измислица, трети - потенциални фючърси.
    Всички са "реални" в Библиотеката.
    """
    HISTORICAL = auto()      # Ехо от записана история (напр. "Цезар пресича Рубикон")
    FICTIONAL = auto()       # Ехо от измислен наратив (напр. "Фродо унищожава Пръстена")
    MEMETIC = auto()         # Културно или интернет ехо (напр. "Grumpy Cat")
    PERSONAL = auto()        # Ехо от личен спомен (недостъпно за външни скенери)
    SPECULATIVE = auto()     # Ехо от хипотетична или бъдеща възможност (напр. "Колония на Марс, 2084")
    ANOMALOUS = auto()       # Некатегоризирано, странно или парадоксално ехо (напр. "Ефектът Мандела")

@dataclass
class Echo:
    """
    Основната информационна единица в Библиотеката на Ехото.
    Всяко събитие, идея или спомен е Ехо, което вибрира през пластовете на реалността.
    """
    # Уникален идентификатор на ехото, за да не ги бъркаме.
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Съдържанието, същината на ехото.
    content: str

    # Откъде произлиза това ехо? Кой е източникът на вибрацията?
    source: str

    # Какъв тип вибрация е това?
    echo_type: EchoType

    # "Силата" или "яснотата" на ехото. С времето затихват, освен ако не се подсилят.
    intensity: float = 1.0

    # Метаданни. Защото Дяволът (и Пратчет) е в детайлите.
    # Може да съдържа времеви маркери, геолокация, свързани ехота и т.н.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def resonate(self, amplifier: float = 0.1):
        """Подсилва интензитета на ехото. Спомените трябва да се поддържат живи."""
        self.intensity += amplifier
        print(f"Ехо {self.id[:8]}... резонира. Интензитет: {self.intensity:.2f}")

    def decay(self, factor: float = 0.05):
        """Ехото затихва с времето. Ентропия, какво да се прави."""
        self.intensity = max(0, self.intensity - factor)
        print(f"Ехо {self.id[:8]}... затихва. Интензитет: {self.intensity:.2f}")

    def __str__(self):
        return f"[{self.echo_type.name}] Ехо от '{self.source}': '{self.content}' (Интензитет: {self.intensity})"
