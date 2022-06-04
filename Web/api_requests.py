import requests
from Core.Data import duration, description, start_time, duration, fixed, parent, server_address


def create_task(params):
    url = server_address + "/tasks/create/"
    response = requests.get(url, params=params)

    return response.json()
