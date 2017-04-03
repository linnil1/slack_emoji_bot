import pprint
import time


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ERR = '\033[91m'
    ENDC = '\033[0m'


def setPrint(title):
    def word(*arg):
        return "{}[{}]{}".format(*arg, Colors.ENDC)

    def cPrint(status="", data="", color="OKGREEN"):
        if Colors.ERR == getattr(Colors, color):
            print(word(Colors.OKBLUE, time.strftime("%c")),
                  end=' ')
        print(word(Colors.HEADER, title) +
              word(getattr(Colors, color), status),
              end=' ')

        if type(data) is str:
            if '\n' in data:
                print('')
            print(data)
            return
        pdata = pprint.pformat(data)
        if '\n' in pdata:
            print("")
        pprint.pprint(data)
    return cPrint
