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
def fly(nykyinen,koodi):
    global cursor
    if koodi not in [airport[1] for airport in airports]:
        print("Virheellinen koodi")
        return

    #koodi löytyy.
    matka = get_distance(nykyinen, koodi)
    update_game(peli, koodi, money, player_range - matka)
    return True
name = input("Pelaajan nimi: ")
airports = get_airports()
starting_location = random.choice(airports)
current_airport = starting_location
money = 1000
player_range = 1500

peli = create_game(name, starting_location, money, player_range)
#peli = 1
while True:
    #peli loop
    print(current_airport[2])
    print(money)
    print(player_range)
    print("""Vaihtoehdot
    1. Tankkaa
    2. Lähde matkalle""")
    tehtava = int(input("Mitä tehdään: "))

    if tehtava == 1:
        maara = int(input("Paljonko rahaa haluat käyttää? (1 euro = 2 kilometriä.) "))
        if maara > money < 0:
            print("Jotain meni pieleen.")
            continue
        else:
            player_range += maara * 2
            money -= maara
            update_game(peli, current_airport[1], money, player_range)
            print("Tankkaus onnistui")
    elif tehtava == 2:
        print("Lentokenttä vaihtoehdot:")
        for airport in airports:
            # jos distance on yli mitä meillä on, älä näytä koska sinne ei päästä
            pituus = get_distance(current_airport, airport[1])
            if player_range > pituus > 1:
                print(airport[2], "ICAO:", airport[1], f"Matka: {pituus}")
        koodi = input("Mihin lennetään: ")
        result = fly(current_airport, koodi)
        if not result:
            print("Virheellinen koodi")
            continue
        else:
            current_airport = get_airport_info(koodi)
            print("Lento onnistui")
    game_info = get_game(peli)
    print(game_info)
    money = game_info[1]
    current_airport = get_airport_info(game_info[2])
    player_range = game_info[4]
