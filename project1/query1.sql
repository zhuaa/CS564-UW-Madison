-- Find the number of users in the database.
with Users(UserID) as 
(
    select UserID from Sellers union select UserID from Bidders
)
select count(UserID) from Users;
