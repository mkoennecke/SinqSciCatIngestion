#!/usr/bin/env python3
"""SciCat Module"""

import json
import sys
from urllib import parse
import requests
from pathlib import Path
import time


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

    def loginPSI(self, username, password):
        """Login"""
        endpoint = '/auth/msad'
        url = self.base_url + endpoint
        payload = {"username": username, "password": password} 
        print(payload)
        res = requests.post(url, json=payload)
        if res.status_code != 200:
            sys.exit(res.text)
        else:
            json_res = res.json()
            self.access_token = json_res["access_token"]
            return json_res["access_token"]

    def dataset_post(self, dataset):
        """Post Dataset"""
        endpoint = "/api/v3/Datasets"
        url = self.base_url + endpoint
        params = {"access_token": self.access_token}
        res = requests.post(
            url, json=json.loads(json.dumps(dataset)), params=params
        ).json()
        return res

    def package_file(self, filename):
        """
        Package a file into the required datablock structure
        for SciCat
        """
        entry = {}
        # Get to the real file, we are looking at symlinks here
        p = Path(filename).resolve()
        stat = p.stat()
        entry['path'] = str(p)
        entry['size'] = stat.st_size
        entry['gid'] = stat.st_gid
        entry['uid'] = stat.st_uid
        tt = time.localtime(stat.st_ctime)
        entry['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', tt)
        entry['perm'] = oct(stat.st_mode)[-3:]
        datablock = {}
        datablock['size'] = entry['size']
        datablock['dataFileList'] = [entry,]
        datablock['datasetId']='Undefined'
        return datablock

    def origdatablock_post(self, dataset_pid, origdatablock):
        """Post Dataset Origdatablock"""
        encoded_pid = parse.quote_plus(dataset_pid)
        endpoint = "/api/v3/Datasets/" + encoded_pid + "/origdatablocks"
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

    def read_proposal(self, proposal_id):
        encoded_proposal=parse.quote_plus(proposal_id)
        endpoint = '/api/v3/Proposals/' + encoded_proposal
        url = self.base_url + endpoint
        params = {"access_token": self.access_token}
        res = requests.get(url, params=params)
        if res.status_code != 200:
            return None
        return res
