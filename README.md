[![Eclipse VOLTTRON™](https://img.shields.io/badge/Eclips%20VOLTTRON--red.svg)](https://eclipse-volttron.readthedocs.io/en/latest/)
![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
[![Run Pytests](https://github.com/eclipse-volttron/volttron-lib-tagging/actions/workflows/run-tests.yml/badge.svg)](https://github.com/eclipse-volttron/volttron-lib-tagging/actions/workflows/run-tests.yml)
[![pypi version](https://img.shields.io/pypi/v/volttron-lib-tagging.svg)](https://pypi.org/project/volttron-lib-tagging/)

VOLTTRON base tagging library that provide common tagging api for users to associate haystack based tags and values to 
topic names and topic name prefixes. Implementing agents can persist tags in specific data store. 

Tags used by this library have to be pre-defined in a resource file at volttron_data/tagging_resources. The
library validates against this predefined list of tags every time user add tags to topics. Tags can be added to one 
topic at a time or multiple topics by using a topic name pattern(regular expression). This library uses tags from 
[project haystack](https://project-haystack.org/) and adds a few custom tags for campus and VOLTTRON point name.

Each tag has an associated value and users can query for topic names based tags and its values using a simplified 
sql-like query string. Queries can specify tag names with values or tags without values for boolean tags(markers). 
Queries can combine multiple conditions with keyword AND, and OR, and use the keyword NOT to negate a conditions.

## Requirements

 - Python >= 3.10

## Installation

This library can be installed using ```pip install volttron-lib-tagging```. However, this is not necessary. Any 
implementing tagging agent that uses this library will automatically install it as part of its installation. 
For example,  installing [SQLiteTaggingAgent](https://github.com/eclipse-volttron/volttron-sqlite-tagging) will 
automatically install volttron-lib-tagging into the same python environment

## Dependencies and Limitations

1. When adding tags to topics this library calls the platform.historian's (or a configured historian's) 
   get_topic_list and hence requires a platform.historian or configured historian to be running, but it doesn't require 
   the historian to use sqlite3 or any specific database. It requires historian to be running only for using this 
   api (add_tags) and does not require historian to be running for any other api. 
2. Resource files that provides the list of valid tags is mandatory and should be in 
   data_model/tags.csv
3. Tagging library only provides APIs to query for topic names based on tags. Once the list of topic names is retrieved, 
   users should use the historian APIs to get the data corresponding to those topics. 
4. Current version of tagging library does not support versioning of tag/values. When tags values are set it will 
   overwrite any existing tag entries in the database

## Development

Please see the following for contributing guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).

Please see the following helpful guide about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)

# Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
