""" script for booking flights based on imput"""
import argparse
import json
import datetime
import requests


def getFlights(date, locationFrom, locationTo, oneWay, ret):
    """return JSON with flights according to paramenters"""
    url = 'https://api.skypicker.com/flights?'
    if oneWay:
        params = {"flyFrom": locationFrom, "to": locationTo, "dateFrom": parseDate(date), "dateTo": parseDate(date)}
    else:
        newDate = datetime.datetime.strptime(date, "%Y-%m-%d")
        newDate = newDate +  datetime.timedelta(days=int(ret))
        newDate = datetime.datetime.strftime(newDate, "%Y-%m-%d")
        params = {"flyFrom": locationFrom, "to": locationTo, "dateFrom": parseDate(date),
                  "dateTo": parseDate(newDate)}
    flights = requests.get(url, params)
    return flights.json()


def parseDate(date):
    """return date in form for geFlight api"""
    splited = date.split('-')
    return splited[2] + '/' + splited[1] + '/' +splited[0]



def findShortest(flights):
    """return shortest flight"""
    flightsData = flights["data"]
    selectedFlight = flightsData[0]
    shortestFlightDuratiron = getDuration(flightsData[0]["fly_duration"])
    for flight in flightsData:
        duration = getDuration(flightsData[0]["fly_duration"])
        if duration < shortestFlightDuratiron:
            shortestFlightDuratiron = duration
            selectedFlight = flightsData[flight]

    return selectedFlight


def getDuration(durationString):
    """parse the duration of flight into minutes int"""
    parsed = durationString.split("h")
    hours = int(parsed[0]) * 60
    minutes = int(parsed[1][0:len(parsed[1]) - 1])
    duration = hours + minutes
    return duration


def findCheapest(flights):
    """return chehapest flight"""
    flightsData = flights["data"]
    selectedFlight = flightsData[0]
    lovestPrice = flightsData[0]["price"]
    for flight in flightsData:
        if flight["price"] < lovestPrice:
            lovestPrice = flight["price"]
            selectedFlight = flight

    return selectedFlight

def bookFlight(flight, currency):
    """send the flight to booking api"""
    body = {}
    body["id"] = flight["id"]
    body["currency"] = currency
    body["booking_token"] = flight["booking_token"]
    body["passengers"] = [{"title": "Mr",
                           "firstName": "jiri",
                           "documentID": "111111111",
                           "birthday": "1999-01-01",
                           "email": "xy@gmail.com",
                           "lastName": "Rejman"}]

    header = {'content-type': 'application/json; charset=utf-8'}
    body = json.dumps(body)
    resp = requests.post("http://37.139.6.125:8080/booking", data=body, headers=header)
    print(resp.json()["pnr"])


def main():
    """maint method"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-date", "--date", dest="date", help="date of flight", required= True)
    parser.add_argument("-from", "--from", dest="locationFrom", help="location of flight start", required=True)
    parser.add_argument("-to", "--to", dest="locationTo", help="desired location of flight", required=True)
    parser.add_argument("-return", "--return", dest="ret", help="nights in location")
    parser.add_argument("-one-way", "--one-way", default=True, action="store_true",
                        dest='oneWay', help="is ticket one way?")
    parser.add_argument("-cheapest", "--cheapest", default=False, action="store_true",
                        dest='cheapest', help="book cheapest ticket")
    parser.add_argument("-shortest", "--shortest", default=False, action="store_true",
                        dest='shortest', help="book shortest ticket")
    args = parser.parse_args()

    if args.ret != None:
        args.oneWay = False

    flights = getFlights(args.date, args.locationFrom, args.locationTo, args.oneWay, args.ret)
    currency = flights["currency"]

    if args.shortest and args.cheapest:
        print("both values shortest and cheapest are not suported choose cheapest or shortest")

    elif args.shortest:

        selectedFlight = findShortest(flights)
        bookFlight(selectedFlight, currency)
    elif args.cheapest:

        selectedFlight = findCheapest(flights)
        bookFlight(selectedFlight, currency)
    else:
        selectedFlight = findCheapest(flights)
        #we return cheapest flight since the user didnt specify if he prefer cheaper od faster
        bookFlight(selectedFlight, currency)

if __name__ == "__main__":
    main()
