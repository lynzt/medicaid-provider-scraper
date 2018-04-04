from database.db import Database
db = Database()

def upsert_subtype(params, type_id):
    sql_params = [params['subtype'], type_id, params['subtype']]
    sql_stmt = '''insert into subtypes (subtype, type_id) values (%s, %s)
        ON CONFLICT (subtype) DO UPDATE
        SET subtype = %s RETURNING id'''
    return db.run_query(sql_stmt, sql_params, 'one')
