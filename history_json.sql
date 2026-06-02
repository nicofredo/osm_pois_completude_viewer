-- in psql
\copy (
WITH history_timestamp AS (
    SELECT '2026-01-01T00:00:00Z'::timestamptz AS value
),

analysis_communes_stats AS (
    SELECT *
    FROM analysis.communes_stats_history
    WHERE update_timestamp = (SELECT value FROM history_timestamp)
),

analysis_epci_stats AS (
    SELECT *
    FROM analysis.epci_stats_history
    WHERE update_timestamp = (SELECT value FROM history_timestamp)
),

analysis_departements_stats AS (
    SELECT *
    FROM analysis.departements_stats_history
    WHERE update_timestamp = (SELECT value FROM history_timestamp)
),

analysis_regions_stats AS (
    SELECT *
    FROM analysis.regions_stats_history
    WHERE update_timestamp = (SELECT value FROM history_timestamp)
)

SELECT json_build_object(
    'date', (SELECT DATE(value) FROM history_timestamp),
    'layers', json_build_object(
        'communes', (
            SELECT json_object_agg(code_commune, json_build_object(
                'nb_pois', nb_pois,
                'nb_siret', nb_siret,
                'nb_name', nb_name,
                'nb_email', nb_email,
                'nb_phone', nb_phone,
                'nb_opening_hours', nb_opening_hours,
                'nb_wheelchair', nb_wheelchair,
                'nb_website_merge', nb_website_merge
            ))
            FROM analysis_communes_stats
        ),
        'epci', (
            SELECT json_object_agg(code_epci, json_build_object(
                'nb_pois', nb_pois,
                'nb_siret', nb_siret,
                'nb_name', nb_name,
                'nb_email', nb_email,
                'nb_phone', nb_phone,
                'nb_opening_hours', nb_opening_hours,
                'nb_wheelchair', nb_wheelchair,
                'nb_website_merge', nb_website_merge
            ))
            FROM analysis_epci_stats
        ),
        'departements', (
            SELECT json_object_agg(code_departement, json_build_object(
                'nb_pois', nb_pois,
                'nb_siret', nb_siret,
                'nb_name', nb_name,
                'nb_email', nb_email,
                'nb_phone', nb_phone,
                'nb_opening_hours', nb_opening_hours,
                'nb_wheelchair', nb_wheelchair,
                'nb_website_merge', nb_website_merge
            ))
            FROM analysis_departements_stats
        ),
        'regions', (
            SELECT json_object_agg(code_region, json_build_object(
                'nb_pois', nb_pois,
                'nb_siret', nb_siret,
                'nb_name', nb_name,
                'nb_email', nb_email,
                'nb_phone', nb_phone,
                'nb_opening_hours', nb_opening_hours,
                'nb_wheelchair', nb_wheelchair,
                'nb_website_merge', nb_website_merge
            ))
            FROM analysis_regions_stats
        )
    )
)
) TO './history.json';