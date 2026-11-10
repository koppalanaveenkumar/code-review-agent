def get_user(db, user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id)).fetchone()

def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
