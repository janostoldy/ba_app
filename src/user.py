import pandas as pd

class User:
    def __init__(self, name: str, role: str, user_id: int, password: str = None):
        self.id = user_id
        self.name = name
        self.password = password
        self.role = role

def get_known_user():
    user1 = User(name="Tester", password="test", user_id=1, role="user")
    user2 = User(name="Admin", password="admin", user_id=1, role="admin")
    users = pd.DataFrame(
            {
                "name": [user1.name, user2.name],
                "password": [user1.password, user2.password],
                "role": [user1.role, user2.role],
                "object": [user1, user2],
            }
        )
    return users
    