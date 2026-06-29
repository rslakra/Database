DROP DATABASE IF EXISTS Library;
CREATE DATABASE Library;
USE Library;

--Users
DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(20) NOT NULL,
	email VARCHAR(20) NOT NULL,
	created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
);


INSERT INTO Users(name, email)
VALUES ('Diane','diana@gmail.com');
INSERT INTO Users(name, email)
VALUES ('Benny','benny@gmail.com');
INSERT INTO Users(name, email)
VALUES ('Gwen','gwen@gmail.com');
INSERT INTO Users(name, email)
VALUES ('Rohtash','rsingh@gmail.com');
INSERT INTO Users(name, email)
VALUES ('Harold','harold@gmail.com');
INSERT INTO Users(name, email)
VALUES ('Kaithy','kaithy@gmail.com');

--Departments
DROP TABLE IF EXISTS Departments;
CREATE TABLE Departments (
    id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(30) NOT NULL,
	PRIMARY KEY (id)
);

INSERT INTO Departments(name) VALUES ('English');
INSERT INTO Departments(name) VALUES ('Hindi');
INSERT INTO Departments(name) VALUES ('Math');
INSERT INTO Departments(name) VALUES ('Computer Science');
INSERT INTO Departments(name) VALUES ('Chemistry');
INSERT INTO Departments(name) VALUES ('Biology');
INSERT INTO Departments(name) VALUES ('Physics');
INSERT INTO Departments(name) VALUES ('History');

--Employees
DROP TABLE IF EXISTS Employees;
CREATE TABLE Employees (
    id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(30) NOT NULL,
	gender VARCHAR(6) NOT NULL,
	birth DATE NOT NULL, 
	salary INT NOT NULL,
	hired_on DATE,
	dept_id INT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (dept_id) REFERENCES Departments(id)
);



INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Diane','Female', '1999-03-30', 2000, 2);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Benny','Male','1996-04-29',3000, 1);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Gwen','Female', '1997-12-09', 4000, 3);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Gwen','Female', '1998-09-11', 3500), 5;
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Diane','Female', '1990-08-27', 6000, 4);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Benny','Male', '1990-08-27', 5000, 2);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Harold','Female', '1989-05-13', 4400, 6);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Gwen','Male','1994-03-17', 4600, 7);
INSERT INTO Employees(name, gender, birth, salary, dept_id)
VALUES ('Harold','Female','1993-02-04', 6500, 8);



DROP TABLE IF EXISTS Orders;
CREATE TABLE Orders (
    id INT NOT NULL AUTO_INCREMENT,
    OrderNumber int NOT NULL,
	OrderedOn DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    PRIMARY KEY (id),
    CONSTRAINT FK_PersonOrder FOREIGN KEY (user_id)
    REFERENCES Users(id)
);

INSERT INTO Orders(OrderNumber, user_id)
VALUES (232, 1);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (4342, 2);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (4322, 3);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (6453, 4);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (1010, 3);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (3210, 4);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (5001, 2);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (4221, 1);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (3333, 2);
INSERT INTO Orders(OrderNumber, user_id)
VALUES (1212, 1);

