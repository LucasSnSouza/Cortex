import Range, random, copy, math # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore

class Interface():
    def __init__(self, behavior, utils, storage):
        self.behavior = behavior
        self.utils = utils
        self.storage = storage

    #Setters
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

            if component.get('components'):
                self.setRenderComponents(InstanceComponent, component['components'], scene)