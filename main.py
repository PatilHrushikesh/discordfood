import asyncio
from typing import  Tuple
import os
# from dotenv import load_dotenv
from discord import Intents, Client, Message, utils
from pollcog import MealTimes
import datetime
import constants
from utils import read_json, write_json
from table2ascii import table2ascii as t2a, PresetStyle

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
# load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
intents.members = True  # NOQA
intents.guilds = True
client: Client = Client(intents=intents)

CURRENT_MEAL = ""
current_data = [[],[]]
ratios = read_json(constants.CURRENT_WORK_FILE_PATH)
mandatory_attachments = True
print(ratios)
ADMINS = ["hrushi"]

sweep_name = kichen_name = None
actual_sweep = actual_kitchen = None

laste_committed_mems = None
        
def get_meal_type(start_time=None, end_time=None)->str:
    """Get meal type i.e LUNCH/DINNER based on current time"""

    if not start_time:
        start_time = MealTimes.LUNCH

    if not end_time:
        end_time = MealTimes.DINNER

    start_time = start_time.replace(tzinfo=None)
    end_time = end_time.replace(tzinfo=None)
    
    current_time = datetime.datetime.now().time()
    return "DINNER" if current_time >= start_time and current_time <= end_time else "LUNCH"

def get_valid_name(nick_name) -> str:
    nick_name = nick_name.lower()
    for actual_name, alternate_names in constants.MEMBERS.items():
        if nick_name in alternate_names:
            return actual_name
    return None

def process_in_out(message) -> Tuple[str, list[str]]:
    '''split input message if it contains "out" add it to 1st index of "current_data" else to 0th index'''

    msg_str:str = message.content
    msg_str = msg_str.lower().replace(',', ' ').split()
    print(f"msg_str:{msg_str}")
    confirm_list = []
    if "in" not in msg_str and "out" not in  msg_str:
        return None,confirm_list
    
    in_out_status = None
    for name in msg_str:
        if name == "in" or name == "out":
            in_out_status = 1 if name=="in" else 0
            continue
        if name == "me" or name == "i" or name == "mi":
            confirm_list.append(message.author.nick)
        elif valid_name := get_valid_name(name):
            confirm_list.append(valid_name)
    
    print(f"Proces inout:{message.author.nick}")
    if not confirm_list:
        if len(msg_str) > 1:
            print("No valid name found")
            return None, None
        confirm_list.append(get_valid_name(message.author.nick))
        
    print(f"in_out_status:{in_out_status}, confirm_list:{confirm_list}")
    return in_out_status, confirm_list

def process_combination(message)-> bool:
    """If some name is added to in before and then to out, remove it from in and move to out"""
    global current_data
    status, names = process_in_out(message)
    
    if status is None:
        return False
    
    current_state = current_data[status]
    cur_state_list = list(set(current_state) | set(names))
    current_data[status] = cur_state_list
    
    other_status = not status
    other_state_list = current_data[other_status]    
    other_state_list = list(set(other_state_list) - set(cur_state_list))
    current_data[other_status] = other_state_list
    return True
    
def create_work_list(in_only=True,limit=100000) -> str:
    global ratios
    iter_on = ratios
    if in_only:
        if not current_data[1]:
            raise Exception("In list not set yet....\n")
        iter_on = current_data[1]
    ratio_list = [(name, ratios[name]['work'] / ratios[name]['total'], ratios[name]['work'], ratios[name]['total']) for name in iter_on]

    sorted_ratios = sorted(ratio_list, key=lambda x: x[1])
    return sorted_ratios

def create_check_msg(ret_all = False):
    try:
        sorted_ratios = create_work_list(in_only=ret_all)
        result = [[name, work, total, f"{ratio:.3f}"] for name, ratio, work, total in sorted_ratios]
        header = ["Name", "Work", "Total", "Ratio"]
        output = t2a(
            header=header,
            body=result,
            style=PresetStyle.thin_compact,
            first_col_heading=True
        )   
        return f"```\n{output}\n```"
    except Exception as Ex:
        return str(Ex)

def create_work_msg():
    try:
        global kichen_name, sweep_name
        sorted_ratios = create_work_list()
        kichen_name = sorted_ratios[0][0]
        sweep_name = sorted_ratios[1][0]
        result = "==============================\n"
        result += f"Kitchen: {sorted_ratios[0][0]}\n"
        result += f"Sweep : {sorted_ratios[1][0]}\n"
        result += "==============================\n"
        return result
    except Exception as Ex:
        return str(Ex)

def process_work_done(message:Message, assigned_to, work_type):
    global actual_kitchen, mandatory_attachments
    try:
        msg_lst = message.content.split()
        work_done_by = message.author.nick
        if len(msg_lst) == 3:
            work_done_by = get_valid_name(msg_lst[-1])
            if not work_done_by:
                raise Exception(f"{msg_lst[-1]} is not valid name, Please check!")
        if mandatory_attachments:
            
            if not message.attachments:
                raise Exception("Please add photo of kichen")
        
        if work_type == "kitchen":
            actual_kitchen == work_done_by
        elif work_type == "sweep":
            actual_sweep == work_done_by
        
        return_msg:str = ""
        if assigned_to != work_done_by:
            return_msg += f"Thanks {work_done_by} for work even though it wasn't your task today!!!\n"
        return_msg += "Waiting for approval...."
        return (return_msg, work_done_by)
    except Exception as E:
        return str(E), '_'
    
def commit_in_members(in_mems=[]):
    global ratios, laste_committed_mems
    if not in_mems:
        in_mems = current_data[1]
        
    laste_committed_mems = in_mems
    for mem in in_mems:
        ratios[mem]["total"] += 1
    
    write_json(ratios, constants.CURRENT_WORK_FILE_PATH)
        
def rollback(members:list=None):
    if not members:
        members = laste_committed_mems
    members = [get_valid_name(mem) for mem in members]
    for mem in members:
        ratios[mem]["total"] -= 1
        
    write_json(ratios, constants.CURRENT_WORK_FILE_PATH)
    return create_check_msg()
    
async def process_message(message:Message):
    try:
        global current_data, CURRENT_MEAL, mandatory_attachments, ratios
        global sweep_name, kichen_name, actual_sweep, actual_kitchen
        meal_type = get_meal_type()
        #Reset current_data and CURRENT_MEAL if meal type get changed
        if CURRENT_MEAL != meal_type:
            print(f"Printing meal type {meal_type}")
            current_data = [[],[]]
            CURRENT_MEAL = meal_type
            sweep_name = kichen_name = None
            actual_sweep = actual_kitchen = None
                
        msg_str:str =  message.content
        msg_str = msg_str.lower()
        if msg_str.startswith("add"):
            auth = message.author.nick
            if auth.lower() != "hrushi":
                return "Only Hrushi can do it"
            
            msg_str = msg_str.split()
            valid_name = get_valid_name(msg_str[1])
            if not valid_name:
                return f"{msg_str[1]} is not valid name"
                
            ADMINS.append(valid_name)
            return f"Current admins {','.join(ADMINS)}"
        if msg_str.startswith("remove"):
            auth = message.author.nick
            if auth.lower() != "hrushi":
                return "Only Hrushi can do it"
            
            msg_str = msg_str.split()
            valid_name = get_valid_name(msg_str[1])
            if not valid_name:
                return f"{msg_str[1]} is not valid name"
                
            ADMINS.remove(valid_name)
            return f"Current admins {','.join(ADMINS)}"
            
        if msg_str.startswith("set"):
            auth = message.author.nick
            if auth.lower() not in ADMINS:
                return "Only admin can set"
            
            msg_str = msg_str.split()
            valid_name = get_valid_name(msg_str[1])
            if not valid_name:
                return f"{msg_str[1]} is not valid name"
            
            ratios[valid_name]["work"] = int(msg_str[2])
            ratios[valid_name]["total"] = int(msg_str[3])
            write_json(ratios, constants.CURRENT_WORK_FILE_PATH)
            return create_check_msg()
            
        if msg_str.startswith("image"):
            auth = message.author.nick
            if auth.lower() not in ADMINS:
                return "Only admin can approve"
            
            msg_str = msg_str.split()
            mandatory_attachments = bool(int(msg_str[1]))
            if mandatory_attachments:
                return "Users now need to add image of kitchen after cleaning"
            else:
                return "Users don't need to add image of kitchen after cleaning"
        if msg_str.startswith("check"):
            msg_lst = msg_str.split()
            ret_all = len(msg_lst)==1
            return create_check_msg(ret_all)
        if msg_str.startswith("result"):
            return create_work_msg()
        
        create_work_msg() # This will just populate kichen_name and sweep_name
        if  msg_str.startswith("sweep done") or msg_str.startswith("kitchen done"):
            sorted_ratios = create_work_list()
            if msg_str.startswith("kitchen"):
                return_msg, _ = process_work_done(message, sorted_ratios[0][0], "kitchen")
            elif msg_str.startswith("sweep"):
                return_msg, _ = process_work_done(message, sorted_ratios[1][0], "sweep")
            
            return return_msg
        
        if msg_str.startswith("approve"):
            sorted_ratios = create_work_list()
            
            auth = message.author.nick
            if auth.lower() not in ADMINS:
                return "Only admin can approve"
            
            user_message = await message.channel.fetch_message(message.reference.message_id)
            user_message_cont = user_message.content.lower()
            if  user_message_cont.startswith("sweep done") or user_message_cont.startswith("kitchen done"):
                if user_message_cont.startswith("kitchen"):
                    _, worker_name = process_work_done(user_message, sorted_ratios[0][0], "kitchen")
                elif user_message_cont.startswith("sweep"):
                    _, worker_name = process_work_done(user_message, sorted_ratios[1][0], "sweep")
                
                ratios[worker_name.lower()]["work"] += 1
                write_json(ratios, constants.CURRENT_WORK_FILE_PATH)
                await message.channel.send(f"{worker_name}, your current work count is {ratios[worker_name]['work']}")
                await asyncio.sleep(1)
                current_standings = create_check_msg()
                return current_standings
        
        if msg_str.startswith("commit"):
            auth = message.author.nick
            if auth.lower() not in ADMINS:
                return "Only admin can commit"
            names = msg_str.split()[1:]
            commit_in_members(names)
            return
            
        if msg_str.startswith("rollback"):
            auth = message.author.nick
            if auth.lower() not in ADMINS:
                return "Only admin can rollback"
            names = msg_str.split()[1:]
            rollback(names)
            return
                    
        if not process_combination(message):
            return ""
        
        return_msg = ""
        if current_data[0]:
            return_msg += f"OUT({len(current_data[0])}): {','.join(current_data[0])}\n"
            
        if current_data[1]:
            return_msg += f"IN({len(current_data[1])}): {','.join(current_data[1])}\n"
        
        print(f"return_msg:{return_msg}")
            
        return return_msg
    except Exception as Ex:
        return str(Ex)
    

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return
    

    # if is_private := user_message[0] == '?':
    #     user_message = user_message[1:]

    try:
        response: str = user_message
        await message.reply(response)
        # return await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')


# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user or str(message.channel) not in constants.CHANNELS:
        return
    
    print(f"Author:{message.author}")
    print(f"message:{message}")
    user_message = await process_message(message)
    if user_message:
        await send_message(message, user_message)


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()