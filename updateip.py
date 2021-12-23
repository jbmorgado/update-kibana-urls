import argparse
import requests
import json
from colorama import Fore

WARNS = 0


def get_index_paterns(ip):
    """
    Retrieves all the Index Patterns present at the elasticsearch deployment with ip {ip}.
    :param ip: the IP of the elasticsearch deployment
    :return: list with Index Patterns ID identifier
    """
    ids = []
    try:
        response = requests.get(
            f"http://{ip}:5601/api/saved_objects/_find?type=index-pattern&search_fields=title&search=*&per_page=1000"
        )
        json_response = response.json()
        print("\tINDEX PATTERNS")
        print("\t--------------")
        print("\tID\t\t\t\t\tTITLE")
        for obj in json_response["saved_objects"]:
            p_id = obj["id"]
            p_title = obj["attributes"]["title"]
            print(f"\t{p_id}\t{p_title}")
            ids.append(p_id)
        return ids
    except:
        print("\tUnable to get index patterns from server.")


def replace_fields_ip(id, ip, old_ip):
    """
    Iterates over all fields in an Index Pattern and replaces any occurrence of {old_ip} for {ip}.
    This method doesn't work on script fields and at the present those must be altered manually.
    TODO: Explore possibility of altering scripts as well. These probably must be done outside of the Index Pattern logic.
    See: https://www.elastic.co/guide/en/elasticsearch/reference/current/create-stored-script-api.html
    :param id: the id of the Index Pattern
    :param ip: the proper ip address of the elasticsearch deployment
    :param old_ip: the outdated ip that we will be replacing
    """
    response = requests.get(f"http://{ip}:5601/api/index_patterns/index_pattern/{id}")
    json_response = response.json()
    title = json_response["index_pattern"]["title"]
    print(f"\tParsing index pattern: {title} ({id})...")
    url = f"http://{ip}:5601/api/index_patterns/index_pattern/{id}/fields"
    headers = {"kbn-xsrf": "reporting"}
    fields = json_response["index_pattern"]["fields"]
    for field in fields:
        global WARNS
        for item in fields[field]:
            item_str = json.dumps(fields[field][item])
            if old_ip in item_str:
                if item == "script":
                    print(
                        Fore.YELLOW
                        + f"\t\tWARNING: field: {field}. Script item cannot be altered by POST request. Alteration must be done manually."
                        + Fore.RESET
                    )
                    WARNS = WARNS + 1
                else:
                    print(f"\t\tReplacing URL in field: {field}")
                    item_str = item_str.replace(old_ip, ip)
                    data = (
                        f'{{ "fields": {{ "{field}": {{ "{item}": {item_str} }} }} }}'
                    )
                    response = requests.post(url, headers=headers, data=data)
                    if response.ok:
                        print("\t\t\tSUCCESS")
                    else:
                        print(Fore.RED + "\t\t\tERROR changing field" + Fore.RESET)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-ip",
        type=str,
        default="10.11.115.6",
        help="IP address of elasticsearch deployment",
        required=False,
    )
    parser.add_argument(
        "-old-ip",
        type=str,
        default="13.80.150.4",
        help="IP address to replace",
        required=False,
    )
    args = parser.parse_args()

    print("Gathering Index Patterns present in the database:")
    ids = get_index_paterns(args.ip)
    print("")
    if len(ids) > 0:
        print(
            f"Found {len(ids)} Index Patterns.\nReplacing {args.old_ip} IP addresses for {args.ip}:"
        )
        for id in ids:
            replace_fields_ip(id, args.ip, args.old_ip)
    else:
        print("No Index Patterns present in the database. Exiting.")

    if WARNS == 0:
        print("Finished succesfull parsing of all Index Patterns.")
    else:
        print(
            f"Finished parsing of all Index Patterns. There where {WARNS} warnings. Please review them."
        )
