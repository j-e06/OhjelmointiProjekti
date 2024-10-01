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
        # restarting the function if the input was invalid
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

# save the current values of the game into the database as a new game
def create_game(name):
    global cursor

    #Decide default money and range amounts here!
    money = 1000
    player_range = 1500
    #set diamond to 0 so we can easily see later if we've won or not
    diamond = 0
    original_airports = get_airports()
    random.shuffle(original_airports)

    starting_airport = random.choice(original_airports)

    #insert basic details into the game table
    sql = f"INSERT INTO game (money,location,starting_airport,screen_name,player_range) VALUES ({money}, '{starting_airport[1]}','{starting_airport[1]}', '{name}', {player_range})"
    cursor.execute(sql)
    game_id = cursor.lastrowid

    #for loop handles creating the lootbox value for each airport that we are playing in.

    create_lootboxes(game_id,original_airports)

    #return game id, and modified airports

    return game_id, money, diamond, player_range, starting_airport, original_airports

# create the lootboxes for the airports
#

"""

    sql = f"INSERT INTO game_airports (game_id, airport_id, lootbox) VALUES ({game_id}, '{modified_airport[1]}', {lootbox})"
    cursor.execute(sql)"""

def create_lootboxes(game_id, original_airports):
    loot = {
        1: 15,
        2: 2,
        3: 3,
        4: 4,
        5: 1,
        6: 5
    }

    for airport in original_airports:
        x = [1,2,3,4,5,6]
        while True:
            lootbox = random.choice(x)
            if loot[lootbox] > 0:
                sql = f"INSERT INTO game_airports (game_id, airport_id, lootbox) VALUES ({game_id}, '{airport[1]}', {lootbox})"
                cursor.execute(sql)
                loot[lootbox] -= 1
                break
            else:
                x.remove(lootbox)
def handle_lootbox(game_id, airport_id):
    sql = f"SELECT lootbox from game_airports WHERE airport_id = '{airport_id}' AND game_id = '{game_id}'"
    cursor.execute(sql)
    lootboxid = cursor.fetchone()[0]
    if lootboxid == 1:
        result = 0
    elif lootboxid == 2:
        result = 100
    elif lootboxid == 3:
        result = 200
    elif lootboxid == 4:
        result = 300
    elif lootboxid == 5:
        result = 1
    elif lootboxid == 6:
        result = -1
    else:
        result = None
    sql = f"UPDATE game_airports SET lootbox = 7 WHERE airport_id = '{airport_id}' AND game_id = '{game_id}'"
    cursor.execute(sql)
    return result

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

def game_over(game_id):
    if current_airport == original_airport and diamond == 1:
        return 0
    else:
        #continue
        return 2
    """
    elif len(accessible_airports(current_airport, player_range+money*2)) == 0:
        return 1
    its borken
    """


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

    game, money, diamond, player_range, current_airport, airports = create_game(name)
    original_airport = current_airport
while True:
    game_state = game_over(game)
    if game_state == 0:
        print("Voitit pelin!")
        break
    elif game_state == 1:
        print("Hävisit pelin!")
        break
    elif game_state == 2:
        pass
    else:
        print("miten vitussa pääsit tähän.")
    # game_over(game_id)
    # game_over handles checking if game is over and what to do in that case.
    print(f"***\nAloituslentokenttä: {original_airport[2]} ({original_airport[1]})")
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
    print(lootbox_sisalto)
    if lootbox_sisalto != 7:
        line +="\n    3. Avaa lootbox"
    print(line)

    try:
        tehtava = int(input("\nMitä tehdään: \n"))
    except ValueError:
        print("Syötä numero.")
        continue
    if tehtava == 0:
        #save game and end in case they want to continue in the future.
        update_game(game, current_airport[1], money, player_range)
        print("Nähdään!")
        quit()
    elif tehtava == 1:
        # ostaa lisää bensaa rahalla.
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
        #checking if we can fly
        #passing in current airports ICAO-code and the range of the player
        usable_airports = accessible_airports(current_airport[1], player_range)


        if len(usable_airports) == 0:
            print("Ei ole mahdollista lentää mihinkään. Tankkaa lisää.")
            continue

        print("Mahdolliset lentokohteet:")

        for destination in usable_airports:
            print(destination)

        print("Lentokenttä vaihtoehdot:")
        koodi = input("Mihin lennetään (ICAO-koodi) (0 päästää ulos): ")
        if koodi == "0":
            continue
        fly_result = fly(current_airport[1], koodi)

        if fly_result is None:
            print("Lentokenttää ei löydy.")
        elif fly_result is False:
            print("Emme voi lentää sinne.")
        else:
            current_airport = fly_result
            update_game(game, current_airport, money, player_range)
            print("Lento onnistui!")

    elif tehtava == 3:
        # lootbox
        valinta = input("Haluatko avata lootboxin rahalla tai bensalla (M/B) (0 päästää ulos)").upper()
        if valinta == "M":
            if money < 100:
                print("Ei ole tarpeeksi rahaa.")
                continue
            else:
                money -= 50
        elif valinta == "B":
            if player_range < 125:
                print("Ei ole tarpeeksi bensaa.")
                continue
            else:
                player_range -= 300
        elif valinta == "0":
            continue
        else:
            print("Virheellinen vastaus!")
        result = handle_lootbox(game, current_airport[1])
        if result == 1:
            print("Löysit timantin! Palaa aloituskentälle voittaaksesi pelin!")
            diamond = 1
        elif result == 0:
            print("Löysit maitoa!")
        elif result > 1:
            money += result
            print("Löysit jalokiven")
        elif result < 0:
            money = 0
            print("Rosvo löyti sinut.")
        update_game(game, current_airport[1], money, player_range)
    else:
        print("Virheellinen syöte.")
        continue

    #update the game info

    game_info = get_game(game)
    money = game_info[1]
    current_airport = get_airport_info(game_info[2])
    player_range = game_info[5]


"""
TODO!
loss tarkistus - pavel
pelin tallennus, jatko ja kirjautuminen - pavel

koodin paranteleminen, kommentointi ja siistiminen - me

updatee useemmin koska kekw - me

muokkaa update_game toimivaks
"""