# OhjelmointiProjekti
Metropolia Ohjelmisto 1 python ryhmätyö



Tietokanta:

lp_project_base.sql (löytyy moodlesta)

ja seuraavat lauseet:

set foreign_key_checks = 0;

CREATE TABLE IF NOT EXISTS `game` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `money` int(11) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `starting_airport` varchar(255) DEFAULT NULL,
  `screen_name` varchar(255) DEFAULT NULL,
  `player_range` float DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL,
  `timantti` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_game_airport` (`starting_airport`),
  CONSTRAINT `FK_game_airport` FOREIGN KEY (`starting_airport`) REFERENCES `airport` (`ident`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table project.game_airports
CREATE TABLE IF NOT EXISTS `game_airports` (
  `game_id` int(11) NOT NULL,
  `airport_id` varchar(255) NOT NULL,
  `lootbox` int(11) DEFAULT NULL,
  PRIMARY KEY (`game_id`,`airport_id`),
  KEY `airport_ident` (`airport_id`),
  CONSTRAINT `game_airports_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `game` (`id`),
  CONSTRAINT `game_airports_ibfk_2` FOREIGN KEY (`airport_id`) REFERENCES `airport` (`ident`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

set foreign_key_checks = 1;
