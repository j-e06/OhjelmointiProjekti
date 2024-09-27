import mariadb
conn = mariadb.connect(
    host='127.0.0.1',
    port=3306,
    database='project',
    user='root',
    password='potatoman',
    autocommit=True
)
cursor = conn.cursor()



"""

create table game_airports (
    game_id int primary key,
    airport_id bigint ,
    FOREIGN KEY (airport_id) REFERENCES airports(ident)
) charset = latin1;


create table game
  (
      id           int auto_increment
          primary key,
      money        int(8)      null,
      location     varchar(10) null,
      screen_name  varchar(40) null,
      player_range int         null,
      airports bigint         null,
      FOREIGN KEY (airports) REFERENCES game_airports(game_id)
  )
   charset = latin1;

"""