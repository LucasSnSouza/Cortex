import Range, random, copy, math # type: ignore
from mathutils import Vector, Euler, noise # type: ignore

class Behavior():
    def __init__(self, storage, utils):
        self.storage = storage
        self.utils = utils

    # Getters
    def getMouseOver(self, distance = 9999, scene = Range.logic.getCurrentScene()) -> object:
        """  """

        Mouse = Range.logic.mouse.position
        ScreenVector = scene.active_camera.getScreenVect(Mouse[0], Mouse[1])
        hitObject, hitPosition, hitNormal = scene.active_camera.rayCast(
            (scene.active_camera.worldPosition - ScreenVector * distance), 
            scene.active_camera.worldPosition
        )
        
        if not hitObject == None:
            return {"object": hitObject, "position": hitPosition, "normal": hitNormal}
        else:
            return {}
        
    def getInstanceBy(self, key: str, array: list = [], value = None):
        finded = []
        for instance in array:
            if value != None:
                if key in instance and instance[key] == value:
                    finded.append(instance)
            else:
                if key in instance:
                    finded.append(instance)
        
        return (finded if len(finded) > 1 else finded[0] if finded else None)


    # Setters
    def SetValue(self, object: object, variable: str, value):
        """  """

        if(object.get(variable, False)):
            object[variable] = value
            return object[variable]
        else:
            return None

    def BooleanToggle(self, object: object, variable: str) -> bool:
        """  """

        if variable in object:
            object[variable] = not object[variable]
            return object[variable]
        else:
            return None

    def SetPosition(self, instance, target: list, offset = [[0,0,0]]) -> object:
        """  """

        offset = [item if item else 0 for item in offset]
        
        if isinstance(instance, list):
            for index, object in enumerate(instance):
                object.worldPosition = target + Vector(offset[index])
        else:
            instance.worldPosition = target + Vector(offset[0])

        return instance
    
    def setLookAt(self, instance: object, target: list, axi: str = "Z"):
        orientation = [
            target[0] - instance.worldPosition[0],
            target[1] - instance.worldPosition[1]
        ]
        angle = math.atan2(orientation[1], orientation[0])
        instance.worldOrientation = Euler(
            (
                angle if axi == "X" else 0, 
                angle if axi == "Y" else 0, 
                angle if axi == "Z" else 0
            ), 
            'XYZ'
        )

    def SimpleMoviment(self, target: object):

        if Range.logic.keyboard.inputs[Range.events.WKEY].active:
            target.applyMovement([0.002,0,0], True)
        elif Range.logic.keyboard.inputs[Range.events.SKEY].active:
            target.applyMovement([-0.002,0,0], True)
        if Range.logic.keyboard.inputs[Range.events.AKEY].active:
            target.applyMovement([0,0.002,0], True)
        elif Range.logic.keyboard.inputs[Range.events.DKEY].active:
            target.applyMovement([0,-0.002,0], True)

    def SeaMoviment(self, target: object, config: bool = False) -> object:
        """  """

        if not config:
            target.worldPosition += target.worldOrientation.col[1] * target['relativeSpeed']

        else:
            if Range.logic.keyboard.inputs[Range.events.WKEY].active:
                target['relativeSpeed'] += target['speed'] * 0.0000001
            elif Range.logic.keyboard.inputs[Range.events.SKEY].active:
                target['relativeSpeed'] -= target['speed'] * 0.0000001
            if Range.logic.keyboard.inputs[Range.events.AKEY].active:
                Euler_target = target.worldOrientation.to_euler()
                Euler_target.z += target['relativeSpeed'] * 0.2
                target.worldOrientation = Euler(Euler_target)
            elif Range.logic.keyboard.inputs[Range.events.DKEY].active:
                Euler_target = target.worldOrientation.to_euler()
                Euler_target.z -= target['relativeSpeed'] * 0.2
                target.worldOrientation = Euler(Euler_target)

            if target['relativeSpeed'] < -0.0001:
                target['relativeSpeed'] = -0.0001
            if target['relativeSpeed'] > target['thresholdSpeed'] * 0.0000001:
                target['relativeSpeed'] = target['thresholdSpeed'] * 0.0000001

            target['absoluteSpeed'] = target['relativeSpeed'] * 10000

        return target
    
    # Actuators

    def setCameraActuator(self, target: object, actuator: str, changes: list = []):
        if target.actuators.get(actuator):
            for function in changes:
                if hasattr(target.actuators[actuator], function['name']):
                    setattr(target.actuators[actuator], function['name'], function['value'])
        else:
            return None


