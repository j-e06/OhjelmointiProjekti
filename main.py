import random

from geopy import distance

from db import cursor
# get all airports from the database that we're going to use for the game
def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
    FROM airport
    WHERE continent = 'EU' 
    AND type='large_airport'
    ORDER by RAND()
    LIMIT 30;"""
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
def create_game(name, password=None):
    global cursor

    #Decide default money and range amounts here!
    money = 1000
    player_range = 2500
    #set diamond to 0 so we can easily see later if we've won or not
    diamond = 0
    original_airports = get_airports()
    random.shuffle(original_airports)

    starting_airport = random.choice(original_airports)

    #insert basic details into the game table
    if password is not None:
        sql = f"INSERT INTO game (money,location,starting_airport,screen_name,player_range,password) VALUES ({money}, '{starting_airport[1]}','{starting_airport[1]}', '{name}', {player_range}, '{password}')"
    else:
        sql = f"INSERT INTO game (money,location,starting_airport,screen_name,player_range) VALUES ({money}, '{starting_airport[1]}','{starting_airport[1]}', '{name}', {player_range})"
    cursor.execute(sql)
    game_id = cursor.lastrowid

    #for loop handles creating the lootbox value for each airport that we are playing in.

    create_lootboxes(game_id,original_airports)

    #return game id, and modified airports

    return game_id, money, diamond, player_range, starting_airport, original_airports

# create the lootboxes for the airports

def create_lootboxes(game_id, original_airports):
    loot = {
        1: 15,
        2: 2,
        3: 3,
        4: 4,
        5: 1,
        6: 5
    }

    x = [1,2,3,4,5,6]
    for airport in original_airports:
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
    print(lootboxid, "debug")
    if lootboxid == 1:
        result = 0
    elif lootboxid == 2:
        result = 1000
    elif lootboxid == 3:
        result = 600
    elif lootboxid == 4:
        result = 300
    elif lootboxid == 5:
        result = 1
    elif lootboxid == 6:
        result = -1
    else:
        result = 7
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
def update_game(game_id, location, money, range, diamond=0):
    sql = f"UPDATE game SET money = {money}, location = '{location}', player_range = {range}, timantti = {diamond} WHERE id = {game_id}"
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
        print("Onneksi olkoon! Löysit timantin ja olet takaisin aloitus lentokentälläsi. Tässä on 🍪 palkkioksi!")
    elif accessible_airports(current_airport[1], player_range+money*2) == []:
        print("Peli päättyi, koska sinulla ei ole enää rahaa tai bensaa. Parempi onni ensi kerralla!")
    else:
        return False
    sql = f"DELETE from game_airports WHERE game_id = {game_id}"
    cursor.execute(sql)
    sql = f"DELETE from game WHERE id = {game_id}"
    cursor.execute(sql)
    return True

# tries to continue a previous game
def continue_game():
    print("0 lopettaa.")

    while True:
        nimi = input("Anna nimi: ")
        salasana = input("Anna salasana: ")
        if nimi == "0" or salasana == "0":
            quit()
        sql = f"SELECT id, money, location, starting_airport, screen_name, player_range, timantti FROM game WHERE screen_name = '{nimi}' and password = '{salasana}'"
        cursor.execute(sql)
        tulos = cursor.fetchone()
        if tulos is None or len(tulos) == []:
            print("Väärä nimi tai salasana.")
            continue
        else:
            airport_sql = f"SELECT iso_country, ident, name, type, latitude_deg, longitude_deg FROM airport WHERE ident IN (SELECT airport_id FROM game_airports WHERE game_id = {tulos[0]}) and continent = 'EU' and type = 'large_airport'"
            cursor.execute(airport_sql)
            airports = cursor.fetchall()
            original_airports = []
            for airport in airports:
                original_airports.append(airport)
            return tulos[0], tulos[1], tulos[6], tulos[5], get_airport_info(tulos[2]), original_airports, get_airport_info(tulos[3])
    #game, money, diamond, player_range, current_airport, airports, original_airport
#check if they have a previous game they want to continue and figure iut out

question = input("Haluatko jatkaa aiempaa gameä? (k/e)\n").lower()
if question == "k":
    game, money, diamond, player_range, current_airport, airports, original_airport = continue_game()
elif question == "e":
    salasana = None
    print("0 lopettaa.")
    while True:
        tallennus = input("Haluatko tallentaa pelin? (k/e)").lower()
        if tallennus == "0": quit()

        name = input("Pelaajan nimi: ")

        if name == "0": quit()

        if len(name) > 0 and len(name) < 20:
            pass
        else:
            print("Nimen pituus 1-20.")
            continue
        if tallennus == "k":
            salasana = input("Keksi salasana:")
            if salasana == "0": quit()
            break
        elif tallennus == "e":
            break
        else:
            print("Virheellinen tulos.")
    game, money, diamond, player_range, current_airport, airports = create_game(name, salasana)
    original_airport = current_airport
else:
    print("Vain k/e hyväksytään.")
    quit()
while True:
    if game_over(game):
        break

    print(f"***\nAloituslentokenttä: {original_airport[2]} ({original_airport[1]})")
    print(f"***\nNykyinen lentokenttä: {current_airport[2]} ({current_airport[1]})\n")
    print(f"Rahaa jäljellä: {money} €\n")
    print(f"Jäljellä oleva lentomatka: {player_range} km\n")
    line = """Vaihtoehdot
    0. Lopeta peli
    1. Tankkaa
    2. Lähde matkalle"""

    sql = f"SELECT lootbox from game_airports WHERE airport_id = '{current_airport[1]}' AND game_id = '{game}'"
    cursor.execute(sql)
    temp = cursor.fetchone()[0]
    # get lootbox
    if temp != 7:
        line +="\n    3. Avaa lootbox"
    print(line)

    try:
        tehtava = int(input("\nMitä tehdään: \n"))
    except ValueError:
        print("Vain numeroita hyväksytään.")
        continue
    if tehtava == 0:
        #save game and end in case they want to continue in the future.
        update_game(game, current_airport[1], money, player_range)
        print("Nähdään!")
        quit()
    elif tehtava == 1:
        # ostaa lisää bensaa rahalla
        try:
            maara = int(input("Paljonko rahaa haluat käyttää? (1 euro = 2 bensaa.) "))
        except ValueError:
            print("Vain positiivisia numeroita hyväksytään.")
            continue
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
            print("Sinulla ei ole tarpeeksi bensaa, tankkaa lisää.")
            continue

        print("Mahdolliset lentokohteet:")

        for destination in usable_airports:
            print(destination)

        koodi = input("\nMihin lennetään (ICAO-koodi) (0 päästää ulos): ")
        if koodi == "0":
            continue
        fly_result = fly(current_airport[1], koodi)

        if fly_result is None:
            print("Lentokenttää ei löytynyt.")
        elif fly_result is False:
            print("Lentokenttä on liian kaukana.")
        else:
            current_airport = fly_result
            print("Lento onnistui!")

    elif tehtava == 3 and temp != 7:
        # lootbox
        valinta = input("Haluatko avata lootboxin maksamalla 50 euroa vai 125 bensaa? (M/B) (0 päästää ulos)").upper()
        if valinta == "M":
            if money < 50:
                print("Sinulla ei ole tarpeeksi rahaa.")
                continue
            else:
                money -= 50
        elif valinta == "B":
            if player_range < 125:
                print("Sinulla ei ole tarpeeksi bensaa.")
                continue
            else:
                player_range -= 125
        elif valinta == "0":
            #ei jatketa lootboxin avaamista
            continue
        else:
            print("Vain M/B/0 hyväksytään.")
            continue
        #result = handle_lootbox(game, current_airport[1])

        lootbox_sisalto = handle_lootbox(game, current_airport[1])

        if lootbox_sisalto == 1:
            print("Löysit timantin! Palaa aloituskentälle voittaaksesi pelin!")
            diamond = 1
        elif lootbox_sisalto == 0:
            print("Löysit maitoa! Mitään ei tapahtunut.")
        elif lootbox_sisalto > 1:
            money += lootbox_sisalto
            if lootbox_sisalto == 1000:
                print("Löysit rubiinin! Sait 1000 euroa!")
            elif lootbox_sisalto == 600:
                print("Löysit smaragdin! Sait 600 euroa!")
            elif lootbox_sisalto == 300:
                print("Löysit topaasin! Sait 300 euroa!")
        elif lootbox_sisalto < 0:
            money = 0
            print("Löysit rosvo, menetit kaikki rahasi!")
        update_game(game, current_airport[1], money, player_range, diamond)
    else:
        print("Virheellinen syöte.")
        continue

    print(diamond, "diamond")
    #update the game info
    game_info = get_game(game)
    money = game_info[1]
    current_airport = get_airport_info(game_info[2])
    player_range = game_info[5]
