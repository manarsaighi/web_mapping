import json
import psycopg2

# Load your GeoJSON with UTF-8 encoding
with open('libraries/data/libraries.geojson', encoding='utf-8') as f:
    data = json.load(f)

# Connect to PostGIS
conn = psycopg2.connect("dbname=libraries_db user=postgres password=1234")
cur = conn.cursor()

for feature in data['features']:
    props = feature['properties']
    geom = feature['geometry']
    
    # Only handle Point geometries for simplicity
    if geom['type'] == 'Point':
        lon, lat = geom['coordinates']
        cur.execute("""
            INSERT INTO libraries (name, street, postcode, opening_hours, phone, website, operator, wheelchair, geom)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,ST_SetSRID(ST_MakePoint(%s,%s),4326))
        """, (
            props.get('name'),
            props.get('addr:street'),
            props.get('addr:postcode'),
            props.get('opening_hours'),
            props.get('phone'),
            props.get('website'),
            props.get('operator'),
            props.get('wheelchair'),
            lon,
            lat
        ))

conn.commit()
cur.close()
conn.close()
