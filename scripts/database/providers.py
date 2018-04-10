from database.db import Database
db = Database()

def upsert_provider(params):
    sql_params = [params['provider_name'], params['provider_name']]
    sql_stmt = '''insert into providers
        (provider) values (%s)
        ON CONFLICT (provider) DO UPDATE
        SET provider = %s RETURNING id'''
    return db.run_query(sql_stmt, sql_params, 'one')


def update_provider(params, provider_id):
    sql_params = [params['provider_name']]
    sql_str = ''
    if 'phone' in params:
        sql_str += ', phone = %s'
        sql_params.append(params['phone'])
    if 'specialty' in params:
        sql_str += ', specialty = %s'
        sql_params.append(params['specialty'])
    if 'critical_access_provider' in params:
        sql_str += ', critical_access_provider = %s'
        sql_params.append(params['critical_access_provider'])
    if 'notes' in params:
        sql_str += ', notes = %s'
        sql_params.append(params['notes'])

    sql_params.append(provider_id)
    sql_stmt = '''update providers set provider = %s '''
    sql_stmt += sql_str + ''' where id = %s returning *'''
    return db.run_query(sql_stmt, sql_params, 'one')
