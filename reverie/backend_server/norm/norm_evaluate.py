import sys

sys.path.append('../')

from norm.run_gpt_prompt_norm import *
from norm.normNode import *
from norm.norm_reflect import *


def generate_immediate_evaluate_recognization(norm, persona):
    '''
    Args:
        norm:

    Returns:
        poi:
        norm_tag: true or false
    '''
    if debug: print("GNS FUNCTION: <generate_immediate_evaluate_recognization>")
    curr_act_norms = "\n"
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    ret = run_gpt_immediate_evaluate_recognization(norm.content, curr_act_norms, norm.related_desc, persona.name)[0]
    if len(ret) == 2:
        return ret[0], ret[1]
    else:
        return False, False


def norm_evaluate(norm, persona):
    '''
    Args:
        norm:

    Returns:
        act_norm:
        act_tag: true or false
    '''
    if norm.poignancy != -1:
        return norm, False
    # immediate_evaluate_recognization
    act_norm = NormNode(norm.id, norm.type, norm.content, norm.subject, norm.predicate,
                        norm.object, norm.related_desc, norm.poignancy)
    poi, norm_tag = generate_immediate_evaluate_recognization(norm, persona)
    if poi:
        act_norm.poignancy = poi
    if norm_tag:
        return act_norm, True
    return act_norm, False


def generate_seeds_content_check(act_norm, persona):
    '''
    Args:
        act_norm:
        persona:
    Returns:
        true or false
    '''
    if debug: print("GNS FUNCTION: <generate_seeds_content_check>")
    norm_str = "{\"norm\": {"
    norm_str += f"\"type\":{act_norm.type},"
    norm_str += f"\"content\":{act_norm.content},"
    norm_str += f"\"subject\":{act_norm.subject},"
    norm_str += f"\"predicate\":{act_norm.predicate},"
    norm_str += f"\"object\":{act_norm.object}"
    norm_str += "}"

    curr_act_norms = "\n"
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    x = run_gpt_seeds_content_check(norm_str, curr_act_norms, act_norm.related_desc)[0]
    ret = []
    if len(x) == 3:
        for i in x[0:3]:
            if i == 'yes':
                ret += [True]
            else:
                ret += [False]
    else:
        return [False]
    y = run_gpt_seeds_type_check(norm_str)[0]
    if len(y) == 2:
        if y[0] == 'correct':
            ret += [True]
        else:
            ret += [False]
        ret += [y[1]]
        return ret
    else:
        return [False]


def seeds_content_check(act_norm, persona):
    '''
    Args:
        act_norm: normNode
        persona:

    Returns:
        tag: true or false
        type_tag: true or false
        type: str
    '''
    x = generate_seeds_content_check(act_norm, persona)
    tag = False
    if len(x) == 5:
        if (not x[0]) and (not x[1]) and x[2]:
            tag = True
        return tag, x[3], x[4]
    return tag, False, ''


def long_term_norm_evaluate_trigger(persona):
    """
    INPUT:
      persona: Current Persona object
    Output:
      True if we are running a norm evaluation.
      False otherwise.
    """
    print(persona.scratch.name, "persona.scratch.norm_evaluate_trigger_curr::",
          persona.scratch.norm_evaluate_trigger_curr)
    print(persona.scratch.norm_evaluate_trigger_max)

    if (persona.scratch.norm_evaluate_trigger_curr <= 0):
        return True
    return False


def generate_active_norms_classfication(persona):
    '''
    Args:
        persona:
    Returns:
        act_norm:str
        tag:true or false
    '''
    if debug: print("GNS FUNCTION: <generate_active_norms_classfication>")

    curr_act_norms = "\n"
    count = 1
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"{str(count)}."
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
        count += 1

    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    x = run_gpt_active_norms_classfication_v2(curr_act_norms)[0]
    if x == False:
        return False, False
    return x, True


def norm_long_term_synthesis_check(classficated_norm):
    '''
    Args:
        classficated_norm: str

    Returns:
        act_norm:[[xxx-related]\n1.xxx\n2.xxx\n3.xxx\n\n[xxx-related]\n1.xxx\n2.xxx\n3.xxx\n\n]
        norm_tag: true or false
    '''
    try:
        ret = ''
        desc = []
        tmp = classficated_norm.split(']\n')[0] + ']\n'
        for str in classficated_norm.split(']\n')[1:]:
            if str.count('.\n') > 1:
                ret += tmp
                ret += str.split('[')[0].split('\n\n')[0]
                desc += ['S_Norms:\n' + str.split('[')[0].split('\n\n')[0]]
                ret += '\n\n'
            if str.count('[') > 0:
                tmp = '[' + str.split('[')[1] + ']\n'
        if ret == '':
            return '', False, ''
        return ret, True, desc
    except:
        return '', False, ''


def generate_norm_long_term_synthesis(classficated_checked_norm):
    if debug: print("GNS FUNCTION: <generate_norm_long_term_synthesis>")
    return run_gpt_norm_long_term_synthesis(classficated_checked_norm)[0]


def specific_norm_deactive(persona, desc):
    for item in desc.split('\n')[1:]:
        try:
            norm = persona.norm_database.content_to_act_norm[item.split('. ')[-1]]
            norm.activation_state = False
        except:
            print("<specific_norm_deactive> act norm not found: ", item)
        try:
            norm_seed = persona.norm_database.content_to_norm_seed[item.split('. ')[-1]]
            norm_seed.activation_state = False
        except:
            print("<specific_norm_deactive> norm seed not found: ", item)


def run_long_term_norm_evaluate(persona, personas):
    '''
    Args:
        persona:
    '''
    classficated_norm, tag = generate_active_norms_classfication(persona)
    if tag == False:
        return
    classficated_checked_norm, norm_tag, desc = norm_long_term_synthesis_check(classficated_norm+'\n')
    if norm_tag:
        act_norm = generate_norm_long_term_synthesis(classficated_checked_norm)
        if act_norm == False or len(act_norm) != len(desc):
            print("run_long_term_norm_evaluate stoped")
            return
        for i in range(len(act_norm)):
            norm_node = generate_format_norm(act_norm[i], desc[i])
            if norm_node == None:
                continue
            persona.norm_database.add_norm_seed(norm_node)
            save_tag, new_norm = norm_evaluate_check(norm_node, persona, personas, long_term_tag=True)
            if save_tag:
                specific_norm_deactive(persona, desc[i])
                new_norm.activation_state = True
                norm_node.activation_state = True
                new_norm.validity_state = True
                norm_node.validity_state = True
                persona.norm_database.add_act_norm(new_norm)
                persona.scratch.norm_evaluate_trigger_curr -= new_norm.poignancy


def reset_norm_norm_evaluate_counter(persona):
    persona_eval_max = persona.scratch.norm_evaluate_trigger_max
    persona.scratch.norm_evaluate_trigger_curr = persona_eval_max


def init_evaluate(personas):
    for persona_name, persona in personas.items():
        if persona.scratch.norm_evaluate:
            for norm_id, norm in persona.norm_database.norm_seed.items():
                act_norm, act_tag = norm_evaluate(norm, persona)
                norm.poignancy = act_norm.poignancy
                if act_tag:
                    persona.norm_database.add_act_norm(act_norm)
            persona.scratch.norm_evaluate = False


def generate_norm_fact_consistency_check(norm):
    '''
    Args:
        norm: node

    Returns:
        cons_tag: true or false
        new_norm_str
    '''
    if debug: print("GNS FUNCTION: <generate_norm_fact_consistency_check>")
    x = run_gpt_norm_fact_consistency_check(norm.content, norm.related_desc)[0]
    if len(x) == 2:
        if x[0] == 'yes':
            return True, ''
        else:
            return False, x[1]
    else:
        return False, ''


def generate_norm_duplicate_check(norm, persona):
    '''

    Args:
        norm:

    Returns:
        true or false
    '''
    if debug: print("GNS FUNCTION: <generate_norm_duplicate_check>")
    curr_act_norms = "\n"
    count = 1
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"{str(count)}."
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
        count += 1
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    x = run_gpt_norm_duplicate_check(norm.content, curr_act_norms)[0]
    if len(x) == 2:
        if x[0] == 'yes':
            return True
    return False

def generate_norm_duplicate_check_for_long_term(norm, persona):
    if debug: print("GNS FUNCTION: <generate_norm_duplicate_check_for_long_term>")
    curr_act_norms = "\n"
    count = 1
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        if a_norm.content.strip('.') in norm.related_desc:
            continue
        curr_act_norms += f"{str(count)}."
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
        count += 1
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    x = run_gpt_norm_duplicate_check(norm.content, curr_act_norms)[0]
    if len(x) == 2:
        if x[0] == 'yes':
            return True
    return False

def generate_seeds_type_check(act_norm):
    '''

    Args:
        act_norm: node

    Returns:
        [true or false, "type"]
    '''
    if debug: print("GNS FUNCTION: <generate_seeds_type_check>")
    norm_str = "{\"norm\": {"
    norm_str += f"\"type\":{act_norm.type},"
    norm_str += f"\"content\":{act_norm.content},"
    norm_str += f"\"subject\":{act_norm.subject},"
    norm_str += f"\"predicate\":{act_norm.predicate},"
    norm_str += f"\"object\":{act_norm.object}"
    norm_str += "}"
    y = run_gpt_seeds_type_check(norm_str)[0]
    ret = []
    if len(y) == 2:
        if y[0] == 'correct':
            ret += [True]
        else:
            ret += [False]
        ret += [y[1]]
        return ret
    else:
        return [False]


def generate_seeds_type_check_v2(act_norm):
    '''

    Args:
        act_norm: node

    Returns:
        [true or false, "type"]
    '''
    if debug: print("GNS FUNCTION: <generate_seeds_type_check_v2>")

    norm_str = f"{act_norm.content}"
    norm_type = f"{act_norm.type}"
    y = run_gpt_seeds_type_check_v2(norm_str, norm_type)[0]
    ret = []
    if len(y) == 3:
        if y[0] == 'no':
            return [False]
        if y[1] == 'correct':
            ret += [True]
        else:
            ret += [False]
        ret += [y[2]]
        return ret
    else:
        return [False]


def generate_norm_utility(norm):
    if debug: print("GNS FUNCTION: <generate_norm_utility>")
    # x=[poi(int), reason(str)]
    x = run_gpt_norm_utility(norm.content)[0]
    if len(x) == 2:
        return x
    else:
        return [False]


def generate_norm_recognize(norm, persona):
    if debug: print("GNS FUNCTION: <generate_norm_recognize>")
    # candidate_norm, curr_active_norms, candidate_norm_utility, persona_ISS, persona_name
    curr_act_norms = "\n"
    count = 1
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"{str(count)}."
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
        count += 1
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    x = run_gpt_norm_recognize(norm.content, curr_act_norms, str(norm.poignancy) + '. ' + norm.poi_reason + '. ',
                               persona.scratch.get_str_iss(), persona.scratch.name)[0]
    if len(x) != 4:
        return False
    # contain
    if x[0] == 'yes':
        return True
    # conflict
    if x[1] == 'yes':
        return False
    # definition
    if x[2] == 'no':
        return False
    # recognize
    if x[3] == 'yes':
        return True
    return False


def generate_recognize_conflict_check(new_norm, persona):
    '''
    Returns:
        if there is a conflict return true, else return false
    '''
    if debug: print("GNS FUNCTION: <generate_recognize_conflict_check>")
    curr_act_norms = "\n"
    count = 1
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"{str(count)}."
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
        count += 1
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    x = run_gpt_norm_recognize_conflict_check(new_norm.content, curr_act_norms)[0]
    if x == False:
        return True
    if x == 'yes':
        return True
    return False


def generate_normal_norm_utility(norm, persona):
    '''
    Args:
        norm:
        persona:
    Returns:
        [score,reason]
    '''
    if debug: print("GNS FUNCTION: <generate_normal_norm_utility>")
    snu = SpecificNormUtility(persona.scratch.get_str_iss())
    return snu.specific_norm_utility(norm.content)


def generate_long_term_norm_utility(norm, persona):
    if debug: print("GNS FUNCTION: <generate_long_term_norm_utility>")
    related_specific_utilities = []
    for s in norm.related_desc.split('\n')[1:]:
        try:
            s = s.split('. ')[1]
            related_specific_utilities += [persona.norm_database.content_to_act_norm[s].poignancy]
        except:
            return False
    related_specific_norms = norm.related_desc.split('S_Norms:')[-1]
    return run_gpt_long_term_norm_utility(norm.content, related_specific_norms, str(related_specific_utilities))[0]

def name_check(norm, personas):
    if norm.subject in personas.keys():
        return True
    return False


def norm_evaluate_check(norm, persona, personas, long_term_tag=False):
    '''

    Args:
        norm: node

    Returns:
        save_tag: true or false
        new_norm: node
    '''
    new_norm = NormNode(norm.id, norm.type, norm.content, norm.subject, norm.predicate, norm.object, norm.related_desc,
                        norm.poignancy, norm.poi_reason, norm.activation_state)
    if new_norm == None:
        return False, new_norm

    # Name Check
    if name_check(norm, personas):
        norm.poignancy = -4
        return False, new_norm

    # Fact Consistency Check
    cons_tag = False
    for i in range(5):
        cons_tag, new_norm_str = generate_norm_fact_consistency_check(new_norm)
        if cons_tag or new_norm_str == '':
            break
        else:
            new_norm = generate_format_norm(new_norm_str, norm.related_desc)
            if new_norm == None:
                return False, new_norm
            norm.subject=new_norm.subject
            norm.content=new_norm.content
            norm.predicate=new_norm.predicate
            norm.object=new_norm.object
    if cons_tag == False:
        norm.poignancy = -2
        return False, new_norm

    # Duplicate Check
    if long_term_tag:
        if generate_norm_duplicate_check_for_long_term(new_norm, persona):
            norm.poignancy = -3
            return False, new_norm
    else:
        if generate_norm_duplicate_check(new_norm, persona):
            norm.poignancy = -3
            return False, new_norm

    # Type Check
    type_tag = generate_seeds_type_check_v2(new_norm)
    if len(type_tag) != 2:
        return False, new_norm
    new_norm.type = type_tag[1]
    norm.type = new_norm.type

    # Conflict Check
    if generate_recognize_conflict_check(new_norm, persona):
        return False, new_norm

    # long_term_norm
    if long_term_tag:
        utility = generate_long_term_norm_utility(new_norm, persona)
        try:
            if len(utility) != 2:
                return False, new_norm
        except:
            return False, new_norm
        new_norm.poignancy = utility[0]
        new_norm.poi_reason = utility[1]
        norm.poignancy = new_norm.poignancy
        norm.poi_reason = new_norm.poi_reason
        return True, new_norm

    # normal norm
    utility = generate_normal_norm_utility(new_norm, persona)
    if len(utility) != 2:
        return False, new_norm
    new_norm.poignancy = utility[0]
    new_norm.poi_reason = utility[1]
    norm.poignancy = new_norm.poignancy
    norm.poi_reason = new_norm.poi_reason
    return True, new_norm


def norms_evaluate(persona, personas):
    # immediate evaluate recognization
    if persona.scratch.norm_evaluate:
        for norm_id, norm in persona.norm_database.norm_seed.items():
            if norm.poignancy != -1:
                continue
            save_tag, new_norm = norm_evaluate_check(norm, persona, personas)
            if save_tag:
                new_norm.activation_state = True
                norm.activation_state = True
                new_norm.validity_state = True
                norm.validity_state = True
                persona.norm_database.add_act_norm(new_norm)
                persona.scratch.norm_evaluate_trigger_curr -= new_norm.poignancy
        persona.scratch.norm_evaluate = False

    # active norm classification and long-term synthesis
    if long_term_norm_evaluate_trigger(persona):
        run_long_term_norm_evaluate(persona, personas)
        reset_norm_norm_evaluate_counter(persona)
