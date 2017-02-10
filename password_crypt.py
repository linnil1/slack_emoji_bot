from getpass import getpass
from simplecrypt import encrypt, decrypt
from base64 import b64decode, b64encode
import json
import os.path

import ColorPrint
colorPrint = ColorPrint.setPrint("PassWord")

def privacyAsk(need):
    func = input
    if need.get("secret"):
        func = getpass
    text = ""
    if need.get("desp"):
        print(need['desp'])
        
    default = "(Default='"+str(need['default'])+"')" if need.get("default") is not None else ""
    inp = func(need['name']+default+": ").strip()
    if default and not inp:
        return need['default']
    else:
        return inp

def dictUpdate(dic,old,need):
    if need['name'] in dic: # duplicated
        return 
    if need['name'] not in old:
        dic.update({need['name']:privacyAsk(need) })
    else:
        dic.update({need['name']:old[need['name']]})

def logIn(needprivacy):
    #pprint(needprivacy)
    # privacy file
    filepath = "data/privacy.json"
    file_exist = os.path.isfile(filepath)
    dict_privacy = {}
    colorPrint("Config Data Exist",file_exist)
    if file_exist :
        dict_privacy= json.loads(open(filepath).read())
        password = getpass("Enter Master password: ")
    else:
        password = getpass("Set Master password: ")

    # decode data
    dict_hash = {}
    if dict_privacy.get("hash"):
        hashdata  = b64decode(dict_privacy['hash'])
        dict_hash = json.loads(decrypt(password,hashdata).decode("utf8"))

    # get new data
    new_privacy = {'hash':dict_privacy['hash']} if dict_privacy.get("hash") else {}
    new_hash    = {}
    for pri in needprivacy:
        if pri.get('module'):
            continue
        if pri['name'] == 'hash':
            raise NameError("No hash key")
        if pri.get('secret'):
            dictUpdate(new_hash,dict_hash,pri)
        else:
            dictUpdate(new_privacy,dict_privacy,pri)

    # check with old data
    if new_hash != dict_hash :
        hashdata = json.dumps(new_hash)
        new_privacy['hash'] = b64encode(encrypt(password,hashdata)).decode("utf8")
    if new_privacy != dict_privacy:
        open(filepath,"w").write(json.dumps(new_privacy))

    colorPrint("Password Correct")
    return {**new_privacy,**new_hash}
