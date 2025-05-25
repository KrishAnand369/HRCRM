import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRandCRM.settings')
import django
django.setup()

from django.db import connection

def drop_table():
    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE invoices_invoice;")
            print("✅ Table 'invoices_invoice' dropped successfully")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    drop_table()