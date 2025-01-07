class InMemoryWaterTracker:
    def __init__(self):
        self.total_water = 0

    def log_water(self, amount: float):
        """Добавляет количество выпитой воды."""
        self.total_water += amount

    def get_total_water(self) -> float:
        """Возвращает общее количество выпитой воды."""
        return self.total_water

    def reset_water(self):
        """Сбрасывает общее количество выпитой воды."""
        self.total_water = 0