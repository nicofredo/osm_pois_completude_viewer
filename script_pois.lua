local allowed_amenity = {
    restaurant = true,
    fast_food = true,
    cafe = true,
    fuel = true,
    pharmacy = true,
    bank = true,
    bar = true,
    hospital = true,
    post_office = true,
    clinic = true,
    pub = true,
    car_wash = true,
    ice_cream = true,
    driving_school = true,
    cinema = true,
    car_rental = true,
    nightclub = true,
    bureau_de_change = true,
    studio = true,
    internet_cafe = true,
    money_transfer = true,
    casino = true,
    vehicle_inspection = true,
    frozen_food = true,
    boat_rental = true,
    coworking_space = true,
    workshop = true,
    personal_service = true,
    camping = true,
    dancing_school = true,
    training = true,
    ski_school = true,
    ski_rental = true,
    dive_centre = true,
    driver_training = true,
    nursing_home = true,
    funeral_hall = true,
    doctors = true,
    dentist = true,
    theatre = true,
    kindergarten = true,
    language_school = true,
    stripclub = true,
    veterinary = true
}

local allowed_shop = {
    convenience=true,
    supermarket=true,
    clothes=true,
    hairdresser=true,
    car_repair=true,
    bakery=true,
    beauty=true,
    car=true,
    hardware=true,
    mobile_phone=true,
    butcher=true,
    furniture=true,
    car_parts=true,
    alcohol=true,
    florist=true,
    scooter=true,
    variety_store=true,
    electronics=true,
    shoes=true,
    optician=true,
    jewelry=true,
    mall=true,
    gift=true,
    doityourself=true,
    greengrocer=true,
    books=true,
    bicycle=true,
    chemist=true,
    department_store=true,
    laundry=true,
    travel_agency=true,
    stationery=true,
    pet=true,
    sports=true,
    confectionery=true,
    tyres=true,
    cosmetics=true,
    computer=true,
    tailor=true,
    tobacco=true,
    storage_rental=true,
    dry_cleaning=true,
    trade=true,
    copyshop=true,
    motorcycle=true,
    funeral_directors=true,
    beverages=true,
    newsagent=true,
    garden_centre=true,
    massage=true,
    pastry=true,
    interior_decoration=true,
    general=true,
    deli=true,
    toys=true,
    houseware=true,
    wine=true,
    seafood=true,
    pawnbroker=true,
    tattoo=true,
    paint=true,
    wholesale=true,
    photo=true,
    second_hand=true,
    bed=true,
    kitchen=true,
    outdoor=true,
    fabric=true,
    antiques=true,
    coffee=true,
    gas=true,
    ["e-cigarette"]=true,
    perfumery=true,
    craft=true,
    hearing_aids=true,
    money_lender=true,
    appliance=true,
    electrical=true,
    tea=true,
    motorcycle_repair=true,
    boutique=true,
    baby_goods=true,
    bag=true,
    musical_instrument=true,
    dairy=true,
    pet_grooming=true,
    music=true,
    carpet=true,
    rental=true,
    fashion_accessories=true,
    cheese=true,
    canabis=true,
    chocolate=true,
    medical_supply=true,
    leather=true,
    sewing=true,
    cannabis=true,
    locksmith=true,
    games=true,
    video_games=true,
    hifi=true,
    window_blind=true,
    caravan=true,
    tool_hire=true,
    household_linen=true,
    bathroom_furnishing=true,
    shoe_repair=true,
    watches=true,
    nutrition_supplements=true,
    fishing=true,
    erotic=true,
    frame=true,
    grocery=true,
    boat=true,
    repair=true,
    weapons=true,
    gold_buyer=true,
    lighting=true,
    pottery=true,
    security=true,
    groundskeeping=true,
    herbalist=true,
    curtain=true,
    health_food=true,
    flooring=true,
    printer_ink=true,
    anime=true,
    camera=true,
    scuba_diving=true,
    candles=true,
    printing=true,
    garden_furniture=true,
    food=true
}

local allowed_office = {
    company=true,
    estate_agent=true,
    insurance=true,
    telecommunication=true,
    it=true,
    accountant=true,
    employment_agency=true,
    tax_advisor=true,
    financial=true,
    advertising_agency=true,
    logistics=true,
    newspaper=true,
    financial_advisor=true,
    consulting=true,
    travel_agent=true,
    coworking=true,
    moving_company=true,
    lawyer=true,
    architect=true,
    construction_company=true,
    developer=true,
    credit_broker=true,
    graphic_design=true,
    construction=true,
    property_management=true,
    cleaning=true,
    notary=true
}

local allowed_craft = {
    carpenter=true,
    winery=true,
    metal_construction=true,
    electronics_repair=true,
    photographer=true,
    electrician=true,
    brewery=true,
    hvac=true,
    plumber=true,
    tailor=true,
    shoemaker=true,
    sawmill=true,
    caterer=true,
    window_construction=true,
    gardener=true,
    dressmaker=true,
    confectionery=true,
    stonemason=true,
    glaziery=true,
    painter=true,
    roofer=true,
    builder=true,
    key_cutter=true,
    upholsterer=true,
    cleaning=true,
    pottery=true,
    distillery=true,
    jeweller=true,
    handicraft=true,
    joiner=true,
    agricultural_engines=true,
    tiler=true,
    insulation=true,
    clockmaker=true,
    sculptor=true,
    printer=true,
    cabinet_maker=true
}

local allowed_tourism = {
    hotel=true,
    hostel=true,
    guest_house=true,
    motel=true
}

local pois = osm2pgsql.define_table({
    name = 'pois',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'timestamp', sql_type = 'timestamp', not_null = true },
        { column = 'name' },
        { column = 'class', not_null = true },
        { column = 'subclass', not_null = true },
        { column = 'geom_4326', type = 'point', not_null = true, projection='4326' },
        { column = 'ref_fr_siret' },
        { column = 'contact_phone' },
        { column = 'phone' },
        { column = 'contact_website' },
        { column = 'website' },
        { column = 'opening_hours' },
        { column = 'wheelchair' },
        { column = 'contact_email' },
        { column = 'email' },
        { column = 'contact_facebook' },
        { column = 'facebook' },
        { column = 'contact_instagram' },
        { column = 'instagram' },
        { column = 'tags', type = 'jsonb' },
}})

local pois_others = osm2pgsql.define_table({
    name = 'pois_others',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'timestamp', sql_type = 'timestamp', not_null = true },
        { column = 'name' },
        { column = 'class', not_null = true },
        { column = 'subclass', not_null = true },
        { column = 'geom_4326', type = 'point', not_null = true, projection='4326' },
        { column = 'ref_fr_siret' },
        { column = 'contact_phone' },
        { column = 'phone' },
        { column = 'contact_website' },
        { column = 'website' },
        { column = 'opening_hours' },
        { column = 'wheelchair' },
        { column = 'contact_email' },
        { column = 'email' },
        { column = 'contact_facebook' },
        { column = 'facebook' },
        { column = 'contact_instagram' },
        { column = 'instagram' },
        { column = 'tags', type = 'jsonb' }
    }})


function format_date(ts)
    return os.date('!%Y-%m-%dT%H:%M:%SZ', ts)
end

function process_poi(object)
    local fields = {
        timestamp = format_date(object.timestamp),

        name = object:grab_tag('name'),
        ref_fr_siret = object:grab_tag("ref:FR:SIRET"),

        contact_phone = object:grab_tag("contact:phone"),
        phone = object:grab_tag('phone'),

        contact_website = object:grab_tag("contact:website"),
        website = object:grab_tag('website'),

        opening_hours = object:grab_tag('opening_hours'),
        wheelchair = object:grab_tag('wheelchair'),

        contact_email = object:grab_tag("contact:email"),
        email = object:grab_tag('email'),

        contact_facebook = object:grab_tag("contact:facebook"),
        facebook = object:grab_tag('facebook'),
        
        contact_instagram = object:grab_tag("contact:instagram"),
        instagram = object:grab_tag('instagram')
    }

    local has_siret = fields.ref_fr_siret ~= nil

    if object.tags.amenity then
        fields.class = "amenity"
        fields.subclass = object:grab_tag('amenity')
        fields.tags = object.tags
        if allowed_amenity[fields.subclass] then
            return fields, pois
        elseif has_siret then
            return fields, pois_others
        end
    elseif object.tags.shop then
        fields.class = "shop"
        fields.subclass = object:grab_tag('shop')
        fields.tags = object.tags
        if allowed_shop[fields.subclass] then
            return fields, pois
        elseif has_siret then
            return fields, pois_others
        end
    elseif object.tags.office then
        fields.class = "office"
        fields.subclass = object:grab_tag('office')
        fields.tags = object.tags
        if allowed_office[fields.subclass] then
            return fields, pois
        elseif has_siret then
            return fields, pois_others
        end
    elseif object.tags.craft then
        fields.class = "craft"
        fields.subclass = object:grab_tag('craft')
        fields.tags = object.tags
        if allowed_craft[fields.subclass] then
            return fields, pois
        elseif has_siret then
            return fields, pois_others
        end
    elseif object.tags.tourism then
        fields.class = "tourism"
        fields.subclass = object:grab_tag('tourism')
        fields.tags = object.tags
        if allowed_tourism[fields.subclass] then
            return fields, pois
        elseif has_siret then
            return fields, pois_others
        end
    else
        return nil, nil
    end
end

function osm2pgsql.process_node(object)
    local record, table_name = process_poi(object)
    if record then
        record.geom_4326 = object:as_point()
        table_name:insert(record)
    end
end

function osm2pgsql.process_way(object)
    if object.is_closed then
        local record, table_name = process_poi(object)
        if record then
            record.geom_4326 = object:as_polygon():centroid()
            table_name:insert(record)
        end
    end
end

function osm2pgsql.process_relation(object)
    local relation_type = object:grab_tag('type')
    if relation_type == 'multipolygon' then
        local record, table_name = process_poi(object)
        if record then
            local max_area = 0.0
            local biggest_poly = nil
            for g in object:as_multipolygon():geometries() do
                local area = g:area()
                if area > max_area then
                    biggest_poly = g
                    max_area = area
                end
            end
            if not biggest_poly then
                print("\n\27[31mNo polygon for relation:", object.id,"\27[0m")
            else
                local point = biggest_poly:pole_of_inaccessibility()
                -- local point = object:as_multipolygon():centroid() -- can return a point that is not contained by the relation
                record.geom_4326 = point
                table_name:insert(record)
            end
        end
    end
end