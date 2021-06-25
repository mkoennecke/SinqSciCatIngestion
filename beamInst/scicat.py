#!/usr/bin/env python3
"""SciCat Module"""

import json
import sys
from urllib import parse
import requests


class SciCat:
    """SciCat Client"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = ""

    def login(self, username, password):
        """Login"""
        endpoint = '/api/v3/Users/login'
        url = self.base_url + endpoint
        payload = {"username": username, "password": password} 
        print(payload)
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            sys.exit(res.text)
        else:
            json_res = res.json()
            self.access_token = json_res["id"]
            return json_res["id"]

    def dataset_post(self, dataset):
        """Post Dataset"""
        endpoint = "/Datasets"
        url = self.base_url + endpoint
        params = {"access_token": self.access_token}
        res = requests.post(
            url, json=json.loads(json.dumps(dataset)), params=params
        ).json()
        return res

    def origdatablock_post(self, dataset_pid, origdatablock):
        """Post Dataset Origdatablock"""
        encoded_pid = parse.quote_plus(dataset_pid)
        endpoint = "/Datasets/" + encoded_pid + "/origdatablocks"
        url = self.base_url + endpoint
        params = {"access_token": self.access_token}
        res = requests.post(url, json=origdatablock, params=params).json()
        return res

    def attachment_post(self, dataset_pid, attachment):
        """Post Dataset Attachment"""
        encoded_pid = parse.quote_plus(dataset_pid)
        endpoint = "/Datasets/" + encoded_pid + "/attachments"
        url = self.base_url + endpoint
        params = {"access_token": self.access_token}
        res = requests.post(url, json=attachment, params=params).json()
        return res
