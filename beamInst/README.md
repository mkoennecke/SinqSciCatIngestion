# beamInst

- Reads hdf5 file from Beam group and posts groups to scicat
- Plots datasets as attachment 
- See https://confluence.esss.lu.se/display/BIG/Data+format+proposal for format
- 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
h5py
matplotlib
requests
```

### Installing

How to install

```
pipenv install
```

### Running

To simply read a file without ingesting it to SciCat, run

```
python file_reader.py path/to/file
```

To ingest a file into scicat, set up config.json with your credentials and set the base url in ingest_file.py, then run

```
python ingest_file.py path/to/file
```

This will ingest a dataset along with the origDatablocks. If the script is able to generate plots from the data, these will be ingested as attachments.

## Running the tests

Explain how to run the automated tests for this system

```
pytest
```

### And coding style tests

Explain what these tests test and why

```
pylint
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

- [Pipenv](https://github.com/pypa/pipenv) - Python development framework

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

- **Gareth Murphy** - _Initial work_ - [garethcmurphy](https://github.com/garethcmurphy)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

- Hat tip to anyone whose code was used
- Inspiration
- etc
- 

## Functions


