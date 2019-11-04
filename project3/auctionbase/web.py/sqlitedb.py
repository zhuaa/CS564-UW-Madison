import web
import traceback

db = web.database(dbn='sqlite',
        db='AuctionBase' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Time # TODO: update this as well to match the
                                  # column name
#########

def changeCurrentTime(newTime):
    time_string = str(newTime)
    # print (time_string)

    #query_string = "UPDATE CurrentTime SET Time = $time"
    db.query("UPDATE CurrentTime SET Time = $id", vars = {'id': time_string})
    #
    #try:
    #    result = query(query_string, {'time': time_string})
    #except Exception as e:
    #    print "error"

def enterBids(itemID,userID,price, currentTime):
    # Deal with itmeID that is not in the relation
    try:
        results = db.query("select * from Items where itemID = $itemID", \
                           vars={'itemID':itemID})
        currentTime = str(currentTime)
        # Get the contents of the tuple
        m = results[0]
        # Check if currentTime is betwwen started and ends time
        if currentTime >= str(m['Started']) and currentTime <= str(m['Ends']):
            if m['Buy_Price']:
                print('BuyPrice alread reached')
                return False
            else:
                print('you can enter bids')
                db.query("INSERT INTO Bids(ItemID, UserID, Amount, Time) VALUES ($iID,$uID, $amo, $cT)",\
                         vars = {'iID': itemID, 'uID': userID, 'amo': price, 'cT': currentTime})
                return True
        else:
            print('Auction not available')
            return False
    except Exception as e:
        traceback.print_exc()
        print('Item ID not found')


def browseAuction(itemID, category, description, userID, min, max, status):

    vars = {}

    # test
    # chooseQuery = "SELECT * FROM Categories"
    # return db.query(chooseQuery, vars)


    chooseQuery = "SELECT * FROM Categories, Items, Bids WHERE Categories.ItemID = Items.itemID \
                    AND Bids.ItemID = Items.itemID"

    # chooseQuery = "SELECT * FROM Items, Bids WHERE Bids.ItemID = Items.itemID"



    if (itemID != ""):
        chooseQuery += ' AND Items.ItemID = $itID'
        vars['itID'] = itemID

    # if (category != ""):
    #     chooseQuery += ' AND category = $cat'
    #     vars['cat'] = category

    # search for substring
    if (description != ""):
        # chooseQuery += ' AND Description = $desc'
        chooseQuery += ' AND Description LIKE $desc'
        description = "%" +  description + "%"
        # print (description)
        vars['desc'] = description

    if (userID != ""):
        chooseQuery += ' AND UserID = $userID'
        vars['userID'] = userID

    # min only
    if (min != "" and max == ""):
        chooseQuery += ' AND (Buy_Price >= $min or First_Bid >= $min2)'
        vars['min'] = min
        vars['min2'] = min

    # max only
    if (min == "" and max != ""):
        chooseQuery += ' AND (Buy_Price <= $max or First_Bid <= $max2)'
        vars['max'] = max
        vars['max2'] = max

    # min & max
    if (min != "" and max != ""):
        chooseQuery += ' AND ((Buy_Price >= $min or Buy_price <= $max) or (First_Bid <= $max2 or First_Bid >= $min2))'
        vars['max'] = max
        vars['max2'] = max
        vars['min'] = min
        vars['min2'] = min

    if (status == 'open'):
        chooseQuery += ' AND ($currtime >= Started AND $currtime <= Ends)'
        vars['currtime'] = getTime()
        # vars['currtime2'] = getTime()

    if (status == 'close'):
        chooseQuery += ' AND ($currtime > Ends)'
        vars['currtime'] = getTime()

    if (status == 'notStarted'):
        chooseQuery += ' AND ($currtime < Started)'
        vars['currtime'] = getTime()

    return db.query(chooseQuery, vars)


###########
# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where item_ID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
#print getTime()
#changeCurrentTime("2001-12-20 00:00:05")

