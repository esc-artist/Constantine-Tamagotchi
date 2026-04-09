# So. I need to create something that takes my input, prases the existing github json file, and edits it according to my input.

# I think the simplest way would actually be not to prompt me, which is sort of annoying, but just have flags. Like tama.py --add 5, or 
# tama.py --spend 10, etc.
#
# --add <x>: add x tokens to ledger.json, add +x to history.json
# --earn <x> <reason>: add x tokens to ledger.json, add +x and reason to history.json
# --subtract <x>: remove x tokens from ledger.json, add -x to history.json
# --spend <x> <reason>: remove x tokens from ledger.json, add -x and reason to history.json
# --spin: spin the wheel of punishment (return randomly selected punishment), add to ledger.json, add to history.json
# --publish: update ledger.txt and history.txt from ledger.json and history.json, push to github

import argparse
import json
import datetime
import random
from git import Repo

def args():
    parser = argparse.ArgumentParser(
                        prog='tama.py',
                        description='Constantine Tamagotchi CLI')
    parser.add_argument('--add', type=int, metavar=('NUM_TOKENS'))
    parser.add_argument('--subtract',type=int, metavar=('NUM_TOKENS'))
    parser.add_argument('--earn', nargs=2, metavar=('NUM_TOKENS', 'REASON'))
    parser.add_argument('--spend', nargs=2, metavar=('NUM_TOKENS', 'REASON'))
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
        return (args.add, None, args.publish, None)
    elif args.subtract is not None:
        return (args.subtract, None, args.publish, None) 
    elif args.earn is not None:
        num_tokens, reason = args.earn
        num_tokens = int(num_tokens)
        return (num_tokens, reason, args.publish, None)
    elif args.spend is not None:
        num_tokens, reason = args.spend
        num_tokens = int(num_tokens)
        return (num_tokens, reason, args.publish, None)
    elif args.spin:
        return (0, None, args.publish, True)
    elif args.publish:
        return (0, None, True, args.spin)
    


def add(num_tokens):
    with open('ledger.json', 'r') as ledger:
        ledger_data = json.load(ledger)
    ledger_data['ledger']['tokens'] += num_tokens
    with open('ledger.json', 'w') as ledger:
        json.dump(ledger_data, ledger)
    with open('history.json', 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, None]
    with open('history.json', 'w') as history:
        json.dump(history_data, history)
    
def earn(num_tokens, reason): 
    with open('ledger.json', 'r') as ledger:
        ledger_data = json.load(ledger)
    ledger_data['ledger']['tokens'] += num_tokens
    with open('ledger.json', 'w') as ledger:
        json.dump(ledger_data, ledger)
    with open('history.json', 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, reason.lower()]
    with open('history.json', 'w') as history:
        json.dump(history_data, history)
    
def subtract(num_tokens):
    with open('ledger.json', 'r') as ledger:
        ledger_data = json.load(ledger)
    ledger_data['ledger']['tokens'] += num_tokens
    with open('ledger.json', 'w') as ledger:
        json.dump(ledger_data, ledger)
    with open('history.json', 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, None]
    with open('history.json', 'w') as history:
        json.dump(history_data, history)

def spend(num_tokens, reason):
    with open('ledger.json', 'r') as ledger:
        ledger_data = json.load(ledger)
    ledger_data['ledger']['tokens'] += num_tokens
    with open('ledger.json','w') as ledger:
        json.dump(ledger_data, ledger)
    with open('history.json', 'r') as history:
        history_data = json.load(history)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    history_data['history'][current] = [num_tokens, reason.lower()]
    with open('history.json', 'w') as history:
        json.dump(history_data, history)

def spin():
    with open('ledger.json', 'r') as ledger:
        ledger_data = json.load(ledger)
    punishment_pool = ledger_data['ledger']['contingencies']['punishment_pool']
    punishment = random.choice(punishment_pool)
    current = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    ledger_data['ledger']['punishment'][0] = current
    ledger_data['ledger']['punishment'][1] = punishment.lower()
    with open('ledger.json', 'w') as ledger:
        json.dump(ledger_data, ledger)

def publish():
    # publish ledger
    with open('ledger.json', 'r') as ledger:
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

    with open('ledger.txt', 'w') as ledger:
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
    with open('history.json', 'r') as history:
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
            history_contents += f"DATE: {date}\nCHANGE TYPE: {change_type}\nREASON:{reason}\n\n" 
    with open('history.txt', 'w') as history:
        history_contents = "HISTORY\n\n" + history_contents
        history.write(history_contents)
    ## publish on github    
    repo = Repo('.')
    repo.index.add(['ledger.txt','history.txt'])
    repo.index.commit(f'Publish {datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")}')
    origin = repo.remote('origin')
    origin.push()

def main():
    num_tokens, reason, do_publish, do_spin = args()
    if num_tokens > 0 and not reason:
        add(num_tokens)
    elif num_tokens and reason:
        earn(num_tokens, reason)
    elif num_tokens < 0 and not reason:
        subtract(num_tokens)
    elif num_tokens < 0 and reason:
        spend(num_tokens, reason)
    elif do_spin:
        spin()

    if do_publish:
        publish()


if __name__ == '__main__':
    main()
