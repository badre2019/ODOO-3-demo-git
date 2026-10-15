from db.db import get_connection

with get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * from users")
        users = cursor.fetchall()

print(users)
print(users[0])