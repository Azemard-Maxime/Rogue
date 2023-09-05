# Rogue 6

########################## ROGUE #################################


import random
import copy
from math import *

#------------------------------------------------------------------------- classe Coord -------------------------------------------------------------------------------------------#


class Coord():      #dans () c'est une classe
    "Coordonnée"      
    def __init__(self,x,y):
        self.x=x
        self.y=y  # attributs d'instances


    def __eq__(self,other):
        if self.x==other.x and self.y==other.y:
            return True
        return False


    def __repr__(self):
        return f"<{self.x},{self.y}>"

    def __add__(self,other):
        a=self.x+other.x
        b=self.y+other.y
        return Coord(a,b)



    def __sub__(self, other) :
        # calcule la différence entre les coordonnées self et other
        return Coord(self.x-other.x,self.y-other.y)



    def distance(self, other) :
        # calcule la distance entre les coordonées self et other
        resultat = sqrt(pow(other.x-self.x,2)+pow(other.y-self.y,2))
        return resultat



    def direction(self, other):
        # parmi les quatre directions cardinales (<1, 0>, <-1, 0>, <0, 1>, <0, -1>),
        # indique la direction depuis self vers other.

        #  calculez cos = d.x / |d|, avec d la différence
        cos = (self.x-other.x) / self.distance(other)

        #Si cos >{\displaystyle 1/{\sqrt {2}}}  : direction <-1, 0>
        if cos > 1/sqrt(2):
            return Coord(-1,0)
        
        #Si cos < -{\displaystyle 1/{\sqrt {2}}}.   : direction <1, 0>
        if cos < -1/sqrt(2):
            return Coord(1,0)
        #Sinon si d.y > 0  : direction <0, -1>
        elif self.y-other.y >0:
            return Coord(0,-1)
        #Sinon                  : direction <0, 1>
        else:
            return Coord(0,1)


#------------------------------------------------------------------------------------- classe Map --------------------------------------------------------------------------------#

class Map():
    "élément de la carte"

    

    # attributs de classes:

    ground="."
    dir={'z': Coord(0,-1), 's': Coord(0,1), 'd': Coord(1,0), 'q': Coord(-1,0)}
    empty=" "
    up="+"
    down="-"

    # Méthodes:

    def __init__(self,size=20,hero=None,nbrooms=7):

        if hero==None:
            hero=Hero()
 
       
        self._elem={} #{hero:pos}

        self.size=size
        self.hero=hero
        self._roomsToReach=[]
        self._rooms=[]
        self.nbrooms=nbrooms

        a=[]
        for i in range(size):
            a.append(size*[Map.empty])
        self._mat=a  


        self.generateRooms(nbrooms)
        self.reachAllRooms()
        self.put(self._rooms[0].center(),hero)

        self.put(self._rooms[1].center(),Etage("escalier",self.up))
        self.put(self._rooms[0].center()+Coord(-1,0),Etage("escalier",self.down))
        
        for n in range(len(self._rooms)):
            self._rooms[n].decorate(self)
        
        
        
        
        

    def __repr__(self):
        chaine=""
        for j in range(self.size):
            for i in range(self.size):
                chaine=chaine+ str(self._mat[j][i])
            chaine=chaine+"\n"
        
        
        return chaine


    def __len__(self):
        return self.size


    def isinstance(o,c):
        if o is c:
            return True
        return False


    def __contains__(self,item):
        if isinstance(item,Coord)==True and ( (0<=item.x<len(self._mat) and 0<=item.y<len(self._mat))):
            return True
        if isinstance(item,Element)==True:
            for i in range(self.size):
                for j in range(self.size):
                    if item==self._mat[j][i]:
                        return True
        return False

    def get(self,c):
        
        self.checkCoord(c)
        return self._mat[c.y][c.x]


    def pos(self,e):
        self.checkElement(e)
        return self._elem[e]
      

    def put(self,c,e):

        self.checkCoord(c)
        self.checkElement(e)
  
        if self._mat[c.y][c.x]==Map.empty or self._mat[c.y][c.x]!=Map.ground:
            raise ValueError('Incorrect cell')
        elif self.__contains__(e)==True:
            raise KeyError('Already placed')

        if isinstance(e,Element)==True:
            self._mat[c.y][c.x]=e
            self._elem[e]=c
        else:
            self._mat[c.y][c.x]=e



    def rm(self,c):
        
        element=self.get(c)
        self._mat[c.y][c.x]=Map.ground
        del self._elem[element]
        
  
    def move(self, e, way): # !!! 2 méthodes moves
        """Moves the element e in the direction way."""
        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
            elif self.get(dest) != Map.empty and self.get(dest).meet(e) and self.get(dest) != self.hero:
                self.rm(dest)
            





    def addRoom(self,room):
        self._roomsToReach.append(room)
        for j in range(room.c1.y,room.c2.y+1):
            for i in range(room.c1.x,room.c2.x+1):
                self._mat[j][i]=self.ground
               

    def findRoom(self,coord):
        for h in range(len(self._roomsToReach)):
            if self._roomsToReach[h].__contains__(coord):
                return self._roomsToReach[h]
        return False

    def intersectNone(self,room):
        for h in range(len(self._roomsToReach)):
            if self._roomsToReach[h].intersect(room)==True:
                return False
        return True



    def dig(self,coord):
        self._mat[coord.y][coord.x]=self.ground
        if self.findRoom(coord)!=False:
            self._rooms.append(self.findRoom(coord))
            self._roomsToReach.remove(self.findRoom(coord))
            


    def corridor(self,start,end):
        self.dig(start)

        # forage vertical
        if start.y < end.y:
            for j in range(start.y,end.y):
                start+=Coord(0,1)
                self.dig(start)
                
        elif start.y > end.y:
            for j in range(start.y,end.y,-1):
                start+=Coord(0,-1)
                self.dig(start)
            
        # forage horizontal
        if start.x < end.x:
            for i in range(start.x,end.x):
                start+=Coord(1,0)
                self.dig(start)
        
        elif start.x > end.x:
            for i in range(start.x,end.x,-1):
                start+=Coord(-1,0)
                self.dig(start)


    def reach(self):
        salleA=random.choice(self._rooms)
        salleB=random.choice(self._roomsToReach)
        self.corridor(salleA.center(),salleB.center())
        


    def reachAllRooms(self):
        # Cette méthode va permettre de rejoindre toutes les salles.
        #Elle enlève la première salle des salles à atteindre et la met dans les salles atteintes 
        #Appelle reach() jusqu'à ce qu'il n'y ai plus de salle à atteindre

        
        self._rooms.append(self._roomsToReach[0])
        self._roomsToReach.remove(self._roomsToReach[0])
        while len(self._roomsToReach)!=0:
            self.reach()


    def randRoom(self):
        # Cette méthode retourne une salle aléatoire dans la carte, en choisissant aléatoirement :
        #une coordonnée <x1,y1> pour le coin en haut en gauche 
        #une largeur et une hauteur 

        
        x1= random.randint(0,len(self) - 3)
        y1= random.randint(0, len(self) - 3)
        
        largeur = random.randint(3,8)
        longueur = random.randint(3,8)
       
        x2= min(len(self) - 1,x1 + (largeur))
        y2= min(len(self) - 1,y1 + (longueur))
        
        return Room (Coord (x1,y1),Coord (x2,y2))


    def  generateRooms(self,n):
        #Cette méthode tente n fois 
        #de créer une salle aléatoire
        #si elle n'est en intersection avec aucune autre salle (intersectNone), l'ajoute dans la carte (addRoom)

        for i in range(n):
            salle=self.randRoom()
            if self.intersectNone(salle)==True:
                self.addRoom(salle)



    def checkCoord(self,c):
        if isinstance(c,Coord)==False:
            raise TypeError('Not a Coord')
        elif self.__contains__(c)==False:
            raise  IndexError('Out of map coord')


    def checkElement(self,c):
        if isinstance(c,Element)==False:
            raise  TypeError('Not a Element')




    def  moveAllMonsters(self):
        #  chaque monstre de la carte la créature se déplace dans la direction du héro si et seulement si :
        # la créature est à une distance du héro inférieure à 6 (la créature "détecte" le héro)
        # le déplacement amène à une case de sol ou au héro (les créatures ne ramassent pas les objets et traversent pas les murs).

        
        posHero = self.pos(self.hero)
        for e in self._elem.keys():                                              # vérifier si l'objet est monstre (pas objet ou héro)
            if isinstance(e,Hero)==False and isinstance(e,Equipment)==False and isinstance(e,Etage)==False:
                posMonstre=self.pos(e)
                chemin=posMonstre.direction(posHero)
                if posMonstre.distance(posHero)<6 and self.get(posMonstre+chemin)==self.ground:
                    self.move(e,chemin)
                elif self.get(posMonstre+chemin)==self.hero:
                    self.hero.meet(e)



#----------------------------------------------------------------------------------------------------------- { getch } -------------------------------------------------------------------------------------#

def getch():
    """Single char input, only works only on mac/linux/windows OS terminals"""
    try:
        import termios
        # POSIX system. Create and return a getch that manipulates the tty.
        import sys, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch().decode('utf-8')


#------------------------------------------------------------------------- classe Element  ----------1-----------------------------------------------------------------------#

class Element():
    "Les elements de la carte"


    def __init__(self,name,abbrv=None):
        
        self.name=name
        
        if abbrv==None:
            self.abbrv=self.name[0]
        else:
            self.abbrv=abbrv

    def __repr__(self):
        return self.abbrv

    def description(self):
        return "<"+self.name+">"

    def meet(self,hero):
        # ATTENTION: chaque sous classe doit avoir sa méthode meet, sinon Erreur !!!

        raise NotImplementedError("Not implemented yet")



    def isinstance(o,c):
        if o is c:
            return True
        return False


#-------------------------------------------------------------------------------classe Creature ------------1A-------------------------------------------------------------------#
    
class Creature(Element):
    "Les créatures du jeu"
    def __init__(self,name,hp,abbrv=None,strength=None,xp=2):
        Element.__init__(self,name,abbrv=None)

        self.name=name
        self.hp=hp
        
        if abbrv==None:
            self.abbrv=self.name[0]
        else:
            self.abbrv=abbrv
            
        if strength==None:
            self.strength=1
        else:
            self.strength=strength

        if isinstance(self,Hero)==False:
            self.xp=xp
        
            
       

    def isinstance(o,c):
        if o is c:
            return True
        return False



    def description(self):
        return Element.description(self)+"("+str(self.hp)+")"

    def meet(self,hero):
        
        self.hp=self.hp-hero.strength
        message ="The " + hero.name + " hits the " + self.description()
        theGame().addMessage(message)
        if self.hp<=0:
            if isinstance(hero,Hero)==True:
                hero.XP+=self.xp
                if hero.XP>=8:
                    hero.nivSup()
            return True
               
        return False
        

    #def nivSup(self):
    #    pass


    #def nivSup(self,hero):
    #    
    #    hero.XP=0
    #    hero.strength+=1
    #    hero.hp+=5

#--------------------------------------------------------------------------------- classe Hero ------------1Aa-------------------------------------------------------------------#


class Hero(Creature):
    "Le héro"

    
    
    def __init__(self,name="Hero",hp=10,abbrv="@",strength=2,armeUtilisé=None):        #!!! HERO AVEC HP=1000
        Creature.__init__(self,name,hp,abbrv=None,strength=None)
            
        self.name=name
        self.hp=hp
        self.abbrv=abbrv
        self.strength=strength                                  #strength
        self._inventory=[]
        self.XP=1
        self.hpMax=hp

        if armeUtilisé==None:
            self.armeUtilisée=[]
        



    def take(self,elem):
        if isinstance(elem,Equipment)==True :
            self._inventory.append(elem)
        else:
            raise TypeError
       


    def description(self):
      
        return Creature.description(self) + str(self._inventory)


    def fullDescription(self):
        dico = self.__dict__
        liste=""
        for i in dico.keys():
            if i != "_inventory":
                liste+="> " +str(i) +" : " + str(dico[i]) + "\n"
        liste+="> INVENTORY : " +  str([x.name for x in self._inventory])
        return liste
           

    def  use(self,item):
        if isinstance(item,Equipment)==False:
            raise TypeError

        elif item not in self._inventory:
            raise ValueError

        if item.use(self)==True and isinstance(item,Etage)==False:
            self._inventory.remove(item)


        # changement d'arme utilisée
        if isinstance(item,Armes)==True:    #si l'objet utilisée est une arme
            self.changeArme(item)

  
    def nivSup(self):
        theGame().addMessage("Niveau supérieur")
        self.XP=0
        self.strength+=1
        self.hpMax+=2
        self.hp=self.hpMax




    def changeArme(self,arme):
        #self.armeUtilisée.append(self._inventory)

        if self.armeUtilisée == []:
            self.armeUtilisée.append(arme)     # changement d'arme

        else:
            self._inventory.append(self.armeUtilisée[0])    # on copie l'ancienne arme dans inventory
            self.strength -= self.armeUtilisée[0].strength
            self.armeUtilisée.remove(self.armeUtilisée[0])  # on vide la liste d'arme
            self.armeUtilisée.append(arme)
        


        
        

#------------------------------------------------------------------------------classe  Equipment ------1B------------------------------------------------------------------#

class Equipment(Element):
    "Les équipements du héro (inventaire)"

    def __init__(self,name,abbrv=None,usage=None):
        self.name=name
        
        if abbrv==None:
            self.abbrv=self.name[0]
        else:
            self.abbrv=abbrv
        self.usage=usage

        



    def meet(self,hero):
       hero.take(self)
       theGame().addMessage("You pick up a "+ str(self.name))
       return True

            

    def use(self,creature):
        if self.usage!=None:
            theGame().addMessage("The "+ str(creature.name) +" uses the "+ str(self.name))
            #if isinstance(self,Armes)==True and isinstance(creature,Hero)==True:
            #    creature.armement(self)
            return self.usage(self,creature)
        else:

            theGame().addMessage( "The " + str(self.name)+" is not usable")
            return False




#-------------------------------------------------------------------------- classe Armes --------1Ba----------------------------------#

class Armes(Equipment):
    "Les armes trouvées sur la carte"

    def __init__(self,name,abbrv=None,usage=None,strength=2):
        self.name=name
        
        if abbrv==None:
            self.abbrv=self.name[0]
        else:
            self.abbrv=abbrv
        self.usage=usage
        self.strength=strength



    def meet(self,hero):
       hero.take(self)
       theGame().addMessage("You pick up a "+ str(self.name))
       return True






#------------------------------------------------------------------------ classe Etage --------1C------------------------------------#

class Etage(Element):
    "Des escaliers de la carte"

    def __init__(self,name,abbrv=None,usage=None):
        self.name=name
        
        if abbrv==None:
            self.abbrv=self.name[0]
        else:
            self.abbrv=abbrv




    def meet(self,hero):
        if self.abbrv==Map.up:
            self.monter(hero)
        else:
            self.descendre(hero)
            

    def use(self,creature):
        if self.usage!=None:
            theGame().addMessage("The "+ str(creature.name) +" uses the "+ str(self.name))
            return self.usage(self,creature)
        else:

            theGame().addMessage( "The " + str(self.name)+" is not usable")
            return False


    def monter(self,creature):
        # monter d'un étage
        
        #enregistrer l'étage
        theGame().addMessage("The "+ str(creature.name) +" uses the "+ str(self.name))
        theGame().changeRooms(True)

    def descendre(self,creature):
        theGame().addMessage("The "+ str(creature.name) +" uses the "+ str(self.name))
        theGame().changeRooms(False)
            
            







#----------------------------------------------------------------------- classe Room --------------------------------------------------------------------------------#

class Room():
    "Les salles du dongeons"
    
    def __init__(self,c1,c2):
        self.c1=c1
        self.c2=c2


    def __repr__(self):
        
        return "[<" + str(self.c1.x) + "," + str(self.c1.y) + ">, <" + str(self.c2.x) + "," + str(self.c2.y) + ">]"
      

    def __contains__(self,c):
        if self.c1.x <= c.x <= self.c2.x and self.c1.y <= c.y <= self.c2.y:
            return True
        
        return False


    def center(self):
        return Coord(((self.c1.x + self.c2.x)//2),(self.c1.y + self.c2.y)//2)



    def intersect (self,room2):
        # renvoie true si les salles se chevauchent

        if room2.__contains__(self.c1)==True or room2.__contains__(self.c2)==True or room2.__contains__(Coord(self.c2.x,self.c1.y))==True or room2.__contains__(Coord(self.c1.x,self.c2.y))==True or self.__contains__(room2.c1)==True or self.__contains__(room2.c2)==True or self.__contains__(Coord(room2.c2.x,room2.c1.y))==True or self.__contains__(Coord(room2.c1.x,room2.c2.y))==True:
            return True
        return False



    def randCoord(self):
        # retourne une coordonnée aléatoire à l'intérieur de la salle

        coordX=random.randint(self.c1.x,self.c2.x)
        coordY=random.randint(self.c1.y,self.c2.y)
        return Coord(coordX,coordY)



    def randEmptyCoord(self,map) :
        # retourne une coordonnée aléatoire à l'intérieur de la salle qui n'est pas déjà occupée par un élément,
        # ni au centre de la salle : tire aléatoirement une coordonnée jusqu'à en trouver une valide.
        
        coord=self.randCoord()
        while coord==self.center() or isinstance(map.get(coord),Element)==True:
            coord=self.randCoord()
        return coord



    def decorate(self,map) :
        # "décore" la salle, en mettant à une coordonnée aléatoire inoccupée:
        # un équipement aléatoire PUIS à une autre coordonnée, une créature aléatoire

        crdVide1=self.randEmptyCoord(map)
        equipment=theGame().randEquipment()
        map.put(crdVide1,equipment)

        crdVide2=self.randEmptyCoord(map)
        monstre=theGame().randMonster()
        map.put(crdVide2,monstre)
        
        











#--------------------------------------------------------------------------- classe Game ------------------------------------------------------------------------------#

class Game(object):
    "classe qui contiendra la mécanique principale du jeu"

    # ATRIBUTS DE CLASSES #

    equipments = { 0: [ Equipment("potionVide","!"),\
                        Equipment("gold","o"),\
                        Equipment("potion","!",usage=lambda self,hero:heal(hero) ), \
                        Armes("knife",strength=2,usage=lambda self,hero:forceAugm(hero,self))],
                   1: [ Armes("sword",strength=3,usage=lambda self,hero:forceAugm(hero,self)), \
                        Armes("bow",strength=1,usage=lambda self,hero: forceAugm(hero,self)) ,\
                        Equipment("potion","!",usage= lambda self, hero : teleport(hero,True))], \
                   2: [ Equipment("chainmail") ],\
                   3: [ Equipment("portoloin","w", usage = lambda self,hero : teleport(hero,False)), \
                        Armes("hache",strength=4,usage=lambda self,hero:forceAugm(hero,self))]}
    
    monsters = { 0: [ Creature("Goblin",4),\
                      Creature("Bat",2,"W",xp=1) ],\
                 1: [ Creature("Ork",6,strength=2),\
                      Creature("Blob",10,xp=3) ],\
                 5: [ Creature("Dragon",20,strength=3,xp=4) ] }
    
        # Ces attributs sont des dictionnaires associant un degré de rareté à une liste d'éléments du jeu
        
    _actions = {"z": lambda hero:theGame().floor.move(hero,Coord(0,-1)), \
                "s": lambda hero:theGame().floor.move(hero,Coord(0,1)), \
                "q": lambda hero:theGame().floor.move(hero,Coord(-1,0)), \
                "d": lambda hero:theGame().floor.move(hero,Coord(1,0)),\
                "i": lambda hero:theGame().addMessage(hero.fullDescription()),\
                "k": lambda hero: hero.__setattr__("hp",0),\
                " ": lambda hero:None,\
                "u": lambda hero: hero.use(theGame().select(hero._inventory)),\
                "!": lambda hero: theGame().stop() }
    
        # un dictionnaire associant des touches du clavier à des actions sous forme de lambda



    




    # METHODES #

    def __init__(self,hero=None,level=1,floor=None,_message=None):

        if hero==None:          #le héros du jeu 
            self.hero=Hero()
        else:
            self.hero=hero
        self.level=level        # le niveau de l'étage où se trouve le héros
        self.floor=None      # la carte de l'étage où se trouve le héros
        self._message=[]        # une liste de messages à afficher au joueur
        self.floors=[]
    

    def buildFloor(self):
        
        self.floor=Map(hero=self.hero)
        self.floors.append(self.floor)
        
  


    def addMessage(self,msg):
        self._message.append(msg)


    def readMessages(self):
        # retourne une chaine de caractère contenant tous les messages de la liste, séparés par ". ",
        # et vide cette liste. Retourne une chaine vide si la liste est vide.
        chaine=""
        for i in range(len(self._message)):
            chaine+=self._message[i]+". "
        self._message=[] #self._message.clear
        return chaine
        


    def randElement(self,collection):
        # retourne un élément pris au hasard dans un dictionnaire d'élément

        X=random.expovariate(1/self.level)
        for i in collection:
            if i<=X:
                element=collection[i]
                
        elem=random.choice(element)
        return copy.copy(elem)


    def randEquipment(self):
        # retourne un équipement aléatoire  #

        return self.randElement(self.equipments)

    def randMonster(self) :
        # retourne un monstre aléatoire #
        
        return self.randElement(self.monsters)


    def select(self,l):
        #  permet de choisir un équipement dans une liste l
        print("Choose item> "+ str([str(l.index(e)) + ": " + str(e.name) for e in l]))                           
        c=getch()
        if str.isdigit(c) and int(c)<len(l):
             return l[int(c)]
        return None
        
         
         

    def play(self):
        """Main game loop"""
        self.buildFloor()
        print("--- Bienvenue Aventurier ! Début de quête !---")
        while self.hero.hp > 0:
            print()
            print("étage ",self.level)
            print(self.floor)
            print(self.hero.description())
            print(self.readMessages())
            c = getch()
            if c in Game._actions:
                Game._actions[c](self.hero)
            self.floor.moveAllMonsters()
        print("--- Game Over ---")

            
    def stop(self):
        print("Abandon, quête teminée !")
        raise SystemExit()
    


    def changeRooms(self,up):
        if up==True:
            self.level+=1
            if len(self.floors)<self.level:
                self.floors.append(Map(hero=self.hero))
                
            self.floor= self.floors[self.level-1]
        else:
            if self.level==1:
                self.addMessage("Chemin bloqué. Ne peux pas descendre")
            else:
                self.level-=1
                self.floor= self.floors[self.level-1]
                









#__________________________________________________________fonctions____________________________________________________________________________________#

def theGame(game = Game()):
    return game



def heal(creature):
        #  soigne la créature: lui ajoute 3 hp, retourne vrai.
        
        creature.hp+=3
        if creature.hp>creature.hpMax:
            creature.hp=creature.hpMax
        return True

def teleport(creature, unique):
    # déplace la créature dans une position aléatoire valide et inoccupée de la carte courante du jeu, retourne unique.

    alRoom = theGame().floor.randRoom()
    alCoord= alRoom.randCoord()
    while theGame().floor.get(alCoord) != theGame().floor.ground:
        alCoord= alRoom.randCoord()
    oldCoord = theGame().floor.pos(creature)
    theGame().floor.rm(oldCoord)
    theGame().floor.put(alCoord,creature)
    return unique
    


def forceAugm(creature,arme):
    creature.strength+=arme.strength
    return True


#def arc(creature,arme):
#    coordHD=creature
#    coordBD=
#    for i:
#        for j:
    
    
    
    

#===========================================================================================================================================================#

theGame().play()
#python3 Rogue6.py

