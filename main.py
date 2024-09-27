import random
from geopy import distance

from db import cursor

def get_airports():
    sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
FROM airport
WHERE continent = 'EU' 
AND type in ('small_airport')
ORDER by RAND()
LIMIT 30;"""
    global cursor
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def get_airport_info(icao):
    sql = f"SELECT iso_country, ident, name, type, latitude_deg, longitude_deg FROM airport WHERE ident = '{icao}'"
    global cursor
    cursor.execute(sql)
    return cursor.fetchone()


def create_game(name, location, money, range, airports):
    sql = f"INSERT INTO game (money,location,starting_airport,screen_name,player_range) VALUES ({money}, '{location[1]}','{location[1]}', '{name}', {range})"
    global cursor
    cursor.execute(sql)
    game_id = cursor.lastrowid
    for airport in airports:
        # numero value of what the fuck lootbox sisältää
        #lootbox = create_lootbox(airport)
        lootbox = 0
        sql = f"INSERT INTO game_airports (game_id, airport_id, lootbox) VALUES ({game_id}, '{airport[1]}', {lootbox})"
        cursor.execute(sql)

    return game_id, airports


def get_game(game_id):
    sql = f"SELECT * FROM game WHERE id = {game_id}"
    global cursor
    cursor.execute(sql)
    return cursor.fetchone()

def get_distance(game, airport):
    cur_cords = get_airport_info(game[1])
    new_cords = get_airport_info(airport)
    #lat, long for both
    coords1 = (cur_cords[4], cur_cords[5])
    coords2 = (new_cords[4], new_cords[5])
    return distance.distance(coords1, coords2).km

def update_game(game_id, location, money, range):
    sql = f"UPDATE game SET money = {money}, location = '{location}', player_range = {range} WHERE id = {game_id}"
    global cursor
    cursor.execute(sql)


def fly(nykyinen, icao_code):
    global cursor

    if icao_code not in [airport[1] for airport in airports]:
        return False

    dist = get_distance(nykyinen, icao_code)
    if player_range>dist>1:
        update_game(game, icao_code, money, player_range - dist)
        return get_airport_info(icao_code)

def accessible_airports(nykyinen, p_range):
    lista = []
    for kentta in airports:
        matka = get_distance(nykyinen, kentta[1])
        if p_range >= matka > 1:
            lista.append(f"{kentta[2]} (ICAO: {kentta[1]}) | Matka: {matka:.2f} km")
    return lista


def create_lootbox():
    pass
def continue_game():
    pass

original_airports = get_airports()

#check if they have a previous game they want to continue and figure iut out
#a = input("Haluatko jatkaa aiempaa gameä? (k/e)")
a = False
if a:
    #continue_game()
    quit()
else:
    name = input("Pelaajan nimi: ")
    current_airport = random.choice(original_airports)
    money = 1000
    player_range = 1500

    game, airports = create_game(name, current_airport, money, player_range, original_airports)
while True:
    # game_over(game_id)
    # game_over handles checking if game is over and what to do in that case.
    #
    print(f"***\nNykyinen lentokenttä: {current_airport[2]}\n")
    print(f"Rahaa jäljellä: {money} €\n")
    print(f"Jäljellä oleva lentomatka: {player_range} km\n")
    line = """Vaihtoehdot
    (0 lopettaa pelin)
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
        tehtava = int(input("\nMitä tehdään: "))
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
        # testataan että voinko tehdä tämän logiikan FLY funktiossa
        usable_airports = accessible_airports(current_airport, player_range)
        # tarkistetaan uudelleen että onko mahdollista lentää mihinkään
        # emme tarkista rahan määrää joten tarkistamme uudelleen jos jokin on muuttunut
        for destination in usable_airports:
            print(destination)
        if len(usable_airports) == 0:
            print("Ei ole mahdollista lentää mihinkään. Tankkaa lisää.")
            continue
        print("Lentokenttä vaihtoehdot:")
        koodi = input("Mihin lennetään (ICAO-koodi): ")

        fly_result = fly(current_airport, koodi)
        if not fly_result:
            # tallennetaan nykyinen sijainti
            print("Lentokenttää ei löydy, tai emme voi lentää sinne.")
        else:
            current_airport = fly_result
    elif tehtava == 3:
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
PAVEL TO DO:
lootboxien generointi
lootboxien avaaminen ja niiden sisältöön reagoiminen
win/loss tarkistus
pelin tallennus, jatko ja kirjautuminen

"""