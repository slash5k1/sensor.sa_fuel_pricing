"""SA Fuel Pricing integration."""
import logging

import voluptuous as vol

from homeassistant import core
from homeassistant.const import CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_TOKEN_ID, CONF_FUEL_STATION_SITE_IDS, \
                   DEFAULT_SCAN_INTERVAL, DOMAIN, CONF_DEBUG, DEFAULT_DEBUG
from .fuel_api import SAFuelPriceBook

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_DEBUG, default=DEFAULT_DEBUG): cv.boolean,
                vol.Required(CONF_TOKEN_ID): cv.string,
                vol.Required(CONF_FUEL_STATION_SITE_IDS): vol.All(cv.ensure_list, [{cv.positive_int: cv.positive_int}]),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(cv.time_period, cv.positive_timedelta),
            }
        )
    },
    # The full HA configurations gets passed to `async_setup` so we need to allow
    # extra keys.
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the platform.
    @NOTE: `config` is the full dict from `configuration.yaml`.
    :returns: A boolean to indicate that initialization was successful.
    """
    conf = config[DOMAIN]
    token_id = conf[CONF_TOKEN_ID]
    scan_interval = conf[CONF_SCAN_INTERVAL]
    fuel_station_price_book = SAFuelPriceBook(token_id, debug=conf[CONF_DEBUG])
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name=DOMAIN,
        update_method=fuel_station_price_book.get_fuel_pricing,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=scan_interval,
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN] = {"conf": conf, "coordinator": coordinator}
    hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, {}, conf))

    return True