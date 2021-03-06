#coding: utf-8

#Import des modules
from Tkinter import *
import random as rd
import time
import pygame.mixer
pygame.mixer.pre_init(44100,-16,2,2048)
pygame.mixer.init()

class fenetre(Tk):
    def __init__(self, taille):
        """Création de l'objet fenêtre et initialisation de ses paramètres"""
        Tk.__init__(self)
        menuBar = Menu(self, tearoff=0)
        menu1 = Menu(menuBar)
        menu1.add_command(label="Nouvelle partie", command=self.nouv)
        menu1.add_command(label="Facile", command=self.difficulte_facile)
        menu1.add_command(label="Intermédiaire", command=self.difficulte_intermediaire)
        menu1.add_command(label="Expert", command=self.difficulte_difficile)
        menu1.add_separator()
        menu1.add_command(label="Quitter", command=self.destroy)
        menuBar.add_cascade(label="Fichier", menu=menu1)
        self.config(menu=menuBar)
        
        self.taille=taille
        self.bombes=taille[2]
        self.title("Démineur")
        dimension = str(self.taille[0]*16)+"x"+str(self.taille[1]*16)
        self.geometry(dimension)
        self.premier_clic = False
        self.partie_en_cours = True
        self.matriceGraph = [(self.taille[0]+2)*["V"]]
        for i in range(self.taille[1]):
            self.matriceGraph.append(["V"]+self.taille[0]*[" "]+["V"])
        self.matriceGraph.append((self.taille[0]+2)*["V"])
        
        #import des images et des fichiers audio
        self.F_blank = PhotoImage(file='ressource//image_png//blank.png')
        self.F_death=PhotoImage(file='ressource//image_png//bombdeath.png')
        self.F_flag=PhotoImage(file='ressource//image_png//bombflagged.png')
        self.F_question=PhotoImage(file='ressource//image_png//bombquestion.png')
        self.F_reveal=PhotoImage(file='ressource//image_png//bombrevealed.png')
        self.F_nbrbl=PhotoImage(file='ressource//image_png//nbrbl.png')
        self.F_open1=PhotoImage(file='ressource//image_png//open1.png')
        self.F_open2=PhotoImage(file='ressource//image_png//open2.png')
        self.F_open3=PhotoImage(file='ressource//image_png//open3.png')
        self.F_open4=PhotoImage(file='ressource//image_png//open4.png')
        self.F_open5=PhotoImage(file='ressource//image_png//open5.png')
        self.F_open6=PhotoImage(file='ressource//image_png//open6.png')
        self.F_open7=PhotoImage(file='ressource//image_png//open7.png')
        self.F_open8=PhotoImage(file='ressource//image_png//open8.png')
        self.detecteur = [self.F_open1, self.F_open2, self.F_open3, self.F_open4, self.F_open5, self.F_open6, self.F_open7, self.F_open8]

        self.mine = pygame.mixer.Sound("ressource//audio//explosion.ogg")
        self.dig = pygame.mixer.Sound("ressource//audio//creuser.ogg")
        self.plant = pygame.mixer.Sound("ressource//audio//flag.ogg")
        self.vict = pygame.mixer.Sound("ressource//audio//victoire.ogg")
        
        #Création de l'interface utilisateur
        self.Fond=Canvas(self,width=16*taille[0],height=16*taille[1])
        self.Fond.place(x=0,y=50)
        for i in range(self.taille[0]):
            for j in range(self.taille[1]):
                self.Fond.create_image(i*16,j*16,image=self.F_blank,anchor="nw")
        self.Fond.grid()
        self.Fond.bind("<ButtonPress-1>", self.clic_gauche)
        self.Fond.bind("<ButtonPress-3>", self.clic_droit)
    def clic_gauche(self, evt):
        """Est activé lorsqu'un clic gauche est effectué sur le Canvas
            recupere les coordonées du curseur et lance la fonction creuser
            Lors du premier clic lance creation_matrice() """
        if not self.partie_en_cours:
            return 0
        x_coord = evt.x
        x_indice = 0
        while x_coord >= 16:
            x_coord -= 16
            x_indice += 1
        y_coord = evt.y
        y_indice = 0
        while y_coord >= 16:
            y_coord -= 16
            y_indice += 1
        if not self.premier_clic:#initialise la matrice virtuelle lors du premier clic
            self.premier_clic = True
            self.creation_matrice(x_indice, y_indice)
            self.debut_partie = time.time() #lance le chronometre
        self.dig.play()
        self.creuser(x_indice, y_indice)
        self.gagne()
    def creuser(self, x_indice, y_indice):
        """Permet d'afficher la case cliquée et de remplire la matrice graphique"""
        if self.matriceGraph[y_indice+1][x_indice+1] == "X" or self.matriceGraph[y_indice+1][x_indice+1] == "?":
            return 0 #ne creuse pas sur les cases marquées d'un drapeau ou d'un point d'interrogation
        elif self.matrice[y_indice][x_indice] == -1: #Il y a une mine
            if self.partie_en_cours == True:
                self.Fond.create_image(x_indice*16,y_indice*16,image=self.F_death,anchor="nw")
                self.matriceGraph[y_indice+1][x_indice+1]="M"
                self.perdu()
            else:
                self.Fond.create_image(x_indice*16,y_indice*16,image=self.F_reveal,anchor="nw")
                self.matriceGraph[y_indice+1][x_indice+1]="M"
        elif self.matrice[y_indice][x_indice] == 0: #La case est vide et n'as pas d'indice
            self.Fond.create_image(x_indice*16,y_indice*16,image=self.F_nbrbl,anchor="nw")
            self.matriceGraph[y_indice+1][x_indice+1]=0
            for i in range(y_indice-1,y_indice+2):  #Creuse les case adjacentes
                for j in range(x_indice-1,x_indice+2):
                    if self.matriceGraph[i+1][j+1] == " ":
                        self.creuser(j,i)
        else: #La case est un indice, détermine cet indice
            if self.matrice[y_indice][x_indice] in [i for i in range (1,9)]:
                self.Fond.create_image(x_indice*16,y_indice*16,image=self.detecteur[self.matrice[y_indice][x_indice]-1],anchor="nw")
                self.matriceGraph[y_indice+1][x_indice+1]=self.matrice[y_indice][x_indice]
    def clic_droit(self, evt):
        """Est appellé lorsqu'un clic droit est effectué sur l'interface utilisateur
        récupère les cordonnées du curseur et affiche un drapeau ou un point d'interrogation"""
        if not self.premier_clic or not self.partie_en_cours:
            return 0
        x_coord = evt.x
        x_indice = 0
        while x_coord >= 16:
            x_coord -= 16
            x_indice += 1
        y_coord = evt.y
        y_indice = 0
        while y_coord >= 16:
            y_coord -= 16
            y_indice += 1
        if self.matriceGraph[y_indice+1][x_indice+1]==" " and self.bombes>0:
            self.plant.play()
            self.Fond.create_image(x_indice*16,y_indice*16,image=self.F_flag,anchor="nw")#Pose un drapeau
            self.matriceGraph[y_indice+1][x_indice+1]="X"
            self.bombes -= 1
        elif self.matriceGraph[y_indice+1][x_indice+1]=="X":
            self.Fond.create_image(x_indice*16,y_indice*16,image=self.F_question,anchor="nw")#Pose un point d'interrogation
            self.matriceGraph[y_indice+1][x_indice+1]="?"
            self.bombes += 1
        elif self.matriceGraph[y_indice+1][x_indice+1]=="?":
            self.Fond.create_image(x_indice*16,y_indice*16,image=self.F_blank,anchor="nw")#Retire les marquages
            self.matriceGraph[y_indice+1][x_indice+1]=" "
    def nouv(self):
        """Disponible dans le menu déroulant, cette fonction relance une partie avec le niveau de difficulté actuel"""
        self.destroy()
        fenetre(self.taille)
    def difficulte_facile(self):
        """Disponible dans le menu déroulant, cette fonction lance une partie en mode facile"""
        taille = [8,8,10]
        self.destroy()
        fenetre(taille)
    def difficulte_intermediaire(self):
        """Disponible dans le menu déroulant, cette fonction lance une partie en mode intermédiaire"""
        taille = [16,16,40]
        self.destroy()
        fenetre(taille)
    def difficulte_difficile(self):
        """Disponible dans le menu déroulant, cette fonction lance une partie en mode difficile"""
        taille = [32,16,99]
        self.destroy()
        fenetre(taille)
    def creation_matrice(self, x_clic, y_clic):
        """creation de la matrice virtuelle
        Permet de situer les mines et les indices"""
        x = self.taille[0]+2
        y = self.taille[1]+2
        bombes = self.taille[2]
        self.matrice= [x*[0] for i in range(y)] #création d'une matrice remplie de 0
        for i in range(y_clic, y_clic+3): #protections des cases adjacentes a la case du premier clic
            for j in range(x_clic, x_clic+3):
                self.matrice[i][j]="X"
        while bombes > 0:
            x, y = rd.randint(1, len(self.matrice[0])-2), rd.randint(1, len(self.matrice)-2)
            if self.matrice[y][x] == 0:
                self.matrice[y][x] = -1
                bombes = bombes -1
        for i in range(y_clic, y_clic+3):#déprotection
            for j in range(x_clic, x_clic+3):
                self.matrice[i][j]=0 
        for i in range(1, len(self.matrice)-1): #+1 aux cases vides autour d'une mine
            for j in range(1, len(self.matrice[0])-1):
                if self.matrice[i][j] == -1:
                    for k in range(i-1, i+2):
                        for m in range(j-1, j+2):
                            if self.matrice[k][m] != -1:
                                self.matrice[k][m] += 1
        #supprimer les bordures
        self.matrice.pop(0)
        self.matrice.pop(-1)
        for i in range(0, len(self.matrice)):
            self.matrice[i].pop(0)
            self.matrice[i].pop(-1)
    def gagne(self):
        """verifie les conditions de victoire"""
        if self.partie_en_cours:
            for i in range(self.taille[1]):
                for j in range(self.taille[0]):
                    if self.matriceGraph[i+1][j+1] == " " and self.matrice[i][j] != -1:
                        return 0
            #A ce point, la partie est gagnée
            self.partie_en_cours = False
            self.vict.play()
            fenetre_gagne=Tk()
            fin_partie = time.time()
            duree = str(int(fin_partie-self.debut_partie))
            texte = Label(fenetre_gagne, text="Félicitation!\n vous avez gagné la partie en "+duree+" secondes").grid()
            fenetre_gagne.mainloop()
    def perdu(self):
        """Met fin a la partie"""
        self.partie_en_cours = False
        self.mine.play()
        for i in range(self.taille[1]):
            for j in range(self.taille[0]):
                if self.matriceGraph[i+1][j+1] == " ":
                    self.creuser(j, i)

taille=[8,8,10]#valeur par defaut des dimensions de la fenêtre
if __name__ =='__main__':
    fenetre(taille).mainloop()
