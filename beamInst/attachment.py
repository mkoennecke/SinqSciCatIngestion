#!/usr/bin/env python3
"""create attachment for scicat"""

import base64
import json
import os
import sys


class Attachment:
    """create attachment for scicat"""

    def create(self, dataset_pid, file_name):
        """create attachment"""
        thumbnail = self.base64encode(file_name)
        assert isinstance(thumbnail, str)
        return {
            "thumbnail": thumbnail,
            "caption": self.parse_file_name(file_name),
            "ownerGroup": "ess",
            "accessGroups": ["ess", "odin", "loki", "nmx"],
            "datasetId": dataset_pid,
        }

    def base64encode(self, file_name):
        """base 64 encode a file"""
        if os.path.exists(file_name):
            header = "data:image/png;base64,"
            with open(file_name, "rb") as image:
                data = image.read()
                image_bytes = base64.b64encode(data)
                image_str = image_bytes.decode("UTF-8")
                return header + image_str
        else:
            return ""

    def parse_file_name(self, file_name):
        """remove path from file name"""
        if "/" in file_name:
            split_file_name = file_name.split("/")
            for part in split_file_name:
                if ".png" in part:
                    return part
        else:
            return file_name


def main(args):
    """main"""
    file_name = str(args[0])
    attachment = Attachment()
    scicat_attachment = attachment.create("testPid123", file_name)
    print(json.dumps(scicat_attachment, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
