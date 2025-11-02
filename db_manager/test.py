from db_manager.db import DatabaseManager

db = DatabaseManager()
db.insert_entry("Test Artist", "Test Album", "2025-10-14")
results = db.fetch_by_date("2025-10-14")
print(results)
db.close()
