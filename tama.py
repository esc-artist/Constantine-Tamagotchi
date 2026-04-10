#!/usr/bin/env python3

import os
import argparse
import json
import datetime
import random
from git import Repo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ledger_json_path = os.path.join(SCRIPT_DIR, 'ledger.json')
ledger_txt_path = os.path.join(SCRIPT_DIR, 'ledger.txt')
history_json_path = os.path.join(SCRIPT_DIR, 'history.json')
history_txt_path = os.path.join(SCRIPT_DIR, 'history.txt')
schedule_txt_path = os.path.join(SCRIPT_DIR, 'schedule.txt')

def add_hour_function(num_hours):
    tokens = 0
    for hour in range(1, num_hours + 1):
        tokens += hour * 2  # tokens earned every half hour increase by 1 every hour
    return tokens

def subtract_hour_function(num_hours):
    tokens = 0
    return -(num_hours * 4) # 1 token per 15 mins tv


def args():
    parser = argparse.ArgumentParser(
                        prog='tama.py',
                        description='Constantine Tamagotchi CLI')
    parser.add_argument('--add', type=int, metavar=('NUM_TOKENS'))
    parser.add_argument('--subtract',type=int, metavar=('NUM_TOKENS'))
    parser.add_argument('--earn', nargs=2, metavar=('NUM_TOKENS', 'REASON'))
    parser.add_argument('--spend', nargs=2, metavar=('NUM_TOKENS', 'REASON'))
    parser.add_argument('--by-hour', action='store_true')
    parser.add_argument('--calc', action='store_true')
    parser.add_argument('--spin', action='store_true')
    parser.add_argument('--publish', action='store_true')

    args = parser.parse_args()

    incompatible_set = {'add','subtract','earn','spend', 'spin'}

    is_set = ""
    for key in vars(args):
        if getattr(args, key) and key in incompatible_set:
            if is_set:
                print(f"Incompatible args: {is_set} {key}")
                exit()
            else:
                is_set = key

    if not is_set and not args.publish:
        print("Need arg(s).")
        exit()


    if args.add is not None:
        if args.by_hour and args.calc:
            num_tokens = add_hour_function(args.add)
            print(f"CALCULATION: {num_tokens} TOKENS.")
            exit()
        return (args.add, None, args.publish, None, args.by_hour)
    elif args.subtract is not None:
        if args.by_hour and args.calc:
            num_tokens = subtract_hour_function(args.subtract)
            print(f"CALCULATION: {num_tokens} TOKENS.")
            exit()
        else:
            neg = -(abs(args.subtract))
        return (neg, None, args.publish, None, args.by_hour) 
    elif args.earn is not None:
        num_tokens, reason = args.earn
        num_tokens = int(num_tokens)
        if args.by_hour and args.calc:
            num_tokens = add_hour_function(num_tokens)
            print(f"CALCULATION: {num_tokens} TOKENS.")
            exit()
        return (num_tokens, reason, args.publish, None, args.by_hour)
    elif args.spend is not None:
        num_tokens, reason = args.spend
        num_tokens = int(num_tokens)
        if args.by_hour and args.calc:
            num_tokens = subtract_hour_function(num_tokens)
            print(f"CALCULATION: {num_tokens} TOKENS.")
            exit()
        else:
            neg = -(abs(num_tokens))
        return (neg, reason, args.publish, None, args.by_hour)
    elif args.spin:
        return (0, None, args.publish, True, False)
    elif args.publish:
        return (0, None, True, False, False)
    
def add(num_tokens, by_hour):
    if by_hour:
        num_tokens = add_hour_function(num_tokens)
    with open(ledger_json_path, 'r') as ledger:
        ledger_data = json.load(ledger)
    ledger_data['ledger']['tokens'] += num_tokens
    with open(ledger_json_path, 'w') as ledger:
        json.dump(ledger_data, ledger)
    with open(history_json_path, 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, None]
    with open(history_json_path, 'w') as history:
        json.dump(history_data, history)
    print(f"ADDED {num_tokens} TOKENS")    
def earn(num_tokens, reason, by_hour): 
    if by_hour:
        num_tokens = add_hour_function(num_tokens)
    with open(ledger_json_path, 'r') as ledger:
        ledger_data = json.load(ledger)
    ledger_data['ledger']['tokens'] += num_tokens
    with open(ledger_json_path, 'w') as ledger:
        json.dump(ledger_data, ledger)
    with open(history_json_path, 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, reason.lower()]
    with open(history_json_path, 'w') as history:
        json.dump(history_data, history)
    print(f"EARNED {num_tokens} TOKENS") 
def subtract(num_tokens, by_hour):
    if by_hour:
        num_tokens = subtract_hour_function(abs(num_tokens))
    with open(ledger_json_path, 'r') as ledger:
        ledger_data = json.load(ledger)
    if ledger_data['ledger']['tokens'] + num_tokens < 0:
        print("Cannot complete operation: Not enough tokens.")
        exit()
    ledger_data['ledger']['tokens'] += num_tokens
    with open(ledger_json_path, 'w') as ledger:
        json.dump(ledger_data, ledger)
    with open(history_json_path, 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, None]
    with open(history_json_path, 'w') as history:
        json.dump(history_data, history)
    print(f"SUBTRACTED {abs(num_tokens)} TOKENS")
def spend(num_tokens, reason, by_hour):
    if by_hour:
        num_tokens = subtract_hour_function(abs(num_tokens))
    with open(ledger_json_path, 'r') as ledger:
        ledger_data = json.load(ledger)
    if ledger_data['ledger']['tokens'] + num_tokens < 0:
        print("Cannot complete operation: Not enough tokens.")
        exit()
    ledger_data['ledger']['tokens'] += num_tokens
    with open(ledger_json_path,'w') as ledger:
        json.dump(ledger_data, ledger)
    with open(history_json_path, 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, reason.lower()]
    with open(history_json_path, 'w') as history:
        json.dump(history_data, history)
    print(f"SPENT {abs(num_tokens)} TOKENS")

def spin():
    with open(ledger_json_path, 'r') as ledger:
        ledger_data = json.load(ledger)
    punishment_pool = ledger_data['ledger']['contingencies']['punishment_pool']
    punishment = random.choice(punishment_pool)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    ledger_data['ledger']['punishment'][0] = current
    ledger_data['ledger']['punishment'][1] = punishment.lower()
    with open(ledger_json_path, 'w') as ledger:
        json.dump(ledger_data, ledger)
    print(f"""
          spinning...
          click click click click click click click...
          click click...
          click.....
          click.......
          THE WHEEL HAS SPOKEN!

          PUNISHMENT: 

          {punishment.title()}

          DO NOT FORGET TO UPLOAD VIDEO EVIDENCE OF PUNISHMENT !

          """)

def publish():
    # publish ledger
    with open(ledger_json_path, 'r') as ledger:
        ledger_data = json.load(ledger)
        tokens = ledger_data['ledger']['tokens']
        punishment = "none" if ledger_data['ledger']['punishment'][1] is None else ledger_data['ledger']['punishment'][1]
        punishment_time = "none" if ledger_data['ledger']['punishment'][0] is None else ledger_data['ledger']['punishment'][0]
        contingencies = ledger_data['ledger']['contingencies']
        earning = contingencies['earning'].items()
        earning_contents = ""
        for contin in earning:
            reason = contin[0]
            num_tokens = contin[1]
            earning_contents += f"{reason.title()}: {num_tokens}\n"
        spending = contingencies['spending'].items()
        spending_contents = ""
        for contin in spending:
            reason = contin[0]
            num_tokens = contin[1]
            spending_contents += f"{reason.title()}: {num_tokens}\n"
        punishment_pool = ledger_data['ledger']['contingencies']['punishment_pool']
        punishment_contents = ""
        for punish in punishment_pool:
            punishment_contents += f"{punish.title()}\n"

    with open(ledger_txt_path, 'w') as ledger:
        ledger_contents= f"""
LEDGER

CURRENT TOKENS: {tokens}

CURRENT PUNISHMENT: {punishment.title()}
Delivered {punishment_time.title()}

CONTINGENCIES

EARNING:

{earning_contents}

SPENDING:

{spending_contents}

PUNISHMENT POOL:

{punishment_contents}

"""
        ledger.write(ledger_contents)
    with open(history_json_path, 'r') as history:
        history_data = json.load(history)
        history_contents = ""
        for date, change in history_data['history'].items():
            if change[0] > 0 and change[1] is None:
                change_type = "add"
            elif change[0] > 0 and change[1] is not None:
                change_type = "earn"
            elif change[0] < 0 and change[1] is None:
                change_type = "subtract"
            elif change[0] < 0 and change[1] is not None:
                change_type = "spend"
            change_type = change_type.title()
            reason = change[1].title() if change[1] else "none"
            history_contents += f"DATE: {date}\nCHANGE TYPE: {change_type}\nCHANGE VALUE: {change[0]}\nREASON: {reason}\n\n" 
    with open(history_txt_path, 'w') as history:
        history_contents = "HISTORY\n\n" + history_contents
        history.write(history_contents)
    ## publish on github    
    repo = Repo(SCRIPT_DIR)
    repo.index.add([ledger_txt_path,history_txt_path, schedule_txt_path])
    repo.index.commit(f'Publish {datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")}')
    origin = repo.remote('origin')
    origin.push()
    print("PUBLISHED.")

def main():
    num_tokens, reason, do_publish, do_spin, by_hour = args()
    if num_tokens > 0 and not reason:
        add(num_tokens, by_hour)
    elif num_tokens > 0 and reason:
        earn(num_tokens, reason, by_hour)
    elif num_tokens < 0 and not reason:
        subtract(num_tokens, by_hour)
    elif num_tokens < 0 and reason:
        spend(num_tokens, reason, by_hour)
    elif do_spin:

        spin()
    if do_publish:
        publish()

if __name__ == '__main__':
    main()
