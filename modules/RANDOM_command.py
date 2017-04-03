import random
import re
import sys

"""
random(1)
random(1,6)
random(1,6,1)
random(1,6)
random(1,6,2.1)
random(1,6,2.1,0.1)

random.choice([1,2])
random.choice([1,2],2)

"""


class Myrandom:
    def int(start, end=None, step=1):
        if end and start >= end:
            raise ValueError("Empty range")
        return random.randrange(start, end, step)

    def floatMult(arr):
        for i, x in enumerate(arr):
            arr[i] = arr[i].strip()
            if x.find('.') == -1:
                arr[i] += '.'
        m = max([len(i) - i.find('.') - 1 for i in arr])
        for i, x in enumerate(arr):
            arr[i] = int(x[:x.find('.')] + x[x.find('.') + 1:] +
                         '0' * (m - (len(x) - x.find('.') - 1)))
        return m

    def floatDiv(m, ans):
        ans = str(ans)
        if len(ans) >= m:
            ans = ans[:len(ans) - m] + '.' + ans[len(ans) - m:]
        else:
            ans = '.' + ans.rjust(m, '0')
        return float(ans)

    # float argument is str
    def float(start=1, end=None, step="0.000000000000001"):
        if end is None:
            start, end = "0", start
        if step == "0.000000000000001":
            return random.uniform(float(start), float(end))

        arr = [start, end, step]
        m = Myrandom.floatMult(arr)
        ans = Myrandom.int(*arr)

        return Myrandom.floatDiv(m, ans)

    # error handle
    def argCheck(arg):
        if len(arg) > 3:
            raise TypeError("Too many args")
        if len(arg) == 0 or (len(arg) == 1 and not arg[0].strip()):
            arg.clear()  # arg = [] not work
            return False

        isint = True
        for i in arg:
            if not i.strip():
                raise SyntaxError("Empty number")
            float(i)
            if 'e' in i:
                raise ValueError("Not support exponential")
            try:
                int(i)
            except BaseException:
                isint = False

        return isint

    def random(arg):
        isint = Myrandom.argCheck(arg)
        if isint:
            return Myrandom.int(*[int(i) for i in arg])
        else:
            return Myrandom.float(*arg)

    def commaSplit(string):
        arr = []
        s = ""
        bs = False
        for i in string:
            if i == ',' and not bs:
                arr.append(s)
                s = ""
                continue
            if i == '\\' and not bs:
                bs = True
                continue
            if bs:
                bs = False
            s += i
        arr.append(s)
        return arr

    def choice(arr, num=1):
        return random.sample(arr, num)

    def sample(arg):
        if len(arg) == 0:
            raise TypeError("not number")
        num, arg = int(arg[0]), arg[1:]
        if num > 100:
            raise ValueError("Number limit: 100")
        isint = Myrandom.argCheck(arg)

        pop, m = [], 1
        if not isint:
            if len(arg) == 0:
                arg.append("1")
            if len(arg) == 1:
                arg = ["0", arg[0]]
            if len(arg) == 2:
                arg.append("0.000000000000001")
            m = Myrandom.floatMult(arg)
        else:
            for i in range(len(arg)):
                arg[i] = int(arg[i])

        pop = range(*arg)
        ans = random.sample(pop, num)

        if not isint:
            for i in range(len(ans)):
                ans[i] = Myrandom.floatDiv(m, ans[i])

        return ans

    def lineParse(string):
        func = None
        if re.match(r"random\s*\(.*?\)$", string):
            args = re.findall(r"random\s*(\(.*?\))$", string)[0]
            args = args[1:-1].split(",")
            return Myrandom.random(args)
        elif re.match(r"random\s*\.\s*sample\s*\(.*?\)$", string):
            args = re.findall(r"random\s*\.\s*sample\s*(\(.*?\))$", string)[0]
            args = args[1:-1].split(",")
            return Myrandom.sample(args)
        elif re.match(r"random\s*\.\s*choice\s*\(.*?\)$", string):
            args = re.findall(r"random\s*\.\s*choice\s*(\(.*?\))$", string)[0]
            args = args[1:-1].strip()
            arr = ""
            num = 1
            if re.match(r"\[.*?\]\s*,\s*\d+$", args):
                arg = re.findall(r"^\[(.*?)\]\s*,\s*(\d+)$", args)
                arr = arg[0][0]
                num = int(arg[0][1])
            elif re.match(r"\[.*?\]$", args):
                arg = re.findall(r"\[(.*?)\]$", args)
                arr = arg[0]
            else:
                raise SyntaxError("Syntax error")
            return Myrandom.choice(Myrandom.commaSplit(arr), num)
        else:
            raise SyntaxError("Syntax error")

    def help():
        return """
random( [start [,end [,step ]]] )
random.sample( num,[start [,end [,step ]]] )
random.choice( list [, num] )"""


class RANDOM:
    def require():
        return []

    def __init__(self, slack, custom):
        self.slack = slack
        self.colorPrint = custom['colorPrint']
        self.payload = {
            "username": "亂數 Randomer",
            "icon_emoji": ":_e4_ba_82:"
        }

    def main(self, datadict):
        if not datadict['type'] == 'message' or 'subtype' in datadict:
            return

        if datadict['text'].startswith("random"):
            if datadict['text'] in ["randomhelp", "random"]:
                text = '```' + Myrandom.help() + '```'
            else:
                try:
                    arr = Myrandom.lineParse(datadict['text'])
                except BaseException:
                    arr = sys.exc_info()[1]
                self.colorPrint("Array of answer", arr)

                if type(arr) is list:
                    arr = ", ".join(['`' + str(i) + '`' for i in arr])
                text = str(arr)

            self.slack.api_call("chat.postMessage",
                                **self.payload,
                                thread_ts=datadict.get("thread_ts")or'',
                                channel=datadict['channel'],
                                text=text)


""" for test
from RANDOM_command import Myrandom
func = Myrandom.lineParse
"""
