local regions = osm2pgsql.define_table({
    name = 'regions',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'name', not_null = true },
        { column = 'iso3166_2', not_null = true },
        { column = 'code_insee', not_null = true },
        { column = 'code_siren', not_null = true },
        { column = 'population', type = 'integer' },
        { column = 'wikidata' },
        { column = 'geom_3857', type = 'multipolygon', projection = '3857' }, -- not_null = true,
        { column = 'geom_4326', type = 'multipolygon', projection = '4326' }, -- not_null = true,
}})

local departements = osm2pgsql.define_table({
    name = 'departements',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'name', not_null = true },
        { column = 'iso3166_2', not_null = true },
        { column = 'code_insee', not_null = true },
        { column = 'code_siren', not_null = true },
        { column = 'population', type = 'integer' },
        { column = 'wikidata' },
        { column = 'geom_3857', type = 'multipolygon', projection = '3857' }, -- not_null = true,
        { column = 'geom_4326', type = 'multipolygon', projection = '4326' }, -- not_null = true,
}})

local epci = osm2pgsql.define_table({
    name = 'epci',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'name', not_null = true },
        { column = 'code_siren', not_null = true },
        { column = 'population', type = 'integer' },
        { column = 'wikidata' },
        { column = 'type', not_null = true },
        { column = 'geom_3857', type = 'multipolygon', projection = '3857' }, -- not_null = true,
        { column = 'geom_4326', type = 'multipolygon', projection = '4326' }, -- not_null = true,
}})

local communes = osm2pgsql.define_table({
    name = 'communes',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'name', not_null = true },
        { column = 'code_insee', not_null = true },
        { column = 'code_siren' },
        { column = 'postal_code' },
        { column = 'population', type= 'integer' },
        { column = 'wikidata' },
        { column = 'type', not_null = true },
        { column = 'geom_3857', type = 'multipolygon', projection = '3857' }, -- not_null = true,
        { column = 'geom_4326', type = 'multipolygon', projection = '4326' }, -- not_null = true,
}})

function osm2pgsql.process_relation(object)
    if object.tags.type == 'boundary' and object.tags.boundary == 'administrative' and object.tags.admin_level == '4' then
        local fields = {
            name = object.tags.name,
            iso3166_2 = object.tags["ISO3166-2"],
            code_insee = object.tags["ref:INSEE"],
            code_siren = object.tags["ref:FR:SIREN"],
            population = object.tags.population,
            wikidata = object.tags.wikidata,
            geom_3857 = object:as_multipolygon(),
            geom_4326 = object:as_multipolygon(),

        }
        regions:insert(fields)

    elseif object.tags.type == 'boundary' and object.tags.boundary == 'administrative' and object.tags.admin_level == '6' then
        local fields = {
            name = object.tags.name,
            iso3166_2 = object.tags["ISO3166-2"],
            code_insee = object.tags["ref:INSEE"],
            code_siren = object.tags["ref:FR:SIREN"],
            population = object.tags.population,
            wikidata = object.tags.wikidata,
            geom_3857 = object:as_multipolygon(),
            geom_4326 = object:as_multipolygon(),
        }
        departements:insert(fields)

    elseif object.tags["local_authority:FR"] == 'CC' or object.tags["local_authority:FR"] == 'CA' or object.tags["local_authority:FR"] == 'CU' or object.tags["local_authority:FR"] == 'metropole' then
        local fields = {
            name = object.tags.name,
            code_siren = object.tags["ref:FR:SIREN"],
            population = object.tags.population,
            wikidata = object.tags.wikidata,
            type = object.tags["local_authority:FR"],
            geom_3857 = object:as_multipolygon(),
            geom_4326 = object:as_multipolygon(),
        }
        epci:insert(fields)

    elseif object.tags.boundary == 'administrative' and (object.tags.admin_level == '8' or (object.tags.admin_level == '9' and object.tags["admin_type:FR"] == 'arrondissement municipal')) then --object.tags.type == 'boundary' and object.tags.boundary == 'administrative'
        local fields = {
            name = object.tags.name,
            code_insee = object.tags["ref:INSEE"],
            code_siren = object.tags["ref:FR:SIREN"],
            postal_code = object.tags.postal_code,
            population = object.tags.population,
            wikidata = object.tags.wikidata,
            type = object.tags.admin_level,
            geom_3857 = object:as_multipolygon(),
            geom_4326 = object:as_multipolygon(),
        }
        communes:insert(fields)
    end
end