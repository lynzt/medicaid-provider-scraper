from database.db import Database
db = Database()

def upsert_doctor(params):
    sql_params = [params['first_name'], params['middle_name'], params['last_name'], params['slug_name'], params['slug_name']]
    sql_stmt = '''insert into doctors
        (first_name, middle_name, last_name, slug_name) values (%s, %s, %s, %s)
        ON CONFLICT (slug_name) DO UPDATE
        SET slug_name = %s RETURNING id'''
    return db.run_query(sql_stmt, sql_params, 'one')


# def update_doctor(params, doctor_id):
#     sql_params = [params['doctor_name']]
#     sql_str = ''
#     if 'street_address' in params:
#         sql_str += ', street_address = %s'
#         sql_params.append(params['street_address'])
#     if 'phone' in params:
#         sql_str += ', phone = %s'
#         sql_params.append(params['phone'])
#     if 'speciality' in params:
#         sql_str += ', speciality = %s'
#         sql_params.append(params['speciality'])
#     if 'notes' in params:
#         sql_str += ', notes = %s'
#         sql_params.append(params['notes'])
#     if 'city' in params:
#         sql_str += ', city = %s'
#         sql_params.append(params['city'])
#     if 'state' in params:
#         sql_str += ', state = %s'
#         sql_params.append(params['state'])
#     if 'zip_code' in params:
#         sql_str += ', zip_code = %s'
#         sql_params.append(params['zip_code'])
#
#     sql_params.append(doctor_id)
#     sql_stmt = '''update doctors set doctor = %s '''
#     sql_stmt += sql_str + ''' where id = %s returning *'''
#     return db.run_query(sql_stmt, sql_params, 'one')
