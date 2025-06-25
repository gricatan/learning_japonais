from os import listdir, path, remove
from json import load, dump
from requests import post
from random import randint
from gtts import gTTS
import pygame
from tkinter import Tk, Label, StringVar, OptionMenu, Entry, Button, Frame, Toplevel, BooleanVar, LEFT, BOTH, RIGHT
from sys import exit
from re import search



# initialisation variables
pygame.mixer.init()
base_dir = path.dirname(path.abspath(__file__))
liste_labels = []# liste utiliser en global pour stocker les labels tkinter et les supprimer
with open(f'{base_dir}\\API.txt', 'r', encoding="utf-8") as fichier:# Chargement de la clé API depuis un fichier
    api_key = fichier.read().strip()


path = listdir(f'{base_dir}\\sujet_de_voc')# Chemin vers les fichiers de vocabulaire

#initialisation de l'API Mistral
url = "https://api.mistral.ai/v1/chat/completions"
headers = {
    'Authorization': f'Bearer {api_key}',
    'content-type': 'application/json'
}


def generer(voc):# Décortiquer la chaîne de caractères contenant le vocabulaire en listes de mots français et japonais
    
    first = 0
    debut = 0
    francais = []
    japonais = []


    while debut != -1:  # Tant que l'on trouve un '=' dans la chaîne


        debut = voc.find('=',first)
        print(voc[first:debut])
        francais.append(voc[first:debut])# Ajout du mot français à la liste
        
        # pour que l'increment ne fasse pas lire hors de la chaine
        if debut == -1:
            break
        
        first = debut+1
        debut = voc.find(',', debut+1)
        japonais.append(voc[first:debut])# Ajout du mot japonais à la liste

        first = debut+1

    return francais, japonais

def send(instruction, demande):# Envoie une requête à l'API Mistral pour générer du vocabulaire
    message = {
        'model': 'mistral-small-latest',
        'messages': [
            {'role': 'user', 'content': f'{instruction} : {demande}'}
        ]
    }
    reponse = post(url, headers=headers, json=message)
    vocabulaire = reponse.json()
    if vocabulaire['object'] == 'error':
        print(f"Erreur de l'API : {vocabulaire['error']['message']}")
        return None
    return vocabulaire['choices'][0] ['message'] ['content']


def apprendre(fichier):
    
    #Réinitialise la fenêtre et les labels pour ne pas aditioner avec les précédents
    global liste_labels, fenetre, base_dir
    fenetre.geometry("400x300")
    for label in liste_labels:
        label.destroy()
    liste_labels = []

    # Ouvre le fichier de vocabulaire et charge les listes de mots
    with open(f'{base_dir}/sujet_de_voc/{fichier}', 'r', encoding="utf-8") as fichier:
        listes = load(fichier)
    
    # Ajuste la taille de la fenêtre en fonction du nombre de mots
    fenetre.geometry(f"400x{len(listes[0])*30+100}")

    # Crée des labels de format japonais : français pour chaque mot
    for i in range(len(listes[0])):
        label = Label(fenetre, text=f'{listes[0][i]} : {listes[1][i]}')
        label.pack()
        liste_labels.append(label)

def creer_nouveau_sujet(sujet):

    global path, fenetre, choix_apprendre, choix_interrogation, base_dir

    # génère un nouveau sujet de vocabulaire
    index = 0
    reponse = '%'# Variable pour stocker la réponse de l'API
    while search(r"[^a-zA-Z= ,āīūēōéèêëàâäîïôöùûüçœ']", reponse):#Bouclez permettant de s'assurer que la réponse ne contient pas de caractères indésirables
        reponse = send('repond seulement par une chaine de caractère avec un mot en japonais en Rōmaji et l\'autre en français sur ce format (minimum 20 mots environ et sans aucun autre commentaire) : mot_japonais=mot_francais,baka=idiot ect sur ce format tout en corespondant a ce sujet :',sujet)
        index += 1
        if index > 1:  # Limite le nombre de tentatives pour éviter une boucle infinie retourne sans charger de fichier
            print(reponse)
            return


    globals()[sujet] = generer(reponse)# Découpe la réponse en deux listes : une pour les mots japonais et une pour les mots français

    # Ajoute le nouveau sujet à la liste des sujets disponibles
    with open(f'{base_dir}/sujet_de_voc/{sujet}', 'w', encoding="utf-8") as fichier:
        dump(globals()[sujet], fichier, indent=2, ensure_ascii=False)

    # raffraichi path 
    '''
    ⚠️
    je n'ai pas trouvé de moyen de rafraichir le menu
    Il faut donc fermer le programme et le relancer pour que le nouveau sujet soit pris en compte
    ⚠️
    '''
    path = listdir(f'{base_dir}/sujet_de_voc')





def interrogation(fichier):


    # Réinitialise la fenêtre et les labels pour ne pas que l'utilisateur puisse avoir les réponses
    global liste_labels, fenetre, base_dir
    fenetre.geometry("400x300")
    for label in liste_labels:
        label.destroy()
    liste_labels = []

    # Fonction pour fermer la fenêtre d'interrogation
    # Ce n'est pas la methode habituel pour eviter le wait_variable et l'arrêt dans une boucle
    def fermer_fenetre():
        nonlocal f_interro
        boutton_cliquer.set(True)
        fermer.set(True)
        f_interro.destroy()
    
    # Ouvre le fichier de vocabulaire et charge les listes de mots
    with open(f'{base_dir}/sujet_de_voc/{fichier}', 'r', encoding="utf-8") as fichier:
            listes = load(fichier)
    
    # initialisation : random francais/japonais, notion
    connu = randint(0, 1)
    inconnu = connu == 0
    j = 0
    note = 0

    # Création de la fenêtre d'interrogation
    f_interro = Toplevel()
    f_interro.title("interrogation") 
    f_interro.geometry("400x300")

    # Création des cadres pour l'interrogation
    separation = Frame(f_interro)
    separation.pack(fill='both', expand=True)

    separation_gauche = Frame(separation, bg='lightblue')
    separation_gauche.pack(side=LEFT, fill=BOTH, expand=True)

    separation_droite = Frame(separation, bg='lightgreen')
    separation_droite.pack(side=RIGHT, fill=BOTH, expand=True)

    # boutton quitter
    boutton_quitter = Button(f_interro, text="Quitter", command=fermer_fenetre)
    boutton_quitter.pack()

    # variables
    boutton_cliquer = BooleanVar(f_interro)
    fermer = BooleanVar(f_interro)
    juste = Label(separation_gauche)
    iaeval = Label(separation_gauche)
    note_info = Label(separation_gauche)

    def soumettre(reponse):

        nonlocal note, j, connu, inconnu, listes, f_interro

        # Vérifie si la réponse est correcte via ia pour contourner les sens proche ou les petites fautes d'orthographe
        correction = send('repond seulement par Bon ou Mauvais selon si les mots ce ressemble, ou on a peu près le même sens ou pas : ', f' {reponse} avec {listes[inconnu][j]}')
        
        #affiche la comparaison que fait l'ia au cas ou l'utilisateur ne comprend pas pourquoi sa réponse est mauvaise
        iaeval.config(text=f' {reponse} avec {listes[inconnu][j]} : {correction}')
        iaeval.pack(padx=10)

        # Vérifie si la réponse est correcte ou non
        if correction[0] == 'B':
            note = note+1
            juste.config(text=f'Bon')# Affiche "Bon" si la réponse est correcte
            juste.pack()
        else:
            juste.config(text=f'Mauvais {listes[connu][j]}')# Affiche "Mauvais et la réponse" si la réponse est incorrecte
            juste.pack()

        # Affiche la note actuelle sur le nombre total de mots
        note_info.config(text=f'Note : {note}/{len(listes[connu])}')
        note_info.pack()


        '''
        ⚠️
        Il y a parfoit un bug avec la prononciation du mot japonais qui fait tout sautez, je ne sais pas pourquoi
        Certaine fois le mot n'est pas jouer, peut être un bug coté gtts
        ⚠️
        '''
        # Joue la prononciation du mot japonais
        texte = f'{listes[0][j]}'
        tts = gTTS(text=texte, lang='ja')
        son_dir = f"{base_dir}\\voix.mp3"
        fichier_audio = son_dir
        tts.save(fichier_audio)
        pygame.mixer.music.load(fichier_audio) # Joue le fichier audio contenant la prononciation du mot japonais
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pass

        remove(fichier_audio)

        # Passe au mot suivant, debloquer wait_variable
        boutton_cliquer.set(True)

    for i in listes[connu]:

        if fermer.get():# permet de sortir de la boucle quand la fenêtre est fermée
            break

        traduction = Label(separation_droite, text=f'Traduction de {i} : ')
        traduction.pack()

        reponse = Entry(separation_droite) # Champ de saisie pour la réponse de l'utilisateur
        reponse.pack()
        boutton = Button(separation_droite, text="Soumettre", command=lambda: soumettre(reponse.get()))# Bouton pour soumettre la réponse
        boutton.pack()

        separation_droite.wait_variable(boutton_cliquer)# on attends avant d'affichée les autres mots interrogée
        
        # On cache les boutton précédent pour laisser les suivants
        reponse.pack_forget()
        boutton.pack_forget()
        traduction.pack_forget()

        boutton_cliquer.set(False)# on remets le booleens a faux
        j += 1 #incrément de l'index
    

# initialise la fenetre principale
fenetre = Tk()
fenetre.title("Apprendre le Japonais") 
fenetre.geometry("400x300")

#initialise le menu déroulant apprendre
Label(fenetre, text="Apprendre").pack()
choix_apprendre = StringVar(fenetre)
choix_apprendre.set(path[0])
choix_apprendre.trace('w', lambda *a: apprendre(choix_apprendre.get()))
menu_apprendre = OptionMenu(fenetre, choix_apprendre, *path)
menu_apprendre.pack()

#initialise le menu déroulant interrogation
Label(fenetre, text="Interrogation").pack()
choix_interrogation = StringVar(fenetre)
choix_interrogation.set(path[0])
choix_interrogation.trace('w', lambda *a: interrogation(choix_interrogation.get()))
menu_interrogation = OptionMenu(fenetre, choix_interrogation, *path)
menu_interrogation.pack()

#initialise la zone de texte pour les nouveaux sujets
Label(fenetre, text="Ajouter un sujet").pack()
sujet_var = StringVar(fenetre)
nouveau_sujet = Entry(fenetre,textvariable=sujet_var, width=30)
nouveau_sujet.pack()

# Boutton pour créé le sujet
Button(fenetre, text="ok", command=lambda: creer_nouveau_sujet(sujet_var.get())).pack()

# Boutton pour quittez fenetre et script
Button(fenetre, text="Quitter", command=lambda *args: (fenetre.destroy(), exit())).pack()

# Boucle principale
fenetre.mainloop()