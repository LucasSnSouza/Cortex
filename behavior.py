import Range, random, copy, math, os # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore

class Behavior():
    def __init__(self, storage, utils):
        self.storage = storage
        self.utils = utils

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

    def SetAddObject(self, instance: str, reference: str, scene = Range.logic.getCurrentScene()):
        return scene.addObject(instance, reference)
    
    def SetEndObject(self, instance: str):
        return instance.endObject()

    def SetTerrainPaint(self, instance: object, waterLevel: float = 1.0):
        """  """

        InstanceMesh = instance.meshes[0]
        for vertice_index in range(InstanceMesh.getVertexArrayLength(0)):
            vertice = InstanceMesh.getVertex(0, vertice_index)
            vertice_global_position = instance.worldTransform * vertice.XYZ

            vertice.color = [0.0,1.0,0.0,1.0]

            if vertice.normal[2] < 0.60:
                vertice.color = [0.0,0.0,0.1,1.0]
            
            if vertice_global_position[2] < waterLevel:
                vertice.color = [1.0,0.0,0.0,1.0]

    def SetGenerateTerrain(self, instance: object, island: bool = False):
        """  """

        instance.worldPosition = [
            random.uniform(-100,100),
            random.uniform(-100,100),
            random.uniform(-100,100),
        ]

        InstanceMesh = instance.meshes[0]
        main_vertice = ( instance.worldTransform * InstanceMesh.getVertex(0, self.GetVertexCenter(instance)['vertice']).XYZ )
        farest_length_vertex = 20.0
        
        for vertice_index in range(InstanceMesh.getVertexArrayLength(0)):
            vertice = InstanceMesh.getVertex(0, vertice_index)
            vertice_global_position = instance.worldTransform * vertice.XYZ
            distance = (vertice_global_position - main_vertice).length
            inverted_distance = max(0.0, farest_length_vertex - distance)

            hetero_terrain_type = noise.fractal(vertice_global_position * 0.2, 1.0, 200.0, 8)
            fractal_terrain_type = noise.multi_fractal(vertice_global_position * 0.003, 1.0, 100.0, 6)
            vertice.z = (hetero_terrain_type * fractal_terrain_type) * -inverted_distance 

        instance.worldPosition = [0,0,0]

    def SetRecalculateNormals(self, instance: object):
        """  """

        InstanceMesh = instance.meshes[0]
        for polygon in InstanceMesh.polygons:
            v1 = InstanceMesh.getVertex(0, polygon.v1).XYZ - InstanceMesh.getVertex(0, polygon.v2).XYZ
            v2 = InstanceMesh.getVertex(0, polygon.v3).XYZ - InstanceMesh.getVertex(0, polygon.v2).XYZ
            for vertice in polygon.vertices:
                vertice.normal = v2.cross(v1).normalized()
        instance.reinstancePhysicsMesh()

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
    
    def SetPositionGrid(self, mouse_sensor: object, instance: object, gap: float = 1.0):
        instance.worldPosition = mouse_sensor.hitObject.worldPosition + mouse_sensor.hitNormal / gap
    
    def SetLookAt(self, instance: object, target: list, axi: str = "Z"):
        """  """

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

        return instance.worldOrientation
    
    def SetApplyRotation(self, instance: object, speed: float, direction_proxy = ['H', 'V']):

        HDirection = Range.logic.keyboard.inputs[Range.events.PAD6].active - Range.logic.keyboard.inputs[Range.events.PAD4].active
        VDirection = Range.logic.keyboard.inputs[Range.events.PAD8].active - Range.logic.keyboard.inputs[Range.events.PAD2].active
        Delta = Range.logic.deltaTime()

        instance.applyRotation([0.0, VDirection * speed, HDirection * speed], True)
    
    def SetMouseLook(self, instance: object, x: bool = True, y: bool = True):
        """  """

        delta = Range.logic.mouse.deltaPosition
        if x:
            instance.applyRotation([0 , 0, delta[0]], 0)
        if y:
            instance.applyRotation([delta[1] , 0, 0], 1)
    
    def SetLookForwardCamera(self, instance, camera):
        """  """

        instance.lookAt(camera.worldOrientation.col[1], 1, 0.1)
        instance.lookAt([0,0,1], 2, 1)

    def CharacterMoviment(self, instance: object, speed: float = 1.0, orientation: bool = True) -> Vector:
        """  """

        CharacterWrapper = Range.constraints.getCharacter(instance)

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active

        Delta = Range.logic.deltaTime()
        if orientation:
            CharacterWrapper.walkDirection = (instance.worldOrientation * (Vector([XDirection * Delta, YDirection * Delta, 0]).normalized() * speed)) 
        else:
            CharacterWrapper.walkDirection = (Vector([XDirection * Delta, YDirection * Delta, 0]).normalized() * speed) 

        if Range.logic.keyboard.inputs[Range.events.SPACEKEY].activated:
            CharacterWrapper.jump()

        return instance.worldPosition

    def SimpleMoviment(self, instance: object, speed: float = 1.0) -> Vector:
        """  """

        XDirection = Range.logic.keyboard.inputs[Range.events.DKEY].active - Range.logic.keyboard.inputs[Range.events.AKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active
        
        instance.applyMovement([XDirection * speed, YDirection * speed, 0], True)

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


