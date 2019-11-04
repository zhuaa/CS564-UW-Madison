-- Find the ID(s) of auction(s) with the highest current price.
select ItemID from Items
where Currently = (
    select max(t.Currently) from items as t 
);
