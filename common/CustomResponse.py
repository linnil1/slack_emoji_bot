from slackclient import SlackClient


class CustomResponse:
    def require():
        return [{"name": "testtoken", "secret": True}]

    def __init__(self, privacy):
        self._slack = SlackClient(privacy["testtoken"])

    def list(self):
        return self._slack.api_call("slackbot.responses.list")

    def base_add(self, triggers, responses):
        return self._slack.api_call(
            "slackbot.responses.add",
            triggers=triggers,
            responses=responses)

    def base_delete(self, delid):
        return self._slack.api_call(
            "slackbot.responses.delete",
            response=delid)

    def base_edit(self, editid, triggers, responses):
        return self._slack.api_call(
            "slackbot.responses.edit",
            response=editid,
            triggers=triggers,
            responses=responses)

    # use element as arg
    def find(self, key, keyword='triggers'):
        replist = self.list()['responses']
        for rep in replist:
            if key in rep[keyword]:
                return rep
        return None  # not found

    def update(self, element):
        return self.base_edit(
            element['id'], ",".join(element['triggers']),
            "\n".join(element['responses']))

    def delete(self, element):
        return self.base_delete(element['id'])

# the function is implement beacuse the server doesn't check same trigger word
# this function is for easy use
    def add(self, key, word):
        element = self.find(key)
        if not element:
            return self.base_add(key, word)
        else:
            element['responses'].append(word)
            return self.upload(element)
