import random
from geopy import distance

from db import cursor
# get all airports from the database that we're going to use for the game
def get_airports():
    ch = input("Haluatko pelata Euroopassa vai maailmanlaajuisesti? (eu/mm): ").lower().strip(" ")

    sql = "SELECT iso_country, ident, name, type, latitude_deg, longitude_deg FROM airport"

    if ch == "eu":
        sql += " WHERE continent = 'EU' AND type in ('large_airport')"
    elif ch == "mm":
        sql += " WHERE type in ('large_airport')"
    else:
        print("Virheellinen syöte.")
        get_airports()

    sql += " ORDER by RAND() LIMIT 30;"
    global cursor
    cursor.execute(sql)
    return cursor.fetchall()

# get the information of an airport based on its ICAO code
def get_airport_info(icao):
    sql = f"SELECT iso_country, ident, name, type, latitude_deg, longitude_deg FROM airport WHERE ident = '{icao}'"
    global cursor
    cursor.execute(sql)
    return cursor.fetchone()

# create the lootboxes for the airports
#
def create_lootbox(airport):
    #TODO!
    pass

# save the current values of the game into the database as a new game
def create_game(name):
    global cursor


    #Decide default money and range amounts here!
    money = 1000
    player_range = 1500

    original_airports = get_airports()

    starting_airport = random.choice(original_airports)

    #insert basic details into the game table
    sql = f"INSERT INTO game (money,location,starting_airport,screen_name,player_range) VALUES ({money}, '{starting_airport[1]}','{starting_airport[1]}', '{name}', {player_range})"
    cursor.execute(sql)
    game_id = cursor.lastrowid

    #for loop handles creating the lootbox value for each airport that we are playing in.
    for airport in original_airports:
        #lootbox = create_lootbox(airport)
        lootbox = 0 # temp
        sql = f"INSERT INTO game_airports (game_id, airport_id, lootbox) VALUES ({game_id}, '{airport[1]}', {lootbox})"
        cursor.execute(sql)
    #return game id, and modified airports


    return game_id, money, player_range, starting_airport, original_airports

# get game details
def get_game(game_id):
    sql = f"SELECT * FROM game WHERE id = {game_id}"
    global cursor
    cursor.execute(sql)
    return cursor.fetchone()

# get distance between 2 given airports
def get_distance(airport1, airport2):
    airport1 = get_airport_info(airport1)
    airport2 = get_airport_info(airport2)
    #lat, long for both
    airport1_cords = (airport1[4], airport1[5])
    airport2_cords = (airport2[4], airport2[5])
    return distance.distance(airport1_cords, airport2_cords).km

# self-explanatory
def update_game(game_id, location, money, range):
    sql = f"UPDATE game SET money = {money}, location = '{location}', player_range = {range} WHERE id = {game_id}"
    global cursor
    cursor.execute(sql)


def fly(nykyinen, icao_code):
    global cursor
    #check if real airport and that it's in the current game
    if icao_code not in [airport[1] for airport in airports]:
        return None

    dist = get_distance(nykyinen, icao_code)
    # check if we can fly there
    if player_range>dist>1:
        update_game(game, icao_code, money, player_range - dist)
        return get_airport_info(icao_code)
    else:
        return False

# get all airports that are within the range of the current airport
def accessible_airports(airport, p_range):
    lista = []
    for kentta in airports:
        matka = get_distance(airport, kentta[1])
        if p_range >= matka > 1:
            lista.append(f"{kentta[2]} (ICAO: {kentta[1]}) | Matka: {matka:.2f} km")
    return lista

# tries to continue a previous game
def continue_game():
    #TODO!
    pass

#check if they have a previous game they want to continue and figure iut out
#question = input("Haluatko jatkaa aiempaa gameä? (k/e)")
question = False
if question:
    #continue_game()
    #TODO!
    quit()
else:
    name = input("Pelaajan nimi: ")

    game, money, player_range, current_airport, airports = create_game(name)
while True:
    # game_over(game_id)
    # game_over handles checking if game is over and what to do in that case.
    #
    print(f"***\nNykyinen lentokenttä: {current_airport[2]} ({current_airport[1]})\n")
    print(f"Rahaa jäljellä: {money} €\n")
    print(f"Jäljellä oleva lentomatka: {player_range} km\n")
    line = """Vaihtoehdot
    0. Lopeta peli
    1. Tankkaa
    2. Lähde matkalle"""

    lootbox_sql = f"SELECT lootbox from game_airports WHERE game_id = {game} AND airport_id = '{current_airport[1]}'"

    cursor.execute(lootbox_sql)
    # get lootbox
    lootbox_sisalto = cursor.fetchone()[0]
    if lootbox_sisalto != 7:
        line +="\n    3. Avaa lootbox"
    print(line)

    try:
        tehtava = int(input("\nMitä tehdään: \n"))
    except ValueError:
        print("Syötä numero.")
        continue
    if tehtava == 0:
        update_game(game, current_airport[1], money, player_range)
        print("Nähdään!")
        quit()
    elif tehtava == 1:
        maara = int(input("Paljonko rahaa haluat käyttää? (1 euro = 2 kilometriä.) "))
        if money >= maara > 0:
            player_range += maara * 2
            money -= maara
            update_game(game, current_airport[1], money, player_range)
            print("Tankkaus onnistui")
        else:
            if maara < 0:
                print("Et voi tankata negatiivista määrää.")
            elif maara > money:
                print("Sinulla ei ole tarpeeksi rahaa.")
            elif maara == 0:
                print("Et voi tankata 0 euroa.")
            else:
                print("Virheellinen syöte.")
            continue
    elif tehtava == 2:
        #passing in current airports ICAO-code and the range of the player
        usable_airports = accessible_airports(current_airport[1], player_range)


        for destination in usable_airports:
            print(destination)
        if len(usable_airports) == 0:
            print("Ei ole mahdollista lentää mihinkään. Tankkaa lisää.")
            continue
        print("Lentokenttä vaihtoehdot:")
        koodi = input("Mihin lennetään (ICAO-koodi): ")

        fly_result = fly(current_airport[1], koodi)
        if fly_result is None:
            print("Lentokenttää ei löydy.")
        elif fly_result is False:
            print("Emme voi lentää sinne.")
        else:
            current_airport = fly_result
            print("Lento onnistui!")
    elif tehtava == 3:
        #TODO!
        # lootbox
        pass
    else:
        print("Virheellinen syöte.")
        continue
    game_info = get_game(game)
    money = game_info[1]
    current_airport = get_airport_info(game_info[2])
    player_range = game_info[5]


"""
TODO!
lootboxien generointi
lootboxien avaaminen ja niiden sisältöön reagoiminen
win/loss tarkistus
pelin tallennus, jatko ja kirjautuminen

"""