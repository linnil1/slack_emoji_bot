import os
import sys
import re
import importlib
sys.path.insert(0, './modules/')
sys.path.insert(0, './common/')
import password_crypt 
import copy

import RunData 
from slackclient import SlackClient
class SLACK():
    def require():
        return [{"name":"TOKEN","secret":True},
                {"name":"reportchannel","default":"workstation"}]
    def __init__(self,privacy):
        self._slack = SlackClient(privacy['TOKEN'])
        self.reportchannel = privacy['reportchannel']
    def api_call(self,*args,**kwargs):
        return self._slack.api_call(*args,**kwargs)
from ColorPrint import *

def importGet():
    imports = [{
        'class': SLACK,
        'name' : "",
        'type' : "common"}]
    modules = [ c for c in os.listdir("common") if c.endswith(".py")]
    for command in modules:
        com = importlib.import_module(command[:-3])
        imports.append({
            'class': getattr(com,command[:-3]),
            'name' : command[:-3],
            'type' : "common"})

    modules = [ c for c in os.listdir("modules") if c.endswith("_command.py")]
    for command in modules:
        com = importlib.import_module(command[:-3])
        c = re.findall(r"(\w+)_command\.py",command)[0]
        imports.append({
            'class': getattr(com,c),
            'name' : c,
            'type' : "command"})
    return imports

def moduleGet():
    imports = importGet()
    for command in imports:
        command['require'] = command['class'].require()
    return imports

def requireGet(imports):
    requires = []
    for require in imports:
        reqs = copy.deepcopy(require['require'])
        for req in reqs:
            if req['name'] in ['colorPrint','data']:
                raise ValueError("require name cannot be "+req['name'])
            req['name'] = require['name']+"_"+req['name']
        requires.extend(reqs)
    return requires

def privacyFilter(privacy,module,commons={}):
    giveprivacy = {}
    for req in module['require']:
        if req.get("module"):
            giveprivacy[req['name']] = commons[ req['name'] ] 
        else:
            giveprivacy[req['name']]=privacy[ module['name']+"_"+req['name'] ]
    return giveprivacy

def initGet(privacy,imports):
    commons = {}
    for module in imports:
        if module['type'] == 'common':
            pri = privacyFilter(privacy,module)
            pri.update({"colorPrint":setPrint(module['name'])})
            commons[ module['name'] ] = module['class'](pri)

    slack = commons[''] # root
    database = RunData.RunDataBase()

    modules = []
    for module in imports:
        if module['type'] != 'common':
            pri = privacyFilter(privacy,module,commons)
            # add rundata module in every module
            pri.update({"data":RunData.RunData(database,module['name'])}) 
            # add colorPrint
            pri.update({"colorPrint":setPrint(module['name'])})
            modules.append( module['class'](slack,pri) )
    return modules 

def ModuleInit():
    imports = moduleGet()
    privacy = password_crypt.logIn(requireGet(imports))
    modules = initGet(privacy,imports)
    return modules ,privacy['_TOKEN']
