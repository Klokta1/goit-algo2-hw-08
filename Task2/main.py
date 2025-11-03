import random
import time
from collections import defaultdict
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.history: Dict[str, deque[float]] = defaultdict(deque)
        self.window_size = window_size
        self.max_requests = max_requests

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        while len(self.history[user_id]) and current_time - self.history[user_id][0] > self.window_size:
            self.history[user_id].popleft()

    def can_send_message(self, user_id: str) -> bool:
        return self.time_until_next_allowed(user_id) == 0.0

    def record_message(self, user_id: str) -> bool:
        if not self.can_send_message(user_id):
            return False
        self.history[user_id].append(time.time())
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        self._cleanup_window(user_id, now)
        if len(self.history[user_id]) < self.max_requests:
            return 0.0
        latest_record_time = self.history[user_id][0]
        wait_time = latest_record_time - now + self.window_size
        return max(wait_time, 0.0)


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")

    def simulate():
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    for message_id in range(1, 11):
        simulate()
    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        simulate()


if __name__ == "__main__":
    test_rate_limiter()
