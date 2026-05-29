# Adicione estes métodos no final da classe Database em core/database.py:

def get_user_by_id(self, user_id: int):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'email': row[3],
            'age': row[4],
            'weight': row[5],
            'height': row[6],
            'goal_weight': row[7],
            'experience': row[8],
            'level': row[9],
            'created_at': row[10]
        }
    return None

def update_user_profile(self, user_id: int, age: int, weight: float, 
                        height: int, goal_weight: float, email: str):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET age = ?, weight = ?, height = ?, goal_weight = ?, email = ?
        WHERE id = ?
    ''', (age, weight, height, goal_weight, email, user_id))
    conn.commit()
    conn.close()
