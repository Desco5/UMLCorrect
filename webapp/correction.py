# TEST TFG PARSE
# BY: C.DESCO
import os
import webapp.umlapi as uml


def quantitives(index):
    if type(index) == int:
        index = float(index)
    if not type(index) == float:
        print("Received parameter is not float number")
        return None
    if index> 1.75:
        return "a lot more"
    if index> 1.25:
        return "some more"
    if index> 0.75:
        return "a similar number"
    if index> 0.25:
        return "some less"
    return "much less"


def remove_dupes(lst):
    if lst:
        aux_list = []
        for elem in lst:
            if elem not in aux_list:
                aux_list.append(elem)
        return aux_list

def anticheat(project, project_compared):
    if not type(project) == type([]):
        print("Original project not of type list")
    if not type(project_compared) == type([]):
        print("Compared project not of type list")
    project_dubious = remove_dupes(project)
    project_compare = remove_dupes(project_compared)
    cheat_index = 0
    total_index = 0
    for item in project_dubious:
        local_cheat_index = 0
        local_index = 1
        clas = uml.get_class_by_id(project_compare,item["id"]) # find if class with same ID
        if clas == None:
            total_index += 1
            continue
        local_cheat_index += 1
        if not len(item["relations"]) == 0 and not len(clas["relations"]):
            for relation in item["relations"]:
                local_index += 1
                if relation in clas["relations"]:
                    local_cheat_index += 1
        if not len(item["attributes"]) == 0 and not len(clas["attributes"]):
            for attribute in item["attributes"]:
                local_index += 1
                if attribute in clas["attributes"]:
                    local_cheat_index += 1
        if not len(item["operations"]) == 0 and not len(clas["operations"]):
            for operation in item["operations"]:
                local_index += 1
                if operation in clas["operations"]:
                    local_cheat_index += 1
        total_index += 1
        cheat_index += local_cheat_index/local_index
    return cheat_index / total_index

def check_number_classes(project,reference):
    return uml.number_classes(project)/ uml.number_classes(reference)

def check_number_relations(project,reference):
    return uml.number_relations(project) / uml.number_relations(reference)

def given_classes(project,given_list):
    correct_list = []
    for element in given_list:
        if not "relations" in element: #check that it's a class and not a relation
            continue
        clas = uml.get_class_by_name(project,element["name"])
        if clas == None:
            correct_list.append("Missing given class: %s"%element["name"])
            continue
        """ Missing given relation functionality
        relation_list = []
        for relation in given_list:
            if "relations" in relation:
                continue
            if relation["parent"] == clas["id"]:
                relation_list.append(relation)"""
    return correct_list

def check_all(project, reference, given_list):
    correction_list = []
    aux_string = quantitives(check_number_classes(project,reference))
    correction_list.append("There are %s classes"%aux_string)
    aux_string = quantitives(check_number_relations(project,reference))
    correction_list.append("There are %s relations"%aux_string)
    correction_list += given_classes(project,given_list)

    return correction_list

