import Range # type: ignore

class Storage():
    def __init__(self):
        self.functions = {
            'functions': {
                    'content': self.ListFunctions,
                }
        }
        self.chargeFunctions = []
        self.serverClients = []
        self.directions = {
            "X": [1.0,0.0,0.0],
            "-X": [-1.0,0.0,0.0],
            "Y": [0.0,1.0,0.0],
            "-Y": [0.0,-1.0,0.0],
            "Z": [0.0,0.0,1.0],
            "-Z": [0.0,0.0,-1.0],
        }
        self.keymapping = {
            "Z": Range.events.ZKEY,
            "X": Range.events.XKEY,
            "C": Range.events.CKEY,
            "V": Range.events.VKEY,
            "B": Range.events.BKEY,
            "N": Range.events.NKEY,
            "M": Range.events.MKEY,
            "A": Range.events.AKEY,
            "S": Range.events.SKEY,
            "D": Range.events.DKEY,
            "F": Range.events.FKEY,
            "G": Range.events.GKEY,
            "H": Range.events.HKEY,
            "J": Range.events.JKEY,
            "K": Range.events.KKEY,
            "L": Range.events.LKEY,
            "Q": Range.events.QKEY,
            "W": Range.events.WKEY,
            "E": Range.events.EKEY,
            "R": Range.events.RKEY,
            "T": Range.events.TKEY,
            "Y": Range.events.YKEY,
            "U": Range.events.UKEY,
            "I": Range.events.IKEY,
            "O": Range.events.OKEY,
            "P": Range.events.PKEY,
            "1": Range.events.ONEKEY,
            "2": Range.events.TWOKEY,
            "3": Range.events.THREEKEY,
            "4": Range.events.FOURKEY,
            "5": Range.events.FIVEKEY,
            "6": Range.events.SIXKEY,
            "7": Range.events.SEVENKEY,
            "8": Range.events.EIGHTKEY,
            "9": Range.events.NINEKEY,
            "0": Range.events.ZEROKEY,
        }
        self.skips = {}

    def SetSkip(self, skip: str, reset: int = 0):
        self.skips[skip] = {
            "value": 0,
            "reset": reset,
            "result": False
        }

    def RunSkip(self):
        for skip, _ in self.skips.items():
            if self.skips[skip]['value'] == self.skips[skip]['reset']:
                self.skips[skip]['result'] = True
                self.skips[skip]['value'] = 0
            else:
                self.skips[skip]['result'] = False
                self.skips[skip]['value'] += 1

    def SetChargeFunction(self, function, params = None):
        """  """
        
        self.chargeFunctions.append({"function": function, "params": params})

    def RunCharge(self):
        """  """

        if len(self.chargeFunctions) != 0:
            for index, function in enumerate(self.chargeFunctions):
                result = None
                if "payload" in function['params']:
                    if function['params'].get('payload') in Range.logic.getSceneList():
                        result = function['function'](function['params'])
                if result:
                    self.chargeFunctions.pop(index)
                
        else:
            return None

    def ListFunctions(self) -> list:
        """  """

        return list(self.functions.keys())
    
    def SetFunction(self, key: str, function) -> dict:
        """  """

        self.functions[key] = {
            'content': function
        }
        return self.functions.get(key, None)
    
    def GetSkips(self) -> list:
        """  """

        keys = []
        for key, sub_key in self.skips.items():
            keys.append(key)
        return keys
    
    def GetSkip(self, skip: str, delete: bool = False) -> bool:
        """  """

        if delete:
            if skip in self.skips and self.skips[skip]['result']:
                del self.skips[skip]
                return True
        if skip in self.skips:
            return self.skips[skip]['result']

    def GetFunction(self, key: str, use: bool = False) -> dict:
        """  """

        if use:
            return self.functions.get(key, None).get('content')
        else:
            return self.functions.get(key, None)
