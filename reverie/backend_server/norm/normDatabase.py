import json
import sys

sys.path.append('../')
from global_methods import *
from norm.normNode import *


class NormDatabase:
    def __init__(self, f_saved, normSeedCount, normCount, persona):
        self.norm_count = 0
        self.norm_seed = {}
        self.kw_to_norm = dict()
        self.act_norm = {}
        self.act_norm_count = 0
        self.content_to_act_norm = {}
        self.content_to_norm_seed = {}
        print(f"INIT NormDatabase: {f_saved}")

        if check_if_file_exists(f"{f_saved}/personal_norm_database.json"):
            print("GNS FUNCTION: <NormDatabase__init__norm_seed>")
            scratch_load = json.load(open(f"{f_saved}/personal_norm_database.json"))
            for i in range(1, normSeedCount + 1, 1):
                norm = scratch_load[f"norm_{i}"]
                try:
                    related_desc = norm["related_desc"]
                except:
                    related_desc = ""
                try:
                    poi_reason = norm["poi_reason"]
                except:
                    poi_reason = ""
                try:
                    poi = norm["utility"]
                except:
                    poi = -1
                node = NormNode(norm["ID"], norm["type"], norm["content"], norm["subject"], norm["predicate"],
                                norm["object"], related_desc, poi, poi_reason, norm["activation_state"],
                                norm["validity_state"])
                self.norm_seed[str(node.id)] = node
                self.norm_count += 1
                self.content_to_norm_seed[norm["content"]] = node
                print("NormSeedNode: ", node.id, node.content)

                keywords = set()
                keywords.update([norm["subject"], norm["object"]])
                keywords = [i.lower() for i in keywords]
                for kw in keywords:
                    if kw in self.kw_to_norm:
                        self.kw_to_norm[kw][0:0] = [node]
                    else:
                        self.kw_to_norm[kw] = [node]
            print(self.norm_seed)
        else:
            print(f"INIT NormDatabase: {f_saved}/personal_norm_database.json could not find")

        if check_if_file_exists(f"{f_saved}/personal_norm_database_validity.json"):
            print("GNS FUNCTION: <NormDatabase__init__act_norm>")
            scratch_load = json.load(open(f"{f_saved}/personal_norm_database_validity.json"))
            for i in range(1, normCount + 1, 1):
                norm = scratch_load[f"norm_{i}"]
                try:
                    related_desc = norm["related_desc"]
                except:
                    related_desc = ""
                try:
                    poi_reason = norm["poi_reason"]
                except:
                    poi_reason = ""
                node = NormNode(norm["ID"], norm["type"], norm["content"], norm["subject"], norm["predicate"],
                                norm["object"], related_desc, norm["utility"], poi_reason, norm["activation_state"],
                                norm["validity_state"])
                self.act_norm[str(node.id)] = node
                self.act_norm_count += 1
                self.content_to_act_norm[norm["content"]] = node
                print("ActNormNode: ", node.id, node.content)

            print(self.act_norm)
        else:
            print(f"INIT NormDatabase: {f_saved}/personal_norm_database_validity.json could not find")

    def retrieve_relevant_norms(self):  # , s_content, p_content, o_content):
        # contents = [s_content, p_content, o_content]
        ret = []
        # for i in contents:
        # if i in self.kw_to_norm:
        for i in range(1, self.act_norm_count + 1, 1):
            # for i in self.norm_seed:
            # ret += self.kw_to_norm[i.lower()]
            if self.act_norm[str(i)].activation_state and self.act_norm[str(i)].validity_state:
                ret += [self.act_norm[str(i)]]
            # ret += i
        # ret = set(ret)
        print("retrieve_norms:", ret)
        return ret

    def add_norm_seed(self, norm):
        if norm == None:
            return
        self.norm_count += 1
        norm.id = self.norm_count
        self.norm_seed[str(self.norm_count)] = norm
        self.content_to_norm_seed[norm.content] = norm

        print("NormSeedNode: ", norm.id, norm.content)


    def add_act_norm(self, norm):
        if norm == None:
            return
        self.act_norm_count += 1
        norm.id = self.act_norm_count
        self.act_norm[str(self.act_norm_count)] = norm
        self.content_to_act_norm[norm.content] = norm

        print("ActNormNode: ", norm.id, norm.content)

