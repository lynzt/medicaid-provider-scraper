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
    if 'address' in params:
        sql_str += ', address = %s'
        sql_params.append(params['address'])
    if 'phone' in params:
        sql_str += ', phone = %s'
        sql_params.append(params['phone'])
    if 'speciality' in params:
        sql_str += ', speciality = %s'
        sql_params.append(params['speciality'])
    if 'notes' in params:
        sql_str += ', notes = %s'
        sql_params.append(params['notes'])
    if 'city' in params:
        sql_str += ', city = %s'
        sql_params.append(params['city'])
    if 'state' in params:
        sql_str += ', state = %s'
        sql_params.append(params['state'])
    if 'zip_code' in params:
        sql_str += ', zip_code = %s'
        sql_params.append(params['zip_code'])

    sql_params.append(provider_id)
    sql_stmt = '''update providers set provider = %s '''
    sql_stmt += sql_str + ''' where id = %s returning *'''
    return db.run_query(sql_stmt, sql_params, 'one')


def get_null_zip_codes(limit):
    sql_params = [limit]
    sql_stmt = '''select id, provider, address
        from providers
        where zip_code is null
        limit %s'''
    return db.run_query(sql_stmt, sql_params)


def update_address_geodata(params, provider_id):
    sql_params = [params['full_address'],
                params['street_nbr']['long_name'],
                params['street']['long_name'],
                params['city']['long_name'],
                params['county']['long_name'],
                params['state']['long_name'],
                params['postal_code']['long_name'],
                params['lng'],
                params['lat'],
                provider_id
    ]

    sql_stmt = '''update providers set full_address = %s,
                                        street_nbr = %s,
                                        street = %s,
                                        city = %s,
                                        county = %s,
                                        state = %s,
                                        zip_code = %s,
                                        geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    where id = %s
                    returning *;'''
    return db.run_query(sql_stmt, sql_params, 'one')
