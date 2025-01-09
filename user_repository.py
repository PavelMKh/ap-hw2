from user import User

class UserRepository:
    def __init__(self):
        self.users = {}
        self.current_user = None

    def create_user(self):
        """Создает нового пользователя и добавляет его в репозиторий."""
        new_user = User()
        self.users[new_user.user_id] = new_user
        self.current_user = new_user.user_id
        return new_user.user_id

    def get_user(self, user_id):
        """Возвращает пользователя по ID."""
        return self.users.get(user_id)

    def set_current_user(self, user_id):
        """Устанавливает текущего пользователя по ID."""
        if user_id in self.users:
            self.current_user = user_id
        else:
            raise ValueError("Пользователь не найден.")

    def get_current_user(self):
        """Возвращает текущего пользователя."""
        return self.get_user(self.current_user) if self.current_user else None

    def reset_user_water(self, user_id):
        """Сбрасывает общее количество выпитой воды для указанного пользователя."""
        user = self.get_user(user_id)
        if user:
            user.reset_water()

