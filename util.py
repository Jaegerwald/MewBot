import random

def generate_meow(happiness: int, length: int) -> str:
    # return "Mrahhhh! (Being maintained rn, smh)"

    result = ""

    if happiness > 0 and length > 0:
        if happiness < 8:
            result += "mr"
        else:
            result += "m"

        letter = random.choice(["a", "e"])

        for i in range(1, length - 8):
            result += letter

        for i in range(1, length - 10):
            result += "o"

        if happiness > 3:
            result += random.choice(["w", "wr", ":3", "w :3", "w >w<", "wr >w<"])
        else:
            for i in range(1, length - 9):
                result += "h"
    elif length > 0:
        result = "3:"
    
    return result

def list_or_int_randint_function(input):
    if type(input) == list:
        def result() -> int:
            return random.randrange(input[0], input[1])
        return result
    else:
        def result() -> int:
            return input
        return result
    
def list_or_str_to_list(input) -> list:
    if type(input) == list:
        return input
    else:
        return [input]
    
def bool_from_dict_or_false(dict: dict, key: str) -> bool:
    if key in dict:
        return dict[key]
    else:
        return False
    
def empty_list_fallback(dict: dict, key: str):
    if key in dict:
        return dict[key]
    else:
        return []