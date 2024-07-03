import random
import pandas as pd
from dataclasses import dataclass
import time
from faker import Faker
import itertools

fake=Faker()


#Voici un petit script de demo je vais pas tout commenter, tu pourras balancer à gpt.
# je développe les étapes quand même
# . je le fais en français, mais saches que ça se fait pas trop en FR



""" DEFINITION DES OBJETS """


# définition de la classe générale

class Personnage:
    def __init__(self, nom) -> None:
        self.nom = nom
        self.pv = 1000
        self.is_alive=True


    def takeDamage(self, dmg):
        if dmg > 0:
            self.pv -= dmg

    def heal(self, points):
        self.pv += points

#définition des sous-classes

class FireWarrior(Personnage):
    def __init__(self, nom) -> None:
        super().__init__(nom)
        self.element = "feu"
        self.nemesis = "eau"
  
class WaterWarrior(Personnage):
    def __init__(self, nom) -> None:
        super().__init__(nom)
        self.element = "eau"
        self.nemesis = "air"

class AirWarrior(Personnage):
    def __init__(self, nom) -> None:
        super().__init__(nom)
        self.element = "air"
        self.nemesis = "terre"

class DirtWarrior(Personnage):
    def __init__(self, nom) -> None:
        super().__init__(nom)
        self.element = "terre"
        self.nemesis = "feu"

#définition du lancé de dé

class Dice:
    def __init__(self, nb_faces, nb_des) -> None:
        self.nb_faces = nb_faces
        self.nb_des = nb_des
        self.resultat = None

    def lancer(self) -> dict:
        resultat = {}
        for de in range(self.nb_des):
            resultat[f"lancé {de}"] = random.randint(1, self.nb_faces)
        self.resultat = resultat
        return resultat
    
    def total(self) -> int:
        """Calcule le total du lancer de dés

        Returns:
            int: le total
        """
        total = sum(self.resultat.values())
        return int(total)

#définition du jeu / modes

class Battle:
    def __init__(self, warrior_1, warrior_2) -> None:
        self.warrior_1 = warrior_1
        self.warrior_2 = warrior_2
        self.crit_value = 3
        self.historique = []
        self.printer = True

    def round(self, attacker:Personnage, defendant:Personnage):

        if not attacker.is_alive:
            #en début de round, il est possible quil soit déja mort s'il a combattu avant. 
            return False #on arrete tout se suite la fonction et on retourne False

        nb_des_attaque = 4 #nombre de des d'attaque
        nb_faces_attaque = 6 #nbre de faces du dé d'attaque
        nb_des_defense = 2 #nombre de des de defense
        nb_faces_defense = 8 #nbre de faces du dé de defense

        #on rajoute des des/faces si le combattant est un nemesis de l'autre

        if defendant.element == attacker.nemesis:
            nb_des_attaque += 1
            nb_faces_attaque -= 1

        if defendant.nemesis == attacker.element:

            nb_faces_defense -= 1
            nb_des_defense +=1

        #On lance les dés grâce à la classe Dice créée plus haut :

        attack_roll = Dice(nb_faces_attaque, nb_des_attaque) #je génère les objets "lancer de dés" (class Dice)
        defense_roll = Dice(nb_faces_defense, nb_des_defense)

        attack_roll.lancer() #je lance les dés avec la methode de ma classe Dice
        defense_roll.lancer()

        valeur_degats = attack_roll.total() - defense_roll.total() #je calcule la valeur des dégats

        defendant.takeDamage(valeur_degats) # on damage le défenseur

        if defendant.pv <= 0 : #si le défenseur se retrouve muerto
            defendant.is_alive = False # on met en False son attribut is_alive
            if self.printer:
                Printer.printDead(defendant)
            return False

        #on retourne toutes les infos de ce round sous forme de dictionnaire
        return {"attacker" : attacker.nom, 
                "defendant" : defendant.nom, 
                "final_damage":valeur_degats,
                "attacker_hp" : attacker.pv,
                "defendant_hp" : defendant.pv,
                "total_attack":attack_roll.total(),
                "total_defense":defense_roll.total(),
                "nb_attack_dice":nb_des_attaque,
                "nb_attack_faces":nb_faces_attaque,
                "nb_defense_dice":nb_des_defense,
                "nb_defense_faces":nb_faces_defense,
                }

    def deathmatch(self):
        
        #ici l'idée c'est de faire une boucle tant que les 2 warriors sont vivants, ils s'attaquent tour à tour
        warriors = [self.warrior_1, self.warrior_2] #je crée une liste avec mes objets
        match_history = []
        round_counter = 0
        everybodyLives = lambda : all([warrior.is_alive for warrior in warriors])
        st = time.time()

        while everybodyLives(): #a chaque début de loop on va vérifier que l'attribut is_alive de nos warriors est True
            round_result = self.round(self.warrior_1, self.warrior_2)
            if not everybodyLives():
                break
            if self.printer:
                Printer.printAttackResult(round_result) #on affiche le résultat du round grâce à notre self.printer
                Printer.printDefenseResult(round_result) #on affiche le résultat du round grâce à notre self.printer
            # on rajoute le résultat à l'historique (une liste)
            match_history.append(dict(round_result, round=round_counter))

           #idem mais on écnahge l'attaquant et le defenseur
            round_result = self.round(self.warrior_2, self.warrior_1)
            if round_result:#si personne n'est mort
                if not everybodyLives():
                    break
                if self.printer:
                    Printer.printAttackResult(round_result)
                    Printer.printDefenseResult(round_result) #on affiche le résultat du round grâce à notre self.printer
                match_history.append(dict(round_result, round=round_counter))

            round_counter +=1
        
        if self.printer:
            Printer.printMatchStats(match_history, time.time()-st) 
        return match_history


class Tournoi:
    def __init__(self, nombre_de_warriors = 100) -> None:
        self.warriors_nb = nombre_de_warriors
        self.warriors = []

    def createWarriors(self):
        for n in range(self.warriors_nb):
            warrior = random.choice([WaterWarrior, AirWarrior, FireWarrior, DirtWarrior])(fake.name())
            self.warriors.append(warrior)
        print([f"{x.nom}, {x.element}" for x in self.warriors])

    def TournoiAPoints(self):
        matches = list(itertools.combinations(self.warriors,2))
        for i,match in enumerate(matches):
            match[0].pv = 1000
            match[1].pv = 1000
            battle = Battle(match[0], match[1])
            battle.printer = False
            recs = battle.deathmatch()
            # print(pd.DataFrame.from_records(recs))










@dataclass
class Printer:


    def printAttackResult(round):
        print(f"{round['attacker']} attaque pour {round['total_attack']}")
    
    def printDefenseResult(round):
        print(f"{round['defendant']} pare {round['total_defense']} dégâts\n")


    def printDead(warrior):

        print("\nXxXxXxX")
        print(f"{warrior.nom} s'est battu avec courage, mais il est mort. Dommage")
        print("XxXxXxX\n")

    def printMatchStats(match_history, chrono=False):
        df = pd.DataFrame.from_records(match_history)
        nombre_de_rounds = df['round'].iloc[-1]
        attaque_de_ouf = max(df['total_attack'])
        parade_de_ouf = max(df['total_defense'])

        print("\nXxXxXxX")
        print(f"Il aura fallu {nombre_de_rounds} rounds pour départager les guerriers")
        print(f"L'attaque la plus puissante a causé {attaque_de_ouf} dégats.")
        print(f"La meilleure parade a esquivé {parade_de_ouf} dégâts.")
        
        if chrono:
            print(f"Le match a duré {round(chrono, 4)} secondes")
        print("XxXxXxX\n")
        
        print(df)


""" SCRIPT """


            

fireboy = FireWarrior('Fireboy')
waterboy = WaterWarrior("Waterboy")
airboy = AirWarrior('Airboy')

# ba = Battle(fireboy, airboy)
# ba.printer = False
# recs = ba.deathmatch()
# df = pd.DataFrame.from_records(recs)
# print(df)
tn = Tournoi()
tn.createWarriors()
tn.TournoiAPoints()
        


        


