import sys

sys.path.append('../')

from norm.run_gpt_prompt_norm import *
from utils import *
from norm.normNode import *


def norm_reflection_trigger(persona):
    """
    INPUT:
      persona: Current Persona object
    Output:
      True if we are running a norm reflection.
      False otherwise.
    """
    print(persona.scratch.name, "persona.scratch.norm_importance_trigger_curr::",
          persona.scratch.norm_importance_trigger_curr)
    print(persona.scratch.norm_importance_trigger_max)

    if (persona.scratch.norm_importance_trigger_curr <= 0 and [] != persona.a_mem.seq_thought):
        return True
    return False


def thoughts_choose(persona):
    thoughts = []
    im_count = persona.scratch.norm_importance_trigger_max
    for thought in persona.a_mem.seq_thought:
        if im_count <= 0:
            break
        im_count -= thought.poignancy
        thoughts += [thought]

    return thoughts


def generate_norms(persona, thought):
    '''
    Args:
        persona: Current Persona object
        thought: node of one thought
    Returns:
        list of str of norms: ["xxxxx", "xxxxx", "xxxxx"]
    '''
    if debug: print("GNS FUNCTION: <generate_norms>")

    # turn into str of thought with its filling thoughts: "1.xxxx\n2.xxxxx\n3.xxxxx\n"
    reletive_thoughts = f"\n1.{thought.description}\n"
    t_count = 2
    if thought == None:
        return False, reletive_thoughts
    if thought.filling != None:
        for filling_node in thought.filling:
            if filling_node == 'n':
                break
            tmp_node = persona.a_mem.id_to_node[filling_node]
            if tmp_node.type == "thought":
                if tmp_node.description.count('plan') > 0:
                    continue
                reletive_thoughts += f"{str(t_count)}.{tmp_node.description}\n"
                t_count += 1
    ret = run_gpt_prompt_norm_reflect_from_thoughts(reletive_thoughts)[0]
    print(ret)
    if len(ret) == 0 or len(ret[0]) != 2:
        return False, reletive_thoughts
    # if ret[0] == 'ChatGPT ERROR':
    #    return False, reletive_thoughts
    return ret, reletive_thoughts


def generate_format_norm(norm_str, desc=""):
    if debug: print("GNS FUNCTION: <generate_format_norm>")
    if norm_str == '':
        return None
    if norm_str == 'None.':
        return None
    ret = run_gpt_prompt_norm_format(norm_str)[0]
    if ret == False:
        return None
    try:
        norm = ret["norm_1"]
    except:
        return None
    node = NormNode(norm["ID"], norm["type"], norm["content"], norm["subject"], norm["predicate"],
                    norm["object"], related_desc=desc)
    return node


def run_norm_reflect(persona):
    """
    INPUT:
      persona: Current Persona object
    Output:
      None
    """
    thoughts = thoughts_choose(persona)

    for thought in thoughts:
        # list of str of norms: ["xxxxx", "xxxxx", "xxxxx"]
        if thought == None:
            continue
        norms, rel_thoughts = generate_norms(persona, thought)
        if norms == False:
            continue
        for norm_str in norms:
            # generate a normNode
            norm = generate_format_norm(norm_str[0], 'Thoughts:' + norm_str[1])
            persona.norm_database.add_norm_seed(norm)
            persona.scratch.norm_evaluate = True


def reset_norm_reflection_counter(persona):
    persona_imt_max = persona.scratch.norm_importance_trigger_max
    persona.scratch.norm_importance_trigger_curr = persona_imt_max


def generate_conflict_chat_reflect(all_utt):
    '''
    Args:
        all_utt:
    Returns:
        norm_str:
        reflect_tag: true or false
    '''
    if debug: print("GNS FUNCTION: <generate_conflict_chat_reflect>")
    x = run_gpt_conflict_chat_reflect(all_utt)[0]
    if len(x) == 2:
        return x[0], x[1]
    else:
        return False, False


def generate_non_norm_conflict_chat_reflect(all_utt):
    if debug: print("GNS FUNCTION: <generate_non_norm_conflict_chat_reflect>")
    return run_gpt_non_norm_conflict_chat_reflect(all_utt)[0]


def generate_chat_norms_summarize(all_utt):
    '''
    Returns:
        list of str of norms: ["xxxxx", "xxxxx", "xxxxx"]
    '''
    if debug: print("GNS FUNCTION: <generate_chat_norms_summarize>")
    return run_gpt_chat_norms_summarize(all_utt)[0]


def norm_reflect(persona):
    """
    INPUT:
      persona: Current Persona object
    Output:
      None
    """
    if norm_reflection_trigger(persona):
        run_norm_reflect(persona)
        reset_norm_reflection_counter(persona)

    # print (persona.scratch.name, "al;sdhfjlsad", persona.scratch.chatting_end_time)
    if persona.scratch.chatting_end_time:
        # print("DEBUG", persona.scratch.curr_time + datetime.timedelta(0,10))
        if persona.scratch.curr_time + datetime.timedelta(0, 10) == persona.scratch.chatting_end_time:
            print("NOOOOOORMMMMMMM")
            all_utt = ""
            if persona.scratch.chat:
                for row in persona.scratch.chat:
                    all_utt += f"{row[0]}: {row[1]}\n"

            if persona.scratch.norm_conflict:
                # chat is generate from norm conflict
                norm_str, reflect_tag = generate_conflict_chat_reflect(all_utt)
                if reflect_tag:
                    norm = generate_format_norm(norm_str, all_utt)
                    persona.norm_database.add_norm_seed(norm)
                    persona.scratch.norm_evaluate = True
                persona.scratch.norm_conflict = False
            else:
                reflect_tag = generate_non_norm_conflict_chat_reflect(all_utt)
                if reflect_tag:
                    norms = generate_chat_norms_summarize(all_utt)
                    for norm_str in norms:
                        norm = generate_format_norm(norm_str, all_utt)
                        persona.norm_database.add_norm_seed(norm)
                        persona.scratch.norm_evaluate = True
