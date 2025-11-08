import pygame
from pygame.locals import *
import os
import json



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
new_path = os.path.dirname(BASE_DIR)


class Quest:
    def __init__(self, screen, max_quests:int = 1):
        with open(os.path.join(new_path, "assets", "quests.json"), "r", encoding="utf-8") as f:
            self.liste_quests = json.load(f)
            print(self.liste_quests)
            self.screen = screen
            self.quests = {}
            self.name_quest = ""
        
    
    def creer_quest(self, name_quest:str): 
        self.quests = {name_quest: {"description": self.liste_quests[name_quest]["description_quest"], "item_required": self.liste_quests[name_quest]["required_items_quest"], "reward_quest": self.liste_quests[name_quest]["reward_quests"], "finish":False}}
        self.name_quest = name_quest

    def verif_objet(self, objet:str): 
        for quest in self.quests:
            for item in self.quests[quest]["item_required"]:
                if item[0] == objet:
                    if not item[1] == item[2]:
                        item[1] += 1
        self.__check_quest()
        
                 
    
    def __check_quest(self): 
        for quest in self.quests:
            for item in self.quests[quest]["item_required"]:
                if not item[1] == item[2]:
                    self.quests[quest]["finish"] = False
                    break
                self.quests[quest]["finish"] = True
            

    
    def rewards_quest(self):
        reward = self.quests["reward_quest"]
        self.quests = {}
        return reward
    
    def get_name(self):
        return self.name_quest
    
    def get_required_items(self):
        
        return self.quests[self.name_quest]["item_required"]
    
    def get_reward(self):
        return self.quests[self.name_quest]["reward_quest"]
    
    def affiche_quete_complete(self):
        for quest in self.quests:
            if self.quests[quest]["finish"]:
                print(f"vous avez fini la quete {quest}")

                

            
