import os
import flask
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations


#docker-compose build
#docker-compose up

app = Flask(__name__)

#os.environ['DB_PORT_27017_TCP_ADDR'], 27017
client = MongoClient("db", 27017)
db = client.tododb

@app.route('/')
def todo():
    return render_template('calc.html')

@app.route('/empty')
def empty():
    return render_template('empty.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("calc")
    return flask.render_template('404.html'), 404



@app.route('/new', methods=['POST'])
def new():
    
    open_list = []
    close_list = []
    km_list = []
    
    open_data = request.form.getlist("open")
    close_data = request.form.getlist("close")
    km_data = request.form.getlist("km")
    
    
    for item in open_data:
        if str(item) != '':
            open_list.append(str(item))
    
    for item in close_data:
        if str(item) != '':
            close_list.append(str(item))

    for item in km_data:
        if str(item) != '':
            km_list.append(str(item))


    open_list_len = len(open_list)

    ### Handle empty controle times
    if open_list_len == 0:
        return redirect(url_for('empty'))
    else:
        #insert data into database
        for i in range(open_list_len):
            item_doc = {
                'km': km_list[i],
                'open_times': open_list[i],
                'close_times': close_list[i]
            }
            db.tododb.insert_one(item_doc)

        return redirect(url_for('todo')) #refresh the page


@app.route('/display')
def display():
    
    item_list = db.tododb.find();

    items = [item for item in item_list]
    
    return render_template('display.html', items=items)


@app.route("/_calc_times")
def _calc_times():
    """
        Calculates open/close times from miles, using rules
        described at https://rusa.org/octime_alg.html.
        Expects one URL-encoded argument, the number of miles.
        """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    
    brevet_dist_km = request.args.get('distance', type=str)
    begin_date = request.args.get('begin_date', type=str)
    begin_time = request.args.get('begin_time', type=str)
    
    time = arrow.get(begin_date + " " + begin_time, "YYYY-MM-DD HH:mm")
    
    app.logger.debug("brevet distance: {}".format(brevet_dist_km))
    app.logger.debug("km={}".format(km))

    open_time = acp_times.open_time(km, brevet_dist_km, time)
    print("open time is " + open_time)
    close_time = acp_times.close_time(km, brevet_dist_km, time)
    print("close time is " + close_time)
    
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
