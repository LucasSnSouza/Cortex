import Range, random, copy, math, os, uuid # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore
from datetime import datetime, timedelta

class Behavior():
    def __init__(self, storage, utils):
        self.storage = storage
        self.list = []
        self.dict = {}
        self.utils = utils
        self.MovementVector = ((0,0,0))
        self.FlyVector = Vector((0,0,0))
        self.SailVector = Vector((0,0,0))
        self.RotationVector = Vector((0,0,0))

    # Getters

    def GetRaycast(self, instance: object, distance: float = 0.0, target = (0,0,0), axi = None):
        """  """
        
        destination = target
        if axi != None:
            destination = axi
        hitObject, hitPosition, hitNormal = instance.rayCast(destination, instance.worldPosition, distance)

        if hitObject == None:
            return None
        else:
            return [
                hitObject,
                hitPosition,
                hitNormal
            ]

    def GetMouseOver(self, distance = 99999, scene = Range.logic.getCurrentScene()) -> object:
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
        
    def GetRandomAreaPosition(self, scale: float, axis: str ="XYZ"):
        return [
            random.uniform(-scale, scale) if "X" in axis else 0.0,
            random.uniform(-scale, scale) if "Y" in axis else 0.0,
            random.uniform(-scale, scale) if "Z" in axis else 0.0,
        ]
    
    def VerifyVector(self, vector: list, vectors: list):
        for vect in vectors:
            if vector == Vector(self.storage.directions[vect]):
                return True
        return False
    
    def VerifyDateGreater(self, From: datetime, To: datetime):
        if From > To:
            return True
        else:
            return False
    
    def FindInstance(self, key: str, array: list, value = None):
        for instance in array:
            if value != None:
                if key in instance and instance[key] == value:
                    return instance
            else:
                if key in instance:
                    return instance
                
    def FindAllInstance(self, key: str, array: list, value = None):
        list_instances = []
        for instance in array:
            if value != None:
                if key in instance and instance[key] == value:
                    list_instances.append(instance)
            else:
                if key in instance:
                    list_instances.append(instance)
        return list_instances
    
    # Setters

    def AddObject(self, instance: str, reference: str, scene = Range.logic.getCurrentScene()):
        element = scene.addObject(instance, reference)
        element['uuid'] = uuid.uuid1()
        return element
    
    def EndObject(self, instance: str):
        return instance.endObject()

    def NormalsNormalized(self, instance: object):
        """  """

        InstanceMesh = instance.meshes[0]
        for polygon in InstanceMesh.polygons:
            v1 = InstanceMesh.getVertex(0, polygon.v1).XYZ - InstanceMesh.getVertex(0, polygon.v2).XYZ
            v2 = InstanceMesh.getVertex(0, polygon.v3).XYZ - InstanceMesh.getVertex(0, polygon.v2).XYZ
            for vertice in polygon.vertices:
                vertice.normal = v2.cross(v1).normalized()
        instance.reinstancePhysicsMesh()

    def LightManager(self, reference: object, sources: list, lights: list, distance: float):
        sorted_sources = sorted(sources, key=lambda source: reference.getDistanceTo(source))
        
        for i, light in enumerate(lights):
            if i < len(sorted_sources):
                source = sorted_sources[i]
                light.worldPosition = source.worldPosition
                light.energy = source.get('energy', 1.0)
                light.color = source.color[:-1]
            else:
                light.energy = 0.0


    def SetValue(self, object: object, variable: str, value):
        """  """
        
        if variable in object:
            object[variable] = value
            return object[variable]
        else:
            return None
        
    def SetText(self, instance: object, value: str):
        instance.text = value

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
    
    def LookAt(self, instance: object, target: list, axi: str = "Z"):
        """  """

        target_x, target_y = target.worldPosition.x, target.worldPosition.y
        pos_x, pos_y = instance.worldPosition.x, instance.worldPosition.y
        angle = math.atan2(target_y - pos_y, target_x - pos_x)
        
        instance.worldOrientation = Euler((0, 0, angle), 'XYZ')
    
    def ApplyRotation(self, instance: object, rotation: float):

        if Range.logic.keyboard.inputs[Range.events.PAD8].activated:
            instance.applyRotation([0.0, rotation, 0.0], True)
        elif Range.logic.keyboard.inputs[Range.events.PAD2].activated:
            instance.applyRotation([0.0, -rotation, 0.0], True)
        elif Range.logic.keyboard.inputs[Range.events.PAD6].activated:
            instance.applyRotation([0.0, 0.0, rotation], True)
        elif Range.logic.keyboard.inputs[Range.events.PAD4].activated:
            instance.applyRotation([0.0, 0.0, -rotation], True)
    
    def MouseLook(self, instance: object, speed: float = 1.0, x: bool = True, y: bool = True):
        """  """

        delta = Range.logic.mouse.deltaPosition
        if x:
            instance.applyRotation([0 , 0, delta[0] * speed], 0)
        if y:
            instance.applyRotation([delta[1] * speed , 0, 0], 1)
    
    def LookForwardCamera(self, instance, camera):
        """  """

        instance.lookAt(camera.worldOrientation.col[1], 1, 0.1)
        instance.lookAt([0,0,1], 2, 1)

    def CharacterMovement(self, instance: object, speed: float = 1.0, orientation: bool = True) -> Vector:
        """  """

        CharacterWrapper = Range.constraints.getCharacter(instance)

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active

        self.onMovement = any([XDirection, YDirection])

        Delta = Range.logic.deltaTime()
        if orientation:
            CharacterWrapper.walkDirection = (instance.worldOrientation * (Vector([XDirection * Delta, YDirection * Delta, 0]).normalized() * speed)) 
        else:
            CharacterWrapper.walkDirection = (Vector([XDirection * Delta, YDirection * Delta, 0]).normalized() * speed) 

        if Range.logic.keyboard.inputs[Range.events.SPACEKEY].activated:
            CharacterWrapper.jump()

        return instance.worldPosition
    
    def SimpleRotation(self, instance: object, speed: float, direction_proxy = ['H', 'V']):

        HDirection = Range.logic.keyboard.inputs[Range.events.PAD6].active - Range.logic.keyboard.inputs[Range.events.PAD4].active
        VDirection = Range.logic.keyboard.inputs[Range.events.PAD8].active - Range.logic.keyboard.inputs[Range.events.PAD2].active
        Delta = Range.logic.deltaTime()

        instance.applyRotation([0.0, VDirection * speed, HDirection * speed], True)

    def SimpleMovement(self, instance: object, speed: float = 1.0) -> Vector:
        """  """

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active

        self.MovementVector = Vector([XDirection * speed, YDirection * speed, 0])

        return self.MovementVector
    
    def AircraftMovement(self, speed: float = 1.0, directions:str = "XYZ"):
        """ """

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active if 'X' in directions else 0.0
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active if 'Y' in directions else 0.0
        ZDirection = Range.logic.keyboard.inputs[Range.events.EKEY].active - Range.logic.keyboard.inputs[Range.events.QKEY].active if 'Z' in directions else 0.0

        if any([XDirection, YDirection, ZDirection]):
            InputVector = Vector((XDirection, YDirection, ZDirection)) * speed
            self.FlyVector += InputVector

        return self.FlyVector
    
    def NavalMovement(self, speed: float = 1.0, directions:str = "XYZ"):
        """ """

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active if 'X' in directions else 0.0
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active if 'Y' in directions else 0.0
        ZDirection = Range.logic.keyboard.inputs[Range.events.EKEY].active - Range.logic.keyboard.inputs[Range.events.QKEY].active if 'Z' in directions else 0.0

        if any([XDirection, YDirection, ZDirection]):
            InputVector = Vector((XDirection, YDirection, ZDirection)) * speed
            self.FlyVector += InputVector

        return self.FlyVector

    def DisplacementMovement(self, instance: object, vector: Vector):
        for index, direction in enumerate(vector):
            instance.worldPosition[index] += direction

    def CameraMovement(self, instance: object, speed: float = 1.0) -> Vector:
        """  """

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.EKEY].active - Range.logic.keyboard.inputs[Range.events.QKEY].active
        ZDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active
        
        self.onMovement = any([XDirection, YDirection, ZDirection])

        instance.applyMovement([XDirection * speed, YDirection * speed, -ZDirection * speed], True)

        return instance.worldPosition
    
    def AxisMovement(self, instance: object, speed: float = 1.0, axis="X") -> Vector:
        """  """

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active
        ZDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active

        self.onMovement = any([XDirection, YDirection])

        instance.applyMovement([
            (XDirection * speed) if "X" in axis else 0, 
            (YDirection * speed) if "Y" in axis else 0, 
            (ZDirection * speed) if "Z" in axis else 0
        ], True)

        return instance.worldPosition
    
    def UseExternalCode(self, locale: str):
        locale = self.utils.GetResolvePath(locale)
        with open(locale, 'r') as file:
            exec(file.read())
        
    # Actuators

    def SetCameraActuator(self, target: object, actuator: str, changes: list = []):
        """  """

        if target.actuators.get(actuator):
            for function in changes:
                if hasattr(target.actuators[actuator], function['name']):
                    setattr(target.actuators[actuator], function['name'], function['value'])
        else:
            return None


