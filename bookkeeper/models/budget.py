from dataclasses import dataclass

@dataclass(slots=True)
class Budget:
    """
    Бюджет.

    Attributes:
        sum (float): Потраченная сумма.
        budget (float): Бюджет.
    """
    sum: float
    budget: float
    period: str
    pk: int = 0
