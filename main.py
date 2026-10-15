from db.db import get_connection
from repository.users_repository import get_all_users

with get_connection() as conn:
    users = get_all_users(conn)
    print(users)

