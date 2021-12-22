import requests
import json

# KIBANA_IP = '10.11.115.6'
KIBANA_IP = '10.11.115.13'
OLD_IP = '13.80.150.4'

def get_index_paterns():
	# ploads = {'things':2,'total':25}
	# r = requests.get('https://httpbin.org/get',params=ploads)
	# TODO: add payload
	# TODO: handle `per_page`
	try:
		response = requests.get(f'http://{KIBANA_IP}:5601/api/saved_objects/_find?type=index-pattern&search_fields=title&search=*&per_page=1000')
		json_response = response.json()
		print("INDEX PATTERNS")
		print("--------------")
		print("ID\t\t\t\t\tTITLE")

		ids = []
		for obj in json_response["saved_objects"]:
			p_id = obj["id"]
			p_title = obj["attributes"]["title"]
			print(f"{p_id}\t{p_title}")
			ids.append(p_id)

		return(ids)
	except:
		print("Unable to get index patterns from server.")

def replace_pattern_fields(pattern_id):
	# ploads = {'things':2,'total':25}
	# r = requests.get('https://httpbin.org/get',params=ploads)
	# TODO: add payload
	# TODO: handle `per_page`
	response = requests.get(f'http://{KIBANA_IP}:5601/api/index_patterns/index_pattern/{pattern_id}')
	json_response = response.json()
	title = json_response["index_pattern"]["title"]
	print(f"\nParsing index pattern: {title} ({pattern_id})...")

	url = f'http://{KIBANA_IP}:5601/api/index_patterns/index_pattern/{pattern_id}/fields'
	headers = {"kbn-xsrf": "reporting"}
	fields = json_response["index_pattern"]["fields"]
	for field in fields:
		for item in fields[field]:
			item_str = json.dumps(fields[field][item])
			if OLD_IP in item_str:
				print(f"\tReplacing URL in field: {field}")
				item_str = item_str.replace(OLD_IP, KIBANA_IP)
				data = f'{{ "fields": {{ "{field}": {{ "{item}": {item_str} }} }} }}'
				test = requests.post(url, headers=headers, data = data)
				for item in test:
					print(item)
				exit(0)

ids = get_index_paterns()
if len(ids) > 0:
	replace_pattern_fields('bff63440-95ee-11ea-a3d7-2d6902bc19dd')
