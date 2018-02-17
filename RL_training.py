#import keras
import go 
import CNN_policy
import RL_player as pl
import go
import time
import features as ft
import visualisation as vis


#initialisation
#player = pl.Player_rd()
opponent =pl.Player_rd()
conv=ft.Preprocess()
filename="model_gen5_02_.hdf5"
#filename="model_gen_8_2_5h54.hdf5"
#filename="model_gen_10_2_18h53.hdf5"
#filename="model_gen_6_2_15h.hdf5"
policy_pl=CNN_policy.CNN()
policy_pl.load (filename) 
player=pl.Player_pl(policy_pl,conv)

def play_game(player,opponent,nb_partie,preprocessor,size=9,verbose=False):
    
    #init
    etat = [go.GameState(size) for _ in range(nb_partie)] #liste des parties actuelle
    coups=[[] for _ in range(nb_partie)]  #liste des coups joués
    parties=[[] for _ in range(nb_partie)] # liste des etats du jeu
    id_gagne=[] #liste des indices des parties gagnées
    ratio=0

    # deroulement
    start=time.time()
    s1=0 #tps premiere partie
    
    # on joue le premier coup de chaque partie
    for i in range(nb_partie):
        coup=opponent.get_move(etat[i]) 
        coups[i].append(coup)
        etat[i].do_move(coup)
        parties[i].append(conv.state_to_tensor(etat[i]))

    #on joue tout les coups
    actuel=player
    ancien=opponent
    fin=0 # pour arreter la boucle
    tour=1 #pour verbose
    while(fin<nb_partie): 
    
        for i in range(nb_partie):
                if(etat[i].is_end_of_game==False): # vérifie que la partie n'est pas fini
                    coup = actuel.get_move(etat[i]) # on récupere le coup jpué 
                    coups[i].append(coup) # on le sauvegarde
                    etat[i].do_move(coup) #on le joue
                    parties[i].append(conv.state_to_tensor(etat[i])) #on sauvegarde l'état du jeu

                    
                    if(etat[i].is_end_of_game==True): 
                        fin+=1  # pour arreter la boucle
                        if(etat[i].get_winner()==-1): # -1 pour blanc
                            id_gagne.append(i)
                            ratio+=1
                    
                    if (i==1 & verbose==True):
                        tour+=1
                        print
                        print("Coup numéro %i" %tour)
                        vis.vis_gs(etat[i])
                                                    
                    if (fin==1&s1==0&verbose==True):
                        print("1ere partie finie en %f secondes" % (time.time()-start))
                        s1=1
        #vis_gs(parties[1])
        
    
        #on change de joueur
        temp=actuel
        actuel=ancien
        ancien=actuel
    
    ratio /=float(nb_partie)
    print("%d parties executées en %f secondes"%(nb_partie,time.time()-start))
    print("ratio de victoire: %f" % ratio)
    return (coups,parties,id_gagne)
    
    
#play_game(player,opponent,20,conv,9,True)
play_game(player,opponent,50,conv,9)


# A FAIRE / APPRENDRE LE RESAEAU 