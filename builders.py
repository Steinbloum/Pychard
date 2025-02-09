import random
import pandas as pd
from dataclasses import dataclass
import time
from faker import Faker
import itertools
from icecream import ic
from tqdm import tqdm
import plotly.express as px

fake=Faker()
ic.configureOutput(includeContext=True)


#Voici un petit script de demo je vais pas tout commenter, tu pourras balancer à gpt.
# je développe les étapes quand même
# . je le fais en français, mais saches que ça se fait pas trop en FR



""" DEFINITION DES METHODES """


# définition de la classe générale

class Personnage:
    def __init__(self, nom) -> None:
        self.nom = nom
        self.pv = 500
        self.is_alive=True
        self.attack_dices = 3
        self.attack_faces = 6
        self.defense_dices = 2
        self.defense_faces = 8


    def takeDamage(self, dmg):
        if dmg>0:
            self.pv -= dmg

    def heal(self, points):
        self.pv += points

    def reset(self):
        self.is_alive=True
        self.pv=1000

    def attack(self):
        des = Dice(self.attack_faces, self.attack_dices)
        des.lancer()
        return des.total()
    
    def defend(self):
        des = Dice(self.defense_faces, self.defense_dices)
        des.lancer()
        return des.total()

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
    def __init__(self, warrior_1:Personnage, warrior_2:Personnage) -> None:
        self.warrior_1 = warrior_1
        self.warrior_2 = warrior_2
        self.crit_value = 3
        self.historique = []
        self.printer = True

    def round(self, attacker:Personnage, defendant:Personnage):

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
            # return False

        #on retourne toutes les infos de ce round sous forme de dictionnaire
        return {
                "defendant_pv":defendant.pv,#'jajoute le pv pour determiner le gagnant
                "attacker_obj":attacker,
                "defendant_obj": defendant,
                "final_damage":valeur_degats,
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
                match_history.append(dict(round_result, round=round_counter))
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
                    match_history.append(dict(round_result, round=round_counter))
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
    def __init__(self) -> None:
        self.warriors_nb = None
        self.warriors = []
        self.scores = {}


    def createBasicWarriors(self):
        ls = []
        for n in range(self.warriors_nb):#generate random unique names
            while True:
                name = fake.name()
                if name not in ls:
                    ls.append(name)
                    break

        for name in ls:#generate the warriors
        
            warrior = random.choice([WaterWarrior, AirWarrior, FireWarrior, DirtWarrior])(name)
            self.warriors.append(warrior)

    def TournoiAPoints(self,nombre_de_warriors = 100):
        """Dans ce mode, chacun des warriors se bat une fois contre tout le monde.
        1 point en cas de victoire.

        Args:
            nombre_de_warriors (int, optional): nb de warrioir. Defaults to 100.
        """
        
        self.warriors_nb = nombre_de_warriors

        self.createBasicWarriors()

        matches = list(itertools.combinations(self.warriors,2)) #génère une liste de combinaisons uniques par 2, donc des matchs[(w1, w2), (w3,w4), etc...]
        print(f"{len(matches)} deathmatchs à disputer")
        scores = {warrior:0 for warrior in self.warriors}#génère un dictionnaire {nomduwarrior : 0} et on incremente ici pour garder le score
        battle_results = [] #crée une liste pour y mettre les résultats

        Printer.PointTournamentStart(self.warriors, matches)

        st = time.time()
        for i,warriors in tqdm(list(
                            enumerate(matches)), desc = "Tournoi cours", unit=" Combats"): #pour chacun des matchs créés plus haut : #tqdm pour afficher la progress bar

            warriors[0].reset()# reset des attributs des warriors pour un nouveau match
            warriors[1].reset()
            # print(warriors[0].nom, warriors[1].nom)
            battle = Battle(warriors[0], warriors[1])#Je crée la battle avec les 2 warriors 
            battle.printer = False # Je mets True si je veux le détail de chaque battle (ralentit A MORT le script, le plus long c'est l'affichage)
            recs = battle.deathmatch()#Je fais un deathmatch entre les 2 warriors
            df = pd.DataFrame.from_records(recs)
            df['battle'] = i
            recs = df.to_dict('records')
            battle_results.append(recs)
            # print(df) #je tchek le résultat du match
            winner = df.loc[(df.defendant_pv<=0)]["attacker_obj"].iloc[0]#je prends le gagnant 
            scores[winner] += 1 #je lui rajoute un point au scoreboard
        
        df = pd.DataFrame({
                           "nom":[warrior.nom for warrior in scores.keys()],
                           "element":[warrior.element for warrior in scores.keys()],
                           "nemesis":[warrior.nemesis for warrior in scores.keys()],
                           "score":scores.values()})
        df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
        chrono = time.time()-st

        Printer.starheader('SCOREBOARD')
        print(df)
       
        details = pd.DataFrame.from_records(list(itertools.chain.from_iterable(battle_results)))
        Printer.PointTournamentEnd(chrono, warriors, matches, df, details)
        
    def BattleRoyale(self,nombre_de_warriors = 100, show_details=True):

        """ REGLES : 
            - A chaque round, chaque warrior se fait assigner un ennemi aléatoirement 
            - Une fois que tous les ennemeis sont choisis, on prend la liste des défenseurs
            - Ceux qui n'ont pas été choisis passent leur tour.
            - Les autres reçoivent les attaques cummulées des assaillants.
            - Si le défenseur se défend contre 3 ou plus d'assaillants, il gagne un bonus permanent :
                - +1 face attaque/ennemi >=3 ex : 5 ennemis = +2 faces
                - +1 dé défense si nombre ennemis >= 5 
            - Lorsqu'un warrior tombe sous 20pv, on active le mode BERSERK, +1dé et +1face en attque et défense
            """
            
            


        self.warriors_nb = nombre_de_warriors
        self.createBasicWarriors()
        for warrior in self.warriors:
            warrior.is_berserk = False
        self.matches = {} #on crée une liste pour accuiliir les matchs
        battle_count = 0
        alive_list = lambda x : [w for w in x if w.is_alive]
        we_have_a_winner = lambda x : len(alive_list(x)) == 1
        recs = []
        Printer.starheader("FIGHT")
        print(f"== COMBATTANTS ENGAGES : {len(self.warriors)}")
        st = time.time()
        while not we_have_a_winner(self.warriors):

            for warrior in alive_list(self.warriors):
                ennemy = random.choice([x for x in alive_list(self.warriors) if (x!= warrior)])#choisi un ennemi au hasard dans la liste ( sauf lui meme et les morts)
                self.matches[warrior]=ennemy
            df = pd.DataFrame({
                "attacker":self.matches.keys(), "defendant": self.matches.values()
            })
            convertColtoName = lambda x : x.nom
            # input(df['defendant'].apply(convertObjtoName))
            for warrior in self.warriors:                    
                    if not warrior.is_alive:
                        continue
                    defense = 0
                    attakdf = df.loc[df.defendant==warrior].reset_index(drop=True)
                    alive_attackers = alive_list(attakdf.attacker)
                    if len(alive_attackers) >=3:
                        warrior.attack_faces += len(alive_attackers)-2

                        attakdf['atakname'] = attakdf['attacker'].map(convertColtoName)
                        attakdf['defendname'] = attakdf['defendant'].map(convertColtoName)
                        # print(attakdf)
                        # input(len(attakdf))
                    if len(alive_attackers) >=5:
                        warrior.defense_dices += 1
                    
                    incoming_damage = sum([attacker.attack() for attacker in alive_attackers])
                    if incoming_damage > 0:
                        battle_count +=1
                        if warrior.pv<20:
                            
                            if not warrior.is_berserk:
                                warrior.attack_faces += 1
                                warrior.attack_dices += 1
                                warrior.defense_faces += 1
                                warrior.defense_dices += 1
                                warrior.is_berserk=True
                            

                        defense = warrior.defend()
                    if incoming_damage-defense >0:
                        warrior.takeDamage(incoming_damage-defense)

                    if warrior.pv<=0:
                        warrior.is_alive=False
                    if show_details:
                        Printer.battleResults(warrior, alive_list(attakdf.attacker), incoming_damage, defense, battle_count)
                        Printer.berserk(warrior.nom)
                    if not warrior.is_alive:
                        if show_details:
                            Printer.printDead(warrior)
                    recs.append(dict(warrior.__dict__, 
                                     attackers_nb=len(alive_attackers),
                                     battle = battle_count,
                                     incoming_damage=incoming_damage))
                    
        df = pd.DataFrame.from_records(recs)
        ti = time.time()-st
        
        Printer.global_results(df, ti)

        



                    




        

@dataclass
class Printer:

    """ SINGLE BATTLE """
    def printAttackResult(round):
        print(f"{round['attacker_obj'].nom} attaque pour {round['total_attack']}")
    
    def printDefenseResult(round):
        print(f"{round['defendant_obj'].nom} pare {round['total_defense']} dégâts\n")

    def printDead(warrior):

        print("\nXxXxXxX")
        print(f"{warrior.nom} s'est battu avec courage, mais il est mort. Dommage !")
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
        
        # print(df)
    
    """ TOURNAMENT """
    
    def PointTournamentStart(warriors, matchs):

        print("\nXxXxXxX\n")
        print("BIENVENUE DANS LE TOURNOI DU SIECLE")
        print(f"\n{len(warriors)} combattants vont s'affronter un à un dans des combats à mort.")
        print(f"{len(matchs)} Deathmatchs à disputer !\n")
        print(f"\n FIGHTERS READY?")
        print("3\n2\n1\n")
        Printer.starheader("FIGHT")

    def PointTournamentEnd(chrono, warriors, matchs, score, details):
        Printer.starheader("STATS")
        print(f"Durée du tournoi : {round(chrono, 2)} secondes")
        print(f"Durée moyenne d'un round : {round(chrono/len(matchs),4)} secondes")
        print()
        df = details

        print(f"Total de dégats infilgés : {Printer.bigNumber(df.total_attack.sum())}")
        print(f"Total de dégats parés : {Printer.bigNumber(df.total_defense.sum())}")
        print(f"Total de dés lancés : {Printer.bigNumber(df.nb_attack_dice.sum() + df.nb_defense_dice.sum())}")
        print()
        print(f"Lancés / seconde : {Printer.bigNumber((df.nb_attack_dice.sum() + df.nb_defense_dice.sum())/chrono)}")
        print(f"Dégats / seconde : {Printer.bigNumber(df.final_damage.sum()/chrono)}")
        Printer.starheader("TOP WARRIORS")

        details['attacker_name'] = [x.nom for x in details.attacker_obj]
        details['defendant_name'] = [x.nom for x in details.defendant_obj]
        gr = details.groupby('attacker_name').sum(['total_damage']).reset_index()
        top_dmg_warrior = gr.sort_values(by='total_attack').iloc[0]['attacker_name']
        top_dmg_value = gr.sort_values(by='total_attack').iloc[0]['total_attack']
        print(f"Plus gros dégats: {top_dmg_warrior} pour {Printer.bigNumber(top_dmg_value)} dégâts")
        gr = details.groupby('defendant_name').sum(['total_damage']).reset_index()
        top_def_warrior = gr.sort_values(by='total_defense').iloc[0]['defendant_name']
        top_def_value = gr.sort_values(by='total_defense').iloc[0]['total_defense']
        print(f"Meilleure défense : {top_def_warrior} avec {Printer.bigNumber(top_def_value)} dégâts esquivés")


    """ BATTLE ROYALE """

    def battleResults(defendant, attackers, total_damage, total_defense, battle_count):
        Printer.starheader(f"BATTLE {battle_count} RESULTS")
        # print(attackers)
        # attackers = attackers.tolist()
        if len(attackers)==0:
            print(f"{defendant.nom} passe à travers les mailles du filet !")
            print(f"Il n'aura pas à se défendre ce tour ci !")
            return
        elif len(attackers)==1:
            print(f"C'est un duel entre {defendant.nom} et {attackers[0].nom}")
        else :
            print(f"{defendant.nom} va devoir se défendre contre {', '.join([x.nom for x in attackers[:-1]])} et {attackers[-1].nom}")
            print()
            final_damage = total_damage-total_defense
            if final_damage <=0:
                print(f"Incroyable défense de {defendant.nom} qui parvient à esquiver les {total_damage} points de dégâts")
            else:
                print(f"{', '.join([x.nom for x in attackers[:-1]])} et {attackers[-1].nom} assènent {total_damage} dégats.")
            print(f"{defendant.nom} réussi à esquiver {total_defense} dégats")
        print(f"{defendant.nom} termine ce round avec {defendant.pv} pv.")

    def berserk(warrior):
        print(f"{warrior} IS IN BERSERK MODE !!!")

    def global_results(df, ti, show_fig=True):
        Printer.subheader(f"{len(df.nom.unique().tolist()) -1} GUERRIERS DECIMES EN {ti:.2f} SECONDES")
        if show_fig:
            fig = px.line(df, x="battle",y="pv", color="nom")
            fig.show()
        Printer.starheader('BATTLE TERMINEE')
        winner = df.loc[df.pv>0].iloc[-1]['nom']
        print(f"{winner} remporte cette battle, il y aura eu {Printer.bigNumber(df.battle.max)} combats !")
        print("Voici ses stats finales :")
        stats = df.loc[df.pv>0].iloc[-1].to_dict()
        for k, v in stats.items():
            if k in ['nom', 'pv', 'attack_dices', 'attack_faces', 'defense_dices', 'defense_faces']:
                print(f"== {k.replace('_', ' ').capitalize()} : {v}")
        max_attackers = max(df.loc[df.nom == winner ].attackers_nb)
        print(f"== Maximum d'ennemis : {max_attackers}")
        battle_rate = (len(df.loc[(df.nom == winner)&(df.attackers_nb > 0)])/len(df.loc[(df.nom == winner)]))*100
        print(f"== Taux de bataille : {battle_rate:.2f}%")
        total_incoming = sum(df.loc[df.nom == winner].incoming_damage)
        print(f"== Total de dégats subis : {Printer.bigNumber(total_incoming)}")
        battle_count = len(df.loc[(df.nom == winner)&(df.attackers_nb > 0)])
        print(f"== Batailles disputées : {battle_count}")
        Printer.starheader('MEDAILLES SPECIALES')
        df = df.sort_values(by=['attackers_nb','incoming_damage'], ascending=[False, False])
        Printer.subheader("GANGBANG AWARD")
        print(f"== Attribué à {df.nom.iloc[0]} qui a pris un total de {df.incoming_damage.iloc[0]} dégâts venant de {df.attackers_nb.iloc[0]} assaillants simultanément")
        Printer.subheader("MARTYR AWARD")
        df = df.sort_values(by="pv")
        print(f"== Attribué à {df.nom.iloc[0]} qui a pris un overkill de {df.pv.iloc[0]*-1} dégats ! Ouch")
        Printer.subheader("LUCKY AWARD")
        gr = df.groupby(["attackers_nb", "nom"]).count().reset_index().sort_values(by=["attackers_nb","pv"], ascending=[True, False])
        print(f"== Attribué à {gr.nom.iloc[0]} qui a esquivé un total de {gr.pv.iloc[0]} batailles")
        Printer.subheader("BERSERKER AWARD")
        _df = df.loc[(df.is_berserk)&(df.attackers_nb>0)]
        gr = _df.groupby("nom").count().reset_index().sort_values(by="is_berserk", ascending=False)
        print(f"== Attribué à {gr.nom.iloc[0]} qui a fait {gr.is_berserk.iloc[0]} batailles en mode BERSERK")
        Printer.subheader("SHIELDER AWARD")
        df = df.sort_values(by=['defense_dices', 'defense_faces'], ascending=[False, False])
        print(f"== Attribué à {df.nom.iloc[0]} qui a obtenu {df.defense_dices.iloc[0]} dés {df.defense_faces.iloc[0]} faces de défense.")
        Printer.subheader("BRUTE AWARD")
        df = df.sort_values(by=['attack_faces', 'defense_faces'], ascending=False)
        print(f"== Attribué à {df.nom.iloc[0]} qui a obtenu {df.attack_faces.iloc[0]} faces d'attaque.")
        Printer.subheader("GLOBAL DATAFRAME")
        print(df.sort_values(by="battle"))


    """ MISC """


    def bigNumber(num):
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}k"
        else:
            return str(num)
        
    def starheader(txt):
        print(f"\n*-*-*-*-*-*-* {txt} *-*-*-*-*-*-*\n")

    def subheader(txt):
        print(f"\n== {txt} ==\n")    

""" SCRIPT """


""" COMBAT UNITAIRE """

fireboy = FireWarrior('Richard')
airboy = AirWarrior('Oscar')

# ba = Battle(fireboy, airboy)
# ba.printer = True
# ba.deathmatch()
# df = pd.DataFrame.from_records(recs)
# print(df)

""" TOURNOI A POINTS """
