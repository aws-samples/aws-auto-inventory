# -*- coding: utf-8 -*-
import boto3
import json
import os


def build_service_sheet():
    session = boto3.Session()

    for service_name in session.get_available_services():
        client = session.client(service_name)
        methods = [
            method
            for method in dir(client)
            if callable(getattr(client, method))
            and method.startswith(("get", "describe", "list"))
        ]

        service_sheet = []

        for method in methods:
            service_sheet.append({"service": service_name, "function": method})

        scan_dir = os.path.join("scan", "sample", "services")
        # Ensure the directory exists
        os.makedirs(scan_dir, exist_ok=True)

        with open(os.path.join(scan_dir, f"{service_name}.json"), "w") as f:
            json.dump(service_sheet, f)


build_service_sheet()
