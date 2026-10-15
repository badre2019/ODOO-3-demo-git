from psycopg import Connection

def get_all_users(conn: "Connection"):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * from users")
        users = cursor.fetchall()
        return users

# with get_connection() as conn:
#     with conn.cursor() as cursor:
#         cursor.execute("SELECT * from users")
#         users = cursor.fetchall()
