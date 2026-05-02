# Outil de visualisation de complétude des POIs OSM

[Site disponible ici](https://nicofredo.github.io/osm_pois_completude_viewer/main.html)

Cet outil utilise une base de donnée des POIs OSM postgresql générée et tenue à jour via osm2pgsql (modes flex & slim) ([script flex](script_pois.lua)), ainsi que les limites administratives des communes, EPCI, départements, régions.

Les tuiles utilisent des fichiers PMTiles générés à partir de la base de données, via ogr2ogr qui génère des geojson (exemples de requêtes utilisées pour les générer dans le dossier [sql_queries](sql_queries/)) puis tippecanoe pour la création des fichiers de tuiles.

L'outil repose donc uniquement sur des fichiers plats, sans besoin d'un serveur de tuiles.