import argparse
from cowpy.cow import *
import re

# this code is modify from https://github.com/jeffbuttars/cowpy/tree/master/cowpy
def cowsay_main(arglist):
    if "--help" in arglist:
        # bad methods need fix
        return """
usage: cowpy [-h] [-l] [-L] [-t] [-u] [-e EYES] [-f COWACTER] [-E] [-r] [-x]
             [-C]
             [msg [msg ...]]

Cowsay for Python. Directly executable and importable.

positional arguments:
  msg                   Message for the cow to say

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            Output all available cowacters
  -L, --list-variations
                        Output all available cowacters and their variations.
  -t, --thoughts        Use a thought bubble instead of a dialog bubble.
  -u, --tongue          Add a tounge to the selected cowacter, if appropriate.
  -e EYES, --eyes EYES  Use a specifice type of eyes on the cowacter
  -f COWACTER, --cowacter COWACTER
                        Specify which cowacter to use. (case insensitive)
  -E, --list-eyes       Print a listing of the available eye types.
  -r, --random          Choose a cowacter at random (consider --nsfw).
  -x, --nsfw            Enable 'not safe for work' cowacters and eyes.
  -C, --copy            Create a local copy of cow.py for you to include in
                        your own python program.
        """

    parser = argparse.ArgumentParser(
        prog="cowpy",
        description=("Cowsay for Python. Directly executable and importable.")
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
    parser.add_argument('-L', '--list-variations',
                        default=False,
                        help=("Output all available cowacters and their variations."),
                        action="store_true")
    parser.add_argument('-t', '--thoughts',
                        default=False,
                        help=("Use a thought bubble instead of a dialog bubble."),
                        action="store_true") 
    parser.add_argument('-u', '--tongue', default=False,
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
    parser.add_argument('-C', '--copy',
                        help=("Create a local copy of cow.py for you to include in your own "
                              "python program."),
                        action="store_true")

    args = parser.parse_args(arglist)

    msg = " ".join(args.msg)

    exit_early = False
    sfw = not args.nsfw

    if args.copy:
        thisfile = os.path.realpath(__file__)
        thisfile = ''.join(os.path.splitext(thisfile)[:-1]) + '.py'

        bname = os.path.basename(thisfile)
        outfile = os.path.join(os.curdir, bname)
        outfile = ''.join(os.path.splitext(outfile)[:-1]) + '.py'

        if os.path.exists(bname):
            return ("The file {} bname already exists, not making the copy.")
            sys.exit(1)
        else:
            return ("{} -> {}".format(thisfile, outfile))

        shutil.copyfile(thisfile, outfile)
        exit_early = True

    if args.list or args.list_variations:
        exit_early = True
        for cow_name, cow in get_cowacters(sfw=sfw, sort=True):
            if args.list_variations:
                for eye_name, _ in get_eyes(sfw=sfw, sort=True):

                    nsfw = (not_safe_for_work(cow=cow_name, eyes=eye_name) and ' : NSFW') or ''

                    return (cow(eyes=eye_name).milk("{}, eye is {}{}".format(
                        cow_name, eye_name, nsfw)))
                    return (cow(
                        eyes=eye_name, thoughts=True).milk(
                            "{}, eye is {}, with bubble{}".format(cow_name, eye_name, nsfw)))
                    return (cow(
                        eyes=eye_name, tongue=True).milk("{}, eye is {}, with tounge{}".format(
                            cow_name, eye_name, nsfw)))
            else:
                nsfw = (not_safe_for_work(cow=cow_name) and ' : NSFW') or ''
                return (cow().milk(cow_name + nsfw))

    if args.list_eyes:
        exit_early = True
        for k, v in get_eyes(sfw=sfw, sort=True):
            return ("{} : '{}'{}".format(k, v, (not_safe_for_work(eyes=k) and ' : NSFW') or ''))

    if exit_early:
        sys.exit(0)

    cow = get_cow()
    if args.cowacter:
        try:
            cow = get_cow(args.cowacter.lower())
        except KeyError:
            return ("{} is an invalid cowacter".format(args.cowacter))
            sys.exit(1)

    if args.random:
        return (milk_random_cow(msg, sfw=sfw))
        sys.exit(0)

    answer = (cow(eyes=args.eyes,
          tongue=args.tongue,
          thoughts=args.thoughts
              ).milk(msg)
          )
    print(answer)
    return answer

#cowsay_main('-t 123'.split())

class COWSAY: 
    def __init__(self,slack,custom):
        self.slack = slack
        self.custom = custom

    def main(self,datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return 

        if re.search(r"^cowsay ",datadict['text']):
            text = re.search(r"(?<=cowsay ).*",datadict['text'],re.DOTALL).group().strip()

            payload = {
                "username": "Cowww Say",
                "icon_emoji": ":_e7_89_9b:",
                "channel": datadict['channel'],
                "text":'```'+cowsay_main(text.split())+'```'}
            self.slack.api_call("chat.postMessage",**payload)

