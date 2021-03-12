#!/usr/bin/env python3
"""ingest beam diagnostics file to scicat"""

import json
import os
import shutil
import sys
from beamInst.file_reader import FileReader
from beamInst.attachment import Attachment
from beamInst.scicat import SciCat


def main(args):
    """main"""
    # file_name = str(args[0])
    # file_reader = FileReader()
    # file_reader.read(file_name)

    scicat = SciCat("http://localhost:3000")
    with open("config.json") as json_file:
        credentials = json.load(json_file)
        scicat.login(credentials["username"], credentials["password"])

    attachment = Attachment()
    i = 0
    for dataset in file_reader.datasets:
        i += 1
        dataset_res = scicat.dataset_post(dataset)
        print(dataset_res)
        dataset_attachment = attachment.create(dataset_res["pid"], f"plots/phs{i}.png")
        dataset_attachment_res = scicat.attachment_post(
            dataset_res["pid"], dataset_attachment
        )
        print(dataset_attachment_res)

    for datablock in file_reader.origdatablocks:
        datablock_res = scicat.origdatablock_post(datablock["datasetId"], datablock)
        print(datablock_res)

    if os.path.exists("plots"):
        shutil.rmtree("plots")


if __name__ == "__main__":
    main(sys.argv[1:])
