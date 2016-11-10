import argparse
from cowpy.cow import *
import re

# this code is modify from https://github.com/jeffbuttars/cowpy/tree/master/cowpy
def cowsay_init():
    parser = argparse.ArgumentParser(
        prog="cowsay",
        description=("cowsay on slackbot")
    )

    parser.add_argument('msg',
                        default=["Cowsay | cowpy. Please seek --help"],
                        type=str, nargs='*',
                        help=("Message for the cow to say"),
                        )

    parser.add_argument('-l', '--list',
                        default=False,
                        help=("Output all available cowacters"),
                        action="store_true")
    parser.add_argument('-t', '--thoughts',
                        default=False,
                        help=("Use a thought bubble instead of a dialog bubble."),
                        action="store_true") 
    parser.add_argument('-u', '--tongue', 
                        default=False,
                        help=("Add a tounge to the selected cowacter,  if appropriate."),
                        action="store_true")
    parser.add_argument('-e', '--eyes',
                        default='default',
                        help=("Use a specifice type of eyes on the cowacter"))
    parser.add_argument('-f', '--cowacter',
                        default='default',
                        help=("Specify which cowacter to use. (case insensitive)"))
    parser.add_argument('-E', '--list-eyes',
                        help=("Print a listing of the available eye types."),
                        action="store_true")
    parser.add_argument('-r', '--random',
                        help=("Choose a cowacter at random (consider --nsfw)."),
                        action="store_true")
    parser.add_argument('-x', '--nsfw',
                        help=("Enable 'not safe for work' cowacters and eyes."),
                        action="store_true")
    return  parser

def cowsay_main(parser,argtext):
    arglist = argtext.split()
    if "-h" in arglist or "--help" in arglist:
        return parser.format_help()

    args = parser.parse_args(arglist)

    msg = " ".join(args.msg)
    sfw = not args.nsfw
    answer = ""

    if args.list:
        for cowname, _ in get_cowacters(sfw=sfw, sort=True):
            answer += ("{} {}\n".format(cowname, (not_safe_for_work(cow=cowname) and ' : NSFW') or ''))
        return answer+ "See more at https://github.com/jeffbuttars/cowpy#available-cowacters\n"

    if args.list_eyes:
        for k, v in get_eyes(sfw=sfw, sort=True):
            answer += ("{} : '{}'{}\n".format(k, v, (not_safe_for_work(eyes=k) and ' : NSFW') or ''))
        return answer 


    cow = get_cow()
    if args.cowacter:
        try:
            cow = get_cow(args.cowacter.lower())
        except KeyError:
            return ("{} is an invalid cowacter".format(args.cowacter))

    if args.random:
        return (milk_random_cow(msg, sfw=sfw))

    answer = (cow(eyes=args.eyes,
          tongue=args.tongue,
          thoughts=args.thoughts
              ).milk(msg)
          )
    print(answer)
    return answer

#cowsay_main('-t 123'.split())

class COWSAY: 
    def require():
        return []
    def __init__(self,slack,custom):
        self.slack = slack
        self.parser = cowsay_init()

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if re.search(r"^cowsay ",datadict['text']):
            text = re.search(r"(?<=cowsay ).*",datadict['text'],re.DOTALL).group().strip()

            payload = {
                "username": "Cowww Say",
                "icon_emoji": ":_e7_89_9b:",
                "channel": datadict['channel'],
                "text":'```'+cowsay_main(self.parser,text)+'```'}
            self.slack.api_call("chat.postMessage",**payload)
