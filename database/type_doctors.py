from database.db import Database
db = Database()

def upsert_type_doctor(type_id, doctor_id):
    sql_params = [type_id, doctor_id]
    sql_stmt = '''insert into type_doctors (type_id, doctor_id) values (%s, %s)
        ON CONFLICT (type_id, doctor_id) DO NOTHING
        returning *'''
    return db.run_query(sql_stmt, sql_params)
