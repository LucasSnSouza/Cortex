import Range, random, copy, math # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore

class Interface():
    def __init__(self, behavior, utils, storage):
        self.behavior = behavior
        self.utils = utils
        self.storage = storage

    #Setters

    def setDefaultInterface(self):
        """  """

        self.utils.setLibrary(f"{self.utils.getLibraryPath('/bin')}/template_interface.range", "Interface")

    def setRenderInterfaces(self, interfaces: list = None, scene: object = Range.logic.getCurrentScene()):
        """  """

        if not interfaces == None:
            for interface in interfaces:
                self.setInterface(interface, scene)
        else:
            return None
        
    def setInterface(self, interface: object, scene: object = Range.logic.getCurrentScene()):
        """  """

        InstanceInterface = scene.addObject('REF_Layout', 'REF_Interface')
        if 'tag' in InstanceInterface:
            InstanceInterface['tag'] = interface.get('layout', 'unnamed')
            if interface.get('components'):
                self.setRenderComponents(InstanceInterface, interface['components'], scene)
    
    def setRenderComponents(self, layout: object, components: list = None, scene: object = Range.logic.getCurrentScene()):
        """  """

        if not components == None:
            for component in components:
                self.setComponent(component, layout, scene)
        else:
            return None
        
    def setComponent(self, component: object, layout: object, scene: object = Range.logic.getCurrentScene()):
        """  """

        if component['model'] in scene.objectsInactive:
            InstanceComponent = scene.addObject(component['model'], layout)
            InstanceComponent.setParent(layout)
            InstanceComponent['type'] = component['type']

            if component.get('offset'):
                componentOffset = component['offset']
                InstanceComponent.worldPosition += Vector([
                    componentOffset[0], 
                    -componentOffset[1], 
                    InstanceComponent.worldPosition.z
                ])
            if component.get('z-index'):
                InstanceComponent.worldPosition.z = component['z-index']
            if component.get('text'):
                InstanceComponent.text = component['text']
            if component.get('color'):
                InstanceComponent.color = component['color']
            if component.get('action'):
                InstanceComponent['action'] = component['action']['type']
                InstanceComponent['params'] = component['action']['params']

            if component.get('components'):
                self.setRenderComponents(InstanceComponent, component['components'], scene)

    def SetComponentAction(self, type: str = None, action: str = None, params: object = None):
        if type and action:
            
            match action:
                case "Print":
                    print(f"{params['text']}")
                case "Code":
                    self.behavior.SetExternalCode(params['locale'])
                case "SaveScene":
                    self.behavior.SetSaveScene(params['locale'], 'teste.json', params['tag'], self.utils.getScene(params['scene']))
                case "LoadScene":
                    self.behavior.SetLoadScene(params['locale'], 'teste.json', self.utils.getScene(params['scene']))
                case "EndGame":
                    Range.logic.endGame()

            if 'action' in params:
                self.SetComponentAction(type, params['action']['type'], params['action']['params'])

        else:
            return None