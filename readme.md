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
* 社課 module

	 Output the class this time

	 Just type "社課"

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

The usage is write inside the command

Usually, you can type xxhelp for help

Please send message "old 算課牛食篆轉我好中不一二三四五六七八九十票行廢同"
when you first run it

## license
MIT ?
