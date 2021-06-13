// -*- mode: javascript; indent-tabs-mode: nil; c-basic-offset: 8 -*-
"use strict";

// Base layers configuration

function createBaseLayers() {
        var layers = [];

        var world = [];
        var us = [];
        var europe = [];

        world.push(new ol.layer.Tile({
                source: new ol.source.OSM({
                        "url" : "https://{a-z}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png",
                        "attributions" : 'Courtesy of <a href="https://carto.com">CARTO.com</a>'
                               + ' using data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                }),
                name: 'carto_dark_nolabels',
                title: 'CARTO.com Dark (No Labels)',
                type: 'base',
        }));

        world.push(new ol.layer.Tile({
                source: new ol.source.OSM(),
                name: 'osm',
                title: 'OpenStreetMap',
                type: 'base',
        }));

        var nexrad = new ol.layer.Tile({
                name: 'nexrad',
                title: 'NEXRAD',
                type: 'overlay',
                opacity: 0.5,
                visible: false
        });
        us.push(nexrad);

        var refreshNexrad = function() {
                // re-build the source to force a refresh of the nexrad tiles
                var now = new Date().getTime();
                nexrad.setSource(new ol.source.XYZ({
                        url : 'http://mesonet{1-3}.agron.iastate.edu/cache/tile.py/1.0.0/nexrad-n0q-900913/{z}/{x}/{y}.png?_=' + now,
                        attributions: 'NEXRAD courtesy of <a href="http://mesonet.agron.iastate.edu/">IEM</a>'
                }));
        };

        refreshNexrad();
        window.setInterval(refreshNexrad, 5 * 60000);

        var createGeoJsonLayer = function (title, name, url, fill, stroke, showLabel = true, strokeWidth = 3, dash = null) {
                return new ol.layer.Vector({
                    type: 'overlay',
                    title: title,
                    name: name,
                    zIndex: 0,
                    visible: false,
                    source: new ol.source.Vector({
                      url: url,
                      format: new ol.format.GeoJSON({
                        defaultDataProjection :'EPSG:4326',
                            projection: 'EPSG:3857'
                      })
                    }),
                    style: function style(feature) {
                        return new ol.style.Style({
                            fill: new ol.style.Fill({
                                color : fill
                            }),
                            stroke: new ol.style.Stroke({
                                color: stroke,
                                width: strokeWidth,
                                lineDash: dash,
                            }),
                            text: new ol.style.Text({
                                text: showLabel ? feature.get("name") : "",
                                overflow: OLMap.getView().getZoom() > 5,
                                scale: 1.25,
                                fill: new ol.style.Fill({
                                    color: '#000000'
                                }),
                                stroke: new ol.style.Stroke({
                                    color: '#FFFFFF',
                                    width: 2
                                })
                            })
                        });
                    }
                });
            };

        // Taken from https://github.com/alkissack/Dump1090-OpenLayers3-html
        us.push(createGeoJsonLayer('Class D Airspace', 'classdairspace', 'geojson/Airspace_CLASS_D.geojson', 'rgba(0, 0, 0, 0)', 'rgba(44, 119, 182, 1)', false, null, [4]));
        us.push(createGeoJsonLayer('Class C Airspace', 'classcairspace', 'geojson/Airspace_CLASS_C.geojson', 'rgba(0, 0, 0, 0)', 'rgba(133, 58, 89, 1)', false));
        us.push(createGeoJsonLayer('Class B Airspace', 'classbairspace', 'geojson/Airspace_CLASS_B.geojson', 'rgba(0, 0, 0, 0)', 'rgba(44, 119, 182, 1)', false, 5));
        us.push(createGeoJsonLayer('Runways', 'runways', 'geojson/Runways.geojson', 'rgba(0, 0, 0, 0)', 'rgba(214, 198, 28, 1)', false, 2));
        us.push(createGeoJsonLayer('Routes', 'routes', 'geojson/ATS_Route.geojson', 'rgba(0, 0, 0, 0)', 'rgba(152, 200, 216, 0.3)', false, 2));
        us.push(createGeoJsonLayer('Designated Points', 'designatedpoints', 'geojson/Designated_Points.geojson', 'rgba(0, 0, 0, 0)', 'rgba(214, 146, 28, 1)', true));
        
        if (world.length > 0) {
                layers.push(new ol.layer.Group({
                        name: 'world',
                        title: 'Worldwide',
                        layers: world
                }));
        }

        if (us.length > 0) {
                layers.push(new ol.layer.Group({
                        name: 'us',
                        title: 'US',
                        layers: us
                }));
        }

        if (europe.length > 0) {
                layers.push(new ol.layer.Group({
                        name: 'europe',
                        title: 'Europe',
                        layers: europe,
                }));
        }

        return layers;
}
