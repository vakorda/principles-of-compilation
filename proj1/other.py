import json

# write a file for each test case in tests folder

with open("teses.json", "r") as f:
    tests = json.load(f)
    for test in tests:
        with open("tests/" + test["name"] + ".txt", "w") as f:
            f.write(test["prog"])