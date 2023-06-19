

def setAccountValue(value:int):
    try:
        with open("av.txt", 'w') as f:
            f.write(str(value))
    except:
        raise Exception("CANNOT WRITE TO av.txt")
    
def getAccountValue():
    try:
        with open("av.txt", 'r') as f:
            avtxt = f.readline()
            av = int(avtxt)
    except:
        setAccountValue(0)
        av = 0
    return av