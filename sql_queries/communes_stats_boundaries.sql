SELECT 
    c.code,
    c.nom,
    o.osm_id,
    count(p.*)::integer AS nb_pois,
    count(p.ref_fr_siret)::integer AS nb_siret,
    count(p.name)::integer AS nb_name,    
    sum(
        CASE
            WHEN p.email IS NOT NULL OR p.contact_email IS NOT NULL THEN 1
            ELSE 0
        END)::integer AS nb_email,
    sum(
        CASE
            WHEN p.phone IS NOT NULL OR p.contact_phone IS NOT NULL THEN 1
            ELSE 0
        END)::integer AS nb_phone,
    sum(
        CASE
            WHEN p.instagram IS NOT NULL
            OR p.contact_instagram IS NOT NULL 
            OR p.facebook IS NOT NULL
            OR p.contact_facebook IS NOT NULL
            OR p.website IS NOT NULL
            OR p.contact_website IS NOT NULL THEN 1
            ELSE 0
        END)::integer AS nb_website_merge,
    count(p.opening_hours)::integer AS nb_opening_hours,
    count(p.wheelchair)::integer AS nb_wheelchair,
    round(avg(EXTRACT(epoch FROM u.value::timestamptz - p."timestamp"::timestamptz)) / 86400::numeric)::integer AS avg_days_since_pois_update,
    c.geom_4326
FROM limites_admin_insee.communes c
LEFT JOIN limites_admin_osm.communes o ON c.code = o.code_insee
LEFT JOIN pois_osm_france_merge.pois p ON st_intersects(p.geom_4326, c.geom_4326)
CROSS JOIN (
    SELECT value
    FROM pois_osm_france_merge.osm2pgsql_properties
    WHERE property = 'replication_timestamp'
    LIMIT 1
) u
WHERE
    c.code NOT IN ('75056', '13055', '69123')
    AND c.code NOT LIKE '984%'
    AND c.code NOT LIKE '989%'
GROUP BY 
    c.code,
    c.nom,
    o.osm_id,
    c.geom_4326
ORDER BY nb_pois DESC;