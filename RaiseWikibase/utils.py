import subprocess
import socket
import requests
import pandas as pd


def execute_shell(command):
    """Run a command in shell and print a live output"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip().decode('ascii'))
    process.poll()


def get_ip():
    """Get and return ip-address (str)

    :return ip: ip-address of a user
    :rtype ip: str
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_wikidata_properties(language='en'):
    """
    Get dataframe with the PIDs, labels, aliases, descriptions and
    datatypes of all properties in Wikidata.

    :param language: A language code for labels, descriptions and aliases. Default is 'en'.
    :type language: str
    :return output: a dataframe with basic info about properties queried from the Wikidata endpoint
    :rtype output: pandas.DataFrame or None
    """
    url = "https://query.wikidata.org/sparql"
    query = """
            SELECT DISTINCT ?propertyWikidata ?propertyLabel ?propertyAlias 
                ?propertyDescription ?propertyType ?fURL ?cURI 
            WHERE {
                ?propertyWikidata wikibase:directClaim ?p;
                wikibase:propertyType ?propertyType;
                schema:description ?propertyDescription;
                rdfs:label ?propertyLabel.
            FILTER((LANG(?propertyLabel)) = """ + '"' + language + '"' + """)
            FILTER((LANG(?propertyDescription)) = """ + '"' + language + '"' + """)
            OPTIONAL { ?propertyWikidata wdt:P1630 ?fURL. }
            OPTIONAL { ?propertyWikidata wdt:P1921 ?cURI. }
            OPTIONAL {?propertyWikidata skos:altLabel ?propertyAlias.
            FILTER((LANG(?propertyAlias)) = """ + '"' + language + '"' + ")}}"
    try:
        r = requests.get(url,
                         params={'format': 'json', 'query': query},
                         headers={'User-Agent': 'RaiseWikibase2021'},
                         timeout=60)
        results = r.json().get('results').get("bindings")
        for prop in results:
            prop.update((key, value.get('value')) for key, value in prop.items())
        if len(results) != 0:
            output = pd.DataFrame(results, dtype=str)
        else:
            output = None
    except Exception:
        output = None

    return output

