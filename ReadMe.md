# SkyAware GeoJSON Plug-In

## About

This script will add new airspace layers for US airspace and routes.  Note, it will also significantly reduce the options available in the OpenLayers window so it is actually useful.

## Installation

Script requires shapely, a Python library for checking and creating shapes.  To install it, `sudo pip install shapely`.  Sudo is typically required because the script must be run with elevated privilages to access the `/usr/share/skyaware/html/geojson` directory.

Backup existing `layers.js` file

`sudo mv /usr/share/skyaware/html/layers.js /usr/share/skyaware/html/layers.js.backup`

Copy the new layers file into the SkyAware directory

`sudo layers.js /usr/share/skyaware/html/`


## Configuration

You MUST configure the settings.json file with a lat/long, at a minimum.  The default lat/long are set for the White House, Washington, DC.

## Downloading Datasets

Datasets can be downloaded from https://adds-faa.opendata.arcgis.com/search?collection=Dataset:
- Runways
- ATS Route
- Class Airspace
- Designated Point