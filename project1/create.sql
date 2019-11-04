--
--  Authors: Jennifer Cao, Tien-Lung Fu, Pan Wu
--  First drop any existing tables. Any errors are ignored.
--  Five Tables, store information of items, sellers, bidders, bid, relationship between them respectively.
--
drop table if exists Items;
drop table if exists Sellers;
drop table if exists Bidders;
drop table if exists Bid;
drop table if exists CategoryUserID;
--
-- Now, add each table.
--
create table Items(
	ItemID integer primary key,
    Name varchar(200),
    Category varchar(80),
	CategoryLength integer,
    Currently integer,
    BuyPrice integer,
    FirstBid integer,
    NumberBid integer,
    Started varchar(20),
    Ends varchar(20),
    SellerID varchar(50),
    Description varchar(1000)
	);

create table Sellers(
    UserID varchar(50) primary key, 
    Rating integer, 
    Location varchar(20), 
    Country varchar(20)
    );

create table Bidders(
    UserID varchar(50) primary key, 
    Rating integer, 
    Location varchar(20), 
    Country varchar(20)
    );

create table Bid(
    ItemID integer, 
    BidderID varchar(50), 
    SellerID varchar(50), 
    Amount float, 
    Time varchar(20),
    primary key(ItemID, BidderID, SellerID)
    foreign key(ItemID) references Items(ItemID),
    foreign key(BidderID) references Bidders(UserID),
	foreign key(SellerID) references Sellers(UserID));

create table CategoryUserID(
    Category varchar(80), 
    ItemID integer 
    );
