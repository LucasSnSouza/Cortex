import os, json

with open(f"{os.path.dirname(os.path.abspath(__file__))}/config.json", 'r', encoding='utf-8') as archive:
    config = json.load(archive)

    if not config == None:
        if config.get('active'):

            from .behavior import Behavior
            from .interface import Interface
            from .utils import Utils
            from .storage import Storage

            Storage = Storage()
            Utils = Utils(Storage)
            Behavior = Behavior(Storage, Utils)
            Interface = Interface(Behavior, Utils, Storage)

        else:
            print("WARNING: A biblioteca Cortex está desativada no momento")

    else:
        print("FATAL: Não foi possivel importar a biblioteca Cortex no seu projeto")