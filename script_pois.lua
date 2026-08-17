local allowed_amenity = {
    bank = true,
    bar = true,
    boat_rental = true,
    bureau_de_change = true,
    cafe = true,
    car_rental = true,
    car_wash = true,
    casino = true,
    cinema = true,
    clinic = true,
    coworking_space = true,
    dancing_school = true,
    dentist = true,
    dive_centre = true,
    doctors = true,
    driving_school = true,
    fast_food = true,
    fuel = true,
    funeral_hall = true,
    hookah_lounge = true,
    hospital = true,
    ice_cream = true,
    internet_cafe = true,
    kindergarten = true,
    language_school = true,
    library = true,
    money_transfer = true,
    music_school = true,
    nightclub = true,
    nursing_home = true,
    personal_service = true,
    pharmacy = true,
    post_office = true,
    prep_school = true,
    pub = true,
    restaurant = true,
    ski_rental = true,
    ski_school = true,
    stripclub = true,
    studio = true,
    swingerclub = true,
    theatre = true,
    toy_library = true,
    training = true,
    vehicle_inspection = true,
    veterinary = true,
    workshop = true,
}

local allowed_shop = {
    ["e-cigarette"] = true,
    agrarian = true,
    alcohol = true,
    anime = true,
    antiques = true,
    appliance = true,
    art = true,
    baby_goods = true,
    bag = true,
    bakery = true,
    bathroom_furnishing = true,
    beauty = true,
    bed = true,
    beverages = true,
    bicycle = true,
    boat = true,
    boat_repair = true,
    books = true,
    boutique = true,
    building_materials = true,
    butcher = true,
    camera = true,
    candles = true,
    cannabis = true,
    car = true,
    car_parts = true,
    car_repair = true,
    caravan = true,
    carpet = true,
    charity = true,
    cheese = true,
    chemist = true,
    chocolate = true,
    clothes = true,
    coffee = true,
    collector = true,
    computer = true,
    confectionery = true,
    convenience = true,
    copyshop = true,
    cosmetics = true,
    country_store = true,
    craft = true,
    curtain = true,
    dairy = true,
    deli = true,
    department_store = true,
    doityourself = true,
    doors = true,
    dry_cleaning = true,
    electrical = true,
    electronics = true,
    energy = true,
    erotic = true,
    esoteric = true,
    estate_agent = true,
    fabric = true,
    farm = true,
    fashion_accessories = true,
    fireplace = true,
    fishing = true,
    flooring = true,
    florist = true,
    food = true,
    frame = true,
    frozen_food = true,
    fuel = true,
    funeral_directors = true,
    furniture = true,
    games = true,
    garden_centre = true,
    garden_furniture = true,
    garden_machinery = true,
    gas = true,
    general = true,
    gift = true,
    glaziery = true,
    gold_buyer = true,
    greengrocer = true,
    grocery = true,
    groundskeeping = true,
    haberdashery = true,
    hairdresser = true,
    hairdresser_supply = true,
    hardware = true,
    health_food = true,
    hearing_aids = true,
    herbalist = true,
    hifi = true,
    honey = true,
    household_linen = true,
    houseware = true,
    hunting = true,
    hvac = true,
    ice_cream = true,
    interior_decoration = true,
    jewelry = true,
    kitchen = true,
    kitchenware = true,
    knives = true,
    laundry = true,
    leather = true,
    lighting = true,
    locksmith = true,
    mall = true,
    massage = true,
    medical_supply = true,
    military_surplus = true,
    mobile_phone = true,
    mobile_phone_accessories = true,
    model = true,
    money_lender = true,
    motorcycle = true,
    motorcycle_repair = true,
    music = true,
    musical_instrument = true,
    newsagent = true,
    nutrition_supplements = true,
    optician = true,
    outdoor = true,
    paint = true,
    party = true,
    pasta = true,
    pastry = true,
    pawnbroker = true,
    perfumery = true,
    pest_control = true,
    pet = true,
    pet_grooming = true,
    photo = true,
    photo_studio = true,
    pottery = true,
    printer_ink = true,
    printing = true,
    psychic = true,
    radiotechnics = true,
    rental = true,
    repair = true,
    scooter = true,
    scuba_diving = true,
    seafood = true,
    second_hand = true,
    security = true,
    sewing = true,
    ship_chandler = true,
    shoe_repair = true,
    shoes = true,
    ski = true,
    spices = true,
    sports = true,
    stationery = true,
    storage_rental = true,
    supermarket = true,
    surf = true,
    swimming_pool = true,
    tailor = true,
    tattoo = true,
    tea = true,
    telecommunication = true,
    tiles = true,
    tobacco = true,
    tool_hire = true,
    toys = true,
    tractor = true,
    trade = true,
    travel_agency = true,
    truck = true,
    truck_repair = true,
    tyres = true,
    vacuum_cleaner = true,
    variety_store = true,
    video = true,
    video_games = true,
    watches = true,
    water_sports = true,
    weapons = true,
    wholesale = true,
    wigs = true,
    window_blind = true,
    windows = true,
    wine = true,
    wool = true,
}

local allowed_office = {
    accountant = true,
    advertising_agency = true,
    architect = true,
    cleaning = true,
    company = true,
    construction = true,
    construction_company = true,
    consulting = true,
    coworking = true,
    credit_broker = true,
    developer = true,
    educational_institution = true,
    employment_agency = true,
    estate_agent = true,
    financial = true,
    financial_advisor = true,
    graphic_design = true,
    guide = true,
    harbour_master = true,
    insurance = true,
    it = true,
    lawyer = true,
    logistics = true,
    moving_company = true,
    newspaper = true,
    notary = true,
    property_management = true,
    publisher = true,
    surveyor = true,
    tax_advisor = true,
    telecommunication = true,
    travel_agent = true,
}

local allowed_craft = {
    agricultural_engines = true,
    blacksmith = true,
    boatbuilder = true,
    bookbinder = true,
    brewery = true,
    builder = true,
    cabinet_maker = true,
    carpenter = true,
    caterer = true,
    chimney_sweeper = true,
    cleaning = true,
    clockmaker = true,
    confectionery = true,
    distillery = true,
    dressmaker = true,
    electrician = true,
    electronics_repair = true,
    floorer = true,
    gardener = true,
    glassblower = true,
    glaziery = true,
    handicraft = true,
    hvac = true,
    insulation = true,
    jeweller = true,
    joiner = true,
    key_cutter = true,
    leather = true,
    locksmith = true,
    luthier = true,
    metal_construction = true,
    painter = true,
    parquet_layer = true,
    photographer = true,
    photographic_laboratory = true,
    plasterer = true,
    plumber = true,
    pottery = true,
    printer = true,
    printmaker = true,
    roofer = true,
    saddler = true,
    sailmaker = true,
    sawmill = true,
    sculptor = true,
    shoemaker = true,
    signmaker = true,
    stonemason = true,
    tailor = true,
    tiler = true,
    upholsterer = true,
    watchmaker = true,
    window_construction = true,
    winery = true,
}

local allowed_tourism = {
    aquarium = true,
    camp_site = true,
    gallery = true,
    guest_house = true,
    hostel = true,
    hotel = true,
    motel = true,
    museum = true,
    theme_park = true,
    zoo = true,
}

local allowed_leisure = {
    adult_gaming_centre = true,
    bowling_alley = true,
    dance = true,
    escape_game = true,
    fitness_centre = true,
    golf_course = true,
    ice_rink = true,
    trampoline_park = true,
    water_park = true,
}

local allowed_healthcare = {
    laboratory = true,
}

local pois = osm2pgsql.define_table({
    name = 'pois',
    ids = { type = 'any', type_column = 'osm_type', id_column = 'osm_id' },
    columns = {
        { column = 'timestamp', sql_type = 'timestamptz', not_null = true },
        { column = 'username', not_null = true },
        { column = 'class', not_null = true },
        { column = 'subclass', not_null = true },
        { column = 'name' },
        { column = 'geom_4326', type = 'point', not_null = true, projection='4326' },
        { column = 'ref_fr_siret' },
        { column = 'contact_phone' },
        { column = 'phone' },
        { column = 'contact_mobile' },
        { column = 'mobile' },
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


function format_date(ts)
    return os.date('!%Y-%m-%dT%H:%M:%SZ', ts)
end

function process_poi(object)
    local fields = {
        timestamp = format_date(object.timestamp),
        username = object.user,

        name = object:grab_tag('name'),
        ref_fr_siret = object:grab_tag("ref:FR:SIRET"),

        contact_phone = object:grab_tag("contact:phone"),
        phone = object:grab_tag('phone'),

        contact_mobile = object:grab_tag("contact:mobile"),
        mobile = object:grab_tag('mobile'),

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

    if object.tags.amenity then
        fields.class = "amenity"
        fields.subclass = object:grab_tag('amenity')
        fields.tags = object.tags
        if allowed_amenity[fields.subclass] then
            return fields, pois
        end
    elseif object.tags.shop then
        fields.class = "shop"
        fields.subclass = object:grab_tag('shop')
        fields.tags = object.tags
        if allowed_shop[fields.subclass] then
            return fields, pois
        end
    elseif object.tags.office then
        fields.class = "office"
        fields.subclass = object:grab_tag('office')
        fields.tags = object.tags
        if allowed_office[fields.subclass] then
            return fields, pois
        end
    elseif object.tags.craft then
        fields.class = "craft"
        fields.subclass = object:grab_tag('craft')
        fields.tags = object.tags
        if allowed_craft[fields.subclass] then
            return fields, pois
        end
    elseif object.tags.tourism then
        fields.class = "tourism"
        fields.subclass = object:grab_tag('tourism')
        fields.tags = object.tags
        if allowed_tourism[fields.subclass] then
            return fields, pois
        end
    elseif object.tags.leisure then
        fields.class = "leisure"
        fields.subclass = object:grab_tag('leisure')
        fields.tags = object.tags
        if allowed_leisure[fields.subclass] then
            return fields, pois
        end
    elseif object.tags.healthcare then
        fields.class = "healthcare"
        fields.subclass = object:grab_tag('healthcare')
        fields.tags = object.tags
        if allowed_healthcare[fields.subclass] then
            return fields, pois
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