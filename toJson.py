import json

dictionary = {
    "data" : {
        "token" : "BOT_TOKEN",
        "dUserPrefix" : "?",
        "dUserGame" : 0,
        "dUserStatus" : "Testing my bot"
    }
}

json_object = json.dumps(dictionary, indent=4)
print(json_object)
