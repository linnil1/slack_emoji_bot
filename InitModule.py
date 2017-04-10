import os
import sys
import re
import importlib
import copy

import password_crypt
import RunData
from slackclient import SlackClient
from ColorPrint import *
sys.path.insert(0, './modules/')
sys.path.insert(0, './common/')


class SLACK():
    def require():
        return [{"name": "TOKEN", "secret": True}]

    def __init__(self, privacy):
        self._slack = SlackClient(privacy['TOKEN'])

    def api_call(self, *args, **kwargs):
        return self._slack.api_call(*args, **kwargs)

    def tokenGet(self):  # it should be private
        return self._slack.token


class BASE():
    def require():
        return [
            {"name": "TOKEN", "secret": True},
            {"name": "postchannel", "default": "workstation"},
            {"name": "postman", "default": "linnil1"}]

    def __init__(self, privacy):
        self._data = {
            'TOKEN': privacy["TOKEN"],
            'postchannel': privacy["postchannel"],
            'postman': privacy["postman"]}

    def get(self, key):
        return self._data[key]


def modulesGet():
    modules = [{
        'class': BASE,
        'name': "",
        'type': "common"}]

    imports_file = [f for f in os.listdir("common") if f.endswith(".py")]
    for import_file in imports_file:
        module = importlib.import_module(import_file[:-3])
        modules.append({
            'class': getattr(module, import_file[:-3]),
            'name': import_file[:-3],
            'type': "common"})

    imports_file = [f for f in os.listdir(
        "modules") if f.endswith("_command.py")]

    command_modules = []
    for import_file in imports_file:
        module = importlib.import_module(import_file[:-3])
        module_name = re.findall(r"(\w+)_command\.py", import_file)[0]
        command_modules.append({
            'class': getattr(module, module_name),
            'name': module_name,
            'type': "command"})

    # number of modules
    mod_number = password_crypt.moduleNumber([
        mod['name'] for mod in command_modules])
    for mod in command_modules:
        for num in range(0, mod_number[mod['name']]):
            copymods = copy.deepcopy(mod)
            if num:
                copymods['name'] += str(num)
            modules.append(copymods)

    return modules


""" require format
{
  'name': "APPID", # name should not use data
  'secret': True, # it will not show on console when writing
  'desp' : "xxx uuuu werwerf skdjfslkdjf", #describition of the key
  'default' : "123" # this will return string
  'module' : True # this will return the class in common
  'other' : True # this is for asking other's data.
                 # The name should be like _TOKEN
}
"""


def requiresGet(modules):
    requires = []
    others = []
    for module in modules:
        module['require'] = module['class'].require()
        reqs = copy.deepcopy(module['require'])
        for req in reqs:
            if not req.get('other'):
                req['name'] = module['name'] + "_" + req['name']
                requires.append(req)
            else:
                others.append(req['name'])

    # check other's data is exist
    for other in others:
        for req in requires:
            if req['name'] == other:
                break
        else:
            raise ValueError("cannot find " + other)

    return requires


def privacyFilter(privacy, module, commons={}):
    giveprivacy = {}
    for req in module['require']:
        if req.get("module"):
            giveprivacy[req['name']] = commons[req['name']]
        elif req.get("other"):
            giveprivacy[req['name']] = privacy[req['name']]
        else:
            giveprivacy[req['name']] = \
                privacy[module['name'] + "_" + req['name']]
    return giveprivacy


def dependFind(modules):
    common_modules = {}
    count_modules = {}
    for module in modules:
        if module['type'] == 'common':
            common_modules[module['name']] = module
            count_modules[module['name']] = 0
    for key, module in common_modules.items():
        for require in module['require']:
            if require.get("module"):
                count_modules[require['name']] += 1

    topo_modules = []
    for c in range(len(common_modules)):
        for name, num in count_modules.items():
            if num == 0:
                topo_modules.append(common_modules[name])
                count_modules[name] = -1
        for name, num in count_modules.items():
            if num == -1:
                for req in common_modules[name]['require']:
                    if require.get("module"):
                        count_modules[req['name']] -= 1

        count_modules = \
            {key: value for key, value in count_modules.items() if value >= 0}

    if count_modules:
        raise ValueError("It may have circular dependency")
    return list(reversed(topo_modules))


def initSet(privacy, modules):
    modules = dependFind(modules) + \
        [module for module in modules if module['type'] == 'command']

    # always add data
    slack = SLACK({"TOKEN": privacy['_TOKEN']})
    database = RunData.RunDataBase()

    commons = {}
    newmodules = []
    for module in modules:
        pri = privacyFilter(privacy, module, commons)
        pri.update({"data": RunData.RunData(database, module['name'])})
        pri.update({"colorPrint": setPrint(module['name'])})

        if module['type'] == 'command':
            newmodules.append(module['class'](slack, pri))
        elif module['type'] == 'common':
            commons[module['name']] = module['class'](pri)

    return newmodules, commons['']


def modulesInit():
    modules = modulesGet()
    privacy = password_crypt.logIn(requiresGet(modules))
    modules, base = initSet(privacy, modules)
    return modules, base
