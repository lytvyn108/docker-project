CREATE DATABASE mydb;
CREATE TABLE mydb.users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
INSERT INTO mydb.users (name) VALUES ('Docker User');
