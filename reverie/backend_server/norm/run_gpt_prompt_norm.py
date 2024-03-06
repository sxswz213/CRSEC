import sys

sys.path.append('../')
from persona.prompt_template.gpt_structure import *
from persona.prompt_template.print_prompt import *
from norm.print_prompt_norm import *


def run_gpt_prompt_decide_if_norm_conflict(target_person_description, init_persona_norms, target_p, init_p_identity,
                                           init_p_innate, verbose=False):
    def create_prompt_input(target_person_description, init_persona_norms, target_p, init_p_identity,
                            init_p_innate):
        prompt_input = []
        prompt_input += [target_person_description]
        prompt_input += [init_persona_norms]
        prompt_input += [init_p_identity]
        prompt_input += [init_p_innate]
        prompt_input += [target_p]
        return prompt_input

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split("FINAL OUTPUT: ")[-1].split("\n")[0].lower() in ["yes", "no"] and \
                    gpt_response.split('whether there is a conflict?\nAnswer in "yes" or "no" and provide a reason: ')[
                        -1].split("//")[0].lower() in ["yes", "no"]:
                return True
            return False
        except:
            return False

    def __func_clean_up(gpt_response, prompt=""):

        return [gpt_response.split("FINAL OUTPUT: ")[-1].split("\n")[0].lower(), gpt_response,
                gpt_response.split('whether there is a conflict?\nAnswer in "yes" or "no" and provide a reason: ')[
                    -1].split("//")[0].lower()]

    def get_fail_safe():
        fs = "ERROR"
        return [fs]

    gpt_param = {"engine": "gpt-4-1106-preview", "max_tokens": 20,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_retrieve_prompt/check_conflict_decide_talk_v5.txt"
    prompt_input = create_prompt_input(target_person_description, init_persona_norms, target_p, init_p_identity,
                                       init_p_innate)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    if len(output) == 3:
        print("check_conflict_decide_talk_vvvvvvvvv5: talk?", output[0],"; conflict?", output[2])
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_norm_reflect_from_thoughts(reletive_thoughts, verbose=False):
    '''
    Args:
        reletive_thoughts: str of thought with its filling thoughts: "1.xxxx\n2.xxxxx\n3.xxxxx\n"

    Returns:
    '''

    def create_prompt_input(reletive_thoughts):
        prompt_input = [reletive_thoughts]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = gpt_response.strip()
        ret = []
        for str in gpt_response.split('- Norm: ')[1:]:
            ret += [[str.split(" Related thought: ")[0].strip('\"'),
                     str.split(" Related thought: ")[1].strip('\n').strip('\"')]]
        print(gpt_response)
        print(ret)
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-4-1106-preview", "max_tokens": 150,
                 "temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_identify_prompt/thought_reflect_v3.txt"
    prompt_input = create_prompt_input(reletive_thoughts)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_norm_format(norm_str, verbose=False):
    def create_prompt_input(norm_str):
        prompt_input = [norm_str]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):

        print(gpt_response)
        j = json.loads(gpt_response.split('OUTPUT:')[-1])
        print(type(j))
        print(j)
        return j

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_identify_prompt/identify_norm_save_v3.txt"
    prompt_input = create_prompt_input(norm_str)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    print(norm_str, output)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_conflict_chat_reflect(all_utt, verbose=False):
    '''
    Returns:
        output=[norm_str, reflect_tag]
    '''

    def create_prompt_input(all_utt):
        prompt_input = [all_utt]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):

        print(gpt_response)
        res = gpt_response.split('Step 3: ')[-1]
        if res[:2].lower() == 'no' and res[:4].lower() != 'norm':
            return ["", False]
        norm_str = res.split(": ")[-1]
        return [norm_str, True]

    def __func_validate(gpt_response, prompt=""):
        try:
            if len(gpt_response.split('Step 3:')) > 1:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_identify_prompt/conflict_chat_reflect_v1.txt"
    prompt_input = create_prompt_input(all_utt)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_non_norm_conflict_chat_reflect(all_utt, verbose=False):
    '''
    Returns:
        output = ture or false
    '''

    def create_prompt_input(all_utt):
        prompt_input = [all_utt]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):

        print(gpt_response)
        if gpt_response.strip().split('.')[0].split(',')[0].lower() == "yes":
            return True
        return False

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.strip().split('.')[0].split(',')[0].lower() in ["yes", "no"]:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_identify_prompt/non_conflict_chat_reflect_v1.txt"
    prompt_input = create_prompt_input(all_utt)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_chat_norms_summarize(all_utt, verbose=False):
    def create_prompt_input(all_utt):
        prompt_input = [all_utt]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        gpt_response = "1. " + gpt_response.strip()
        ret = []
        for str in gpt_response.split("\n"):
            ret += [str.split(". ")[-1]]
        print(gpt_response)
        print(ret)
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0.5, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_identify_prompt/chat_summarize_norms_v1.txt"
    prompt_input = create_prompt_input(all_utt)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_immediate_evaluate_recognization(curr_norm_seed, curr_active_norms, seed_related_desc, curr_person_name,
                                             verbose=False):
    '''

    Args:
        curr_norm_seed: str
        curr_active_norms:str
        seed_related_desc:str
        curr_person_name:str

    Returns:
        output = [poi, norm_tag]
    '''

    def create_prompt_input(curr_norm_seed, curr_active_norms, seed_related_desc, curr_person_name):
        prompt_input = [curr_norm_seed]
        prompt_input += [curr_active_norms]
        prompt_input += [seed_related_desc]
        prompt_input += [curr_person_name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        poi = int(gpt_response.split("NORM UTILITY: ")[-1].split("\n")[0])
        tag = gpt_response.split("ANSWER: ")[-1].lower()
        if tag == 'yes':
            return [poi, True]
        return [poi, False]

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/immediate_evaluate_recognization_v1.txt"
    prompt_input = create_prompt_input(curr_norm_seed, curr_active_norms, seed_related_desc, curr_person_name)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
                                    __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_seeds_content_check(candidate_norm, curr_active_norms, seed_related_desc, verbose=False):
    def create_prompt_input(candidate_norm, curr_active_norms, seed_related_desc):
        prompt_input = [candidate_norm]
        prompt_input += [curr_active_norms]
        prompt_input += [seed_related_desc]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('Answer 1 (return only in "YES" or "NO")###:')[-1].strip().split('\n')[0].lower().split(
            '\"')[0]
        x2 = gpt_response.split('Answer 2###:')[-1].strip().split('\n')[0].lower().split('\"')[0]
        x3 = gpt_response.split('STAGE 1:')[-1].strip().split('\n')[0].lower().split('\"')[0]
        return [x1, x2, x3]

    def __func_validate(gpt_response, prompt=""):
        try:
            if \
                    gpt_response.split('Answer 1 (return only in "YES" or "NO")###:')[-1].strip().split('\n')[
                        0].lower().split(
                        '\"')[0] in ["yes", "no"] and \
                            gpt_response.split('Answer 2###:')[-1].strip().split('\n')[0].lower().split('\"')[0] in [
                        "yes",
                        "no"] and \
                            gpt_response.split('STAGE 1:')[-1].strip().split('\n')[0].lower().split('\"')[0] in ["yes",
                                                                                                                 "no"]:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-4", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/seeds_content_check_v1.txt"
    prompt_input = create_prompt_input(candidate_norm, curr_active_norms, seed_related_desc)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_active_norms_classfication(curr_active_norms, verbose=False):
    def create_prompt_input(curr_active_norms):
        prompt_input = [curr_active_norms]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        ret = []
        for str in gpt_response.split("ABSTRACT: ")[1:]:
            ret += [[str.split('\n')[0], str.split('\n')[1]]]
        return ret

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/active_norms_classfication_v1.txt"
    prompt_input = create_prompt_input(curr_active_norms)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = safe_generate_response(prompt, gpt_param, 5, fail_safe,
                                    __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_seeds_type_check(candidate_norm, verbose=False):
    def create_prompt_input(candidate_norm):
        prompt_input = [candidate_norm]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('OUTPUT: <"')[-1].split('"')[0].lower()
        x2 = gpt_response.lower().split('the type classification for input is "')[-1].split('"')[0]
        return [x1, x2]

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split('OUTPUT: <"')[-1].split('"')[0].lower() in ['incorrect', 'correct'] and \
                    gpt_response.lower().split('the type classification for input is "')[-1].split('"')[0] in [
                'descriptive', 'prohibitive', 'prescriptive']:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-4", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/seeds_type_check_v1.txt"
    prompt_input = create_prompt_input(candidate_norm)
    prompt = generate_prompt(prompt_input, prompt_template)

    print(prompt)
    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_norm_recognize(candidate_norm, curr_active_norms, candidate_norm_utility, persona_ISS, persona_name,
                           verbose=False):
    def create_prompt_input(candidate_norm, curr_active_norms, candidate_norm_utility, persona_ISS, persona_name):
        prompt_input = [candidate_norm]
        prompt_input += [curr_active_norms]
        prompt_input += [candidate_norm_utility]
        prompt_input += [persona_ISS]
        prompt_input += [persona_name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('Answer 1: ')[-1].split('\n')[0].lower()
        x2 = gpt_response.split('Answer 2: ')[-1].split('\n')[0].lower()
        x3 = gpt_response.split('Answer 3: ')[-1].split('\n')[0].lower()
        x4 = gpt_response.split('Answer 4: ')[-1].split('\n')[0].lower()
        return [x1, x2, x3, x4]

    def __func_validate(gpt_response, prompt=""):
        print(gpt_response)
        try:
            x1 = gpt_response.split('Answer 1: ')[-1].split('\n')[0].lower()
            x2 = gpt_response.split('Answer 2: ')[-1].split('\n')[0].lower()
            x3 = gpt_response.split('Answer 3: ')[-1].split('\n')[0].lower()
            x4 = gpt_response.split('Answer 4: ')[-1].split('\n')[0].lower()
            if x1 in ['yes', 'no'] and x2 in ['yes', 'no'] and x3 in ['yes', 'no'] and x4 in ['yes', 'no']:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-4", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/recognization_v1.txt"
    prompt_input = create_prompt_input(candidate_norm, curr_active_norms, candidate_norm_utility, persona_ISS,
                                       persona_name)
    prompt = generate_prompt(prompt_input, prompt_template)

    print(prompt)
    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_norm_duplicate_check(candidate_norm, curr_active_norms, verbose=False):
    def create_prompt_input(candidate_norm, curr_active_norms):
        prompt_input = [candidate_norm]
        prompt_input += [curr_active_norms]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        return [gpt_response.strip().lower(), True]

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.strip().lower() in ['yes', 'no']:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-4-1106-preview", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/duplicate_check_v1.txt"
    prompt_input = create_prompt_input(candidate_norm, curr_active_norms)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()

    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_norm_fact_consistency_check(candidate_norm, seed_related_desc, verbose=False):
    def create_prompt_input(candidate_norm, seed_related_desc):
        prompt_input = [candidate_norm]
        prompt_input += [seed_related_desc]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('Answer: ')[-1].split('.')[0].lower()
        x2 = gpt_response.split('New norm: ')[-1]
        return [x1, x2]

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split('Answer: ')[-1].split('.')[0].lower() in ['yes', 'no']:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/fact_consistency_check_v1.txt"
    prompt_input = create_prompt_input(candidate_norm, seed_related_desc)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_norm_utility(candidate_norm, verbose=False):
    def create_prompt_input(candidate_norm):
        prompt_input = [candidate_norm]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = int(gpt_response.split('OUTPUT: ')[-1].split('.')[0])
        x2 = gpt_response.split('OUTPUT: ')[-1].split('.')[1].strip()
        return [x1, x2]

    def __func_validate(gpt_response, prompt=""):
        print(gpt_response)
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/norm_utility_v2.txt"
    prompt_input = create_prompt_input(candidate_norm)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD_t0(prompt, 3, fail_safe,
                                                   __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_norm_long_term_synthesis(classified_act_norms, verbose=False):
    def create_prompt_input(classified_act_norms):
        prompt_input = [classified_act_norms]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        ret = []
        for str in gpt_response.split(": ")[1:]:
            ret += [str.split('\n')[0]]
        return ret

    def __func_validate(gpt_response, prompt=""):
        print(gpt_response)
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/long_term_synthesis_v2.txt"
    prompt_input = create_prompt_input(classified_act_norms)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_active_norms_classfication_v2(curr_active_norms, verbose=False):
    def create_prompt_input(curr_active_norms):
        prompt_input = [curr_active_norms]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-4-1106-preview", "max_tokens": 150,
                 "temperature": 1, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/active_norms_classfication_v3.txt"
    prompt_input = create_prompt_input(curr_active_norms)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD_t1(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_seeds_type_check_v2(candidate_norm, norm_type, verbose=False):
    def create_prompt_input(candidate_norm, norm_type):
        prompt_input = [norm_type]
        prompt_input += [candidate_norm]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('STEP 1: <"')[-1].split('"')[0].lower()
        x2 = gpt_response.split('STEP 2: <"')[-1].split('"')[0].lower()
        x3 = gpt_response.split('The type classification for INPUT is <"')[-1].split('"')[0].lower()
        return [x1, x2, x3]

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split('STEP 1: <"')[-1].split('"')[0].lower() in ['yes', 'no'] and \
                    gpt_response.split('STEP 2: <"')[-1].split('"')[0].lower() in ['incorrect', 'correct'] and \
                    gpt_response.split('The type classification for INPUT is <"')[-1].split('"')[0].lower() in [
                'descriptive', 'injunctive']:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-4", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/seeds_type_check_v3.txt"
    prompt_input = create_prompt_input(candidate_norm, norm_type)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_norm_recognize_conflict_check(candidate_norm, curr_active_norms, verbose=False):
    def create_prompt_input(candidate_norm, curr_active_norms):
        prompt_input = [candidate_norm]
        prompt_input += [curr_active_norms]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('Answer: ')[-1].split('.')[0].lower()
        return x1

    def __func_validate(gpt_response, prompt=""):
        try:
            if gpt_response.split('Answer: ')[-1].split('.')[0].lower() in ['yes', 'no']:
                return True
            return False
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-4", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/recognize_conflict_check_v1.txt"
    prompt_input = create_prompt_input(candidate_norm, curr_active_norms)
    prompt = generate_prompt(prompt_input, prompt_template)

    print(prompt)
    fail_safe = get_fail_safe()
    output = GPT4_safe_generate_response_OLD(prompt, 3, fail_safe,
                                             __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_long_term_norm_utility(candidate_norm, related_specific_norms, related_specific_utilities, verbose=False):
    def create_prompt_input(candidate_norm, related_specific_norms, related_specific_utilities):
        prompt_input = [candidate_norm]
        prompt_input += [related_specific_norms]
        prompt_input += [related_specific_utilities]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        x1 = gpt_response.split('>. ')[-1].split('\n')[0]
        x2 = int(float(gpt_response.split('FINAL SCORE: [')[-1].split(']')[0]))
        return [x2, x1]

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return ["I am hungry"]

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_evaluate_prompt/abstract_norm_utility_v1.txt"
    prompt_input = create_prompt_input(candidate_norm, related_specific_norms, related_specific_utilities)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD_t0(prompt, 3, fail_safe,
                                                   __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


class SpecificNormUtility:
    def __init__(self, system_msg, model="gpt-3.5-turbo-16k", temprature=0, max_tokens=4096, top_p=1,
                 frequency_penalty=0, presence_penalty=0):
        # parameter
        self.msg = [{"role": "system", "content": system_msg}]
        self.model = model
        self.temp = temprature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    # input prompt, return explicit norms
    def specific_norm_utility(self, candidate_norm):
        prompt_template = "norm/norm_evaluate_prompt/specific_norm_utility_v2.txt"
        prompt = generate_prompt([candidate_norm], prompt_template)

        user_prompt = {"role": "user", "content": prompt}
        self.msg.append(user_prompt)
        print(self.msg)
        try:
            gpt_ret = openai.ChatCompletion.create(model=self.model, messages=self.msg, temperature=self.temp,
                                                   max_tokens=self.max_tokens, top_p=self.top_p,
                                                   frequency_penalty=self.frequency_penalty,
                                                   presence_penalty=self.presence_penalty)
        except:
            return False
        print(gpt_ret)
        ret_str = gpt_ret["choices"][0]["message"]["content"]
        try:
            x1 = int(ret_str.split("OUTPUT: ")[-1].split('.')[0])
            x2 = ret_str.split("OUTPUT: ")[-1].split('. ')[1]
            return [x1, x2]
        except:
            return [False]


def run_gpt_revise_identity_plan(statements, p_name, time, verbose=False):
    def create_prompt_input(statements, p_name, time):
        prompt_input = [statements]
        prompt_input += [p_name]
        prompt_input += [time]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_compliance_prompt/revise_identity_plan_v1.txt"
    prompt_input = create_prompt_input(statements, p_name, time)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_revise_identity_thought(statements, p_name, verbose=False):
    def create_prompt_input(statements, p_name):
        prompt_input = [statements]
        prompt_input += [p_name]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_compliance_prompt/revise_identity_thought_v1.txt"
    prompt_input = create_prompt_input(statements, p_name)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_revise_identity_currently(persona, plan_note, thought_note, curr_active_norms_and_utility, verbose=False):
    def create_prompt_input(persona, plan_note, thought_note, curr_active_norms_and_utility):
        prompt_input = [persona.scratch.name]
        prompt_input += [(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')]
        prompt_input += [persona.scratch.currently]
        prompt_input += [(plan_note + thought_note).replace('\n', '')]
        prompt_input += [persona.scratch.curr_time.strftime('%A %B %d')]
        prompt_input += [curr_active_norms_and_utility]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        return gpt_response.split("Status: ")[-1]

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_compliance_prompt/revise_identity_currently_v1.txt"
    prompt_input = create_prompt_input(persona, plan_note, thought_note, curr_active_norms_and_utility)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_revise_identity_daily_plan_req(persona, curr_act_norms, verbose=False):
    def create_prompt_input(persona, curr_act_norms):
        prompt_input = [persona.scratch.get_str_iss()]
        prompt_input += [persona.scratch.curr_time.strftime('%A %B %d')]
        prompt_input += [persona.scratch.name]
        prompt_input += [curr_act_norms]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        print(gpt_response)
        return gpt_response

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt)
            return True
        except:
            return False

    def get_fail_safe():
        return False

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 150,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_compliance_prompt/revise_identity_daily_plan_req_v1.txt"
    prompt_input = create_prompt_input(persona, curr_act_norms)
    prompt = generate_prompt(prompt_input, prompt_template)

    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    if debug or verbose:
        print_run_prompts_norm(prompt_template, gpt_param, prompt_input, prompt, output)
    return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_daily_plan_v2(persona, wake_up_hour, curr_act_norm, test_input=None, verbose=False):
    def create_prompt_input(persona, wake_up_hour, curr_act_norm, test_input=None):
        if test_input: return test_input
        prompt_input = []
        prompt_input += [persona.scratch.get_str_iss()]
        prompt_input += [persona.scratch.get_str_lifestyle()]
        prompt_input += [persona.scratch.get_str_curr_date_str()]
        prompt_input += [persona.scratch.get_str_firstname()]
        prompt_input += [f"{str(wake_up_hour)}:00 am"]
        prompt_input += [curr_act_norm]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = []
        _cr = gpt_response.split(")")
        for i in _cr:
            if i[-1].isdigit():
                i = i[:-1].strip()
                if i[-1] == "." or i[-1] == ",":
                    cr += [i[:-1].strip()]
        return cr

    def __func_validate(gpt_response, prompt=""):
        try:
            __func_clean_up(gpt_response, prompt="")
        except:
            return False
        return True

    def get_fail_safe():
        fs = ['wake up and complete the morning routine at 6:00 am',
              'eat breakfast at 7:00 am',
              'read a book from 8:00 am to 12:00 pm',
              'have lunch at 12:00 pm',
              'take a nap from 1:00 pm to 4:00 pm',
              'relax and watch TV from 7:00 pm to 8:00 pm',
              'go to bed at 11:00 pm']
        return fs

    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 500,
                 "temperature": 1, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/norm_compliance_prompt/daily_planning_compliance_v2.txt"
    prompt_input = create_prompt_input(persona, wake_up_hour, curr_act_norm, test_input)
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()

    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)

    output = ([f"wake up and complete the morning routine at {wake_up_hour}:00 am"]
              + output)

    if debug or verbose:
        print_run_prompts(prompt_template, persona, gpt_param,
                          prompt_input, prompt, output)

    return output, [output, prompt, gpt_param, prompt_input, fail_safe]
