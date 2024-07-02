**Hello Richard**

Bienvenue dans ce tutoriel personalisé d'installation d'un environement propre pour pythoniser !
---

Autant prendre tout de suite les bonnes habitudes! 

* Tu vas rapidement être amené à importer des biblithèques tierces et à les installer.
    
    Rien de plus simple avec la commande pip dans le terminal : 
    pip install *bibli*
    par exemple pip install pandas. 
    Tu trouveras d'ailleurs un lien vers la commande d'install dans la doc de ladite lib. 
    par exemple pandas encore : https://pandas.pydata.org/docs/getting_started/install.html (tu remarqueras l'inspiration pour la doc de copilot)

* en général dans un projet python tu trouveras à la root du dossier un fichier qui s'appelle requirements.txt.

    Ce fichier permet de lister les libs dont le projet a besoin pour tourner. 
    C'est bien foutu la commande pip. 
    Si tu fais `pip install -r requirements.txt (voir cheatsheet), ça t'installe tout d'un coup. 
    Et comme je suis sympa je t'en ai fait un dans le dossier, avec les libs de base de tous les jours en python.

* Ne le fait pas encore. On va d'abord créer un environement virtuel 
    C'est une copie de la version de python que tu installée sur ton ordi. 
    Tu n'en vois pas encore l'utilité mais *trust me* fais le ! 
    Un coup j'ai du passer plusieurs jours a refaire des installs à cause d'une lib qui a merdé... depuis j'ai appris
    C'est d'ailleurs dans les bonne pratiques que j'aurais aimé connaitre. 

    Donc pour créer un environnement virtuel (VirtualENVironment) tu vas dans le dossier ou tu veux le faire (en général à la racine du projet)
    tu ouvre le terminal à cette adresse ( cd path/to/file ) 
    et tu fais simplement la commande : python -m venv .venv
    ça va créer un dossier caché (.venv) avec la copie de python. 
    venv est une commande intégrée dans python (c'est dire si c'est important), et le .venv c'est le nom du dossier. 
    Si je faid python -m venv caca ça fait la même chose mais dans un dossier nommé caca, c'est moins pro.

    Si tu executes cette commande dans ton terminal vscode, il va certainement te demander si tu veux selectionner le nouvel interpreteur, tu dis oui.
    Si tu le fais dans cmd, il va falloir activer l'environement :
    dans le terminal : .venv/Scripts/activate.bat
    tu vas voir ça te mettra un (venv) avant l'invite, ça a marché. 

* une fois que tu es dans ton environement virtuel, tu peux pip à foison. 

    donc tu fais pip install -r requirements.txt 

* te voici prêt à coder en toute sérénité !


**Bon je t'ai fait un fichier .bat pour que tu ne te fasses pas chier, en gros tu le doubleclik dans explorer et ça fait tout ce que je viens d'écrire. tu as juste à attendre les instalations**
**Néanoins je t'invite à faire ces commandes manuellement, ça amène des questions, et c'est bien de savoir ce qu'on fabrique quand même !**







