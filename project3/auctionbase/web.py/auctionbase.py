#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    # print (context)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/add_bid', 'add_bid',
        '/search', 'search',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)



class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        sqlitedb.changeCurrentTime(selected_time)
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)

class add_bid:
    def GET(self):
        return render_template('add_bid.html')


    def POST(self):
        post_params = web.input()
        itemID = post_params['itemID']
        userID = post_params['userID']
        price = post_params['price']
        sqlitedb.enterBids(itemID, userID, price, sqlitedb.getTime())
        success_message = "successfully insert" + itemID + userID + price + "at" + sqlitedb.getTime()
        success = 1
        return render_template('add_bid.html', message2 = success_message, add_result = success)

class search:
    def GET(self):
        return render_template('search.html')

    def POST(self):
        post_params = web.input()

        itemID = post_params['itemID']
        category = post_params['category']
        description = post_params['description']
        userID = post_params['userID']
        max = post_params['maxPrice']
        min = post_params['minPrice']
        status = post_params['status']
        result = sqlitedb.browseAuction(itemID, category, description, userID, min, max, status)
        
        # calculate the status and winner for every item in result
        #for item in result:
        #    if item.Time > item.Ends:
        #       Status.append('close')
        #    else:
        #        if result.Time < result.Started:
        #            Status.append('not open')
        #        else:
        #            Status.append('open')
        #the highest, in close status: winner
        #map itemID & winner
        Winner = {}
        Max_price = {}
        for row in result:
            Winner[row.itemID] = 'None'
            Max_price[row.itemID] = 0
            if row.Time < row.Ends:
                Winner[row.itemID] = 'None'
            else:
                if row.Buy_Price > Max_price[row.itemID]:
                    Winner[row.itemID] = row.userID
                    Max_price[row.itemID] = row.Buy_Price

        return render_template('search2.html', search_result = result,  winner = Winner)
###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
