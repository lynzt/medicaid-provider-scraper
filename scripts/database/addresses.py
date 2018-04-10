from database.db import Database
db = Database()

def upsert_address(params):
    sql_params = [params['address'], params['address']]
    sql_stmt = '''insert into addresses
        (address) values (%s)
        ON CONFLICT (address) DO UPDATE
        SET address = %s RETURNING id'''
    return db.run_query(sql_stmt, sql_params, 'one')

def get_null_zip_codes(limit):
    sql_params = ['%' + '55' + '%', limit]
    sql_stmt = '''select p.provider, a.id, address
        from addresses a
        inner join provider_addresses pa on a.id = pa.address_id
        inner join providers p on p.id = pa.provider_id
        where zip_code is null
        and address ilike %s
        limit %s'''
    return db.run_query(sql_stmt, sql_params)


def update_address_geodata(params, address_id):
    sql_params = [params['full_address'],
                params['street_nbr'],
                params['street'],
                params['city'],
                params['county'],
                params['state'],
                params['postal_code'],
                params['lng'],
                params['lat'],
                address_id
    ]

    sql_stmt = '''update addresses set full_address = %s,
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
