#!/usr/bin/env python3
"""File reader module"""

import datetime
import json
import os
import sys
import h5py
import matplotlib.pyplot as plt


class FileReader:
    """File reader"""

    def __init__(self):
        self.datasets = []
        self.origdatablocks = []
        self.dataset = {
            "contactEmail": "clement.derrez@ess.eu",
            "creationTime": datetime.datetime.now().isoformat(),
            "owner": "Clement Derrez",
            "principalInvestigator": "Clement Derrez",
            "proposalId": "ZJKF12",
            "creationLocation": "ZJKF12",
            "ownerGroup": "ess",
            "sourceFolder": "http://meas01.esss.lu.se/owncloud/index.php/apps/files/?dir=/FCFE",
            "keywords": ["beam_test"],
            "type": "raw",
        }
        self.origdatablock = {
            "size": 0,
            "dataFileList": [
                {
                    "path": "",
                    "size": 0,
                    "time": datetime.datetime.now().isoformat(),
                    "chk": "34782",
                    "uid": "101",
                    "gid": "101",
                    "perm": "755",
                }
            ],
            "ownerGroup": "ess",
            "accessGroups": ["ess", "odin", "loki", "nmx"],
            "createdBy": "ingestor",
            "datasetId": "20.500.12269/beam_test1",
        }
        self.orig_file_name = ""
        self.fixed_file_name = ""

    __pid_prefix = "20.500.12269/"

    def read(self, file_name):
        """Read hdf5 file"""
        print(f"Reading file: {file_name}")
        parsed_file_name = self.__parse_file_name(file_name)
        self.orig_file_name = file_name
        self.fixed_file_name = parsed_file_name
        pid_file_name = self.__extract_pid(parsed_file_name)

        file_size = self.__get_file_size(parsed_file_name)
        self.origdatablock["size"] = file_size
        for data_file in self.origdatablock["dataFileList"]:
            data_file["path"] = self.orig_file_name.split("/")[-1]
            data_file["size"] = file_size

        hdf5_file = h5py.File(parsed_file_name, "r")
        entry_name = list(hdf5_file.keys()).pop()
        nx_entry = hdf5_file[entry_name]
        nx_entry_attributes = dict(list(nx_entry.attrs.items()))
        user_dict = self.__get_user_dict(nx_entry)

        self.dataset["principalInvestigator"] = user_dict["name"]
        self.dataset["owner"] = user_dict["name"]

        nx_instruments = self.__get_instruments(nx_entry)
        group_number = 0
        for group in nx_instruments:
            group_number += 1
            print(group)
            group_attributes = self.__get_group_attributes(nx_instruments, group)
            print(group_attributes)
            self.dataset["scientificMetadata"] = self.__format_scientific_metadata(
                nx_entry_attributes, group_attributes
            )
            self.dataset["description"] = group_attributes["description"]
            self.dataset["datasetName"] = group
            self.dataset["creationTime"] = nx_entry_attributes.get("start_time")
            self.dataset["pid"] = pid_file_name + "_" + str(group_number)
            self.origdatablock["datasetId"] = self.__pid_prefix + self.dataset["pid"]
            for data_file in self.origdatablock["dataFileList"]:
                data_file["time"] = nx_entry_attributes.get("start_time")
            self.origdatablocks.append(self.origdatablock.copy())

            arrays = {}
            i = 0
            for dset in nx_instruments[group].keys():
                i += 1
                arrays[dset] = nx_instruments[group][dset]
                self.dataset["scientificMetadata"][dset] = dset
            self.__plot_arrays(arrays, group_number)
            self.datasets.append(self.dataset.copy())

    def __get_user_dict(self, nx_entry):
        nx_entry_contents = list(nx_entry.keys())
        if "NXUSER" in nx_entry:
            nx_user = nx_entry["NXUSER"]
            user_dict = dict(list(nx_user.attrs.items()))
            return user_dict
        elif "user" in nx_entry_contents:
            nx_user = nx_entry["user"]
            user_dict = dict(list(nx_user.attrs.items()))
            return user_dict
        else:
            sys.exit("Could not find user information in file")

    def __get_instruments(self, nx_entry):
        nx_entry_contents = list(nx_entry.keys())
        if "NXInstruments" in nx_entry_contents:
            return nx_entry["NXInstruments"]
        elif "instruments" in nx_entry_contents:
            return nx_entry["instruments"]
        else:
            sys.exit("Could not find intstrument information in file")

    def __get_group_attributes(self, instruments, group):
        group_attributes = dict(list(instruments[group].attrs.items()))
        if "NX_class" in group_attributes:
            group_attributes.pop("NX_class")
        elif "NXClass" in group_attributes:
            group_attributes.pop("NXClass")
        return group_attributes

    def __parse_file_name(self, file_name):
        if " " in file_name:
            split_file_name = file_name.split(" ")
            fixed_file_name = "".join(split_file_name)
            os.rename(file_name, fixed_file_name)
            return fixed_file_name
        else:
            return file_name

    def __extract_pid(self, file_name):
        if "/" in file_name:
            file_name = file_name.split("/")[-1]
        if "." in file_name:
            file_name = file_name.split(".")[0]
        return file_name

    def __plot_arrays(self, arrays, group_number):
        """plot"""
        if len(arrays) > 0:
            if "plots" not in os.listdir():
                os.mkdir("plots")

            i = 0
            number_of_plots = len(arrays.keys())
            print(f"Number of plots: {number_of_plots}")
            plt.figure(figsize=(8, 12))
            for key in arrays:
                i += 1
                plt.subplot(number_of_plots, 1, i)
                plt.plot(arrays[key])
                ylabel = key.split("_")[1]
                plt.ylabel(ylabel)
            plt.savefig(f"plots/phs{group_number}.png")
            plt.close()

    def __get_file_size(self, file_name):
        return os.stat(file_name).st_size

    def __format_scientific_metadata(self, nx_entry_attributes, group_attributes):
        parameters = {}
        for key in group_attributes.keys():
            if "." in group_attributes[key]:
                try:
                    group_attributes[key] = float(group_attributes[key])
                except ValueError:
                    pass
            else:
                try:
                    group_attributes[key] = int(group_attributes[key])
                except ValueError:
                    pass
            if isinstance(group_attributes[key], (int, float)):
                parameters[key] = {
                    "type": "number",
                    "value": group_attributes[key],
                    "unit": "",
                }
            elif isinstance(group_attributes[key], str):
                parameters[key] = {
                    "type": "string",
                    "value": group_attributes[key],
                    "unit": "",
                }
        if "entry_identifier" in nx_entry_attributes:
            parameters["entry_identifier"] = {
                "type": "number",
                "value": int(nx_entry_attributes["entry_identifier"]),
                "unit": "",
            }
        return parameters


def main(args):
    """main"""
    file_name = str(args[0])
    file_reader = FileReader()
    file_reader.read(file_name)
    print(json.dumps(file_reader.datasets, indent=2))
    print(json.dumps(file_reader.origdatablocks, indent=2))
    os.rename(file_reader.fixed_file_name, file_reader.orig_file_name)


if __name__ == "__main__":
    main(sys.argv[1:])
