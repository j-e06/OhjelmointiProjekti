from colored import Fore, Back, style

def colored_output(type_of_text, text, text_modification):
    if type_of_text == "input":
        # example:
        # colored_output("input", "Enter your name: ", "")
        # would just be a normal input

        # example of a edited one:
        # colored_output("input", "Enter your name: ", f'{Fore.green}{Back.blue}')
        return input(Fore.GREEN + text + text_modification)
    elif type_of_text == "print":
        pass
    else:
        return None


colored_output("input", "Enter your name: ", f'{Fore.green}{Back.blue}')




smaragdi = 3


emerald = 2

rosvo = 5

from random import randint

a = randint(1, 6)

if a == 6:
    rosvo -= 1
