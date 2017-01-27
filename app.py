#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    print("Input to processRequest")
    print("action:")
    print(req.get("result").get("action"))
    if req.get("result").get("action") == "yahooWeatherForecast":
        print("Input to yahooWeatherForecast")
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
        result = urllib.request.urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWeatherWebhookResult(data)
        return res
    if req.get("result").get("action") == "productHunt":
        print("Input to productHunt")
        baseurl = "https://0h4smabbsg-dsn.algolia.net/1/indexes/Post_production?query=whatsapp"
        yql_url = baseurl
        print("Start make request")
        req = urllib.request.Request(yql_url, headers={'X-Algolia-API-Key': '9670d2d619b9d07859448d7628eea5f3','X-Algolia-Application-Id': '0H4SMABBSG'}, method='GET')
        print("End make request")
        #result = urllib.request.urlopen(req).read()
        try:
            print("Start urlopen")
            response = urllib.request.urlopen(req)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        else:
            # everything is fine
            print('everything is fine')
            result = response.read()

        print(result)
        data = json.loads(result)
        res = makeProductHuntWebhookResult(data)
        return res
    elif req.get("result").get("action") == "testRtB":
        print("Input to testRtB")
        speech = "Success!!!"
        return {
            "speech": speech,
            "displayText": speech,
            # "data": data,
            # "contextOut": [],
            "source": "apiai-rtbbotresearch"
        }        
    else:    
        return {}


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWeatherWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-rtbbotresearch"
    }

def makeProductHuntWebhookResult(data):
    print("Input to makeProductHuntWebhookResult")
    hits = data.get('hits')
    if hits is None:
        return {}

    cnt = 0;
    speech = "Top product 5:"

    for x in hits:
        speech = speech + "\n" + x.get('name')
        cnt = cnt + 1
        if cnt == 5:
            break

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-rtbbotresearch"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
