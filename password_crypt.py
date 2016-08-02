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
            "testtoken":getpass("testtoken(Option): ").strip()}

    privacytext = json.dumps(privacy)
    return  encrypt(password,privacytext)

def logIn():
    file_exist = os.path.isfile("privacy.json")
    if file_exist :
        print("File exist")
        hashdata = open("privacy.json","rb").read()
    else:
        print("File no exist")
        hashdata = passwordInit()
        print("OK")
        open("privacy.json","wb").write(hashdata)

    password = getpass("Enter Master password: ")
    jsondata =  decrypt(password,hashdata).decode("utf8")
    print("Password OK")
    #print(json.loads(jsondata))
    return json.loads(jsondata)
