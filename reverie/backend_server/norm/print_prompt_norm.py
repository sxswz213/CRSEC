import sys
sys.path.append('../')

import json
import numpy
import datetime
import random

from global_methods import *
from persona.prompt_template.gpt_structure import *
from utils import *

##############################################################################
#                    PERSONA Chapter 1: Prompt Structures                    #
##############################################################################

def print_run_prompts_norm(prompt_template=None,
                      gpt_param=None,
                      prompt_input=None,
                      prompt=None,
                      output=None):
  print (f"=== {prompt_template}")
  print ("~~~ persona    ---------------------------------------------------")
  print (gpt_param, "\n")
  print ("~~~ prompt_input    ----------------------------------------------")
  print (prompt_input, "\n")
  print ("~~~ prompt    ----------------------------------------------------")
  print (prompt, "\n")
  print ("~~~ output    ----------------------------------------------------")
  print (output, "\n")
  print ("=== END ==========================================================")
  print ("\n\n\n")
