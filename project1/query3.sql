-- Find the number of auctions belonging to exactly four categories.
with Auctions(CategoryCount) as 
(
    select count(Category) as CategoryCount from CategoryUserID
    group by ItemID
)
select count(CategoryCount) from Auctions where CategoryCount = 4;

