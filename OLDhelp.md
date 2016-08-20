# SlackBot OLD module

## MetaData
This module is to transform Chinese word to 小篆 and store as emoji on Slack

Author : linnil1

Source : https://github.com/linnil1/slack_emoji_bot

You can see detail BY oldhelp

## Operations
* old 

  Usage: `old [text]` **transfer text to 小篆emoji.**

  If we cannot find the same word of 小篆, it will output the same as you type.

  For example:

  `old 小篆測試 ^_^`

  `old 這個字 two of them cannot be found`

  In advance, it was designed for recursive usage

  For example:

  `old old 你好!`

* oldask

  Usage: `oldask [6characters]` **To ask what is the chinese word of the url-encoded string**

  The form of emoji name is "_ab_cd_ef" (abcdef is hex)

  And 6characters is the emoji name without "_"

  In python, 6characters should be same as `urllib.parse.quote("字").replace("_","")`

  If we cannot find the word, it doesn't ouput anything

  For example: 黑 is "_e9_bb_91" and the 6characters is "e9bb91"

  `oldask e9bb91`

* oldreact

  Usage: `oldreact (floor=-1) [text]` **give reactions of 小篆emoji to specific floor message**

  If we cannot find the same word of 小篆, it will be ignore

  The emoji can only be reacted once a message

  If floor <0 , means previous message

  floor = 0  means yourself

  floor > 0 means to future messages , [floor] below yourself
  
  And the range of floor is [-F,F] . If this command is accped , the bot will react "行" which means OK in chinese 

  For example:

  `oldreact 表情OAO`

  `oldreact :_e8_a1_a8::_e6_83_85:好笑OAO`

  `oldreact -1 樓上`
  
  `oldreact a 十樓`

  In advance, it was designed for recursive usage

  For example:

  `old oldreact old 遞迴!`

* oldset

  Usage: `oldset [aWord] [newName]` **set alias for 小篆emoji**

  The newName should obey the rule of emoji name on Slack

  A word should be a word can be found in 小篆

  If some error happened , it will output error message

  For example:

  `oldset 吃 eat`

* oldhelp

  Usage: `oldhelp` **get help for the usage of this module**

  for example: oldhelp

  You will get the link of this [document](OLDhelp.md)
  
* oldtime

  Usage: `oldtime (time)` **show date and time by 小篆emoji**

  if time is not specific , it will output now time

  if your time format is wrong , it will not output anything

  there are several format for time

	`2016/1/2 3:4` `2016/1/2 3:` `2016/1/2` `2016` `3:4` `3:` `:4`

  For example:

  `oldtime`

  `oldtime 2014/1/12 3:`

* oldgif 

  Usage: `oldgif (-t second=0.5) [text]` **combine 小篆emojis into gif**

  delay is float and it's range is 0<=delay<=10(second)

  For example:

  `oldgif 小篆`
  
  `oldgif -t 1 小篆`

* oldgifreact

  Usage: `oldgifreact (floor=-1) [text]` **give reactions of 小篆emoji gif to specific floor message**

  For example:

  `oldgifreact 小篆`
  
  `oldgifreact -2 小篆`
  
  `oldgifreact 2 -t 1 小篆`
