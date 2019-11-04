-- Find the number of users from New York (i.e., users whose location is the string "New York").
with Users(UserID) as 
(
    select UserID from Sellers 
    where Sellers.Location = "New York" union 
    select UserID from Bidders 
    where Bidders.Location = "New York"
    ) 
select count(UserID) from Users;
