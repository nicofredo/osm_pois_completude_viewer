echo "Running osm2pgsql replication..."
osm2pgsql-replication update -d <db> --schema pois_osm -U <user>

echo "Generating pmtiles..."
ogr2ogr -f GeoJSON regions_stats_boundaries.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.regions_stats_boundaries
ogr2ogr -f GeoJSON departements_stats_boundaries.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.departements_stats_boundaries
ogr2ogr -f GeoJSON epci_stats_boundaries.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.epci_stats_boundaries
ogr2ogr -f GeoJSON communes_stats_boundaries.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.communes_stats_boundaries
ogr2ogr -f GeoJSON regions_stats_centroid.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.regions_stats_centroid
ogr2ogr -f GeoJSON departements_stats_centroid.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.departements_stats_centroid
ogr2ogr -f GeoJSON epci_stats_centroid.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.epci_stats_centroid
ogr2ogr -f GeoJSON communes_stats_centroid.geojson \
    PG:"host=<host> dbname=<db> user=<user>" \
    analysis.communes_stats_centroid

tippecanoe -o regions_stats_boundaries.mbtiles -l regions_stats_boundaries \
    -Z 0 -z 9 regions_stats_boundaries.geojson
tippecanoe -o departements_stats_boundaries.mbtiles -l departements_stats_boundaries \
    -Z 0 -z 9 departements_stats_boundaries.geojson
tippecanoe -o epci_stats_boundaries.mbtiles -l epci_stats_boundaries \
    -Z 3 -z 9 epci_stats_boundaries.geojson
tippecanoe -o communes_stats_boundaries.mbtiles -l communes_stats_boundaries \
    -Z 5 -z 9 --no-tile-size-limit communes_stats_boundaries.geojson
tippecanoe -o regions_stats_centroid.mbtiles -l regions_stats_centroid \
    -Z 0 -z 9 -r1 regions_stats_centroid.geojson
tippecanoe -o departements_stats_centroid.mbtiles -l departements_stats_centroid \
    -Z 0 -z 9 -r1 departements_stats_centroid.geojson
tippecanoe -o epci_stats_centroid.mbtiles -l epci_stats_centroid \
    -Z 3 -z 9 -r1 epci_stats_centroid.geojson
tippecanoe -o communes_stats_centroid.mbtiles -l communes_stats_centroid \
    -Z 5 -z 9 -r1 --no-tile-size-limit communes_stats_centroid.geojson

pmtiles convert regions_stats_boundaries.mbtiles regions_stats_boundaries.pmtiles
pmtiles convert departements_stats_boundaries.mbtiles departements_stats_boundaries.pmtiles
pmtiles convert epci_stats_boundaries.mbtiles epci_stats_boundaries.pmtiles
pmtiles convert communes_stats_boundaries.mbtiles communes_stats_boundaries.pmtiles
pmtiles convert regions_stats_centroid.mbtiles regions_stats_centroid.pmtiles
pmtiles convert departements_stats_centroid.mbtiles departements_stats_centroid.pmtiles
pmtiles convert epci_stats_centroid.mbtiles epci_stats_centroid.pmtiles
pmtiles convert communes_stats_centroid.mbtiles communes_stats_centroid.pmtiles

rm regions_stats_boundaries.mbtiles regions_stats_boundaries.geojson
rm departements_stats_boundaries.mbtiles departements_stats_boundaries.geojson
rm epci_stats_boundaries.mbtiles epci_stats_boundaries.geojson
rm communes_stats_boundaries.mbtiles communes_stats_boundaries.geojson
rm regions_stats_centroid.mbtiles regions_stats_centroid.geojson
rm departements_stats_centroid.mbtiles departements_stats_centroid.geojson
rm epci_stats_centroid.mbtiles epci_stats_centroid.geojson
rm communes_stats_centroid.mbtiles communes_stats_centroid.geojson

echo "Generating update_timestamp.json..."
psql -U <user> -d <db> -t -A -c \
    "SELECT json_build_object('updated_at', value)
     FROM pois_osm.osm2pgsql_properties
     WHERE property = 'replication_timestamp'" \
    > update_timestamp.json