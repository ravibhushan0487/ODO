#!/usr/bin/python

# Pending
# -------
# AUTO DETECT IP ADDRESSES OF JETSONS USING MAC ADDRESSES
# Memory leaks are there...Free memory once done
# Implementing user timeout wwhile waiting for input from Max
# import signal
# TIMEOUT = 5 # number of seconds your want for timeout

# def interrupted(signum, frame):
#    "called when read times out"
#    print 'interrupted!'
#signal.signal(signal.SIGALRM, interrupted)

#def input():
#    try:
#            print 'You have 5 seconds to type in your stuff...'
#            foo = raw_input()
#            return foo
#    except:
            # timeout
#            return

# set alarm
# signal.alarm(TIMEOUT)
# s = input()
# disable the alarm after success
# signal.alarm(0)
# print 'You typed', s

# Check whatever user types is a valid word or not



######## Stuffs to do 02/19/2020 ##########
# Tag for Haiku poem generator

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import tensorflow as tf
from tensorflow import keras
from keras import backend as K

from models.dialogue_system.dialogue_system import Chatbot, UnivEncoder
from models.poem_generator.poem_generator import Haiku_Bot, Generator, create_training_model
import cv2
import warnings
import numpy as np
import logging
import sys
import re

from random import randrange

from multiprocessing import Process, Queue
import time

from pathlib import Path
import joblib

import socket
import sys
import json
import argparse
from pythonosc import udp_client
from oscpy.server import OSCThreadServer



parser = argparse.ArgumentParser(description="Parse command line arguments.", 
                           formatter_class=argparse.RawTextHelpFormatter)

# parse the command line: All options are optional. Usage $ python3 odo_chatbot.py --maxip 2.1.0.4 --maxport 7400
parser.add_argument("--chatip", type=str, default="2.1.0.10", help="The ip of chatbot.")
parser.add_argument("--chatport", type=int, default=7403, help="The port on which chat server is listening to osc connection.")
parser.add_argument("--maxip", type=str, default="2.1.0.227", help="The ip on which max server is listening.")
parser.add_argument("--maxport", type=int, default=7400, help="The port on which max server is listening.")
parser.add_argument("--camip1", type=str, default="2.1.0.11", help="The ip on which camera 1 server is listening.")
parser.add_argument("--camport1", type=int, default=7401, help="The port on which camera 1 server is listening.")
parser.add_argument("--camip2", type=str, default="2.1.0.12", help="The ip on which camera 2 server is listening.")
parser.add_argument("--camport2", type=int, default=7402, help="The port on which camera 2 server is listening.")

opt, argv = parser.parse_known_args()
try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

#MAX Tags for chatbot server
chatbot = "/chat"
command = "/command"
kill    = "/kill" #Kill everything

# Max Tags for chatbot client
chat_tag = "/chat"
move_tag = "/move_lights"

#Chat response speed in secs
chat_speed = 5

## kk code start##
chat_speed_slow = 10

# Total number of players
players = 5
players_names = []
## kk code start##

emotion_queue = Queue(-1)
total_faces = Queue(-1)

# Max Commands:
# Kill everything: /kill kill
# Kill everything: /command kill 
# Start chatbot: /command chat
# Pause chatbot: /command pause
# Start New Session: /command new
# Say Poem: /command poem
# Detect Emotion: /command emotion
# Comment on something interesting about audinece: /command comment
# User chat. Please note to keep user chat in quotes: /chat "what user said"

max_response = Queue(-1)

output_intent = Queue(-1)
request_poem = Queue(-1)
response_poem = Queue(-1)
USE_MAX = False
user_name = None
callback = False
global pauser
pauser = False

def max_callback(values):
    #Do something. Here we are just printing
    global output_intent
    output_intent.put({'name': values})
    print("got values: {}".format(values))

def printbot(input_txt):
    #tag "/ame_chatbot" #sample tag
    #message = "abcd26872    09u7iuogh" #sample message
    ip = "2.1.0.2" #sample ip
    port = 7400 #sample port
    try:
        client = udp_client.SimpleUDPClient(ip, port)
        client.send_message(input_txt, message)
    finally:
        return True

# NOt being used
# def chatbot_process(emotion_queue, total_faces, stop_detecting, chatbot, fileno, user_intent, output_intent, request_poem, response_poem):
#     users = False
#     faces_count = 0
#     chat_start = True
#     sys.stdin = os.fdopen(fileno)  #open stdin in this process

#     print('started chatbot process')
#     while stop_detecting.empty() == False:
#         returning_user = False
#         ask_user_name = True
#         try:
#             os.mkdir("users")
#         except:
#             users = True
#             #print('users directory already exists')
            
#         while total_faces.empty() == False:
#             faces_count = total_faces.get()['faces_count']
#         while emotion_queue.empty() == False:   
#             emotion_queue.get()

#         if chat_start:
#             chat_start = False
#             print('\n')
#             print('\n')
#             print('\n')
#             print('Waiting for a user to join')

#         while faces_count > 0:
#             #if total_faces.empty() == False:
#                 #faces_count = total_faces.get()
#             if ask_user_name:
#                 ask_user_name = False
#                 #index = np.random.randint(0,2)
#                 salutations = printbot(str("\nHello\nMy name is Odo.\n What is your name?\n>>"));

#                 while output_intent.empty():
#                     osc = OSCThreadServer()
#                     sock = osc.listen(address="2.1.0.10", port=7400, default=True)
#                     #Here the function "callback_sample_commmands_on_the_basis_of_tag" is called on the basis of the tag's value
#                     osc.bind("chatbot", callback_sample_commmands_on_the_basis_of_tag)
#                     osc.stop()

#                 intent_match = output_intent.get()
#                 user_name = intent_match['name']
#                 dir_name = ''.join(e for e in user_name if e.isalnum())
#                 dir_name = dir_name.capitalize()
#                 try:
#                     os.mkdir("users/"+dir_name)
#                 except:
#                     returning_user = True
                
#                 img = np.zeros((64, 64, 3), dtype = "uint8") 
#                 cv2.imwrite(str("users/"+user_name + "/profile_pic.jpg"), img)
#                 #if returning_user:
#                 printbot(str('Hi '+user_name +'.\nWhere do you come from?\n'))
#                 #else:
#                 #    printbot(str('hi '+user_name))
#                 #user_location = input(">>")
#                 printbot('I am Chris Ziegler. Welcome to my world.')
#                 emotion = emotion_queue.get()
#                 printbot(str('Nice to meet you'+user_name))
#                 printbot('I am from very far away.')
#                 printbot('I live here.')
#                 printbot('Here on stage.')
#                 printbot('I cannot leave the stage.')
#                 printbot('This is my body.')
#                 printbot('Do you see me?')
#                 #TODO:pass signal to Max to lift lights up and down.

#             try:
#                 user_input = input('>>')
#                 chatbot.chat_history.append(user_input)
#                 user_intent.put({'intent': user_input, 'story_progress': chatbot.story_progress})
#                 while output_intent.empty():
#                     stopping = False
#                 intent_match = output_intent.get()
#                 intent = intent_match['intent']
#                 #print("intent received",intent)
#                 if(intent == 'bye'):
#                     #l = len(chatbot.intents[intent].responses)
#                     #chatbot.story_progress = chatbot.intents[intent].weight
#                     #printbot(chatbot.intents[intent].responses[randrange(l)])
#                     printbot('It was nice talking to you!!!')
#                     if stop_detecting.empty():
#                         pass
#                     else:
#                         stop = stop_detecting.get()
#                     break
#                 elif(intent == 'no_matching_intent'):
#                     printbot('I did not get you. But i have a poem for you')
#                     request_poem.put({'haiku': intent})
#                     while response_poem.empty():
#                         stopping = False
#                     poem = response_poem.get()
#                     printbot(str(poem['line1']))
#                     printbot(str(poem['line2']))
#                     printbot(str(poem['line3']))
                    
#                     if emotion_queue.empty():
#                         pass
#                     else:
#                         emotion = emotion_queue.get()
#                         printbot(str('You are '+ emotion['emotion']))
#                 elif(intent == 'GIVE_POETRY'):
#                     request_poem.put({'haiku': intent})
#                     while response_poem.empty():
#                         stopping = False
#                     poem = response_poem.get()
#                     printbot(str(poem['line1']))
#                     printbot(str(poem['line2']))
#                     printbot(str(poem['line3']))
                    
#                     if emotion_queue.empty():
#                         pass
#                     else:
#                         emotion = emotion_queue.get()
#                         printbot(str('You are '+ emotion['emotion']))
#                 elif "transition" in intent:
#                     next_story = intent.split("_")[2]
#                     chatbot.change_story(next_story)
#                     l = len(chatbot.intents[intent].responses)
#                     if l > 0:
#                         chatbot.story_progress = chatbot.intents[intent].weight
#                         printbot(chatbot.intents[intent].responses[randrange(l)])
#                     else:    
#                         request_poem.put({'haiku': intent})
#                         while response_poem.empty():
#                             stopping = False
#                         poem = response_poem.get()
#                         printbot(str(poem['line1']))
#                         printbot(str(poem['line2']))
#                         printbot(str(poem['line3']))
#                 else:
#                     l = len(chatbot.intents[intent].responses)
#                     if l > 0:
#                         chatbot.story_progress = chatbot.intents[intent].weight
#                         printbot(chatbot.intents[intent].responses[randrange(l)])
#                     else:    
#                         request_poem.put({'haiku': intent})
#                         while response_poem.empty():
#                             stopping = False
#                         poem = response_poem.get()
#                         printbot(str(poem['line1']))
#                         printbot(str(poem['line2']))
#                         printbot(str(poem['line3']))

#             except Exception as e:
#                 print('Exception Generated', str(e))
#                 request_poem.put({'haiku': intent})
#                 while response_poem.empty():
#                     stopping = False
#                 poem = response_poem.get()
#                 printbot(poem['line1'])
#                 printbot(poem['line2'])
#                 printbot(poem['line3'])
#                 if stop_detecting.empty():
#                     pass
#                 else:
#                     stop = stop_detecting.get()
#                 break

#     print('Closing Chatbot prompt')

def chat_callback(values):
    if not pauser:
        print(pauser)
        global max_response
        values = values.decode("utf-8").strip("'")
        print("User Chat:"+values)
        max_response.put({'intent': values})

def command_callback(values):
    global max_response
    values = values.decode("utf-8").strip("'")
    print("Max Command:"+values)
    max_response.put({'command': values})

def kill_switch(values):
    global max_response
    values = values.decode("utf-8").strip("'")
    print("Kill Switch command:"+values)
    max_response.put({'kill': values})

def stop_resume_operation(values):
    print(values)
    global pauser
    if values.decode() == "True":
        print("here")
        pauser = True
        print(pauser)
    elif values.decode() == "False":
        pauser = False
def history(text):
  with open("history.txt", "a") as file:
    file.write(text + '\n')
  file.close()

def main():
    global pauser
    pauser = False
    warnings.filterwarnings("ignore")
    logging.disable(logging.CRITICAL)

    tf_session = tf.Session()
    K.set_session(tf_session)
    

    #Connection Initialization
    print("Creating Connections")
    #Connecting to max
    #Max client: Receive from Max
    try:
        max_client = udp_client.SimpleUDPClient(opt.maxip, opt.maxport)
        print("UDP Client connection to Max established")
    except:
        print("UDP Client connection to Max failed. Will not be able to send from Max.")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
     

    #Max server: Listen to Max
    try:
        osc = OSCThreadServer()
        try:
            max_server = osc.listen(address=opt.chatip, port=opt.chatport, default=True)
            print("OSC Server initialized to listen to Max")
            osc.bind(b"/chat", chat_callback)
            osc.bind(b"/command", command_callback)
            osc.bind(b"/kill", kill_switch)
            ##########sddrd to test Vishal#########################
            osc.bind(b"/stop", stop_resume_operation)

        except:
            print("Tag is not in exceptable format")
        ##########sddrd to test Vishal#########################
    except:
        print("OSC Server initialization failed. Will not be able to listen to Max")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))



    #################  Connecting to Camera 1  #####################

    try:
        cam1_socket = socket.socket()
        cam1_socket.connect((opt.camip1, opt.camport1))
        print("Connection to Camera 1 established")
    except:
        print("Unable to connect to Camera 1")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            

    ############### Connecting to Camera 2 #######################

    try:
        cam2_socket = socket.socket()
        cam2_socket.connect((opt.camip2, opt.camport2))
        print("Connection to Camera 2 established")
    except:
        print("Unable to connect to Camera 2")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))



    ########### Chatbot Generator #####################

    try:
        chatbot = Chatbot(tf_session)
        univEncoder = UnivEncoder(tf_session, chatbot.intents)
        print("Initialized chatbot dialogue system")
    except:
        print("Unable to initialize chatbot dialogue system. Exiting.")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
        exit()



    #################### Code for Haiku Poem Generation #######################
    # try:
    #     haiku_bot = Haiku_Bot(tf_session)
    #     output_dir = Path('models/poem_generator/trained_models')
    #     Get the parameters used for creating the model
    #     latent_dim, n_tokens, max_line_length, tokenizer = joblib.load(output_dir / 'metadata.pkl')
    #     # Create the new placeholder model
    #     training_model, lstm, lines, inputs, outputs = create_training_model(latent_dim, n_tokens)
    #     # Load the specified weights
    #     training_model.load_weights(output_dir / 'poem_generator_weights.hdf5')
    #     haiku_bot = Generator(lstm, lines, tf_session, tokenizer, n_tokens, max_line_length)
    #     print("Initialized chatbot poem generator.")
    # except:
    #     print("Unable to initialize chatbot poem generator.")
    #     print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
    #                                      sys.exc_info()[1],
    #                                      sys.exc_info()[2].tb_lineno))

    #Waiting for max command to start chatbot
    command = "stopped"
    # while command != "chat":
    #     while max_response.empty():
    #         stopped = True
    #     max_request = max_response.get()
    #     command = max_request['command']

    print(time.time())
    print("Starting chatbot for the first time")
    
    while command != "kill":

        users = False
        faces_count = 0
        chat_start = True
        returning_user = False
        ask_user_name = True

        while command != "pause" and command != "new" and command !="kill":

            try:
                if ask_user_name:
                    ask_user_name = False
                    try:
                        os.mkdir("users")
                    except:
                        users = True

                    ## Creating a txt file and storing all the sentence ##

                    global file
                    ## kk code to open and close history file start ## 
                    file = open("history.txt", "w+")
                    file.close()
                    ## kk code to open and close history file end ##

                    #TODO: There is no kill switch check or command check. Need to implement it.
                    first_sentence = "Hello world!"
                    max_client.send_message(chat_tag, first_sentence)
                    history(first_sentence)
                    # time.sleep(chat_speed_slow)

                    while max_response.empty():
                        waiting_for_user = True
                    user_response = max_response.get()
                    history(user_response['intent'])
                    
                    
                    ## kk code start##
                    chat = "Hello! My name is Odo. I see {0} players. What are your names?".format(players)
                    max_client.send_message(chat_tag, chat)
                    while max_response.empty():
                        waiting_for_user = True

                    history(chat)
                    try:
                        while max_response.empty():
                            waiting_for_user = True

                        for __ in range(players):
                            user_response = max_response.get()
                            print(user_response)
                    #TODO: We might need to validate the names
                            players_names.append(user_response['intent'])
                            history(user_response['intent'])
                    except excep as e:
                        print(e)


                    ######### Making directory for each user, commented for now start- kkk ##########
                    # dir_name = ''.join(e for e in user_name if e.isalnum())
                    # dir_name = dir_name.capitalize()
                    # try:
                    #     os.mkdir("users/"+dir_name)
                    # except:
                    #     returning_user = True
                    ######### Making directory for each user, commented for now end- kkk ##########

                    ## Greeting all the users ##
                    for name in players_names:
                        print("inside for loop")
                        chat = "Hi " + name + ", nice to meet you"
                        max_client.send_message(chat_tag, chat)
                        history(chat)
                        time.sleep(chat_speed)

                    while max_response.empty():
                       waiting_for_user = True

                    chat = "Where do you come from?"
                    max_client.send_message(chat_tag, chat)
                    history(chat)
                    while max_response.empty():
                       waiting_for_user = True
                    
                    user_response = max_response.get()
                    #TODO: We might need to validate the cities
                    user_location = user_response['intent']
                    history(user_location)

                    #Monologue
                    # chat = "Nice to meet you. I am from very far away. I live here. Here on stage. I can’t leave the stage. This is my body. Do you see me?"

                    # max_client.send_message(chat_tag, chat)
                    # time.sleep(chat_speed)

                    ######### Get user emotion, commenting for now start - kkk ##############
                    try:
                        camera_message = "send_emotion"
                        cam1_socket.send(camera_message.encode('utf-8'))
                        emotion1 = cam1_socket.recv(1024).decode('utf-8')
                        emotion1 = json.loads(emotion1)
                        user_emotion1 = emotion1['emotion']
                        total_faces1 = emotion1['total_faces']
                        time1 = emotion1['time']

                        cam2_socket.send(camera_message.encode('utf-8'))
                        emotion2 = cam2_socket.recv(1024).decode('utf-8')
                        emotion2 = json.loads(emotion2)
                        user_emotion2 = emotion2['emotion']
                        total_faces2 = emotion2['total_faces']
                        time2 = emotion2['time']
                    except:
                        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                             sys.exc_info()[1],
                                             sys.exc_info()[2].tb_lineno))



                    # chat = 'It seems you are ' + user_emotion1
                    # max_client.send_message(chat_tag, chat)
                    # time.sleep(chat_speed)

                    ######### Get user emotion, commenting for now end - kkk ##############


                    # chat = 'Nice to meet you ' + user_name
                    # max_client.send_message(chat_tag, chat)
                    # history(chat)
                    # time.sleep(chat_speed)

                    chat = 'I am from very far away.'
                    max_client.send_message(chat_tag, chat)
                    history(chat)
                    time.sleep(chat_speed)

                    chat = 'I live here.'
                    max_client.send_message(chat_tag, chat)
                    history(chat)
                    time.sleep(chat_speed)

                    chat = 'Here on the stage'
                    max_client.send_message(chat_tag, chat)
                    history(chat)
                    time.sleep(chat_speed)

                    chat = 'I cannot leave the stage. This is my body.'
                    max_client.send_message(chat_tag, chat)
                    history(chat)
                    time.sleep(chat_speed)

                    chat = 'Do you see me?'
                    max_client.send_message(chat_tag, chat)
                    history(chat)
                    time.sleep(chat_speed)

                #TODO: Add kill switch check and command check
                try:
                    while max_response.empty():
                        waiting_for_user = True
                    
                    user_response = max_response.get()
                    history(user_response['intent'])
                    user_chat = user_response['intent']
                    intent = univEncoder.match_intent(user_chat,chatbot.story_progress)
                    if(intent == 'bye'):
                        chat = 'It was nice talking to you.'
                        max_client.send_message(chat_tag, chat)
                        history(chat)
                        command = 'kill'
                        file.close()
                    elif(intent == 'no_matching_intent'):
                        # chat = 'I am sorry. I did not get you. Try saying something else.'
                        chat = "Sorry I didnt get you, try saying something else"
                        # chat = univEncoder.chat_eliza(user_chat)
                        # print("Response from Eliza \n {0}".format(chat))
                        max_client.send_message(chat_tag, chat)
                        history(chat)

                        ##### Haiku poems, Disabling for now start - kkk ##### 
                        # poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                        # poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                        # line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
                        # line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
                        # line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
                        # chat = line1 + line2 + line3
                        # max_client.send_message(chat_tag, chat)


                    # elif(intent == 'GIVE_POETRY'):
                    #     poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                    #     poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                    #     line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
                    #     line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
                    #     line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
                    #     chat = line1 + line2 + line3
                    #     max_client.send_message(chat_tag, chat)


                    ##### Haiku poems, Disabling for now end - kkk #####



                    elif "transition" in intent:
                        next_story = intent.split("_")[2]
                        chatbot.change_story(next_story)
                        univEncoder.set_intent(chatbot.intents)
                        l = len(chatbot.intents[intent].responses)
                        if l > 0:
                            chatbot.story_progress = chatbot.intents[intent].weight
                            chat = chatbot.intents[intent].responses[randrange(l)]
                            max_client.send_message(chat_tag, chat)
                            history(chat)


                        ##### Haiku poems, Disabling for now start - kkk #####
                        # else:    
                        #     poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                        #     poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                        #     line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
                        #     line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
                        #     line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
                        #     chat = line1 + line2 + line3
                        #     max_client.send_message(chat_tag, chat)
                        ##### Haiku poems, Disabling for now end - kkk #####


                    else:
                        l = len(chatbot.intents[intent].responses)
                        if l > 0:
                            chatbot.story_progress = chatbot.intents[intent].weight
                            chat = chatbot.intents[intent].responses[randrange(l)]
                            max_client.send_message(chat_tag, chat)
                            history(chat)

                        ##### Haiku poems, Disabling for now start - kkk #####
                        # else:    
                        #     poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                        #     poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                        #     line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
                        #     line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
                        #     line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
                        #     chat = line1 + line2 + line3
                        #     max_client.send_message(chat_tag, chat)
                        ##### Haiku poems, Disabling for now end - kkk #####

                except:
                    print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                             sys.exc_info()[1],
                                             sys.exc_info()[2].tb_lineno))
                    chat = 'I am sorry. I did not get you. Try saying something else.'
                    max_client.send_message(chat_tag, chat)
                    history(chat)

                ##### Haiku poems, Disabling for now start - kkk #####
                # poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                # poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                # line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
                # line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
                # line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
                # chat = line1 + line2 + line3
                # max_client.send_message(chat_tag, chat)
                ##### Haiku poems, Disabling for now end - kkk #####

            except KeyboardInterrupt:
                print("Closing all active connections")
                command = "kill"

                  
    try:
        camera_message = "stop_camera"
        try:
            cam1_socket.send(camera_message.encode('utf-8'))
            cam1_socket.close()
            print("Connection to Camera 1 closed")
        except:
            print("unable to close camera 1")

        try:
            cam2_socket.send(camera_message.encode('utf-8'))
            cam2_socket.close()
            print("Connection to Camera 2 closed")
        except:
            print("unable to close camera 2")

        try:
            osc.stop()
            print("Connection to Max closed")
        except:
            print("unable to close connectoin to Max")
            
    except:
        print('unable to close connections')

if __name__== "__main__":
  main()
  print('Exiting the application')
  exit()

#### Commented code for other code options #################

### Haiku Generator Options ################################
#for i in range(3):
#  poem = generator.generate_haiku([5, 7, 7, 5], temperature=.3, first_char='summer')
#  print(poem[0])
#  print(poem[1])
#  print(poem[2])
#  print("\n")
