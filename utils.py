import Range, os, json, socket, re # type: ignore
from mathutils import Vector, Matrix, Euler, noise # type: ignore
from dicttoxml import dicttoxml
import xml.etree.ElementTree as XML

class Utils():

    def __init__(self, storage):
        self.storage = storage

        self.startup_await = False

    def GetStartupAwait(self):
        real_information = None
        if self.startup_await:
            real_information = self.startup_await
        self.startup_await = True
        return real_information

    def GetRoamingPath(self):
        """  """

        getter_path = os.environ.get("APPDATA", None)
        if "?" in getter_path:
            return getter_path[4:]
        else:
            return getter_path

    def GetLibraryPath(self, extendedPath: str = ""):
        """  """

        getter_path = f"{os.path.dirname(os.path.abspath(__file__))}/{extendedPath}"
        if "?" in getter_path:
            return getter_path[4:]
        else:
            return getter_path

    def GetDictPath(self, extendedPath: str = ""):
        """  """

        getter_path = Range.logic.expandPath(f'//{extendedPath}')
        if "?" in getter_path:
            return getter_path[4:]
        else:
            return getter_path
        
    def GetResolvePath(self, path: str):
        if '@' in path:
            return os.path.normpath(path.replace('@', self.GetDictPath()))
        
    # Getters
    def GetScene(self, scene: str):
        """  """
        
        return Range.logic.getSceneList().get(scene, None)
    
    def GetRoundedArray(self, array: list) -> list:
        rouded = []
        for indice in array:
            if isinstance(indice, int) or isinstance(indice, float):
                rouded.append(round(indice))
        return rouded
    
    def GetDictList(self, dict: str, form: dict = None) -> list:
        """
            Lista diretórios de um caminho fornecido com um sistema de filtragem robusto para buscas.
            Performace: Extreme (~80ms)

            Args:
                dict (str): Caminho inicial onde a busca será realizada.
                form (dict, optional): Dicionário com filtros opcionais.
                    Pode conter os seguintes campos:
                        - 'type': Tipo de item a ser filtrado ('file' para arquivos, 'folder' para diretórios).
                        - 'extension': Extensão dos arquivos a serem filtrados.

            Returns:
                list: Lista de itens encontrados no diretório conforme os filtros aplicados.

            Example:
                getDictList('project/folder/', {'type': 'file', 'extension': '.py'})
        """

        getter_dict_list = []
        if os.path.exists(dict):
            if os.path.isdir(dict):
                for item in os.listdir(dict):
                    if form != None:
                        if 'type' in form and form['type'] == 'folder':
                            if os.path.isdir(os.path.join(dict, item)):
                                getter_dict_list.append(
                                    {
                                        'wayTo': dict,
                                        'fullPath': os.path.join(dict, item),
                                        'item': item
                                    })
                        else:
                            if os.path.isfile(os.path.join(dict, item)):
                                if 'extension' in form:
                                    if item.endswith(form['extension']):
                                        getter_dict_list.append(
                                            {
                                                'wayTo': dict,
                                                'fullPath': os.path.join(dict, item),
                                                'item': item
                                            })
                                else:
                                    getter_dict_list.append(
                                        {
                                            'wayTo': dict,
                                            'fullPath': os.path.join(dict, item),
                                            'item': item
                                        })
                    else:
                        getter_dict_list.append(
                            {
                                'wayTo': dict,
                                'fullPath': os.path.join(dict, item),

                                
                                'item': item
                            })
        return getter_dict_list
    
    def GetRGBNormalized(self, color: list) -> list:
        """  """

        if len(color) == 3:
            return [color[0] / 255, color[1] / 255, color[2] / 255, 1.0]
        elif len(color) == 4:
            return [color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255]
        else:
            return None
        
    def GetDimensions(self, instance: object) -> list:
        """  """

        if instance is not None:
            instance_mesh = instance.meshes[0]
            collection = [[], [], []]
            for mat_index in range(instance_mesh.numMaterials):
                for vert_index in range(instance_mesh.getVertexArrayLength(mat_index)):
                    vertice_XYZ = instance_mesh.getVertex(mat_index, vert_index).XYZ
                for i in range(3):
                    collection[i].append(vertice_XYZ[i])
                    dimensions = Vector([max(axis) - min(axis) for axis in collection])
            return dimensions
        else:
            return None
    
    def GetJsonFile(self, location: str, file: str) -> object:
        """  """
        
        with open(f"{location}/{file}", 'r', encoding='utf-8') as archive:
            return json.load(archive)
        
    def GetFile(self, location: str, file: str) -> object:
        """  """
        
        with open(f"{location}/{file}", 'r', encoding='utf-8') as archive:
            return archive.read()
        
    def GetCDATA(self, text):
        return re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", text, flags=re.DOTALL)
    
    def GetXMLFile(self, location: str, file: str) -> object:
        """  """
        
        return XML.parse(f"{location}/{file}")

    def DictToXML(self, json: dict):
        return dicttoxml(json)
    
    # Setters
    def SetJsonFile(self, location: str, file: str, content: object):
        with open(f"{location}/{file}", 'w') as json_file:
            json.dump(content, json_file, indent=4)

    def SetManifest(self, location: str, manifest: str):
        """  """

        manifest = self.GetJsonFile(location, manifest)
        loadTime = 0

        if "inserts" in manifest:
            for insert in manifest.get('inserts'):
                if insert.get('action') == "component":
                    def loadLibrary(param):
                        self.SetLibrary(param['location'], param['blend'])
                        return True
                    self.storage.SetChargeFunction(
                        loadLibrary, 
                        {
                            "location": f"{insert['location'].replace('@', location)}/{insert['component']}", 
                            "blend": insert.get('scene'),
                            "payload": insert.get('scene')
                        }
                    )
                elif insert.get('action') == "storage":
                    for item in insert['data']:
                        if '__external__' in item:
                            external_content_data = None
                            if 'json' in item['__external__']:
                                external_content_data = self.GetJsonFile(location, item['__external__'])
                                if isinstance(external_content_data, dict):
                                    self.SetRegister(insert['storage'], self.GetJsonFile(location, item['__external__']))
                                elif isinstance(external_content_data, list):
                                    for data in external_content_data:
                                        self.SetRegister(insert['storage'], data)
                            elif 'xml' in item['__external__']:
                                self.SetRegister(insert['storage'], self.GetFile(location, item['__external__']))
                            else:
                                pass

                        else:
                            self.SetRegister(insert['storage'], item)

        print(f"Manifest Load: {manifest['name']}, v{manifest['version'].get('current')}, {len(manifest.get('inserts'))} Insert(s)")
        self.storage.RunCharge()


    def SetRegister(self, key: str, information) -> list:
        """  """

        if key in Range.logic.globalDict:
            Range.logic.globalDict[key].append(information)
        else:
            Range.logic.globalDict[key] = [information]

        return Range.logic.globalDict.get(key)
    
    def SetServerClient(self, host: str, port: int):
        """  """

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        self.storage.serverClients.append({'name': 'socket', 'conection': client})

    def SetTemplateDict(self, target: str, template: object):
        """  """

        for instance in template:
            if instance['type'] == "folder":
                os.makedirs(f"{target}/{instance['name']}")
            
            if 'structure' in instance:
                self.SetTemplateDict(f"{target}/{instance['name']}", instance['structure'])

    def SetLibrary(self, library: str, blendIn: str = None):
        """  """
        form_data_library = {
            'library': library,
            'type': 'Scene'
        }

        if blendIn != None:
            form_data_library['scene'] = blendIn

        return Range.logic.LibLoad(
            os.path.normpath(form_data_library.get('library')), 
            form_data_library.get('type'),
            load_actions=True,
            scene=self.GetScene(form_data_library.get('scene'))
        )