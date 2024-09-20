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

def fly(nykyinen, koodi):
    global cursor

    if koodi not in [airport[1] for airport in airports]:
        return "Koodia ei löytynyt."

    matka = get_distance(nykyinen, koodi)
    if player_range>matka>1:
        update_game(peli, koodi, money, player_range - matka)
        return

def accessible_airports(nykyinen, player_range):
    lista = []
    for kenttä in airports:
        matka = get_distance(nykyinen, kenttä[1])
        if player_range > matka > 1:
            lista.append(f"{kenttä[2]} (ICAO: {kenttä[1]}) | Matka: {matka:.2f} km")
    return lista

def create_lootboxes(airports):
    # lets decide the chances of a lootbox appearing
    # returning value will be airports so we'll redefine it
    # 30 airports with 10 gems, 1 diamond, 4 robbers and 15 air

    pass

name = input("Pelaajan nimi: ")
airports = get_airports()

#create_lootboxes(airports)

starting_location = random.choice(airports)
current_airport = starting_location
money = 1000
player_range = 1500

peli = create_game(name, starting_location, money, player_range)

while True:

    #game_over(game_id)
    # game_over handles checking if game is over and what to do in that case.

    #
    print(f"Nykyinen lentokenttä: {current_airport[2]}")
    print(f"Rahaa jäljellä: {money} €")
    print(f"Jäljellä oleva lentomatka: {player_range} km\n")
    print("""Vaihtoehdot
    1. Tankkaa
    2. Lähde matkalle""")
    try:
        tehtava = int(input("\nMitä tehdään: "))
    except ValueError:
        print("Syötä numero.")
        continue
    if tehtava == 1:
        maara = int(input("Paljonko rahaa haluat käyttää? (1 euro = 2 kilometriä.) "))
        if money > maara > 0:
            player_range += maara * 2
            money -= maara
            update_game(peli, current_airport[1], money, player_range)
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
        #testataan että voinko tehdä tämän logiikan FLY funktiossa
        usable_airports = accessible_airports(current_airport, player_range)
        #tarkistetaan uudelleen että onko mahdollista lentää mihinkään
        #emme tarkista rahan määrää joten tarkistamme uudelleen jos jokin on muuttunut
        for a in usable_airports:
            print(a)
        if len(usable_airports) == 0:
            print("Ei ole mahdollista lentää mihinkään. Tankkaa lisää.")
            continue
        print("Lentokenttä vaihtoehdot:")
        koodi = input("Mihin lennetään (ICAO-koodi): ")

        fly_result = fly(current_airport, koodi)
        if fly_result is None:
            # tallennetaan nykyinen sijainti
            current_airport = get_airport_info(fly_result)
        else:
            print(fly_result)
    elif tehtava == 3:
        # lootbox
        """
        Tarkistetaan onko kentän lootboxia avattu
        
        jos kyllä, voidaan mennä takaisin alkuun
        
        jos ei ole, voidaan avata lootboxi
        
        open_lootbox(current_airport)
        """
    game_info = get_game(peli)
    money = game_info[1]
    current_airport = get_airport_info(game_info[2])
    player_range = game_info[4]
