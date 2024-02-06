import requests
from geopy.distance import distance

from foodcartapp.models import Order
from django.conf import settings


def get_coordinates(address: str) -> tuple[str, str]:
    try:
        coordinate = fetch_coordinates(settings.GEO_TOKEN, address)
    except requests.exceptions.HTTPError:
        coordinate = None
    return coordinate


def fetch_coordinates(apikey: str, address: str) -> tuple[str, str]:
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


def get_distance(orders: Order) -> Order:
    for order in orders:
        distance_by_restaurant = []
        for restaurant in order.restaurants:
            order_coordinate = get_coordinates(order.address)
            restaurant_coordinate = get_coordinates(restaurant.address)
            space = distance(order_coordinate, restaurant_coordinate).km
            distance_by_restaurant.append((restaurant, round(space, 3)))

        order.restaurants = sorted(distance_by_restaurant, key=lambda x: x[1])
    return orders
