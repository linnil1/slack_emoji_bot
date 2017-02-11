import pprint
import time
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ERR  = '\033[91m'
    ENDC = '\033[0m'

def setPrint(title):
    def cPrint(status="",data="",color="OKGREEN"):
        if color == Colors.ERR:
            print(Colors.OKBLUE + "[{}]".format(time.strftime("%s")) + Colors.ENDC)
        print( Colors.HEADER +"[{}]".format(title )+Colors.ENDC+
        getattr(Colors,color)+"[{}]".format(status)+Colors.ENDC,end=' ')
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

