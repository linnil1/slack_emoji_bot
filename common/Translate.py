import subprocess


class Translate:
    def require():
        return []

    def __init__(self, privacy):
        pass

    def translate(self, text, opt={}):
        args = ["node", "common/translate.js", text]
        arg = [opt.get("from") or "auto", opt.get("to") or "zh-TW"]
        args.extend(arg)

        ans = subprocess.run(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if ans.stderr:
            raise ValueError(ans.stderr.decode().split('\n')[0][2:])
        return ans.stdout.decode()
