-- Find the number of categories that include at least one item with a bid of more than $100.
select count(distinct CategoryUserID.Category)
from CategoryUserID, Bid
where Bid.Amount > 100 and Bid.ItemID = CategoryUserID.ItemID;
