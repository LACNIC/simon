__author__ = 'agustin'

import json, sys, subprocess

file_name = sys.argv[1]
json_name = sys.argv[2]

with open(json_name, "r") as f:
    obj = json.loads(f.read())
num_of_tests = len(obj)

process = []

for counter in range(num_of_tests):
    cmd = "python %s %s %s" % (str(file_name), str(json_name), str(counter))
    process.append(subprocess.Popen(cmd, shell=True))

# Wait for all chunk's processes to finish (n subprocesses)
for counter in range(num_of_tests):
    process[counter].wait()