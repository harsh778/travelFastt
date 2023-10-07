CREATE DATABASE IF NOT EXISTS 'TravelFastDB' DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE 'TravelFastDB';

CREATE TABLE IF NOT EXISTS 'users' {
    'id' int(10) NOT NULL AUTO_INCREMENT,
    'username' varchar(50) NOT NULL,
    'password' varchar(255) NOT NULL,
    PRIMARY KEY ('id')
} ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS 'routes' {
    'id' int(10) NOT NULL,
    'place1' varchar,
    'place2' varchar,
    'place3' varchar,
    'place4' varchar,
    'place5' varchar,
    'place6' varchar,
    'place7' varchar,
    'place8' varchar,
    'place9' varchar,
    'place10' varchar,
    FOREIGN KEY ('id') REFERENCES users('id')
} ENGINE=InnoDB DEFAULT CHARSET=utf8;