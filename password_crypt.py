from getpass import getpass
from simplecrypt import encrypt, decrypt
from base64 import b64decode, b64encode
import json
import os.path

import ColorPrint
colorPrint = ColorPrint.setPrint("PassWord")
filepath = "data/privacy.json"


def privacyAsk(need):
    func = input
    if need.get("secret"):
        func = getpass
    text = ""
    if need.get("desp"):
        print(need['desp'])

    default = "(Default='" + str(need['default']) + \
        "')" if need.get("default") is not None else ""
    inp = func(need['name'] + default + ": ").strip()
    if default and not inp:
        return need['default']
    else:
        return inp


def dictUpdate(dic, old, need):
    if need['name'] in dic:  # duplicated
        return
    if need['name'] not in old:
        dic.update({need['name']: privacyAsk(need)})
    else:
        dic.update({need['name']: old[need['name']]})


def fileOpen():
    # privacy file
    dict_privacy = {}
    if os.path.isfile(filepath):
        dict_privacy = json.load(open(filepath))
    return dict_privacy


def moduleNumber(module_name):
    dict_privacy = fileOpen()
    new_number_mod = {}
    for modname in module_name:
        dictUpdate(new_number_mod, dict_privacy, {
            'name': "_number_of_" + modname,
            'default': 1})
    for item in new_number_mod:
        new_number_mod[item] = int(new_number_mod[item])

    dict_privacy = {key: val for key, val in dict_privacy.items() if
                    not key.startswith("_number_of_")}
    dict_privacy.update(new_number_mod)
    json.dump(dict_privacy, open(filepath, "w"), sort_keys=True, indent=4)
    return {key[11:]: val for key, val in new_number_mod.items()}


def logIn(needprivacy):
    # password
    dict_privacy = fileOpen()
    file_exist = bool(dict_privacy.get("hash"))
    colorPrint("Config Data Exist", file_exist)
    if file_exist:
        password = getpass("Enter Master password: ")
    else:
        password = getpass("Set Master password: ")

    # decode data
    dict_hash = {}
    if dict_privacy.get("hash"):
        hashdata = b64decode(dict_privacy['hash'])
        dict_hash = json.loads(decrypt(password, hashdata).decode("utf8"))

    # get new data
    new_privacy = {'hash': dict_privacy.get('hash', {})}
    new_hash = {}
    for pri in needprivacy:
        if pri.get('module'):
            continue
        if pri['name'] == 'hash':
            raise NameError("No hash key")
        if pri.get('secret'):
            dictUpdate(new_hash, dict_hash, pri)
        else:
            dictUpdate(new_privacy, dict_privacy, pri)

    new_privacy.update({key: val for key, val in dict_privacy.items() if
                        key.startswith("_number_of_")})

    # check with old data
    if new_hash != dict_hash:
        hashdata = json.dumps(new_hash, sort_keys=True, indent=4)
        new_privacy['hash'] = b64encode(
            encrypt(password, hashdata)).decode("utf8")
    if new_privacy != dict_privacy:
        open(filepath, "w").write(json.dumps(
            new_privacy, sort_keys=True, indent=4))

    colorPrint("Password Correct")
    return {**new_privacy, **new_hash}
