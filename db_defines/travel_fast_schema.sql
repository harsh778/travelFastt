-- CREATE DATABASE IF NOT EXISTS `travelfast` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
-- USE 'travelfast';

-- CREATE TABLE `users` (
--   `id` int NOT NULL AUTO_INCREMENT,
--   `username` varchar(50) DEFAULT NULL,
--   `password` varchar(255) DEFAULT NULL,
--   PRIMARY KEY (`id`),
--   UNIQUE KEY `id_UNIQUE` (`id`)
-- ) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- CREATE TABLE `routes` (
--   `id` int NOT NULL,
--   `route_id` int unsigned DEFAULT NULL AUTO_INCREMENT,
--   `latitude` mediumblob,
--   `longitude` mediumblob,
--   UNIQUE KEY `id_UNIQUE` (`id`),
--   CONSTRAINT `id` FOREIGN KEY (`id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE DATABASE IF NOT EXISTS `travelfast` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE travelfast;

CREATE TABLE IF NOT EXISTS users (
  id int NOT NULL AUTO_INCREMENT,
  username varchar(50) DEFAULT NULL,
  password varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY id_UNIQUE (id)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS routes (
  route_id int NOT NULL AUTO_INCREMENT,
  latitude mediumblob DEFAULT NULL,
  longitude mediumblob DEFAULT NULL,
  location_names mediumblob DEFAULT NULL,
  user_id INT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (route_id),
  UNIQUE KEY id_UNIQUE (route_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
