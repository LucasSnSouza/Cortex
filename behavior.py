import Range, random, copy, math, os # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore

class Behavior():
    def __init__(self, storage, utils):
        self.storage = storage
        self.utils = utils

    # Getters
    def GetSquareMatrix(self, amount: int):
        """  """

        find = int(math.sqrt(len(amount)))
        if find * find == amount:
            return find
        else:
            return None
    
    def GetVertexCenter(self, instance: object):
        """  """

        InstanceMesh = instance.meshes[0]
        for vertice_index in range(InstanceMesh.getVertexArrayLength(0)):
            vertice = InstanceMesh.getVertex(0, vertice_index)
            vertice_global_position = instance.worldTransform * vertice.XYZ
            if vertice_global_position == instance.worldPosition:
                return {
                    "vertice": vertice_index,
                    "position": vertice_global_position
                }
            
    def GetFarestDistanceVertex(self, instance: object):
        """  """

        InstanceMesh = instance.meshes[0]
        farest_distance_vertex_length = -1
        farest_distance_vertex = None

        for vertice_index in range(InstanceMesh.getVertexArrayLength(0)):
            vertice = InstanceMesh.getVertex(0, vertice_index)
            vertice_global_position = instance.worldTransform * vertice.XYZ
            distance = (vertice_global_position - instance.worldPosition).length
            if distance > farest_distance_vertex_length:
                farest_distance_vertex = distance
                farest_distance_vertex_length = vertice_index
        return { 
            "vertice": farest_distance_vertex, 
            "distance": farest_distance_vertex_length 
        } 

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
        
    def GetInstanceBy(self, key: str, array: list = [], value = None):
        """  """

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

    def SetAddObject(self, instance: str, reference: str, scene = Range.logic.getCurrentScene()):
        #instance = scene.addObject(instance, reference)
        return scene.addObject(instance, reference)

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
    
    def SetPositionGrid(self, instance: object, gap: float = 1.0, useMouse = False):
        if useMouse:
            Colide = self.GetMouseOver()
            if Colide:
                instance.worldPosition = Colide['object'].worldPosition + Colide['normal'] / gap
    
    def SetLookAt(self, instance: object, target: list, axi: str = "Z") -> Matrix:
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

    def CharacterMoviment(self, instance: object, speed: float = 0.001, onOrientation: bool = True) -> Vector:
        """  """

        CharacterWrapper = Range.constraints.getCharacter(instance)

        XDirection = Range.logic.keyboard.inputs[Range.events.WKEY].active - Range.logic.keyboard.inputs[Range.events.SKEY].active
        YDirection = Range.logic.keyboard.inputs[Range.events.AKEY].active - Range.logic.keyboard.inputs[Range.events.DKEY].active

        if onOrientation:
            CharacterWrapper.walkDirection = instance.worldOrientation * (Vector([XDirection, YDirection, 0]).normalized() * speed)
        else:
            CharacterWrapper.walkDirection = Vector([XDirection, YDirection, 0]).normalized() * speed

        if Range.logic.keyboard.inputs[Range.events.SPACEKEY].activated:
            CharacterWrapper.jump()

        return instance.worldPosition

    def SimpleMoviment(self, instance: object, speed: float = 1.0) -> Vector:
        """  """

        if Range.logic.keyboard.inputs[Range.events.WKEY].active:
            instance.applyMovement([speed,0,0], True)
        elif Range.logic.keyboard.inputs[Range.events.SKEY].active:
            instance.applyMovement([-speed,0,0], True)
        if Range.logic.keyboard.inputs[Range.events.AKEY].active:
            instance.applyMovement([0,speed,0], True)
        elif Range.logic.keyboard.inputs[Range.events.DKEY].active:
            instance.applyMovement([0,-speed,0], True)
        
        return instance.worldPosition

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

        return target.worldPosition
    
    def SetExternalCode(self, locale: str):
        locale = self.utils.getResolvePath(locale)
        with open(locale, 'r') as file:
            exec(file.read())

    def SetSaveScene(self, locale: str, file: str, tag: str = None, scene = Range.logic.getCurrentScene()):
        locale = self.utils.getResolvePath(locale)
        instances = None
        if tag:
            instances = self.getInstanceBy(tag, scene.objects)
        else:
            instances = scene.objects

        if instances:
            formInstances = []
            for instance in instances:
                formInstances.append({
                    "name": instance.name,
                    "position": list(instance.worldPosition),
                    "color": list(instance.color)
                })
            self.utils.setJsonFile(locale, file, formInstances)
        else:
            return instances
    
    def SetLoadScene(self, locale: str, file: str, scene = Range.logic.getCurrentScene()):
        locale = self.utils.getResolvePath(locale)
        
        if file:
            instances = self.utils.getJsonFile(locale, file)
            for instance in instances:
                wrapper = scene.addObject(instance['name'], scene.objects[0])
                wrapper.worldPosition = instance['position']
        
    # Actuators

    def SetCameraActuator(self, target: object, actuator: str, changes: list = []):
        """  """

        if target.actuators.get(actuator):
            for function in changes:
                if hasattr(target.actuators[actuator], function['name']):
                    setattr(target.actuators[actuator], function['name'], function['value'])
        else:
            return None


