# NTUOSC SlackBot


This module is set to be used by message as command line in the channel in Slack

Requirement :

	Python 3.5


There are some command : 
* old module

	This module transfer 中文字 to 小篆
	* old [text]                 **transfer text to 小篆emoji.**
	* oldask [6characters]       **To ask what is the chinese word of the url-encoded string**
	* oldreact (floor=-1) [text] **give reactions of 小篆emoji to specific floor message**
	* oldset [aWord] [newName]   **set alias for 小篆emoji**
	* oldhelp                    **get help for the usage of this module**
	* oldtime (time)             **show date and time by 小篆emoji**
	* oldgif (-t second=0.5) [text] **combine 小篆emojis into gif**
	* oldgifreact (floor=-1) [text] **give reactions of 小篆emoji gif to specific floor message**
	
    You can see it at oldhelp.md
 
* KXGEN module
 
 	This module will grab the png data from kxgen website
 	* kxgen [name] [(param=)value]
 	* kxgenhelp (name)
 
* VOTE module

 	Use this module to vote
    * vote xxx oooo xxx
    * votehelp 
* 社課 社聚 module

	 Output the class this time

	 Just type "社課"
	 
	 Just type "社聚"


* Food module
 	
	Use this module to find food on midnight channel
	**(it will fail if you don't have midnight channel)** 

    * food [foodname]
    * foodadd [foodname] 
    * fooddel [foodname] 

* poFB module
 
   this module will help you post your text on slack to ntuosc fb

   I will obtain "publish actions" **only** for the permission of post message on NTUOSC's FB

   * poFB [text]

* FBTOSLACK module

	this module will copy the fb post to slack message

	change configure at FBTOSLACK.py

* ASK module
 	
	Get the answer of your text

	Power by WolframAlpha 

    * ASK [text]
    * ASK [text]
	* ASK {your question} Ask wolfram about your question
	* ASKmore  {quetsion} Ask and get more data 
	* ASKall   {quetsion} Ask and get all  data 
	If your want to choose the meaning in `Did you mean?`
	* ASK[{num}] {question}
	* ASK[{num}]more {question}
	* ASK[{num}]all  {question}

* COWSAY module
	
	same as cowsay command

	when install, you should install the newest from github

	https://github.com/jeffbuttars/cowpy

	* cowsay [-h] [-l] [-t] [-u] [-e EYES] [-f COWACTER] [-E] [-r] [-x] [msg [msg ...]]
	* cowsay --help 

* FBTOSLACK module

	sync your fb post to slack 

	If your token is expire, it will remind you by slack user

	if you want to connect to two more fb

	just copy file and modify the class name as module name

* ANON module

	anonymous send data to the channel

	* anon [text] to command_bot and you will see your data in channel anonymously

	* anon --who=name [text] to command_bot and you can post message with others name

* NTU118 module

	NTU118 118restaurant bot

	* 118random       **get a random restaurant**
	* 118type         **get all type of restaurant**
	* 118type [type]  **get all restaurant of that type**
	* 118list         **get all restaurant in 118**
	* 118find [name]  **list all restaurant which match**
	* 18info [name]   **get detailed of that restaurant**
	* 118help         **get help**

* RANDOM module

	* random( [start [,end [,step ]]] )
	* random.choice( [option0,...] , num )
	* random.sample( num [,start [,end [,step ]]] )
	* randomhelp

* Translate module

	* translate text
	* translate text --from=en --to=zh-TW 
	* translatehelp

* REGEX module

	Extend Slackbot response
	
	*python syntax of regex*

	* Use `""` as regex keyword
	* `{{who}}` for the name of who trigger the resopnse
	* `{{all}}` for the all text of what trigger
	* `{{1}}` for first match

* WEATHER module

	Show NTU weather by Image

	* weather

The usage is also write inside the command

Usually, you can type xxhelp for help

# how to run it

First, Initize it.
```
pip3 install -r requirement.txt
cd common/
npm install google-translate-api
npm install phantomjs
cd ..
mkdir data/word_data
mkdir data/tmp

```

* Warning : Pillow should use linnil1/Pillow

And, Run it
`python3 slack_server.py`

Please send message "old 巷算課牛食篆轉我好中不一二三四五六七八九十票行廢同車亂譯氣"
when you first run it

# create new module

create XXX_command.py

In script,  XXX is a class name

XXX.require() will return privacy setting

XXX(slack,custom) will init the module

## privacy setting

an array of privacy object

privacy object : 
``` python
{ 
  'name': "APPID", # name should not use data
  'secret': True, # it will not show on console when writing
  'desp' : "xxx uuuu werwerf skdjfslkdjf", #describition of the key
  'default' : "123" # this will return string
  'module' : True # this will return the class in common/ and module name is name
  'other' : True # this is for asking another's data and name should be like Token
}
```

## init module

your `__init__` need to parameters

`def __init__(self,slack,custom)`

the slack is SlackClient

and custom is the data given by our require . 
and it is a dictionary

## run module

set `def main(self,data)`

server will run it everytime when new message come

the message format is same as slack rtm format


## license
MIT ?
