from database.db import Database
db = Database()

def upsert_provider_addresses(provider_id, address_id):
    sql_params = [provider_id, address_id]
    sql_stmt = '''insert into provider_addresses (provider_id, address_id) values (%s, %s)
        ON CONFLICT (provider_id, address_id) DO NOTHING
        returning *'''
    return db.run_query(sql_stmt, sql_params)
