DROP DATABASE IF EXISTS Blog;
CREATE DATABASE Blog;
USE Blog;

--Posts
DROP TABLE IF EXISTS Posts;
CREATE TABLE Posts (
    id INT NOT NULL AUTO_INCREMENT,
	title VARCHAR(255) NOT NULL,
	body TEXT,
	email VARCHAR(20) NOT NULL,
	created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
);

INSERT INTO Posts(title, body, email)
VALUES ('Java', 'Java is an object oriented language', 'diana@gmail.com');
INSERT INTO Posts(title, body, email)
VALUES ('Objective-C', 'The iOS development language', 'benny@gmail.com');
INSERT INTO Posts(title, body, email)
VALUES ('Gradle', 'Gradle eases the build process', 'gwen@gmail.com');
INSERT INTO Posts(title, body, email)
VALUES ('Android', 'Android is an opensource project for android devices', 'rsingh@gmail.com');
INSERT INTO Posts(title, body, email)
VALUES ('Relation Database', 'Provides the data handling copabilities', 'harold@gmail.com');
INSERT INTO Posts(title, body, email)
VALUES ('Microservices', 'Helps to develop loosely coupled application', 'kaithy@gmail.com');


--Comments
DROP TABLE IF EXISTS Comments;
CREATE TABLE Comments (
    id INT NOT NULL AUTO_INCREMENT,
    post_id INT,
	title VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (post_id) REFERENCES Posts(id)
);

INSERT INTO Comments(post_id, title)
VALUES (1, 'Great');
INSERT INTO Comments(post_id, title)
VALUES (2, 'Awesome');
INSERT INTO Comments(post_id, title)
VALUES (5, 'Nice');
INSERT INTO Comments(post_id, title)
VALUES (6, 'Cool');

