# python container
docker build -t py/medicaid .

# run docker postgres container
docker pull kartoza/postgis:10.0-2.4

docker run -d --name "psql-medicaid" -p 5433:5432 -v pg-data:/var/lib/postgresql/data --network mpnetwork kartoza/postgis:10.0-2.4
docker run -it \
  -v ${PWD}:/usr/src/app \
  -v /usr/src/app/node_modules \
  -p 3030:3000 \
  --network mpnetwork \
  --rm \
  node/mp

<!-- docker run -d --name psql-medicaid -p 5432:5433 -v $PWD:/tmp -v pg-data:/var/lib/postgresql/data postgres:10.3 -->

* this can be (should be) simplified into a docker-compose file...
* load db from txt files
<!-- docker run -it --rm -v "$PWD":/usr/src/app --link psql-medicaid:postgres --env-file config/dev.env py/medicaid python3 ./scrape2.py -->
docker run -it --rm -v "$PWD":/usr/src/app --link psql-medicaid:postgres --network mpnetwork --env-file config/dev.env py/medicaid python3 ./scripts/02_load_db.py




32056: FAMILY & COSMETIC DENTISTRY