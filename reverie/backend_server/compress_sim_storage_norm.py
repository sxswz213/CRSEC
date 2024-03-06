import shutil
import json

#from persona.prompt_template.run_gpt_prompt import *
from utils import *
from global_methods import *
import openai

openai.api_key = openai_api_key


def generate_prompt(curr_input, prompt_lib_file, example=""):
    if type(curr_input) == type("string"):
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]

    f = open(prompt_lib_file, "r")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt:
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    prompt = example + prompt
    return prompt.strip()


def ChatGPT_request(prompt):
    """
    Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
    server and returns the response.
    ARGS:
      prompt: a str prompt
      gpt_parameter: a python dictionary with the keys indicating the names of
                     the parameter and the values indicating the parameter
                     values.
    RETURNS:
      a str of GPT-3's response.
    """
    # temp_sleep()
    try:
        completion = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        print(completion)
        return completion["choices"][0]["message"]["content"]

    except:
        print("ChatGPT ERROR")
        return "ChatGPT ERROR"


def ChatGPT_safe_generate_response_OLD(prompt,
                                       repeat=3,
                                       fail_safe_response="error",
                                       func_validate=None,
                                       func_clean_up=None,
                                       verbose=False):
    if verbose:
        print("CHAT GPT PROMPT")
        print(prompt)

    for i in range(repeat):
        try:
            curr_gpt_response = ChatGPT_request(prompt)  # .strip()
            if func_validate(curr_gpt_response, prompt=prompt):
                return func_clean_up(curr_gpt_response, prompt=prompt)
            if verbose:
                print(f"---- repeat count: {i}")
                print(curr_gpt_response)
                print("~~~~")

        except:
            pass
    print("FAIL SAFE TRIGGERED")
    return fail_safe_response

def run_gpt_prompt_pronunciatio_for_chat(action_description, persona, chat, example, verbose=False):
    def create_prompt_input(action_description, persona, chat, example):
        if "(" in action_description:
            action_description = action_description.split("(")[-1].split(")")[0]
        prompt_input = [action_description, example]
        return prompt_input

    def __func_clean_up(gpt_response, prompt=""):
        cr = gpt_response.strip()
        if len(cr) > 2:
            cr = cr[:2]
        return cr

    def __func_validate(gpt_response, prompt=""):
        print(gpt_response)
        try:
            __func_clean_up(gpt_response, prompt="")
            if len(gpt_response) == 0:
                return False
            if gpt_response == "ChatGPT ERROR":
                return False
        except:
            return False
        return True

    def get_fail_safe():
        fs = "?"
        return fs


    print("asdhfapsh8p9hfaiafdsi;ldfj as DEBUG 4")  ########
    gpt_param = {"engine": "gpt-3.5-turbo", "max_tokens": 15,
                 "temperature": 0, "top_p": 1, "stream": False,
                 "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
    prompt_template = "norm/other_prompt/generate_pronunciatio_v2.txt"  ########
    prompt_input = create_prompt_input(action_description, persona, chat, example)  ########
    prompt = generate_prompt(prompt_input, prompt_template)
    fail_safe = get_fail_safe()
    output = ChatGPT_safe_generate_response_OLD(prompt, 3, fail_safe,
                                                __func_validate, __func_clean_up)
    #print(prompt)
    if output != False:
        return output, [output, prompt, gpt_param, prompt_input, fail_safe]

def generate_action_pronunciatio_for_chat(act_desp, persona,chat,example): 
  """TODO 
  Given an action description, creates an emoji string description via a few
  shot prompt. 

  Does not really need any information from persona. 

  INPUT: 
    act_desp: the description of the action (e.g., "sleeping")
    persona: The Persona class instance
  OUTPUT: 
    a string of emoji that translates action description.
  EXAMPLE OUTPUT: 
    "🧈🍞"
  """
  if debug: print ("GNS FUNCTION: <generate_action_pronunciatio_for_chat>")
  #temp_sleep()
  x = run_gpt_prompt_pronunciatio_for_chat(act_desp, persona, chat, example)[0]

  if not x or x=="Cha": 
    return "🙂"
  return x

def compress(sim_code):
  sim_storage = f"../../environment/frontend_server/storage/{sim_code}"
  compressed_storage = f"../../environment/frontend_server/compressed_storage/{sim_code}"
  persona_folder = sim_storage + "/personas"
  move_folder = sim_storage + "/movement"
  meta_file = sim_storage + "/reverie/meta.json"

  persona_names = []
  for i in find_filenames(persona_folder, ""): 
    x = i.split("/")[-1].strip()
    if x[0] != ".": 
      persona_names += [x]

  max_move_count = max([int(i.split("/")[-1].split(".")[0]) 
                 for i in find_filenames(move_folder, "json")])
  
  persona_last_move = dict()
  master_move = dict()  
  for i in range(max_move_count+1): 
    master_move[i] = dict()
    with open(f"{move_folder}/{str(i)}.json") as json_file:  
      i_move_dict = json.load(json_file)["persona"]
      for p in persona_names: 
        move = False
        if i == 0: 
          move = True
        elif (i_move_dict[p]["movement"] != persona_last_move[p]["movement"]
          #or i_move_dict[p]["pronunciatio"] != persona_last_move[p]["pronunciatio"]
          or i_move_dict[p]["description"] != persona_last_move[p]["description"]
          or i_move_dict[p]["chat"] != persona_last_move[p]["chat"]): 
          move = True

        if move: 
          if i_move_dict[p]["chat"] != None:
              example='''Example:
                  Action description: conversing about the benefits and drawbacks of smoking indoors and the importance of respecting Hobbs Cafe's strict no smoking policy to maintain a healthy and respectful environment for everyone, between Francisco Lopez and Abigail Chen.
                  Emoji:💬🚭'''
              pronunciatio = generate_action_pronunciatio_for_chat(i_move_dict[p]["description"], p, i_move_dict[p]["chat"], example)
              
              if "💬" not in pronunciatio:
                 if len(pronunciatio.strip()) >= 2:
                    pronunciatio=pronunciatio[-1]
                 pronunciatio = "💬" + pronunciatio
              print(pronunciatio)
          else:
              pronunciatio = i_move_dict[p]["pronunciatio"] 
          persona_last_move[p] = {"movement": i_move_dict[p]["movement"],
                                  "pronunciatio": pronunciatio, 
                                  "description": i_move_dict[p]["description"], 
                                  "chat": i_move_dict[p]["chat"]}
          master_move[i][p] = {"movement": i_move_dict[p]["movement"],
                               "pronunciatio": pronunciatio, 
                               "description": i_move_dict[p]["description"], 
                               "chat": i_move_dict[p]["chat"]}


  create_folder_if_not_there(compressed_storage)
  with open(f"{compressed_storage}/master_movement.json", "w") as outfile:
    outfile.write(json.dumps(master_move, indent=2))

  shutil.copyfile(meta_file, f"{compressed_storage}/meta.json")
  shutil.copytree(persona_folder, f"{compressed_storage}/personas/")


if __name__ == '__main__':
  compress("the_ville_n10_with_norm_day_1_19")









  











