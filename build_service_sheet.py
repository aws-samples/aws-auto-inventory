import boto3
import json

def build_service_sheet():
    session = boto3.Session()

    service_sheet = []

    for service_name in session.get_available_services():
        client = session.client(service_name)
        methods = [method for method in dir(client) if callable(getattr(client, method)) and method.startswith(('get', 'describe', 'list'))]

        for method in methods:
            service_sheet.append({
                "service": service_name,
                "function": method
            })

    with open('service_sheet.json', 'w') as f:
        json.dump(service_sheet, f)

build_service_sheet()
