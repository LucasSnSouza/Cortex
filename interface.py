import Range, random, copy, math # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore

class Interface():
    def __init__(self, behavior, utils, storage):
        self.behavior = behavior
        self.utils = utils
        self.storage = storage
        self.view = None
        self.modal = None

        self.cortex_window_scale = [20.0, -11.0]

    # Getters

    def GetCurrentView(self) -> str:
        if self.view != None:
            return self.view['tag'], self.view

    # Setters

    def SetDefaultInterface(self):
        """  """

        self.utils.SetLibrary(f"{self.utils.getLibraryPath('/bin')}/template_interface.range", "Interface")

    def SetRefresh(self, scene: object = Range.logic.getCurrentScene()) -> object:
        for instance in scene.objects:
            if "refresh" in instance and instance["refresh"] == True:
                self.SetComponentAction(
                    instance['type'],
                    instance['action'],
                    instance['params']
                )             

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
    
    def SetRenderComponents(self, layout: object, components: list = None, scene: object = Range.logic.getCurrentScene(), local: bool = False):
        """  """

        if not components == None:
            for component in components:
                self.SetComponent(component, layout, scene, local)
        else:
            return None
        
    def SetComponent(self, component: object, layout: object, scene: object = Range.logic.getCurrentScene(), local: bool = False):
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
                if '%' in componentOffset:
                    InstanceComponentDimension = self.utils.GetDimensions(InstanceComponent)
                    if local:
                        InstanceComponent.worldPosition += Vector([
                            ( InstanceComponent.worldPosition[0] * ( componentOffset[0] / 100 )) - ( InstanceComponentDimension[0] / 2 ), 
                            ( InstanceComponent.worldPosition[1] * ( componentOffset[1] / 100 )) + ( InstanceComponentDimension[1] / 2 ), 
                            InstanceComponent.worldPosition.z
                        ])
                    else:
                        InstanceComponent.worldPosition += Vector([
                            ( self.cortex_window_scale[0] * ( componentOffset[0] / 100 )) - ( InstanceComponentDimension[0] / 2 ), 
                            ( self.cortex_window_scale[1] * ( componentOffset[1] / 100 )) + ( InstanceComponentDimension[1] / 2 ), 
                            InstanceComponent.worldPosition.z
                        ])
                else:
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
                InstanceComponent.color = self.utils.GetRGBNormalized(component['color'])
            if component.get('tag'):
                if 'tag' in InstanceComponent:
                    InstanceComponent['tag'] = component['tag']
            if component.get('refresh') and "refresh" in InstanceComponent:
                InstanceComponent['refresh'] = component['refresh']
            if component.get('scale'):
                if len(component['scale']) == 1:
                    InstanceComponent.worldScale = [
                        component['scale'][0],
                        component['scale'][0],
                        InstanceComponent.worldScale.z
                    ]
                else:
                    InstanceComponent.worldScale = [
                        component['scale'][0],
                        component['scale'][1],
                        InstanceComponent.worldScale.z
                    ]
                
            if component.get('action'):
                InstanceComponent['action'] = component['action']['type']
                InstanceComponent['params'] = component['action']['params']

            if component.get('list'):
                if isinstance(component['list'], str):
                    ListRender(
                        Range.logic.globalDict[component['list']],
                        component.get('columns'),
                        component.get('rows'),
                        component.get('gap')
                    )
                else:
                    ListRender(
                        component['list'],
                        component.get('columns'),
                        component.get('rows'),
                        component.get('gap')
                    )

            if component.get('components'):
                self.SetRenderComponents(InstanceComponent, component['components'], scene, True)

    def SetComponentAction(self, type: str = None, action: str = None, params: object = None):
        """  """

        if type and action:
            match action:
                case "Print":
                    print(f"{params['text']}")
                case "ExternalCode":
                    self.behavior.UseExternalCode(params['locale'])
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