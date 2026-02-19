import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecomm.settings')
django.setup()

def reset_database():
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            print(f"Dropping table {table[0]}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table[0]}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("All tables dropped.")

if __name__ == '__main__':
    reset_database()
