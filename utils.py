import Range, os, json, socket # type: ignore
class Utils():

    def __init__(self, storage):
        self.storage = storage

    def getLibraryPath(self, extendedPath: str = ""):
        """  """

        getter_path = f"{os.path.dirname(os.path.abspath(__file__))}/{extendedPath}"
        if "?" in getter_path:
            return getter_path[4:]
        else:
            return getter_path

    def getDictPath(self, extendedPath: str = ""):
        """  """

        getter_path = Range.logic.expandPath(f'//{extendedPath}')
        if "?" in getter_path:
            return getter_path[4:]
        else:
            return getter_path
        
    def getResolvePath(self, path: str):
        if '@' in path:
            return os.path.normpath(path.replace('@', self.getDictPath()))
        
    # Getters
    def getScene(self, scene: str):
        """  """
        
        return Range.logic.getSceneList().get(scene, None)
    
    def getDictList(self, dict: str, form: dict = None) -> list:
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
    
    def getJsonFile(self, location: str, file: str) -> object:
        """  """
        
        with open(f"{location}/{file}", 'r', encoding='utf-8') as archive:
            return json.load(archive)
    
    # Setters
    def setJsonFile(self, location: str, file: str, content: object):
        with open(f"{location}/{file}", 'w') as json_file:
            json.dump(content, json_file, indent=4)

    def setManifest(self, location: str, manifest: str):
        """  """

        manifest = self.getJsonFile(location, manifest)
        loadTime = 0

        if "inserts" in manifest:
            for insert in manifest.get('inserts'):
                if insert.get('action') == "component":
                    def loadLibrary(param):
                        self.setLibrary(param['location'], param['blend'])
                        return True
                    self.storage.setChargeFunction(
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
                            self.setRegister(insert['storage'], self.getJsonFile(location, item['__external__']))
                        else:
                            self.setRegister(insert['storage'], item)

        print(f"Manifest Load: {manifest['name']}, v{manifest['version'].get('current')}, {len(manifest.get('inserts'))} Insert(s)")


    def setRegister(self, key: str, information) -> list:
        """  """

        if key in Range.logic.globalDict:
            Range.logic.globalDict[key].append(information)
        else:
            Range.logic.globalDict[key] = [information]

        return Range.logic.globalDict.get(key)
    
    def setServerClient(self, host: str, port: int):
        """  """

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        self.storage.serverClients.append({'name': 'socket', 'conection': client})

    def setTemplateDict(self, target: str, template: object):
        """  """

        for instance in template:
            if instance['type'] == "folder":
                os.makedirs(f"{target}/{instance['name']}")
            
            if 'structure' in instance:
                self.setTemplateDict(f"{target}/{instance['name']}", instance['structure'])

    def setLibrary(self, library: str, blendIn: str = None):
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
            scene=self.getScene(form_data_library.get('scene'))
        )