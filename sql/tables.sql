-- CREATE EXTENSION postgis;
-- CREATE DATABASE providers ENCODING 'utf8' TEMPLATE template0;
-- create user providers_web password 'pass';

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO providers_web;
-- grant all on all sequences in schema public to providers_web;

drop table providers;
drop table doctors;
drop table types;
drop table subtypes;
drop table type_providers;
drop table subtype_types;
drop table doctor_providers;

-- these should hvae fk - but not having them makes it easier to drop and reload...
-- tables
CREATE TABLE IF NOT EXISTS "providers" (
    id serial,
    provider character varying,
    phone character varying,
    address character varying,
    full_address character varying,
    street_nbr character varying,
    street character varying,
    city character varying,
    state character varying,
    zip_code character varying,
    county character varying,
    geom geometry(Point, 4326),
    speciality character varying,
    notes character varying,
    CONSTRAINT providers_pkey PRIMARY KEY (id)
);
CREATE Unique INDEX providers_provider_idx ON providers (provider);
CREATE INDEX providers_city_idx ON providers (city);
CREATE INDEX providers_zip_idx ON providers (zip_code);
CREATE INDEX providers_county_idx ON providers (county);
CREATE index ON providers using gist (geom);


CREATE TABLE IF NOT EXISTS "doctors" (
    id serial,
    first_name character varying,
    middle_name character varying,
    last_name character varying,
    slug_name character varying,
    CONSTRAINT doctors_pkey PRIMARY KEY (id)
);
CREATE INDEX doctors_name_idx ON doctors (last_name, first_name, middle_name);
CREATE UNIQUE INDEX doctors_slug_idx ON doctors (slug_name);


CREATE TABLE IF NOT EXISTS "types" (
    id serial,
    type character varying,
    CONSTRAINT types_pkey PRIMARY KEY (id)
);
CREATE unique  INDEX types_type_idx ON types (type);


CREATE TABLE IF NOT EXISTS "subtypes" (
    id serial,
    subtype character varying,
    type_id integer NOT NULL,
    CONSTRAINT subtypes_pkey PRIMARY KEY (id)
);
CREATE unique INDEX subtypes_subtype_idx ON subtypes (subtype);
CREATE INDEX ON subtypes (type_id);


-- join tables
CREATE TABLE IF NOT EXISTS "type_providers" (
    id serial,
    type_name varchar(15),
    type_id integer NOT NULL,
    provider_id integer NOT NULL,
    CONSTRAINT type_providers_pkey PRIMARY KEY (id)
);
CREATE unique INDEX type_providers_type_idx ON type_providers (type_name, type_id, provider_id);
CREATE INDEX type_providers_provider_idx ON type_providers (provider_id);


-- CREATE TABLE IF NOT EXISTS "subtype_types" (
--     id serial,
--     subtype_id integer NOT NULL,
--     type_id integer NOT NULL,
--     CONSTRAINT subtype_types_pkey PRIMARY KEY (id)
-- );
-- CREATE unique INDEX subtype_types_subtype_idx ON subtype_types (subtype_id, type_id);
-- CREATE INDEX subtype_types_type_idx ON subtype_types (type_id);


CREATE TABLE IF NOT EXISTS "doctor_providers" (
    id serial,
    doctor_id integer NOT NULL,
    provider_id integer NOT NULL,
    CONSTRAINT doctor_providers_pkey PRIMARY KEY (id)
);
CREATE unique INDEX doctor_providers_doctor_idx ON doctor_providers (doctor_id, provider_id);
CREATE INDEX doctor_providers_provider_idx ON doctor_providers (provider_id);


GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO providers_web;
grant all on all sequences in schema public to providers_web;
