##
## run this code to capture the site_id and fuel_id to be used in configuration.yaml
##
## example configuration.yaml:
##
## sa_fuel_pricing:
##  debug: true
##  token_id: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
##  fuel_station_site_ids:
##    - 61501126: 5
##    - 61501126: 8
##

import os

from fuel_api import SAFuelPriceBook
import asyncio
from collections import OrderedDict

DEBUG = False
TOKEN_ID = os.getenv('TOKEN_ID')

if TOKEN_ID is None:
    print()
    print("set TOKEN_ID environment variable")
    print(" - export TOKEN_ID='xxxxxxxxxxx'")
    print()
    exit()

async def fuel_station_price_book_setup(token, debug):
    fuel_station_price_book = SAFuelPriceBook(token, debug)
    await fuel_station_price_book.update_fuel_pricing()
    
    return fuel_station_price_book

def print_results(fuel_station_price_book):
    fuel_station_dict = dict()

    for station_id in fuel_station_price_book.pricing:
        fuel_station = fuel_station_price_book.pricing[station_id]
        fuel_station_dict[fuel_station.site_id] = fuel_station.name

    fuel_station_dict_sorted_by_name = OrderedDict(sorted(fuel_station_dict.items(), key=lambda t: t[1]))

    print ("________________________________________________________________________________________________")
    print ("  site_id  ||                          Station Name                        ||      Address      ")
    print ("------------------------------------------------------------------------------------------------")

    for site_id, fuel_station_name in fuel_station_dict_sorted_by_name.items():
        print (f"({site_id}) || {fuel_station_name:60} || {fuel_station_price_book.pricing[site_id].address}")

        if fuel_station_price_book.pricing[site_id].fuel_list is not None:
            for fuel in fuel_station_price_book.pricing[site_id].fuel_list:
                print (f" |- {fuel.fuel_type.fuel_id:<2} - {fuel.fuel_type.name}")
        
        print ()

async def main():
    fuel_station_price_book = await fuel_station_price_book_setup(TOKEN_ID, DEBUG)
    print_results(fuel_station_price_book)

if __name__ == '__main__':
    asyncio.run(main())
