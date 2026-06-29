DROP DATABASE IF EXISTS Animal;
CREATE DATABASE Animal;
USE Animals;

DROP TABLE Pets;
CREATE TABLE Pets(
    id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(20) NOT NULL, 
	owner VARCHAR(20),
	species VARCHAR(20), 
	sex CHAR(1), 
	birth DATE, 
	death DATE,
	PRIMARY KEY (id)
);


INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Puffball','Diane','hamster','f','1999-03-30',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Slim','Benny','snake','m','1996-04-29',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Whistler','Gwen','bird','f','1997-12-09',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Chirpy','Gwen','bird','f','1998-09-11',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Bowser','Diane','dog','m','1990-08-27','1995-07-29');
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Fang','Benny','dog','m','1990-08-27',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Buffy','Harold','dog','f','1989-05-13',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Claws','Gwen','cat','m','1994-03-17',NULL);
INSERT INTO Pets(name, owner,species, sex, birth, death)
VALUES ('Luffy','Harold','cat','f','1993-02-04', NULL);