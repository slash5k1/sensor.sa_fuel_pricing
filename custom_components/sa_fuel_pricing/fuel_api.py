####################################################################################################
##
## Code to query SAGov Fuel Pricing API - Slash5k1
##
## 1) Instantiate SAFuelPriceBook with token_id
## 2) await get_fuel_pricing()
##    - Query SAGov Fuel Pricing API
##    - Build dictionary of objects (fuel_type, fuel, fuel_station) - order matters
##    - Returns result from self.pricing
##
## API information can be found @ https://www.safuelpricinginformation.com.au/publishers.html
##
####################################################################################################
from datetime import datetime
from dateutil import tz

import aiohttp
import asyncio

from functools import wraps
import time

import ssl
import certifi
ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

import logging
_LOGGER = logging.getLogger(__name__)
####################################################################################################
prod_url = 'https://fppdirectapi-prod.safuelpricinginformation.com.au'

urls = {'Fuels': {'url': '/Subscriber/GetCountryFuelTypes?countryId=21'},
        'Brands': {'url': '/Subscriber/GetCountryBrands?countryId=21'},
        'S': {'url': '/Subscriber/GetFullSiteDetails?countryId=21&geoRegionLevel=3&geoRegionId=4'},
        'SitePrices': {'url': '/Price/GetSitesPrices?countryId=21&geoRegionLevel=3&geoRegionId=4'},
        }

####################################################################################################
class fuel_station(object):
    def __init__(self, site_id, name, address, lat_lng, fuel_list):
        self.site_id = site_id
        self.name = name
        self.address = address
        self.lat_lng = lat_lng
        self.fuel_list = fuel_list

    def __str__(self):
        string = f"{{'site_id': {self.site_id}, 'name': {self.name}, 'address': {self.address}, 'lat_lng': {self.lat_lng}, 'fuel_list': {self.fuel_list}}}"
        return string

    def __repr__(self):
        return self.__str__()

class fuel_type(object):
    def __init__(self, fuel_id, name):
        self.fuel_id = fuel_id
        self.name = name

    def __str__(self):
        string = f"{{'fuel_id': {self.fuel_id}, 'name': {self.name}}}"
        return string       

    def __repr__(self):
        return self.__str__()
              
class fuel(object):
    def __init__(self, site_id, fuel_type, date_utc, price):
        self.site_id = site_id
        self.fuel_type = fuel_type
        self.date_utc = date_utc
        self.price = price

    @property
    def date_local(self):
        utc = datetime.strptime(self.date_utc.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        utc = utc.replace(tzinfo=tz.tzutc())
        return (utc.astimezone(tz.tzlocal()))

    def __str__(self):
        string = f"{{'site_id': {self.site_id}, 'fuel_type': {self.fuel_type}, 'date_local': {self.date_local}, 'price': {self.price}}}"
        return string

    def __repr__(self):
        return self.__str__()

class SAFuelPriceBook():
    def __init__(self, token_id, debug=False):
        self._token_id = token_id
        self._headers = {'Authorization': f'FPDAPI SubscriberToken={self._token_id}'}
        self._debug = debug

        self._fuel_type_dict = None
        self._fuel_dict = None
        self._fuel_station_dict = None

    @property
    def pricing(self):
        return self._fuel_station_dict

    def dprint(self, string):
        if self._debug is True:
            _LOGGER.debug(string)
            print(string)

    def measure(func):
        @wraps(func)
        def _time_it(self, *args, **kwargs):
            start = int(round(time.time() * 1000))
            try:
                return func(self, *args, **kwargs)
            finally:
                end_ = int(round(time.time() * 1000)) - start
                self.dprint(f"({func.__name__}) Total execution time: {end_ if end_ > 0 else 0} ms")
        
        return _time_it

    @measure
    async def return_json_data(self, key):
        async with aiohttp.ClientSession(headers=self._headers) as session:
            try:
                self.dprint(f"pulling data from - {prod_url + urls[key]['url']}")
                async with session.get(prod_url + urls[key]['url'], ssl=ssl_context) as response:
                    json_response = await response.json()
            except Exception as e:
                print (e)
                return None
            else:
                return json_response[key]

    # Example json_data
    # {"Fuels": [{"FuelId": 2, "Name": "Unleaded"}]}
    @measure
    def return_dict_of_fuel_types(self, json_data):
        fuel_type_dict = dict()

        for data in json_data:
            fuel_type_dict[data['FuelId']] = fuel_type(data['FuelId'], data['Name'])

        return fuel_type_dict

    ## Example json_data
    ## {"SitePrices": [{"SiteId": 61577318, "FuelId": 2, "CollectionMethod": "T", "TransactionDateUtc": "2021-03-02T04:01:24.13", "Price": 9999.0}]}
    @measure
    def return_dict_of_fuel(self, json_data):
        fuel_dict = dict()

        for data in json_data:
            fuel_dict[data['SiteId']] = list()

        for data in json_data:
            try:
                fuel_type = self._fuel_type_dict[data['FuelId']]
            except KeyError:
                self.dprint(f"ERROR - 'FuelId' {fuel_type_dict[data['FuelId']]} doesnt exist in fuel_type_dict")
                fuel_type = 'Unknown'

            fuel_dict[data['SiteId']].append(fuel(data['SiteId'], fuel_type, data['TransactionDateUtc'], data['Price']))

        return fuel_dict

    ## Example json_data
    ## {"S": [{"S": 61205460, "A": "11 Vader Street", "N": "OTR Dry Creek", "B": 169, "P": "5094", "G1": 170227225, 
    ## "G2": 189, "G3": 4, "G4": 0, "G5": 0, "Lat": -34.819297, "Lng": 138.592116, "M": "2021-03-12T04:30:53.43",
    ## "GPI": "ChIJKy0p_ra3sGoRaWz3bT-5iEk", "MO": "00:00", "MC": "23:59", "TO": "00:00", "TC": "23:59", "WO": "00:00",
    ## "WC": "23:59", "THO": "00:00", "THC": "23:59", "FO": "00:00", "FC": "23:59", "SO": "00:00", "SC": "23:59",
    ## "SUO": "00:00", "SUC": "23:59"}]}
    @measure
    def return_dict_of_fuel_stations(self, json_data):
        dict_of_fuel_stations = dict()
        station_dict = dict()

        if json_data is not None:
            for data in json_data:
                station_dict['site_id'] = data['S']
                station_dict['name'] = data['N']
                station_dict['address'] = data['A']
                station_dict['lat_lng'] = (data['Lat'], data['Lng'])
                try:
                    station_dict['fuel_list'] = self._fuel_dict[station_dict['site_id']]
                except KeyError:
                    self.dprint (f"{station_dict['site_id']} - contains no fuel information")
                    station_dict['fuel_list'] = None

                dict_of_fuel_stations[station_dict['site_id']] = fuel_station(**station_dict)

        return dict_of_fuel_stations

    @measure
    async def update_fuel_pricing(self):
        fuel_type = asyncio.create_task(self.return_json_data("Fuels"))
        fuel = asyncio.create_task(self.return_json_data("SitePrices"))
        fuel_stations = asyncio.create_task(self.return_json_data("S"))

        await asyncio.wait([fuel_type, fuel, fuel_stations])

        self._fuel_type_dict = self.return_dict_of_fuel_types(fuel_type.result())
        self._fuel_dict = self.return_dict_of_fuel(fuel.result())
        self._fuel_station_dict = self.return_dict_of_fuel_stations(fuel_stations.result())

    @measure
    async def get_fuel_pricing(self):
        await self.update_fuel_pricing()
        return self.pricing
