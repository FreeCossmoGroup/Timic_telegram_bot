import requests
from Core.Data import server_address


def create_task(params):
    url = server_address + "/tasks/create/"
    response = requests.get(url, params=params)

    return response.json()


def get_all_tasks():
    url = server_address + "/tasks/get/all"
    response = requests.get(url)

    return response.json()
