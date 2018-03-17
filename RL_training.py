#import keras
import go 
import CNN_policy
import RL_player as pl
import go
import time
import features as ft
#import visualisation as vis
from keras.optimizers import SGD
import numpy as np
from Tools import Tools
import datetime




def play_game(player,opponent,nb_partie,preprocessor,size=9,verbose=False):
    
    #init
    etat = [go.GameState(size) for _ in range(nb_partie)] #liste des parties actuelle
    coups=[[] for _ in range(nb_partie)]  #liste des coups joues
    parties=[[] for _ in range(nb_partie)] # liste des etats du jeu
    id_gagne=[] #liste des indices des parties gagnees
    id_aband=[]#liste des parties non finies
    ratio=0

    # deroulement
    start=time.time()
    s1=0 #tps premiere partie
    
    # on joue le premier coup de chaque partie
    for i in range(nb_partie):
        coup=opponent.get_move(etat[i]) 
        coups[i].append(Tools.one_hot_action(coup,19).flatten())
        etat[i].do_move(coup)
        parties[i].append(conv.state_to_tensor(etat[i]))

    #on joue tout les coups
    actuel=player
    ancien=opponent
    fin=0 # pour arreter la boucle
    tour=1 #pour verbose
    while(fin<nb_partie): 
        for i in range(nb_partie):

                if(etat[i].is_end_of_game==False): # verifie que la partie n'est pas fini
                    coup = actuel.get_move(etat[i]) # on recupere le coup joue 
    
                    if etat[i].is_legal(coup)!=True:
                        #print("on entrre")
                        etat[i].is_end_of_game=True # met fin a la partie -> qui a gagne?
                        id_aband.append(i)
                        fin+=1
                        
                    else:   
                        etat[i].do_move(coup) #on le joue
			# a ajouter et tester que les parties de player ?
			if actuel == player: 
                        	coups[i].append(Tools.one_hot_action(coup,19).flatten()) # on le sauvegarde
                        	parties[i].append(conv.state_to_tensor(etat[i])) #on sauvegarde l'etat du jeu

                    
                    if(etat[i].is_end_of_game==True ): 
                        fin+=1  # pour arreter la boucle
                        if(etat[i].get_winner()==-1): # -1 pour blanc
                            id_gagne.append(i)
                            ratio+=1
                    
                    if (i==1 & verbose==True):
                        tour+=1
                        print
                        print("Coup numero %i" %tour)
                        vis.vis_gs(etat[i])
                                                    
                    if (fin==1&s1==0&verbose==True):
                        print("1ere partie finie en %f secondes" % (time.time()-start))
                        s1=1
        		#vis_gs(parties[1])
        
    
        #on change de joueur
        temp=actuel
        actuel=ancien
        ancien=temp
    
     
    
    if(len(id_aband)!=nb_partie):
#        ratio /=float(nb_partie-len(id_aband))
	ratio/=float(nb_partie)

    else:
	ratio/=float(nb_partie)


    print("%d parties executees en %f secondes"%(nb_partie,time.time()-start))
    print("ratio de victoire: %f" % ratio)
   
    if(len(id_aband)!=0):
        print("Nombre de partie abandonnee: %d" % len(id_aband))

    return (coups,parties,id_gagne)
    
    



def R_learning(coups,parties,id_gagnes,policy,player):
    #print ('-'*15, 'Apprentissage', '-'*15)
    nb_coup_total=0
    for i in range(len(parties)):
        #print ('-'*15, 'Parties %d' %i, '-'*15)
        coups[i]=np.array(coups[i])
        parties[i]=np.array(parties[i])
        parties[i]=np.concatenate(parties[i], axis=0)
        
        nb_coup_total+=len(coups[i])
        if i in id_gagnes:
        	optimizer.lr = np.absolute(optimizer.lr)
        else :
            optimizer.lr = np.absolute(optimizer.lr)*-1
        #player.policy.model.train_on_batch(np.concatenate(parties[i], axis=0),np.concatenate(coups[i],axis=0))
        loss=player.policy.model.train_on_batch(parties[i],coups[i])
        #print("loss =",loss)
        #player.policy.model.train_on_batch(np.concatenate(parties[i], axis=0),coups[i])
    date = datetime.datetime.now()   
    filepath = ("%s/model_%s_%s_%sh%s.hdf5" %("RL",date.day,date.month,date.hour, date.minute))
    tfilepath = ("%s/model_%s_%s_%sh%s.txt" %("RL",date.day,date.month,date.hour, date.minute))
    player.policy.model.save(filepath)
    print ( '%d coups sur  %d parties appris' %(nb_coup_total,len(parties)))
    Tools.text_file(tfilepath,player.policy.model.model, nb_coup_total,len(parties), date)


    return filepath 

def play_learn(player,opponent,nb_partie,preprocessor,epoch,policy,size=19,verbose=False):
	date = datetime.datetime.now()   
	
	print("apprentissage debute a _%s_%s_%sh%s" %(date.day,date.month,date.hour, date.minute))          

	i=1
	print ('-'*15, 'Epoch %d' %i, '-'*15)

	(coups,parties,id_gagne)=play_game(player,opponent,nb_partie,preprocessor,19,False)
	new_model=R_learning(coups,parties,id_gagne,policy,player)
	policy_pl=CNN_policy.CNN()
	policy_pl.load (new_model)
	policy_pl.model.compile(loss='categorical_crossentropy',optimizer=optimizer)
	del player
	player=pl.Player_pl(policy_pl,preprocessor) 
	
	while i<epoch+1	:
		i+=1
		print ('-'*15, 'Epoch %d' %i, '-'*15)
		(coups,parties,id_gagne)=play_game(player,opponent,nb_partie,preprocessor,19,False)
		new_model=R_learning(coups,parties,id_gagne,policy_pl,player)	
		del policy_pl
		policy_pl=CNN_policy.CNN()
		policy_pl.load (new_model)
		policy_pl.model.compile(loss='categorical_crossentropy',optimizer=optimizer)
		del player
		player=pl.Player_pl(policy_pl,preprocessor)   
	date = datetime.datetime.now()   

	print("apprentissage termine a _%s_%s_%sh%s" %(date.day,date.month,date.hour, date.minute))          
            
#initialisation
FEATURES = ["stone_color_feature", "ones", "turns_since_move", "liberties", "capture_size",
                    "atari_size",  "sensibleness", "zeros"]
conv=ft.Preprocess(FEATURES)
filename="model_26_2_19h53.hdf5"


player_rd = pl.Player_rd()
opponent_rd =pl.Player_rd()
learning_rate=0.001
optimizer = SGD(lr=learning_rate)


            
print("joueur random contre random")
play_game(player_rd,opponent_rd,1,conv,19,False)

policy_pl=CNN_policy.CNN()
policy_pl.load (filename) 
policy_pl.model.compile(loss='categorical_crossentropy',optimizer=optimizer)
player=pl.Player_pl(policy_pl,conv) 

nb_partie=100
preprocessor=ft.Preprocess(FEATURES)
epoch=10
policy=policy_pl
play_learn(player,opponent_rd ,nb_partie,preprocessor,epoch,policy,size=19,verbose=False)




