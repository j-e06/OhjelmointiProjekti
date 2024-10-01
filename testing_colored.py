
from colored import Fore, Back, Style

def output(type_of_text,text, color_info):
    #assuming i pass in print, and input
    #how would i pass out the color info?
    if type_of_text == "input":
        result = input(Fore.GREEN + text + Style.RESET_ALL)
    pass