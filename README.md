# SA Fuel Pricing

A sensor that keeps track of SA fuel pricing in home assistant.

## Installation
Download sa_fuel_pricing to custom_components folder within the /config directory of home-assistant

### Configuration
> **debug**  - (true or false) additional information printed to logger

> **token_id** - request from https://www.safuelpricinginformation.com.au/publishers.html

> **fuel_station_site_ids** - 1 or more station_site_id: fuel_type_id

#### Generate station_site_id and fuel_type_id
Run "print_fuel_station_ids.py" from custom_components/sa_fuel_pricing
   
    sample output:
    ________________________________________________________________________________________________
      site_id  ||                          Station Name                        ||      Address      
    ------------------------------------------------------------------------------------------------
    (61501683) || 24 Seven Blanchetown                                         || 8657 Sturt Highway
     |- 2  - Unleaded
     |- 3  - Diesel
     |- 4  - LPG
     |- 8  - Premium Unleaded 98
    
    (61501678) || 24 Seven Keith                                               || 14 Dukes Hwy
     |- 2  - Unleaded
     |- 3  - Diesel
     |- 4  - LPG
     |- 8  - Premium Unleaded 98
    
#### Example configuration.yaml

    sa_fuel_pricing:
      debug: true
      token_id: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      fuel_station_site_ids:
        - 61501126: 5
        - 61501126: 8

    logger:
      default: info
      logs:
        custom_components.sa_fuel_pricing: debug
