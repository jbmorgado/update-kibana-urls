import requests
import json
from colorama import Fore

# KIBANA_IP = '10.11.115.6'
KIBANA_IP = "10.11.115.13"
OLD_IP = "13.80.150.4"
WARNS = 0

# TODO: Explore possibility of altering scripts as well. These probably must be done outside of the Index Pattern logic. See: https://www.elastic.co/guide/en/elasticsearch/reference/current/create-stored-script-api.html


def get_index_paterns():
    # ploads = {'things':2,'total':25}
    # r = requests.get('https://httpbin.org/get',params=ploads)
    # TODO: add payload
    # TODO: handle `per_page`
    try:
        response = requests.get(
            f"http://{KIBANA_IP}:5601/api/saved_objects/_find?type=index-pattern&search_fields=title&search=*&per_page=1000"
        )
        json_response = response.json()
        print("\tINDEX PATTERNS")
        print("\t--------------")
        print("\tID\t\t\t\t\tTITLE")
        ids = []
        for obj in json_response["saved_objects"]:
            p_id = obj["id"]
            p_title = obj["attributes"]["title"]
            print(f"\t{p_id}\t{p_title}")
            ids.append(p_id)
        return ids
    except:
        print("\tUnable to get index patterns from server.")


def replace_pattern_fields(pattern_id):
    # ploads = {'things':2,'total':25}
    # r = requests.get('https://httpbin.org/get',params=ploads)
    # TODO: add payload
    # TODO: handle `per_page`
    response = requests.get(
        f"http://{KIBANA_IP}:5601/api/index_patterns/index_pattern/{pattern_id}"
    )
    json_response = response.json()
    title = json_response["index_pattern"]["title"]
    print(f"\tParsing index pattern: {title} ({pattern_id})...")
    url = (
        f"http://{KIBANA_IP}:5601/api/index_patterns/index_pattern/{pattern_id}/fields"
    )
    headers = {"kbn-xsrf": "reporting"}
    fields = json_response["index_pattern"]["fields"]
    for field in fields:
        global WARNS
        for item in fields[field]:
            item_str = json.dumps(fields[field][item])
            if OLD_IP in item_str:
                if item == "script":
                    print(
                        Fore.YELLOW
                        + f"\t\tWARNING: field: {field}. Script item cannot be altered by POST request. Alteration must be done manually."
                        + Fore.RESET
                    )
                    WARNS = WARNS + 1
                else:
                    print(f"\t\tReplacing URL in field: {field}")
                    item_str = item_str.replace(OLD_IP, KIBANA_IP)
                    data = (
                        f'{{ "fields": {{ "{field}": {{ "{item}": {item_str} }} }} }}'
                    )
                    response = requests.post(url, headers=headers, data=data)
                    if response.ok:
                        print("\t\t\tSUCCESS")
                    else:
                        print(Fore.RED + "\t\t\tERROR changing field" + Fore.RESET)


if __name__ == "__main__":
    print("Gathering Index Patterns present in the database:")
    ids = get_index_paterns()
    print("")
    if len(ids) > 0:
        print(
            f"Found {len(ids)} Index Patterns.\nReplacing {OLD_IP} IP addresses for {KIBANA_IP}:"
        )
        for id in ids:
            replace_pattern_fields(id)
    else:
        print("No Index Patterns presen in the database. Exiting.")

    if WARNS == 0:
        print("Finished succesfull parsing of all Index Patterns.")
    else:
        print(
            f"Finished parsing of all Index Patterns. There where {WARNS} warnings. Please review them."
        )
