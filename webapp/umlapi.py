# TEST TFG PARSE
# BY: C.DESCO
import datetime
import json
import os
import pickle

# VARIABLES for debugging
"""project_name = ""
project_id = ""
test_file_name = "Prueba3.mdj"

project_classes_local = []  # List format [{Dict with classes info (see below)}],..."""

"""Classes dict parameters:
    id = class identifier
    name = class name
    *stereotype = stereotype given to the class
    *relations = list of dict containing class relations
        relations parameters:
            id = relation identifier
            *name = name of the relation "" if not given
            parent = id of the owner of the relation
            type = type of relation
                Association
                Generalization
                Dependency
                Interface Realization
            pointsTo = id of the other end of the relation
    type = UML type of the class
    parent = class parent id
    *attributes = list dict containing class attributes
        attributes parameters:
            id = attribute id
            name = attribute name
            parent = id of the owner of the attribute
            *type = type of the attribute
            *visibility = attribute visibility (default set to public if not given)
            static = boolean indicating if the operation is static or not
    *operations = list of dict containing class operations
        operations parameters:
            id = operation id
            name = operation name
            parent = id of the owner of the operation
            *visibility = operation visibility (default set to public if not given)
            *parameters = list of operations required parameters
            *return = type of the returning value
            static = boolean indicating if the operation is static or not


    *OPTIONAL
    """

# CODE
def read_file(test_file):
    try:
        file = open(test_file)
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            print("JSON decoding error")
            return None
        finally:
            file.close()
    except FileNotFoundError:
        print("File doesn't exist")
    except Exception as exception:
        print("Unknown error: " + exception.__class__.__name__)

"""Read and parse information from the given Json data"""
def j_parse(data):
    if type(data) is not dict:
        raise TypeError("Received data in wrong format when parsing, must be dictionary, got:", type(data))
    project_classes = []
    for element in data["ownedElements"][0]["ownedElements"]:
        if element["_type"] != "UMLClassDiagram":
            if element["_type"] == "UMLPackage":
                for subelement in element["ownedElements"]:
                    project_classes.append(parse_class(subelement))
            else:
                project_classes.append(parse_class(element))
    project_classes = add_additions(project_classes)
    return project_classes

def parse_class(clas):
    aux_dict = {"id": clas["_id"],
                "name": clas["name"],
                "relations": [],
                "type": clas["_type"],
                "parent": clas["_parent"]["$ref"],
                "attributes": [],
                "operations": [],
                }
    if "stereotype" in clas:
        if len(clas["stereotype"]) > 0:
            aux_dict["stereotype"] = clas["stereotype"]
    if "attributes" in clas:  # Attributes
        for attribute in clas["attributes"]:
            aux_dict["attributes"].append(parse_attribute(attribute))
    if "operations" in clas:  # Operations
        for operation in clas["operations"]:
            aux_dict["operations"].append(parse_operation(operation))
    if "ownedElements" in clas:  # Relations
        for relation in clas["ownedElements"]:
            aux_dict["relations"].append(parse_relation(relation))
    return aux_dict

def parse_attribute(attribute):
    if "name" not in attribute:
        attribute["name"] = ""
    if "type" not in attribute:
        attribute["type"] = ""
    aux_att = {"id": attribute["_id"], "parent": attribute["_parent"]["$ref"], "name": attribute["name"], "type": attribute["type"]}
    if "visibility" in attribute:
        aux_att["visibility"] = attribute["visibility"]
    else:
        aux_att["visibility"] = "public"
    if "multiplicity" in attribute:
        aux_att["multiplicity"] = attribute["multiplicity"]
    else:
        aux_att["multiplicity"] = ""
    if "isStatic" in attribute:
        aux_att["static"] = True
    else:
        aux_att["static"] = False
    return aux_att

def parse_operation(operation):
    aux_ope = {"id": operation["_id"], "parent": operation["_parent"]["$ref"], "name": operation["name"]}
    if "visibility" in operation:
        aux_ope["visibility"] = operation["visibility"]
    else:
        aux_ope["visibility"] = "public"
    if "isStatic" in operation:
        aux_ope["static"] = True
    else:
        aux_ope["static"] = False
    if "parameters" in operation:
        aux_ope["parameters"] = []
        for parameter in operation["parameters"]:
            if not "direction" in parameter:
                aux_ope["parameters"].append({"name": parameter["name"], "type": parameter["type"]})
            elif "type" in parameter:
                aux_ope["return"] = parameter["type"]

        if len(aux_ope["parameters"]) == 0:
            del aux_ope["parameters"]
    return aux_ope

def parse_relation(relation):
    aux_aso = {"id": relation["_id"], "parent": relation["_parent"]["$ref"]}
    if "name" in relation:
        aux_aso["name"] = relation["name"]
    else:
        aux_aso["name"] = ""
    if relation["_type"] == "UMLAssociation":
        aux_aso["type"] = "Association"
    elif relation["_type"] == "UMLDependency":
        aux_aso["type"] = "Dependency"
    elif relation["_type"] == "UMLGeneralization":
        aux_aso["type"] = "Generalization"
    elif relation["_type"] == "UMLInterfaceRealization":
        aux_aso["type"] = "InterfaceRealization"
    if "end2" in relation:
        aux_aso["pointsTo"] = relation["end2"]["reference"]["$ref"]
    elif "source" in relation:
        aux_aso["pointsTo"] = relation["source"]["$ref"]
    return aux_aso

def add_additions(project):
    for clas in project:
        if "attributes" in clas:
            for attribute in clas["attributes"]:
                if type(attribute["type"]) is dict:
                    attribute["type"] = get_class_by_id(project, attribute["type"]["$ref"])["name"]
        if "relations" in clas:
            for relation in clas["relations"]:
                relation["pointsTo"] = get_class_by_id(project, relation["pointsTo"])["name"]
        if "operations" in clas:
            for operation in clas["operations"]:
                if "return" in operation and type(operation["return"]) is dict:
                    operation["return"] = get_class_by_id(project,operation["return"]["$ref"])["name"]
                if "parameters" in operation:
                    for parameter in operation["parameters"]:
                        if type(parameter["type"]) is dict:
                            parameter["type"] = get_class_by_id(project,parameter["type"]["$ref"])["name"]

    return project





"""Print project information to console""" #DEPRECATED
"""def project_info():
    print("Project name: {}".format(project_name))
    print("Project ID: {}".format(project_id))"""

"""Print all classes in the given project"""
def print_classes(project):
    for clas in project:
        print_class(clas)
        print("------------------------")

"""Receives a class in the class dict format and prints its information"""
def print_class(clas):
    if type(clas) is not dict:
        print("Received parameter is not a dict")
        return
    print("Class ID: {}".format(clas["id"]))
    print("Class Name: {}".format(clas["name"]))
    print("Class Relations: ")
    if not "relations" in clas:
        print("\tNo relations")
    else:
        for aso in clas["relations"]:
            print_relation(aso)

    print("Class Type: {}".format(clas["type"]))
    print("Class Parent ID: {}".format(clas["parent"]))

    print("Class attributes:")
    if not "attributes" in clas:
        print("\tNo attributes")
    else:
        for att in clas["attributes"]:
            print_attribute(att)
    print("Class operations:")
    if not "operations" in clas:
        print("\tNo operations")
    else:
        for ope in clas["operations"]:
            print_operation(ope)

def print_relation(relation):
    print("\tID: {}".format(relation["id"]))
    print("\tName: {}".format(relation["name"]))
    if "type" in relation:
        print("\t\tType: {}".format(relation["type"]))
    print("\t\tParent ID: {}".format(relation["parent"]))

def print_attribute(attribute):
    print("\tID: {}".format(attribute["id"]))
    print("\tName: {}".format(attribute["name"]))
    print("\t\tType: {}".format(attribute["type"]))
    print("\t\tParent ID: {}".format(attribute["parent"]))
    print("\t\tVisibility: {}".format(attribute["visibility"]))
    print("\t\tMultiplicity: {}".format(attribute["multiplicity"]))

def print_operation(operation):
    print("\tID: {}".format(operation["id"]))
    print("\tName: {}".format(operation["name"]))
    print("\t\tParent ID: {}".format(operation["parent"]))
    print("\t\tVisibility: {}".format(operation["visibility"]))

"""Prints all classes json data (excluding the visual diagram)""" #DEPRECATED
"""def print_j_classes():
    for element in jdata["ownedElements"][0]["ownedElements"]:
        if element["_type"] != "UMLClassDiagram":
            print(element)
            if "attributes" in element:
                print(element["attributes"])
            print("=============")"""

"""Prints the elements of the given class (ID)""" #DEPRECATED
"""def print_j_class_elements(id):
    for clas in jdata["ownedElements"][0]["ownedElements"]:
        if clas["_type"] != "UMLClassDiagram":
            if clas["_id"] == id:
                for element in clas["ownedElements"]:
                    print(element)
                    print("-----------")"""

"""def print_associations_j(): #DEPRECATED
    for clas in jdata["ownedElements"][0]["ownedElements"]:
        if clas["_type"] != "UMLClassDiagram":
            if "ownedElements" in clas:
                print(clas["name"])
                for ele in clas["ownedElements"]:
                    print(ele)
                print("=========")
"""
"""Returns the dictionary object that contains all the information of the class with the given ID
If not found returns a None object
""" #DEPRECATED
"""def get_class_by_id(id): 
    if not type(id) == str:
        print("Parameter is not a string")
        return None
    else:
        for clas in project_classes_local:
            if clas["id"] == id:
                return clas
        return None"""

def get_class_by_id(project_list, id):
    if type(id) is not str:
        raise TypeError("ID for get_class_by_id must be a string, got:", type(id))
    if type(project_list) is not list:
        raise TypeError("Project for get_class_by_id must be of type list, got:",type(project_list))
    else:
        for clas in project_list:
            if clas["id"] == id:
                return clas
        return None

"""Returns the dictionary object that contains all the information of the relation with the given ID
If not found returns a None object
"""
def get_relation_by_id(project_list,id):
    for clas in project_list:
        if len(clas["relations"]) == 0:
            continue
        for relation in clas["relations"]:
            if relation["id"] == id:
                return relation
    return None


"""Returns the dictionary object that contains all the information of the object with the given ID
If not found returns a None object
Searches for:
    Classes
    Relations
"""
def get_element_by_id(project_list,id):
    element = get_class_by_id(project_list,id)
    if element != None:
        return element
    element = get_relation_by_id(project_list,id)
    if element != None:
        return element



"""Returns the dictionary object that contains all the information of the class with the given name (not case sensitive)
If not found returns a None object
""" #DEPRECATED
"""def get_class_by_name(name):
    if not type(name) == str:
        print("Parameter is not a string")
        return None
    else:
        for clas in project_classes_local:
            if clas["name"].casefold() == name.casefold():
                return clas
        return None"""

def get_class_by_name(project,name):
    if type(name) is not str:
        raise TypeError("Name for get_class_by_name must be a string, got:",type(name))
    else:
        for clas in project:
            if clas["name"].casefold() == name.casefold():
                return clas
        return None

"""Returns a list of the names of the classes in the project"""
def get_classes(project):
    aux_list = []
    for clas in project:
        if clas["type"] == "UMLClass":
            aux_list.append(clas["name"])
    return aux_list

"""Returns a list of the relations of a class (given by name or Id)"""
def get_class_relations(clas):
    if type(clas) is not str:
        raise TypeError("Clas ID for get_class_relations must be a string, got:",type(clas))
    aux_clas = get_class_by_id(clas)
    if aux_clas == None:
        aux_clas = get_class_by_name(clas)
    aux_list = []
    if aux_clas != None:
        for relation in aux_clas["relations"]:
            aux_list.append(relation)
        return aux_list
    else:
        print("Class not found")
        return None

"""Returns a list consisting of the name parameters of a list of dict"""
def get_names(dics):
    if type(dics) is not list:
        raise TypeError("Parameter for get_names must be a list, got:",type(dics))
    aux_list = []
    for dic in dics:
        if type(dic) is not dict:
            print("Found non dictionary element in list")
        else:
            aux_list.append(dic["name"])
    return aux_list

"""Get number of classes in project"""
def number_classes(project):
    if type(project) is not list:
        raise TypeError("Project for number_classes must be of type list, got:",type(project))
        return None

    return len(project)

def number_relations(project):
    index = 0
    for clas in project:
        index += len(clas["relations"])
    return index

def class_name_list(project):
    list = []
    for clas in project:
        list.append(clas["name"])
    return list

"""Adds relations to the given project"""
"""def add_relations(project):
    if project:
        for clas in project:
            if clas["relations"]:
                for relation in clas["relations"]:
                    print("A VER")
                    print(relation)
                    print(clas)
                    print("==================")
                    print("------------------------")
                    print_classes(project)
                    if "pointsTo" in relation:
                        relation["points"] = get_class_by_id(project, relation["pointsTo"])["name"]
                    else:
                        relation["points"] = None
    return project"""

"""Reads file,  parses data and adds relations, returns the final list"""
def prepare_uml(path):
    umldata = read_file(path)
    parsed = j_parse(umldata)
    return parsed

"""Saves"""
def save_project(directory,name,project):
    if not os.path.isdir(directory):
        raise NotADirectoryError("The following directory doesn't exist:",directory)
    if not type(project) is list:
        raise TypeError("Project for save_project must be of type list, got:",type(project))
    if os.path.isfile(os.path.join(directory,name)):
        raise FileExistsError("File with name %s already exists at %s" % (name,directory))
    path = os.path.join(directory,name)
    with open(path,"wb") as file:
        pickle.dump(project,file)
        return path
    return None


"""Loads"""
def load_project(path):
    if not os.path.isfile(path):
        raise FileNotFoundError("File not found",path)
    with open(path,"rb") as file:
        project = pickle.load(file)
        return project
    return None

"""TEST"""
test_class = "Esquirla no direct"
test_id = "AAAAAAF+2JRXoy34Aj8="

#project_classes_local = prepare_uml("Prueba3.mdj")
# save_project("D:\\Escritorio\\tfg infor\\Obsidian",prepare_uml(test_file_name),"prueba.txt")
# load_project("D:\\Escritorio\\tfg infor\\Obsidian\\prueba.txt")
# print_class(get_class_by_id(test_id))
# print_class(get_class_by_name(test_class))
# print_associations_j()
#print_classes(project_classes_local)
# print(get_by_id(test_id))
# print_j_classes()
# print_j_class_elements(test_id)
# get_classes())
# print(get_class_relations(test_class))
# print(get_names(get_class_relations(test_class)))