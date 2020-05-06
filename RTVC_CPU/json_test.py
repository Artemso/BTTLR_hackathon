import json
import sys

with open(sys.argv[1]) as text_json:
	data = json.load(text_json)
	for key in data:
		print(key['translation'])