from builders import FireWarrior, AirWarrior, Tournoi, Battle
import pandas as pd

""" SCRIPT """


""" COMBAT UNITAIRE """

fireboy = FireWarrior('Richard')
airboy = AirWarrior('Oscar')

ba = Battle(fireboy, airboy)
ba.printer = True
recs = ba.deathmatch()
df = pd.DataFrame.from_records(recs)
df['Nom Attaquant'] = [x.nom for x in df.attacker_obj]
df['Dégats'] = df.total_attack
df['Défense'] = df.total_defense
df['Dégats infligés'] = df.final_damage
print(df[['Nom Attaquant','Dégats', 'Défense','Dégats infligés', 'round']])


        


        


