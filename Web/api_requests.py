import requests
from Core.Data import server_address


def create_task(params):
    url = server_address + "/tasks/create/"
    return requests.get(url, params=params).json()


def get_all_tasks():
    url = server_address + "/tasks/get/all"
    return requests.get(url).json()


def modify_task(params):
    url = server_address + "/tasks/modify"
    return requests.get(url, params=params).json()
