import sys

sys.path.append('../')

from norm.run_gpt_prompt_norm import *
from persona.cognitive_modules.retrieve import *


def generate_revise_identity_plan(statements, p_name, time):
    if debug: print("GNS FUNCTION: <generate_revise_identity_plan>")
    return run_gpt_revise_identity_plan(statements, p_name, time)[0]


def generate_revise_identity_thought(statements, p_name):
    if debug: print("GNS FUNCTION: <generate_revise_identity_thought>")
    return run_gpt_revise_identity_thought(statements, p_name)[0]


def generate_revise_identity_currently(persona, plan_note, thought_note):
    if debug: print("GNS FUNCTION: <generate_revise_identity_currently>")
    curr_act_norms = "\n"
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"- [{str(a_norm.poignancy)}] "
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    return run_gpt_revise_identity_currently(persona, plan_note, thought_note, curr_act_norms)[0]


def generate_revise_identity_daily_plan_req(persona):
    if debug: print("GNS FUNCTION: <generate_revise_identity_daily_plan_req>")
    curr_act_norms = "\n"
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"- [{str(a_norm.poignancy)}] "
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    return run_gpt_revise_identity_daily_plan_req(persona, curr_act_norms)[0]


def revise_identity_v2(persona):
    p_name = persona.scratch.name

    focal_points = [f"{p_name}'s plan for {persona.scratch.get_str_curr_date_str()}.",
                    f"Important recent events for {p_name}'s life."]
    retrieved = new_retrieve(persona, focal_points)

    statements = "[Statements]\n"
    for key, val in retrieved.items():
        for i in val:
            statements += f"{i.created.strftime('%A %B %d -- %H:%M %p')}: {i.embedding_key}\n"
    if len(retrieved)==0:
        statements+="None\n"

    plan_note = generate_revise_identity_plan(statements, p_name, persona.scratch.curr_time.strftime('%A %B %d'))
    if plan_note == False:
        return

    thought_note = generate_revise_identity_thought(statements, p_name)
    if thought_note == False:
        return

    new_currently = generate_revise_identity_currently(persona, plan_note, thought_note)
    if new_currently == False:
        return
    persona.scratch.currently = new_currently

    new_daily_req = generate_revise_identity_daily_plan_req(persona)
    if new_daily_req == False:
        return
    new_daily_req = new_daily_req.replace('\n', ' ')
    print("WE ARE HERE!!!", new_daily_req)
    persona.scratch.daily_plan_req = new_daily_req


def generate_new_daily_plan(persona, wake_up_hour):
    if debug: print("GNS FUNCTION: <generate_new_daily_plan>")
    curr_act_norms = "\n"
    for norm_id, a_norm in persona.norm_database.act_norm.items():
        if a_norm.activation_state == False:
            continue
        curr_act_norms += f"- [{str(a_norm.poignancy)}] "
        curr_act_norms += a_norm.content
        curr_act_norms += "\n"
    if curr_act_norms == "\n":
        curr_act_norms = "There is no norm.\n"
    # return run_gpt_prompt_daily_plan(persona, wake_up_hour)[0]
    return run_gpt_prompt_daily_plan_v2(persona, wake_up_hour, curr_act_norms)[0]
