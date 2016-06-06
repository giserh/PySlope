import sys

def contains(character, string):
    equals = 0
    for char in string:
        if char == character:
            equals += 1
    if equals == 0:
        return False
    else:
        return True


def raiseGeneralError(*args):
    sys.exit(*args)

def isInt(value):
    try:
        return int(value)
    except:
        return False
def isFloat(value):
    try:
        return float(value)
    except:
        return False
def isString(value):
    try:
        return str(value)
    except:
        return False

def hasComma(value):
    for index in range(len(value)-1):
        current, next = value[index], value[index+1]
        if current == ',' or next == ',':
            return True
        else:
            return False

def isEllipse(value):
    if hasComma(value):
        for char in value:
            if char == "(" or char == ")":
                return True
        return False

def formatCircleData(coordinates):
    results = []

    coordinates = coordinates.replace(',', ' ')
    coordinates = coordinates.replace('(', '')
    coordinates = coordinates.replace(')', '')

    for element in coordinates.split():
        results.append(element)

    if len(results) > 4:
        raiseGeneralError("There are too many data points for your ellipse. Check config file")
    elif len(results) < 3:
        raiseGeneralError("There are too few data points for your circle/ellipse. Check config file.")
    else:
        return results

