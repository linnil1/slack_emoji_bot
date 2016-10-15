from getpass import getpass
from simplecrypt import encrypt, decrypt
import json
import os.path

def passwordInit():
    password = getpass("Set Master password: ")
    privacy = {
            "team_name":input("team_name: ").strip(),
            "email":input("email: ").strip(),
            "password":getpass("password: ").strip(),
            "token":getpass("token: ").strip(),
            "testtoken":getpass("testtoken(Option): ").strip(),
            "imgur_id":input("imgur_id: ").strip(),
            "imgur_secret":getpass("imgur_serect: ").strip(),
            "wolfram_app":getpass("wolfram_app: ").strip()
            }

    privacytext = json.dumps(privacy)
    return  encrypt(password,privacytext)

def logIn():
    filepath = "data/privacy.json"
    file_exist = os.path.isfile(filepath)
    if file_exist :
        print("File exist")
        hashdata = open(filepath,"rb").read()
    else:
        print("File no exist")
        hashdata = passwordInit()
        print("OK")
        open(filepath,"wb").write(hashdata)

    password = getpass("Enter Master password: ")
    jsondata =  decrypt(password,hashdata).decode("utf8")
    print("Password OK")
    #print(json.loads(jsondata))
    return json.loads(jsondata)
