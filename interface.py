import Range, random, copy, math # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore

class Interface():
    def __init__(self, behavior, utils, storage):
        self.behavior = behavior
        self.utils = utils
        self.storage = storage
        self.view = None
        self.modal = None


    # Getters

    def GetCurrentView(self) -> str:
        if self.view != None:
            return self.view['tag'], self.view

    # Setters

    def SetDefaultInterface(self):
        """  """

        self.utils.SetLibrary(f"{self.utils.getLibraryPath('/bin')}/template_interface.range", "Interface")

    def SetView(self, view: str, scene: object = Range.logic.getCurrentScene()) -> object:
        """  """
        if self.view == None:
            self.view = self.behavior.FindInstance("tag", scene.objects, view)
            self.view.worldPosition = [0,0,0]
        else:
            self.view.worldPosition = [0,0,999]
            self.view = self.behavior.FindInstance("tag", scene.objects, view)
            self.view.worldPosition = [0,0,0]

        return self.view

    def SetModal(self, instance: str, scene: object = Range.logic.getCurrentScene()):
        if self.modal == None:
            pass
        else: 
            pass

    def SetRenderInterfaces(self, interfaces: list = None, scene: object = Range.logic.getCurrentScene()):
        """  """

        if not interfaces == None:
            for interface in interfaces:
                self.SetInterface(interface, scene)
        else:
            return None
        
    def SetInterface(self, interface: object, scene: object = Range.logic.getCurrentScene()):
        """  """

        InstanceInterface = scene.addObject('REF_Layout', 'REF_Interface')
        if 'tag' in InstanceInterface:
            InstanceInterface['tag'] = interface.get('layout', 'unnamed')
            if interface.get('components'):
                self.SetRenderComponents(InstanceInterface, interface['components'], scene)
            InstanceInterface.worldPosition = [100, 100, 0]
        else:
            print('NOT: Não foi encontrado uma tag sobre o perfil de layout')
    
    def SetRenderComponents(self, layout: object, components: list = None, scene: object = Range.logic.getCurrentScene()):
        """  """

        if not components == None:
            for component in components:
                self.SetComponent(component, layout, scene)
        else:
            return None
        
    def SetComponent(self, component: object, layout: object, scene: object = Range.logic.getCurrentScene()):
        """  """

        def ListRender(__list__, columns, rows, gap = [1,1]):
            column = 0
            row = 0
            for indice, object in enumerate(__list__):
                if object.get('__component__'):
                    object['__component__']['offset'][0] += ( column * gap[0] )
                    object['__component__']['offset'][1] += ( row * gap[1] )
                    self.SetComponent(object['__component__'], layout, scene)
                column += 1
                if column >= columns:
                    column = 0
                    row += 1
                

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
            if component.get('scale'):
                InstanceComponent.worldScale = [
                    component['scale'][0],
                    component['scale'][1],
                    0.0
                ]
            if component.get('action'):
                InstanceComponent['action'] = component['action']['type']
                InstanceComponent['params'] = component['action']['params']

            if component.get('__list__'):
                if "@" in component['__list__']:
                    ListRender(
                        Range.logic.globalDict[component['__list__'].replace('@', "")],
                        component.get('columns'),
                        component.get('rows'),
                        component.get('gap')
                    )
                else:
                    ListRender(
                        component['__list__'],
                        component.get('columns'),
                        component.get('rows'),
                        component.get('gap')
                    )

            if component.get('components'):
                self.SetRenderComponents(InstanceComponent, component['components'], scene)

    def SetComponentAction(self, type: str = None, action: str = None, params: object = None):
        """  """

        if type and action:
            match action:
                case "Print":
                    print(f"{params['text']}")
                case "Code":
                    self.behavior.SetExternalCode(params['locale'])
                case "SaveScene":
                    self.behavior.SetSaveScene(params['locale'], 'teste.json', params['tag'], self.utils.GetScene(params['scene']))
                case "LoadScene":
                    self.behavior.SetLoadScene(params['locale'], 'teste.json', self.utils.GetScene(params['scene']))
                case "SetValue":
                    if isinstance(params['variable'], list):
                        for indice, variable in enumerate(params['variable']):
                            self.behavior.SetValue(self.utils.GetScene(params['scene']).objects[params['object']], variable, params['value'][indice])
                    else:
                        self.behavior.SetValue(self.utils.GetScene(params['scene']).objects[params['object']], params['variable'], params['value'])
                case "SetAddObject":
                    self.behavior.SetAddObject(params['object'], params['reference'], self.utils.GetScene(params['scene']))
                case "SetView":
                    self.SetView(params['view'], self.utils.GetScene(params['scene']))
                case "SetModal":
                    self.SetView(params['modal'], self.utils.GetScene(params['scene']))
                case "EndGame":
                    Range.logic.endGame()

            if 'action' in params:
                self.SetComponentAction(type, params['action']['type'], params['action']['params'])

        else:
            return None