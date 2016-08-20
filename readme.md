# NTUOSC SlackBot


This module is set to be used by message as command line in the channel in Slack

Requirement :

	Python 3.5


There are some command :

* old module

	This module transfer 中文字 to 小篆
	* old xxx
	* oldreact [floor] xxx
	* oldtime [time] 
	* oldset [a_word] [new_name]
	* oldask [6characters]
	* oldhelp [funcs...]
	* oldgif (-t second=0.5) [text]
	* oldgifreact (floor=-1) [text]
	
    You can see it at oldhelp.md
 
 * KXGEN module
 
 	This module will grab the png data from kxgen website
 	* kxgen [name] [(param=)value]
 	* kxgenhelp (name)
 
 * VOTE module

 	Use this module to vote
    * vote xxx oooo xxx
    * votehelp

The usage is write inside the command

Usually, you can type xxhelp for help


## license
MIT ?
