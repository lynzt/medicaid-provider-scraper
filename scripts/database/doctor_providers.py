from database.db import Database
db = Database()

def upsert_doctor_providers(doctor_id, provider_id):
    sql_params = [doctor_id, provider_id]
    sql_stmt = '''insert into doctor_providers (doctor_id, provider_id) values (%s, %s)
        ON CONFLICT (doctor_id, provider_id) DO NOTHING
        returning *'''
    return db.run_query(sql_stmt, sql_params)
