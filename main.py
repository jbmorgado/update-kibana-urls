import requests

KIBANA_IP = '10.11.115.6'
OLD_IP = '13.80.150.4'

def get_index_paterns():
	# ploads = {'things':2,'total':25}
	# r = requests.get('https://httpbin.org/get',params=ploads)
	# TODO: add payload
	# TODO: handle `per_page`
	response = requests.get(f'http://{KIBANA_IP}:5601/api/saved_objects/_find?type=index-pattern&search_fields=title&search=*&per_page=1000')
	json_response = response.json()

	ids = []
	for obj in json_response["saved_objects"]:
		p_id = obj["id"]
		p_title = obj["attributes"]["title"]
		print(p_id, p_title)
		ids.append(p_id)

	return(ids)

def get_pattern_fields(pattern_id):
	# ploads = {'things':2,'total':25}
	# r = requests.get('https://httpbin.org/get',params=ploads)
	# TODO: add payload
	# TODO: handle `per_page`
	response = requests.get(f'http://{KIBANA_IP}:5601/api/index_patterns/index_pattern/{pattern_id}')
	json_response = response.json()

	urls = []
	for obj in json_response["index_pattern"]["fields"].items():
		try:
			field = obj[0]
			url = obj[1]["format"]["params"]["urlTemplate"]
			if OLD_IP in url:
				new_url = url.replace(OLD_IP, KIBANA_IP)
				myobj = {
							'fields': {
								field: {
									'format': {
										'params': {
											'urlTemplate': new_url
										}
									}
								}
							}
						}
				# post_url = f'http://{KIBANA_IP}:5601/api/index_patterns/index_pattern/{pattern_id}/fields'
				post_url = f'http://localhost:5601/api/index_patterns/index_pattern/{pattern_id}/fields'
				requests.post(post_url, data = myobj)
		except:
			None
	
ids = get_index_paterns()
get_pattern_fields('bff63440-95ee-11ea-a3d7-2d6902bc19dd')
