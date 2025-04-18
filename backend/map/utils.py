from functools import lru_cache

import requests
from geopy.distance import distance

from foodcartapp.models import Order
from django.conf import settings

from map.models import Location
from map.serializers import LocationSerializer


def get_distance(orders: Order) -> Order:
    for order in orders:
        distance_by_restaurants = []
        for restaurant in order.restaurants:
            order_location = get_or_create_location(order.address)
            restaurant_location = get_or_create_location(restaurant.address)
            if order_location and restaurant_location:
                space = round(distance(
                    order_location.coordinates,
                    restaurant_location.coordinates
                ).km, 3)
            else:
                space = None
            distance_by_restaurants.append((restaurant, space))

        order.restaurants = sorted(distance_by_restaurants, key=lambda x: x[1])
    return orders


@lru_cache
def get_or_create_location(address: str) -> Location | None:
    location = Location.objects.filter(address=address).first()
    if not location:
        try:
            lon, lat = _fetch_coordinates(settings.GEO_TOKEN, address)
        except requests.exceptions.HTTPError:
            location = None
        else:
            serializer = LocationSerializer(data={
                'address': address,
                'latitude': float(lat),
                'longitude': float(lon),
            })
            serializer.is_valid(raise_exception=True)
            location = serializer.save()
    return location


def _fetch_coordinates(apikey: str, address: str) -> tuple[str, str] | None:
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
