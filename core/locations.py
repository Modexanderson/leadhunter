"""
Global Locations Database
Every major city and region worldwide, organized by continent and country
"""

LOCATIONS = {
    "🌍 Africa": {
        "🇳🇬 Nigeria": [
            "Lagos, Nigeria", "Abuja, Nigeria", "Port Harcourt, Nigeria",
            "Kano, Nigeria", "Ibadan, Nigeria", "Benin City, Nigeria",
            "Enugu, Nigeria", "Kaduna, Nigeria", "Jos, Nigeria", "Warri, Nigeria",
        ],
        "🇿🇦 South Africa": [
            "Johannesburg, South Africa", "Cape Town, South Africa", "Durban, South Africa",
            "Pretoria, South Africa", "Port Elizabeth, South Africa", "Bloemfontein, South Africa",
            "Soweto, South Africa", "Sandton, South Africa", "East London, South Africa",
        ],
        "🇰🇪 Kenya": [
            "Nairobi, Kenya", "Mombasa, Kenya", "Kisumu, Kenya",
            "Nakuru, Kenya", "Eldoret, Kenya", "Thika, Kenya",
        ],
        "🇬🇭 Ghana": [
            "Accra, Ghana", "Kumasi, Ghana", "Tamale, Ghana",
            "Sekondi-Takoradi, Ghana", "Cape Coast, Ghana",
        ],
        "🇪🇬 Egypt": [
            "Cairo, Egypt", "Alexandria, Egypt", "Giza, Egypt",
            "Shubra El Kheima, Egypt", "Luxor, Egypt", "Aswan, Egypt",
        ],
        "🇲🇦 Morocco": [
            "Casablanca, Morocco", "Rabat, Morocco", "Fes, Morocco",
            "Marrakech, Morocco", "Tangier, Morocco", "Agadir, Morocco",
        ],
        "🇪🇹 Ethiopia": [
            "Addis Ababa, Ethiopia", "Dire Dawa, Ethiopia", "Mekelle, Ethiopia",
        ],
        "🇹🇿 Tanzania": [
            "Dar es Salaam, Tanzania", "Mwanza, Tanzania", "Arusha, Tanzania",
        ],
        "🇺🇬 Uganda": [
            "Kampala, Uganda", "Gulu, Uganda", "Lira, Uganda",
        ],
        "🇸🇳 Senegal": [
            "Dakar, Senegal", "Touba, Senegal", "Thies, Senegal",
        ],
        "🇨🇮 Ivory Coast": [
            "Abidjan, Ivory Coast", "Bouake, Ivory Coast", "Yamoussoukro, Ivory Coast",
        ],
        "🇨🇲 Cameroon": [
            "Douala, Cameroon", "Yaounde, Cameroon", "Bamenda, Cameroon",
        ],
        "🇿🇲 Zambia": [
            "Lusaka, Zambia", "Kitwe, Zambia", "Ndola, Zambia",
        ],
        "🇿🇼 Zimbabwe": [
            "Harare, Zimbabwe", "Bulawayo, Zimbabwe", "Mutare, Zimbabwe",
        ],
        "🇷🇼 Rwanda": [
            "Kigali, Rwanda", "Butare, Rwanda",
        ],
        "🇹🇳 Tunisia": [
            "Tunis, Tunisia", "Sfax, Tunisia", "Sousse, Tunisia",
        ],
        "🇦🇴 Angola": [
            "Luanda, Angola", "Huambo, Angola", "Lobito, Angola",
        ],
        "🇲🇿 Mozambique": [
            "Maputo, Mozambique", "Beira, Mozambique", "Nampula, Mozambique",
        ],
    },

    "🌎 North America": {
        "🇺🇸 United States - Northeast": [
            "New York, NY", "Boston, MA", "Philadelphia, PA",
            "Washington DC", "Baltimore, MD", "Newark, NJ",
            "Providence, RI", "Hartford, CT", "Albany, NY", "Buffalo, NY",
            "Pittsburgh, PA", "Richmond, VA", "Norfolk, VA",
        ],
        "🇺🇸 United States - South": [
            "Houston, TX", "Dallas, TX", "San Antonio, TX", "Austin, TX",
            "Fort Worth, TX", "El Paso, TX", "Atlanta, GA", "Miami, FL",
            "Tampa, FL", "Orlando, FL", "Jacksonville, FL", "Charlotte, NC",
            "Raleigh, NC", "Nashville, TN", "Memphis, TN", "Louisville, KY",
            "New Orleans, LA", "Oklahoma City, OK", "Tulsa, OK",
            "Birmingham, AL", "Little Rock, AR",
        ],
        "🇺🇸 United States - Midwest": [
            "Chicago, IL", "Indianapolis, IN", "Columbus, OH", "Detroit, MI",
            "Milwaukee, WI", "Minneapolis, MN", "Kansas City, MO",
            "St. Louis, MO", "Omaha, NE", "Cleveland, OH", "Cincinnati, OH",
            "Grand Rapids, MI", "Madison, WI", "Des Moines, IA",
        ],
        "🇺🇸 United States - West": [
            "Los Angeles, CA", "San Diego, CA", "San Francisco, CA",
            "San Jose, CA", "Seattle, WA", "Portland, OR", "Denver, CO",
            "Las Vegas, NV", "Phoenix, AZ", "Tucson, AZ", "Sacramento, CA",
            "Fresno, CA", "Long Beach, CA", "Oakland, CA", "Bakersfield, CA",
            "Albuquerque, NM", "Salt Lake City, UT", "Boise, ID",
            "Spokane, WA", "Tacoma, WA",
        ],
        "🇨🇦 Canada": [
            "Toronto, Canada", "Vancouver, Canada", "Montreal, Canada",
            "Calgary, Canada", "Edmonton, Canada", "Ottawa, Canada",
            "Winnipeg, Canada", "Quebec City, Canada", "Hamilton, Canada",
            "Kitchener, Canada", "London, Canada", "Halifax, Canada",
            "Victoria, Canada", "Saskatoon, Canada", "Regina, Canada",
        ],
        "🇲🇽 Mexico": [
            "Mexico City, Mexico", "Guadalajara, Mexico", "Monterrey, Mexico",
            "Puebla, Mexico", "Tijuana, Mexico", "Leon, Mexico",
            "Ciudad Juarez, Mexico", "Torreon, Mexico", "Cancun, Mexico",
            "Merida, Mexico", "Queretaro, Mexico", "San Luis Potosi, Mexico",
        ],
    },

    "🌎 South America": {
        "🇧🇷 Brazil": [
            "São Paulo, Brazil", "Rio de Janeiro, Brazil", "Brasilia, Brazil",
            "Salvador, Brazil", "Fortaleza, Brazil", "Belo Horizonte, Brazil",
            "Manaus, Brazil", "Curitiba, Brazil", "Recife, Brazil",
            "Porto Alegre, Brazil", "Goiania, Brazil", "Belem, Brazil",
        ],
        "🇦🇷 Argentina": [
            "Buenos Aires, Argentina", "Cordoba, Argentina", "Rosario, Argentina",
            "Mendoza, Argentina", "La Plata, Argentina", "Tucuman, Argentina",
        ],
        "🇨🇱 Chile": [
            "Santiago, Chile", "Valparaiso, Chile", "Concepcion, Chile",
            "Antofagasta, Chile", "Vina del Mar, Chile",
        ],
        "🇨🇴 Colombia": [
            "Bogota, Colombia", "Medellin, Colombia", "Cali, Colombia",
            "Barranquilla, Colombia", "Cartagena, Colombia", "Bucaramanga, Colombia",
        ],
        "🇵🇪 Peru": [
            "Lima, Peru", "Arequipa, Peru", "Trujillo, Peru",
            "Chiclayo, Peru", "Piura, Peru",
        ],
        "🇻🇪 Venezuela": [
            "Caracas, Venezuela", "Maracaibo, Venezuela", "Valencia, Venezuela",
        ],
        "🇪🇨 Ecuador": [
            "Quito, Ecuador", "Guayaquil, Ecuador", "Cuenca, Ecuador",
        ],
        "🇧🇴 Bolivia": [
            "La Paz, Bolivia", "Santa Cruz, Bolivia", "Cochabamba, Bolivia",
        ],
        "🇵🇾 Paraguay": [
            "Asuncion, Paraguay", "Ciudad del Este, Paraguay",
        ],
        "🇺🇾 Uruguay": [
            "Montevideo, Uruguay", "Salto, Uruguay",
        ],
    },

    "🌍 Europe": {
        "🇬🇧 United Kingdom": [
            "London, UK", "Manchester, UK", "Birmingham, UK", "Leeds, UK",
            "Glasgow, UK", "Liverpool, UK", "Bristol, UK", "Sheffield, UK",
            "Edinburgh, UK", "Leicester, UK", "Coventry, UK", "Bradford, UK",
            "Cardiff, UK", "Nottingham, UK", "Newcastle, UK", "Belfast, UK",
            "Southampton, UK", "Portsmouth, UK", "Oxford, UK", "Cambridge, UK",
        ],
        "🇩🇪 Germany": [
            "Berlin, Germany", "Hamburg, Germany", "Munich, Germany",
            "Cologne, Germany", "Frankfurt, Germany", "Stuttgart, Germany",
            "Dusseldorf, Germany", "Dortmund, Germany", "Essen, Germany",
            "Leipzig, Germany", "Bremen, Germany", "Dresden, Germany",
            "Hanover, Germany", "Nuremberg, Germany", "Duisburg, Germany",
        ],
        "🇫🇷 France": [
            "Paris, France", "Marseille, France", "Lyon, France",
            "Toulouse, France", "Nice, France", "Nantes, France",
            "Strasbourg, France", "Montpellier, France", "Bordeaux, France",
            "Lille, France", "Rennes, France", "Reims, France",
        ],
        "🇮🇹 Italy": [
            "Rome, Italy", "Milan, Italy", "Naples, Italy", "Turin, Italy",
            "Palermo, Italy", "Genoa, Italy", "Bologna, Italy", "Florence, Italy",
            "Bari, Italy", "Venice, Italy", "Verona, Italy",
        ],
        "🇪🇸 Spain": [
            "Madrid, Spain", "Barcelona, Spain", "Valencia, Spain",
            "Seville, Spain", "Zaragoza, Spain", "Malaga, Spain",
            "Murcia, Spain", "Palma, Spain", "Bilbao, Spain", "Alicante, Spain",
        ],
        "🇳🇱 Netherlands": [
            "Amsterdam, Netherlands", "Rotterdam, Netherlands", "The Hague, Netherlands",
            "Utrecht, Netherlands", "Eindhoven, Netherlands",
        ],
        "🇧🇪 Belgium": [
            "Brussels, Belgium", "Antwerp, Belgium", "Ghent, Belgium",
            "Bruges, Belgium", "Liege, Belgium",
        ],
        "🇨🇭 Switzerland": [
            "Zurich, Switzerland", "Geneva, Switzerland", "Basel, Switzerland",
            "Bern, Switzerland", "Lausanne, Switzerland",
        ],
        "🇦🇹 Austria": [
            "Vienna, Austria", "Graz, Austria", "Linz, Austria", "Salzburg, Austria",
        ],
        "🇵🇹 Portugal": [
            "Lisbon, Portugal", "Porto, Portugal", "Braga, Portugal",
            "Amadora, Portugal", "Funchal, Portugal",
        ],
        "🇸🇪 Sweden": [
            "Stockholm, Sweden", "Gothenburg, Sweden", "Malmo, Sweden",
            "Uppsala, Sweden", "Vasteras, Sweden",
        ],
        "🇳🇴 Norway": [
            "Oslo, Norway", "Bergen, Norway", "Trondheim, Norway", "Stavanger, Norway",
        ],
        "🇩🇰 Denmark": [
            "Copenhagen, Denmark", "Aarhus, Denmark", "Odense, Denmark",
        ],
        "🇫🇮 Finland": [
            "Helsinki, Finland", "Espoo, Finland", "Tampere, Finland", "Turku, Finland",
        ],
        "🇵🇱 Poland": [
            "Warsaw, Poland", "Krakow, Poland", "Lodz, Poland", "Wroclaw, Poland",
            "Poznan, Poland", "Gdansk, Poland", "Katowice, Poland",
        ],
        "🇨🇿 Czech Republic": [
            "Prague, Czech Republic", "Brno, Czech Republic", "Ostrava, Czech Republic",
        ],
        "🇭🇺 Hungary": [
            "Budapest, Hungary", "Debrecen, Hungary", "Miskolc, Hungary",
        ],
        "🇷🇴 Romania": [
            "Bucharest, Romania", "Cluj-Napoca, Romania", "Timisoara, Romania",
            "Iasi, Romania", "Constanta, Romania",
        ],
        "🇬🇷 Greece": [
            "Athens, Greece", "Thessaloniki, Greece", "Patras, Greece",
        ],
        "🇮🇪 Ireland": [
            "Dublin, Ireland", "Cork, Ireland", "Limerick, Ireland", "Galway, Ireland",
        ],
        "🇷🇺 Russia": [
            "Moscow, Russia", "Saint Petersburg, Russia", "Novosibirsk, Russia",
            "Yekaterinburg, Russia", "Kazan, Russia", "Chelyabinsk, Russia",
        ],
        "🇺🇦 Ukraine": [
            "Kyiv, Ukraine", "Kharkiv, Ukraine", "Odessa, Ukraine", "Dnipro, Ukraine",
        ],
    },

    "🌏 Asia": {
        "🇮🇳 India": [
            "Mumbai, India", "Delhi, India", "Bangalore, India", "Hyderabad, India",
            "Ahmedabad, India", "Chennai, India", "Kolkata, India", "Surat, India",
            "Pune, India", "Jaipur, India", "Lucknow, India", "Kanpur, India",
            "Nagpur, India", "Indore, India", "Thane, India", "Bhopal, India",
            "Visakhapatnam, India", "Pimpri, India", "Patna, India", "Vadodara, India",
        ],
        "🇨🇳 China": [
            "Shanghai, China", "Beijing, China", "Guangzhou, China", "Shenzhen, China",
            "Chengdu, China", "Chongqing, China", "Tianjin, China", "Wuhan, China",
            "Xian, China", "Hangzhou, China", "Nanjing, China", "Suzhou, China",
        ],
        "🇯🇵 Japan": [
            "Tokyo, Japan", "Osaka, Japan", "Yokohama, Japan", "Nagoya, Japan",
            "Sapporo, Japan", "Fukuoka, Japan", "Kyoto, Japan", "Kobe, Japan",
            "Kawasaki, Japan", "Hiroshima, Japan",
        ],
        "🇰🇷 South Korea": [
            "Seoul, South Korea", "Busan, South Korea", "Incheon, South Korea",
            "Daegu, South Korea", "Daejeon, South Korea", "Gwangju, South Korea",
        ],
        "🇸🇬 Singapore": [
            "Singapore", "Jurong, Singapore", "Tampines, Singapore",
        ],
        "🇲🇾 Malaysia": [
            "Kuala Lumpur, Malaysia", "George Town, Malaysia", "Ipoh, Malaysia",
            "Shah Alam, Malaysia", "Johor Bahru, Malaysia", "Kota Kinabalu, Malaysia",
        ],
        "🇮🇩 Indonesia": [
            "Jakarta, Indonesia", "Surabaya, Indonesia", "Bandung, Indonesia",
            "Medan, Indonesia", "Bekasi, Indonesia", "Tangerang, Indonesia",
            "Semarang, Indonesia", "Makassar, Indonesia", "Yogyakarta, Indonesia",
        ],
        "🇵🇭 Philippines": [
            "Manila, Philippines", "Quezon City, Philippines", "Davao, Philippines",
            "Caloocan, Philippines", "Cebu City, Philippines", "Zamboanga, Philippines",
        ],
        "🇹🇭 Thailand": [
            "Bangkok, Thailand", "Chiang Mai, Thailand", "Pattaya, Thailand",
            "Hat Yai, Thailand", "Nonthaburi, Thailand",
        ],
        "🇻🇳 Vietnam": [
            "Ho Chi Minh City, Vietnam", "Hanoi, Vietnam", "Da Nang, Vietnam",
            "Hai Phong, Vietnam", "Can Tho, Vietnam",
        ],
        "🇵🇰 Pakistan": [
            "Karachi, Pakistan", "Lahore, Pakistan", "Faisalabad, Pakistan",
            "Rawalpindi, Pakistan", "Islamabad, Pakistan", "Multan, Pakistan",
        ],
        "🇧🇩 Bangladesh": [
            "Dhaka, Bangladesh", "Chittagong, Bangladesh", "Sylhet, Bangladesh",
        ],
        "🇱🇰 Sri Lanka": [
            "Colombo, Sri Lanka", "Kandy, Sri Lanka", "Galle, Sri Lanka",
        ],
        "🇳🇵 Nepal": [
            "Kathmandu, Nepal", "Pokhara, Nepal", "Lalitpur, Nepal",
        ],
        "🇦🇪 UAE": [
            "Dubai, UAE", "Abu Dhabi, UAE", "Sharjah, UAE",
            "Al Ain, UAE", "Ajman, UAE",
        ],
        "🇸🇦 Saudi Arabia": [
            "Riyadh, Saudi Arabia", "Jeddah, Saudi Arabia", "Mecca, Saudi Arabia",
            "Medina, Saudi Arabia", "Dammam, Saudi Arabia",
        ],
        "🇮🇱 Israel": [
            "Tel Aviv, Israel", "Jerusalem, Israel", "Haifa, Israel",
        ],
        "🇹🇷 Turkey": [
            "Istanbul, Turkey", "Ankara, Turkey", "Izmir, Turkey",
            "Bursa, Turkey", "Adana, Turkey", "Antalya, Turkey",
        ],
        "🇮🇷 Iran": [
            "Tehran, Iran", "Mashhad, Iran", "Isfahan, Iran",
            "Karaj, Iran", "Tabriz, Iran", "Shiraz, Iran",
        ],
        "🇶🇦 Qatar": [
            "Doha, Qatar", "Al Rayyan, Qatar",
        ],
        "🇰🇼 Kuwait": [
            "Kuwait City, Kuwait", "Hawalli, Kuwait",
        ],
        "🇧🇭 Bahrain": [
            "Manama, Bahrain",
        ],
        "🇴🇲 Oman": [
            "Muscat, Oman", "Salalah, Oman",
        ],
        "🇯🇴 Jordan": [
            "Amman, Jordan", "Zarqa, Jordan", "Irbid, Jordan",
        ],
        "🇱🇧 Lebanon": [
            "Beirut, Lebanon", "Tripoli, Lebanon",
        ],
    },

    "🌏 Oceania": {
        "🇦🇺 Australia": [
            "Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia",
            "Perth, Australia", "Adelaide, Australia", "Gold Coast, Australia",
            "Newcastle, Australia", "Canberra, Australia", "Sunshine Coast, Australia",
            "Wollongong, Australia", "Hobart, Australia", "Geelong, Australia",
            "Townsville, Australia", "Cairns, Australia", "Darwin, Australia",
        ],
        "🇳🇿 New Zealand": [
            "Auckland, New Zealand", "Wellington, New Zealand", "Christchurch, New Zealand",
            "Hamilton, New Zealand", "Dunedin, New Zealand", "Tauranga, New Zealand",
        ],
        "🇵🇬 Papua New Guinea": [
            "Port Moresby, Papua New Guinea",
        ],
        "🇫🇯 Fiji": [
            "Suva, Fiji", "Nadi, Fiji",
        ],
    },

    "🌍 Middle East & Central Asia": {
        "🇦🇫 Afghanistan": [
            "Kabul, Afghanistan", "Kandahar, Afghanistan",
        ],
        "🇰🇿 Kazakhstan": [
            "Almaty, Kazakhstan", "Nur-Sultan, Kazakhstan", "Shymkent, Kazakhstan",
        ],
        "🇺🇿 Uzbekistan": [
            "Tashkent, Uzbekistan", "Samarkand, Uzbekistan",
        ],
        "🇦🇿 Azerbaijan": [
            "Baku, Azerbaijan",
        ],
        "🇬🇪 Georgia": [
            "Tbilisi, Georgia", "Batumi, Georgia",
        ],
        "🇦🇲 Armenia": [
            "Yerevan, Armenia",
        ],
    },

    "🌎 Caribbean & Central America": {
        "🇨🇺 Cuba": [
            "Havana, Cuba", "Santiago de Cuba, Cuba",
        ],
        "🇩🇴 Dominican Republic": [
            "Santo Domingo, Dominican Republic", "Santiago, Dominican Republic",
        ],
        "🇯🇲 Jamaica": [
            "Kingston, Jamaica", "Montego Bay, Jamaica",
        ],
        "🇹🇹 Trinidad and Tobago": [
            "Port of Spain, Trinidad and Tobago",
        ],
        "🇬🇹 Guatemala": [
            "Guatemala City, Guatemala",
        ],
        "🇸🇻 El Salvador": [
            "San Salvador, El Salvador",
        ],
        "🇭🇳 Honduras": [
            "Tegucigalpa, Honduras", "San Pedro Sula, Honduras",
        ],
        "🇨🇷 Costa Rica": [
            "San Jose, Costa Rica", "Alajuela, Costa Rica",
        ],
        "🇵🇦 Panama": [
            "Panama City, Panama",
        ],
    },
}


def get_all_cities() -> list[str]:
    """Returns every city in the database"""
    cities = []
    for continent, countries in LOCATIONS.items():
        for country, city_list in countries.items():
            cities.extend(city_list)
    return cities


def get_continent_cities(continent: str) -> list[str]:
    cities = []
    for country, city_list in LOCATIONS.get(continent, {}).items():
        cities.extend(city_list)
    return cities


def get_country_cities(country_key: str) -> list[str]:
    for continent, countries in LOCATIONS.items():
        for country, city_list in countries.items():
            if country_key.lower() in country.lower():
                return city_list
    return []


def search_cities(query: str) -> list[str]:
    """Search cities/countries by name"""
    query = query.lower()
    results = []
    for continent, countries in LOCATIONS.items():
        for country, city_list in countries.items():
            if query in country.lower():
                results.extend(city_list)
            else:
                results.extend([c for c in city_list if query in c.lower()])
    return results


def get_stats() -> dict:
    total_cities = 0
    total_countries = 0
    for continent, countries in LOCATIONS.items():
        total_countries += len(countries)
        for country, cities in countries.items():
            total_cities += len(cities)
    return {
        "continents": len(LOCATIONS),
        "countries": total_countries,
        "cities": total_cities
    }
