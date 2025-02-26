import datetime
import re
from warnings import warn

"""
The template provides one other helper module, being the `escape_helpers`-module. It contains functions for SPARQL query-escaping. Example import:
```py
from escape_helpers import *
```

Available functions:
"""

def sparql_escape_string(obj):
    """Converts the given string to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, str):
        warn("You are escaping something that isn't a string with \
        the 'sparql_escape_string'-method. Implicit casting will occurr.")
        obj = str(obj)
    return '"""' + re.sub(r'[\\\'"]', lambda s: "\\" + s.group(0), obj) + '"""'

def sparql_escape_datetime(obj):
    """Converts the given datetime to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, datetime.datetime):
        warn("You are escaping something that isn't a datetime with \
        the 'sparql_escape_datetime'-method. Implicit casting will occurr.")
        obj = datetime.datetime.fromisoformat(str(obj)) # only supports 3 or 6 digit microsecond notation (https://docs.python.org/3.7/library/datetime.html#datetime.datetime.fromisoformat)
    return '"{}"^^xsd:dateTime'.format(obj.isoformat())

def sparql_escape_date(obj):
    """Converts the given date to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, datetime.date):
        warn("You are escaping something that isn't a date with \
        the 'sparql_escape_date'-method. Implicit casting will occurr.")
        obj = datetime.date.fromisoformat(str(obj))
    return '"{}"^^xsd:date'.format(obj.isoformat())

def sparql_escape_time(obj):
    """Converts the given time to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, datetime.time):
        warn("You are escaping something that isn't a time with \
        the 'sparql_escape_time'-method. Implicit casting will occurr.")
        obj = datetime.time.fromisoformat(str(obj)) # only supports 3 or 6 digit microsecond notation (https://docs.python.org/3.7/library/datetime.html#datetime.time.fromisoformat)
    return '"{}"^^xsd:time'.format(obj.isoformat())

def sparql_escape_int(obj):
    """Converts the given int to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, int):
        warn("You are escaping something that isn't an int with \
        the 'sparql_escape_int'-method. Implicit casting will occurr.")
        obj = str(int(obj))
    return '"{}"^^xsd:integer'.format(obj)

def sparql_escape_float(obj):
    """Converts the given float to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, float):
        warn("You are escaping something that isn't a float with \
        the 'sparql_escape_float'-method. Implicit casting will occurr.")
        obj = str(float(obj))
    return '"{}"^^xsd:float'.format(obj)

def sparql_escape_bool(obj):
    """Converts the given bool to a SPARQL-safe RDF object string with the right RDF-datatype. """
    if not isinstance(obj, bool):
        warn("You are escaping something that isn't a bool with \
        the 'sparql_escape_bool'-method. Implicit casting will occurr.")
        obj = bool(obj)
    return '"{}"^^xsd:boolean'.format("true" if obj else "false")

def sparql_escape_uri(obj):
    """Converts the given URI to a SPARQL-safe RDF object string with the right RDF-datatype. """
    obj = str(obj)
    return '<' + re.sub(r'[\\"<>]', lambda s: "\\" + s.group(0), obj) + '>'

def sparql_escape(obj):
    """
    Converts the given object to a SPARQL-safe RDF object string with the right RDF-datatype. 

    These functions should be used especially when inserting user-input to avoid SPARQL-injection.
    Separate functions are available for different python datatypes.
    The `sparql_escape` function however can automatically select the right method to use, for the following Python datatypes:

    - `str`
    - `int`
    - `float`
    - `datetime.datetime`
    - `datetime.date`
    - `datetime.time`
    - `boolean`

    The `sparql_escape_uri`-function can be used for escaping URI's.
    """
    if isinstance(obj, str):
        escaped_val = sparql_escape_string(obj)
    elif isinstance(obj, datetime.datetime):
        escaped_val = sparql_escape_datetime(obj)
    elif isinstance(obj, datetime.date):
        escaped_val = sparql_escape_date(obj)
    elif isinstance(obj, datetime.time):
        escaped_val = sparql_escape_time(obj)
    elif isinstance(obj, int):
        escaped_val = sparql_escape_int(obj)
    elif isinstance(obj, float):
        escaped_val = sparql_escape_float(obj)
    elif isinstance(obj, bool):
        escaped_val = sparql_escape_bool(obj)
    else:
        warn("Unknown escape type '{}'. Escaping as string".format(type(obj)))
        escaped_val = sparql_escape_string(obj)
    return escaped_val
