import sys

sys.path.append('../')
from persona.persona import *
def norm_save(persona, out_json):
    '''

    Args:
        persona:
        save_folder:

    Returns:

    '''
    r = {}
    for count in range(1, persona.norm_database.norm_count+1, 1):
        print("persona.norm_database.norm_count:",persona.norm_database.norm_count)
        #node_id = f"norm_{str(count)}"
        node = persona.norm_database.norm_seed[str(count)]
        print(node)

        r[f"norm_{str(count)}"] = dict()
        r[f"norm_{str(count)}"]["ID"] = node.id
        r[f"norm_{str(count)}"]["type"] = node.type
        r[f"norm_{str(count)}"]["content"] = node.content
        r[f"norm_{str(count)}"]["subject"] = node.subject
        r[f"norm_{str(count)}"]["predicate"] = node.predicate
        r[f"norm_{str(count)}"]["object"] = node.object
        r[f"norm_{str(count)}"]["related_desc"] = node.related_desc
        r[f"norm_{str(count)}"]["utility"] = node.poignancy
        r[f"norm_{str(count)}"]["poi_reason"] = node.poi_reason
        r[f"norm_{str(count)}"]["activation_state"] = node.activation_state
        r[f"norm_{str(count)}"]["validity_state"] = node.validity_state

    with open(f"{out_json}/personal_norm_database.json", "w") as outfile:
        json.dump(r, outfile)

    r1 = {}
    for count in range(1, persona.norm_database.act_norm_count + 1, 1):
        print("persona.norm_database.act_norm_count:", persona.norm_database.act_norm_count)
        # node_id = f"norm_{str(count)}"
        node = persona.norm_database.act_norm[str(count)]
        print(node)

        r1[f"norm_{str(count)}"] = dict()
        r1[f"norm_{str(count)}"]["ID"] = node.id
        r1[f"norm_{str(count)}"]["type"] = node.type
        r1[f"norm_{str(count)}"]["content"] = node.content
        r1[f"norm_{str(count)}"]["subject"] = node.subject
        r1[f"norm_{str(count)}"]["predicate"] = node.predicate
        r1[f"norm_{str(count)}"]["object"] = node.object
        r1[f"norm_{str(count)}"]["related_desc"] = node.related_desc
        r1[f"norm_{str(count)}"]["utility"] = node.poignancy
        r1[f"norm_{str(count)}"]["poi_reason"] = node.poi_reason
        r1[f"norm_{str(count)}"]["activation_state"] = node.activation_state
        r1[f"norm_{str(count)}"]["validity_state"] = node.validity_state

    with open(f"{out_json}/personal_norm_database_validity.json", "w") as outfile:
        json.dump(r1, outfile)