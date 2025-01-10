CREATE DATABASE IF NOT EXISTS mydb;
USE mydb;

-- Create table for Customer
CREATE TABLE IF NOT EXISTS Customer (
    customerID INT PRIMARY KEY AUTO_INCREMENT,
    firstname VARCHAR(50),
    surname VARCHAR(50),
    email VARCHAR(50)
);

-- Create table for Wine
CREATE TABLE IF NOT EXISTS Wine (
    wineID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    type VARCHAR(50),
    price DECIMAL(10, 2),
    country VARCHAR(50),
    alcoholPercentage DECIMAL(5, 2)
);

-- Create table for CollectionWine
CREATE TABLE IF NOT EXISTS CollectionWine (
    wineID INT PRIMARY KEY,
    numberInCollection INT,
    specialPackaging VARCHAR(50),
    FOREIGN KEY (wineID) REFERENCES Wine(wineID)
);

-- Create table for Order
CREATE TABLE IF NOT EXISTS `Order` (
    orderID INT PRIMARY KEY AUTO_INCREMENT,
    customerID INT,
    status VARCHAR(50),
    deliveryPrice DECIMAL(10, 2),
    FOREIGN KEY (customerID) REFERENCES Customer(customerID)
);

-- Create a table for relationship between Order and Wine
CREATE TABLE IF NOT EXISTS Contains (
    orderID INT,
    wineID INT,
    PRIMARY KEY (orderID, wineID),
    FOREIGN KEY (orderID) REFERENCES `Order`(orderID),
    FOREIGN KEY (wineID) REFERENCES Wine(wineID)
);

-- Create a table for many-to-many recursive relationship for wine pairings
CREATE TABLE IF NOT EXISTS IsPaired (
    wineID1 INT,
    wineID2 INT,
    PRIMARY KEY (wineID1, wineID2),
    FOREIGN KEY (wineID1) REFERENCES Wine(wineID),
    FOREIGN KEY (wineID2) REFERENCES Wine(wineID)
);

-- Create table for Review (Weak Entity)
CREATE TABLE IF NOT EXISTS Review (
    reviewID INT AUTO_INCREMENT,
<<<<<<< HEAD
    customerID INT,
    wineID INT,
=======
    wineID INT,
    customerID INT,
>>>>>>> e910508 (Database populated successfully)
    authorFirstName VARCHAR(50),
    authorLastName VARCHAR(50),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
<<<<<<< HEAD
    PRIMARY KEY (wineID, reviewID),
=======
    PRIMARY KEY (reviewID, wineID),
>>>>>>> e910508 (Database populated successfully)
    FOREIGN KEY (wineID) REFERENCES Wine(wineID),
    FOREIGN KEY (customerID) REFERENCES Customer(customerID)
);
