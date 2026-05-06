CREATE OR REPLACE VIEW analysis.epci_stats_centroid AS
SELECT 
    t.code,
    t.nom,
    o.osm_id,
    count(p.*)::int AS nb_pois,
    count(p.ref_fr_siret)::int AS nb_siret,
    count(p.name)::int AS nb_name,
    sum(
        CASE
            WHEN p.email IS NOT NULL 
            OR p.contact_email IS NOT NULL THEN 1
            ELSE 0
        END
    )::int AS nb_email,
    sum(
        CASE
            WHEN p.phone IS NOT NULL 
            OR p.contact_phone IS NOT NULL
            OR p.tags->>'mobile' IS NOT NULL
            OR p.tags->>'contact:mobile' IS NOT NULL THEN 1
            ELSE 0
        END
    )::int AS nb_phone,
    sum(
        CASE
            WHEN p.instagram IS NOT NULL 
            OR p.contact_instagram IS NOT NULL 
            OR p.facebook IS NOT NULL 
            OR p.contact_facebook IS NOT NULL 
            OR p.website IS NOT NULL 
            OR p.contact_website IS NOT NULL THEN 1
            ELSE 0
        END
    )::int AS nb_website_merge,
    sum(
        CASE
            WHEN p."timestamp"::timestamptz < u.value::timestamptz - interval '5 years'
            THEN 1
            ELSE 0
        END
    )::int AS nb_pois_outdated,
    count(p.opening_hours)::int AS nb_opening_hours,
    count(p.wheelchair)::int AS nb_wheelchair,
    round(avg(EXTRACT(epoch FROM u.value::timestamptz - p."timestamp"::timestamptz)) / 86400::numeric)::int AS avg_days_since_pois_update,
    st_setsrid((st_maximuminscribedcircle(t.geom_4326)).center, 4326)::geometry(Point,4326) AS center
FROM limites_admin_insee.epci t
LEFT JOIN limites_admin_osm.epci o ON t.code = o.code_siren
LEFT JOIN pois_osm_france_merge.pois p ON st_intersects(p.geom_4326, t.geom_4326)
CROSS JOIN (
    SELECT value
    FROM pois_osm_france_merge.osm2pgsql_properties
    WHERE property = 'replication_timestamp'
    LIMIT 1
    ) u
GROUP BY 
    t.code,
    t.nom,
    o.osm_id,
    t.geom_4326
ORDER BY nb_pois DESC;