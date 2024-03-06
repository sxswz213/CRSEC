class NormNode:
    def __init__(self, id, type, content, subject, predicate, object, related_desc="", poi=-1, reason="",
                 activation_state=False, validity_state=False):
        self.id = id
        self.type = type
        self.content = content
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.related_desc = related_desc
        self.poignancy = poi
        self.poi_reason = reason
        self.activation_state = activation_state
        self.validity_state = validity_state

    '''
      "norm_1": {
        "ID": 1,
        "type": "prohibitive",
        "content": "No smoking is allowed inside the cafe.",
        "subject": "no one",
        "predicate": "is allowed",
        "object": "to smoke inside the cafe",
        "utility": 1-100, -1(no evaluate), -2(Fact Consistency Check False), -3(Duplicate Check True)
      },
    '''
