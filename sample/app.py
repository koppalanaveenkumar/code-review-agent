API_KEY = "sk-live-12345abcdef"


def get_user(db, user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()


def average(numbers):
    return sum(numbers) / len(numbers)


def get_last_items(items, n):
    return items[len(items) - n - 1:]