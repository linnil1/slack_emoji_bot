# SlackBot OLD module

## MetaData
This module is to transform Chinese word to 小篆 and store as emoji on Slack

Author : linnil1

Source : https://github.com/linnil1/slack_emoji_bot

There are 5 operations : ["old","oldask","oldreact","oldset","oldhelp"]

You can see detail of operation by oldhelp (func...)

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

  Usage: `oldask [6characters]` **ask what is the emoji character**
  
  The form of emoji name is "_ab_cd_ef" (abcdef is hex)
  
  And 6characters is the emoji name without "_"
  
  In python, 6characters should be same as `urllib.parse.quote("字").replace(",","")`
  
  If we cannot find the word, it doesn't ouput anything
  
  For example: 黑 is _e9_bb_91 and the 6characters is "e9bb91"
  
  `oldask e9bb91`

* oldreact
  
  Usage: `oldreact [text]` **give the previous message reactions of 小篆emoji**

  If we cannot find the same word of 小篆, it will be ignore

  The emoji can only be reacted once a message

  For example:

  `oldreact 表情OAO`

  `oldreact :_e8_a1_a8::_e6_83_85:表情OAO`

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

* oldhelp (func...)

  Usage: `oldhelp` **get help for the usage of this modle or the function**

  for example: oldhelp old oldask

  If you want to see more clear statement see [OLDhelp.md]
  
