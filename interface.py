import Range, random, copy, math, pyautogui, uuid, re # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore
import xml.etree.ElementTree as XML

class Interface():
    def __init__(self, behavior, utils, storage):
        self.behavior = behavior
        self.utils = utils
        self.storage = storage
        self.functions = []
        
        self.templates = None
        self.bindings = []
        self.mouse = Vector((0,0))
        self.over = None
        self.click = False
        self.textbox = None

        self.cortex_window_scale = [20.0, -11.0]

    # Getters

    def GetCurrentView(self) -> str:
        if self.view != None:
            return self.view['tag'], self.view

    # Setters

    def ListenEvents(self, scene: object):
        viewport = scene.active_camera

        self.mouse = Range.logic.mouse.position
        self.over = viewport.getScreenRay(self.mouse[0], self.mouse[1], 100)

        if Range.logic.mouse.inputs[Range.events.LEFTMOUSE].activated:
            self.click = True
        else:
            self.click = False

        if not self.over == None:
            pass

        if self.click:
            if not self.over == None:
                if 'onclick' in self.over:
                    self.over['onclick']()
            if self.storage.typing:
                self.storage.typing = False
                self.textbox = None

        if self.textbox != None:
            key_events = Range.logic.keyboard.inputs
            self.storage.typing = True
            for key, status in key_events.items():
                if status.activated:
                    if key == 7:
                        self.textbox = None
                        self.storage.typing = False
                    elif key == 59:
                        self.textbox.text = self.textbox.text[:-1]
                    else:
                        self.textbox.text += Range.events.EventToCharacter(key, False)
                    
    def UpdateBindings(self):

        bindings = globals().get('_BINDINGS')
        for bind in self.bindings:

            bind_value = bindings[bind[2]]()
            bind_instance = bind[1]
            
            if bind[0] == 'text':
                updated_text = bind[3]
                for bind_item in self.bindings:
                    if bind_item[0] == 'text':
                        pattern = r"\{\{\s*" + re.escape(f"{bind_item[2]}") + r"\s*\}\}"
                        replacement = str(bindings[bind_item[2]]())
                        updated_text = re.sub(pattern, replacement, updated_text)
                bind[1].text = updated_text

            if bind[0] == 'attribute':

                match bind[3]:
                    case "width":
                        bind_instance.worldScale.x = float(bind_value)
                    case "heigth":
                        bind_instance.worldScale.x = float(bind_value)
                    case "z-index":
                        bind_instance.worldPosition.z = float(bind_value)
                    case "top":
                        bind_instance.worldPosition.y = -float(bind_value)
                    case "bottom":
                        bind_instance.worldPosition.y = float(bind_value)
                    case "left":
                        bind_instance.worldPosition.y = float(bind_value)
                    case "right":
                        bind_instance.worldPosition.y = -float(bind_value)

    def CreateInterfaces(self, interfaces: list = None, scene: object = Range.logic.getCurrentScene()):
        """  """

        for interface in interfaces:
            interface = XML.fromstring(interface)
            
            self.templates = self.utils.GetJsonFile(
                self.utils.GetResolvePath(
                    interface.find('import').get('src')
                ), 
                "template.json"
            )
            
            if not interface.find('script') == None:
                exec(interface.find('script').text, globals())

            if interface.find('body') is not None:
                for body in interface.find('body'):
                    self.CreateElement(body, scene, scene.objects['REF_Interface'])

    def CreateElement(self, element: object, scene: object = Range.logic.getCurrentScene(), parent: object = None):

        if element.tag in self.templates:
            instance = scene.addObject(self.templates[element.tag], parent)
            instance['uid'] = uuid.uuid1()
            instance['xml'] = element
            instance['parent'] = {"xml": element, "object": parent}

            for attr_name, attr_value in element.attrib.items():
                match = re.search(r"\{\{\s*(.*?)\s*\}\}", attr_value)  # Diretamente sem verificar '{{'
                if match:
                    variable = match.group(1)
                    self.bindings.append(('attribute', instance, variable, attr_name))
                    element.set(attr_name, "1")

            text = element.text.strip()
            if text:
                instance.text = text
                for match in re.findall(r"\{\{\s*(.*?)\s*\}\}", text):
                    variable = match.strip()
                    self.bindings.append(('text', instance, variable, text))

            if element.get('scale'):
                scale = element.get('scale')
                if ',' in scale:
                    scale = element.get('scale').split(',')
                instance.worldScale = [
                    float(scale) if isinstance(scale, str) else scale[0],
                    float(scale[1]) if isinstance(scale, list) else float(scale),
                    0.01
                ]          
            if element.get('width'):
                if 'auto' in element.get('width'):
                    instance.worldScale.x = instance.worldScale.y
                else:
                    instance.worldScale.x += float(element.get('width'))
            if element.get('heigth'):
                if 'auto' in element.get('heigth'):
                    instance.worldScale.y = instance.worldScale.x
                else:
                    instance.worldScale.y += float(element.get('heigth'))
            if element.get('top'):
                instance.worldPosition.y += -float(element.get('top'))
            if element.get('bottom'):
                instance.worldPosition.y += float(element.get('bottom'))
            if element.get('left'):
                instance.worldPosition.x += float(element.get('left'))
            if element.get('right'):
                instance.worldPosition.x += -float(element.get('right'))

            if element.get('z-index'):
                instance.worldPosition.z = float(element.get('z-index'))

            if element.get('onclick'):
                instance['onclick'] = lambda: eval(element.get('onclick'), globals())
            if element.get('textbox'):
                parent['onclick'] = lambda: setattr(self, 'textbox', parent.children[0])

            if element.get('name'):
                instance.name = element.get('name')
            if element.get('id'):
                instance['id'] = element.get('id')
            if element.get('class'):
                instance['class'] = element.get('class')

            if not parent == None:
                instance.setParent(parent)

            if not len(element) == 0:
                for child_element in element:
                    self.CreateElement(child_element, scene, instance)

            return instance
