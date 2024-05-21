import json

with open("zerobias_files.txt", 'r') as file:
    lines = file.readlines()

lines = [line.strip() for line in lines]

json_data = json.dumps(lines, indent=4)

with open("zerobias_files.json", 'w') as json_file:
    json_file.write(json_data)
