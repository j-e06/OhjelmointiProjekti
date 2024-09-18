import random

from geopy import distance
from db import cursor

def get_airports():
        sql = """SELECT iso_country, ident, name, type, latitude_deg, longitude_deg
    FROM airport
    WHERE continent = 'EU' 
    AND type='large_airport'
    ORDER by RAND()
    LIMIT 30;"""
        global cursor
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

def get_goals():
    sql = "SELECT * FROM goal ORDER     BY RAND()"
    global cursor
    cursor.execute(sql)
    return cursor.fetchall()

def create_game(name, location, money, range):
    sql = f"INSERT INTO game (money,location,screen_name,player_range) VALUES ({money}, '{location[1]}', '{name}', {range})"
    global cursor
    cursor.execute(sql)
    return cursor.lastrowid

def get_game(game_id):
    sql = f"SELECT * FROM game WHERE id = {game_id}"
    global cursor
    cursor.execute(sql)
    return cursor.fetchone()

def get_airport_info(icao):
    sql = f"SELECT iso_country, ident, name, type, latitude_deg, longitude_deg FROM airport WHERE ident = '{icao}'"
    global cursor
    cursor.execute(sql)
    return cursor.fetchone()

def get_distance(game, airport):
    test = get_airport_info(game[1])
    test2 = get_airport_info(airport)
    #lat, long for both
    coords1 = (test[4], test[5])
    coords2 = (test2[4], test2[5])
    return distance.distance(coords1, coords2).km

def update_game(game_id, location, money, range):
    sql = f"UPDATE game SET money = {money}, location = '{location}', player_range = {range} WHERE id = {game_id}"
    global cursor
    cursor.execute(sql)

def fly(nykyinen):
    global cursor
    koodi = input("Mihin lennetään (ICAO-koodi): ")

    if koodi not in [airport[1] for airport in airports]:
        return False

    matka = get_distance(nykyinen, koodi)
    if player_range>matka>1:
        update_game(peli, koodi, money, player_range - matka)
        return True

def accessible_airports(nykyinen, player_range):
    test = 0
    for kenttä in airports:
        matka = get_distance(nykyinen, kenttä[1])
        if player_range > matka > 1:
            print(f"{kenttä[2]} (ICAO: {kenttä[1]}) | Matka: {matka:.2f} km")
            test += 1
    return test
name = input("Pelaajan nimi: ")
airports = get_airports()
starting_location = random.choice(airports)
current_airport = starting_location
money = 1000
player_range = 1500
peli = create_game(name, starting_location, money, player_range)
while True:
    #peli loop
    print(f"Nykyinen lentokenttä: {current_airport[2]}")
    print(f"Rahaa jäljellä: {money} €")
    print(f"Jäljellä oleva lentomatka: {player_range} km\n")
    print("""Vaihtoehdot
    1. Tankkaa
    2. Lähde matkalle""")
    tehtava = int(input("\nMitä tehdään: "))

    if tehtava == 1:
        maara = int(input("Paljonko rahaa haluat käyttää? (1 euro = 2 kilometriä.) "))
        if money > maara and maara > 0:
            player_range += maara * 2
            money -= maara
            update_game(peli, current_airport[1], money, player_range)
            print("Tankkaus onnistui")
        else:
            print("Jotain meni pieleen.")
            continue
    elif tehtava == 2:
        #testataan että voinko tehdä tämän logiikan FLY funktiossa
        test = accessible_airports(current_airport, player_range)
        if test == 0:
            print("Ei ole mahdollista lentää mihinkään. Tankkaa lisää.")
            continue
        print("Lentokenttä vaihtoehdot:")

        fly_result = fly(current_airport)
        if fly_result:
            # tallennetaan nykyinen sijainti
            current_airport = get_airport_info(fly_result)
        else:
            print("Virheellinen syöte tai väärä ICAO-koodi.")
    elif tehtava == 3:
        # lootbox

        pass
    game_info = get_game(peli)
    money = game_info[1]
    current_airport = get_airport_info(game_info[2])
    player_range = game_info[4]
