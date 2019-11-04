-- Find the number of users who are both sellers and bidders.
with Users(UserID) as
(
    select UserID from Sellers
    intersect
    select UserID from Bidders
)
select count(UserID) from Users;
