import logging

from homeassistant import core
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: core.HomeAssistant, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    fuel_station_list = list()

    conf = hass.data[DOMAIN]["conf"]
    coordinator = hass.data[DOMAIN]["coordinator"]
    fuel_station_site_ids = conf['fuel_station_site_ids']
    fuel_station = coordinator.data

    for fuel_station_site_id in fuel_station_site_ids:
        for site_id in fuel_station_site_id:
            fuel_type_id = fuel_station_site_id[site_id]
            fuel_station_list.append(FuelStationEntity(coordinator, site_id, fuel_type_id))

    async_add_entities(fuel_station_list)

class FuelStationEntity(CoordinatorEntity):
    """Representation of a sensor."""
    def __init__(self, coordinator, site_id, fuel_type_id):
        super().__init__(coordinator)
        self.site_id = site_id
        self.fuel_type_id = fuel_type_id
        self._state = None
        self.attrs = {}
        self.conf = self.coordinator.hass.data[DOMAIN]['conf']
        self.fuel_station = self.coordinator.data[site_id]
        self.fuel_type_dict = {}

        for fuel in self.fuel_station.fuel_list:
            fuel_id = fuel.fuel_type.fuel_id
            fuel_name = fuel.fuel_type.name

            self.fuel_type_dict[fuel_id] = fuel_name

    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return f"{self.site_id}_{self.fuel_type_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        fuel_station = self.coordinator.data[self.site_id]
        
        try:
            fuel_name = self.fuel_type_dict[self.fuel_type_id]
        except KeyError:
            fuel_name = "ERROR"
        finally:
            return f"Fuel Station - {fuel_station.name} - {fuel_name}"

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return "$"

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return "mdi:gas-station"

    @property
    def state(self) -> int:
        """Return state of the sensor."""
        fuel_station = self.coordinator.data[self.site_id]
        self._state = None

        if fuel_station.fuel_list is not None:
            for fuel in fuel_station.fuel_list:
                if fuel.fuel_type.fuel_id == self.fuel_type_id:
                    self._state = round(fuel.price / 1000, 3)
                    return self._state

            return self._state
        
        else:
            return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes of the sensor."""
        fuel_station = self.coordinator.data[self.site_id]

        self.attrs['site_id'] = f"{fuel_station.site_id}"
        self.attrs['name'] = fuel_station.name
        self.attrs['address'] = fuel_station.address
        self.attrs['lat_lng'] = fuel_station.lat_lng

        return self.attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if self.state is not None and self.coordinator.last_update_success:
            return True
        else:
            return False
