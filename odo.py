#!/usr/bin/python

# Pending
# -------
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

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import tensorflow as tf
from tensorflow import keras
from keras import backend as K

from models.dialogue_system import Chatbot, UnivEncoder
from models.poem_generator import Haiku_Bot, Generator, create_training_model
from models.face_recognition import Face_Recognizer
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

emotion_queue = Queue(-1)
total_faces = Queue(-1)
stop_detecting = Queue(-1)
user_intent = Queue(-1)
output_intent = Queue(-1)
request_poem = Queue(-1)
response_poem = Queue(-1)
USE_MAX = False

def printbot(input_txt):
    input_txt = input_txt.rstrip()
    bot_response = list(input_txt)
    for word in bot_response:
      print(word, end ="", flush=True)
      time.sleep(0.05)
    print('')

def chatbot_process(emotion_queue, total_faces, stop_detecting, chatbot, fileno, user_intent, output_intent, request_poem, response_poem):
   
    users = False
    faces_count = 0
    chat_start = True
    sys.stdin = os.fdopen(fileno)  #open stdin in this process

    print('started chatbot process')
    while stop_detecting.empty() == False:
        returning_user = False
        ask_user_name = True
        try:
            os.mkdir("users")
        except:
            users = True
            #print('users directory already exists')
            
        while total_faces.empty() == False:
            faces_count = total_faces.get()['faces_count']
        while emotion_queue.empty() == False:   
            emotion_queue.get()

        if chat_start:
            chat_start = False
            print('\n')
            print('\n')
            print('\n')
            print('Waiting for a user to join')

        while faces_count > 0:
            if total_faces.empty() == False:
                face_count = total_faces.get()
            if ask_user_name:
                ask_user_name = False
                index = np.random.randint(0,2)
                salutations = ["\nMay I know your good name please\n>>", "\nWhat is your good name?\n>>", "\nCan I have your good name, please?\n>>"]
                user_name = input(salutations[index])
                dir_name = ''.join(e for e in user_name if e.isalnum())
                dir_name = dir_name.capitalize()
                try:
                    os.mkdir("users/"+dir_name)
                except:
                    returning_user = True
                
                img = np.zeros((64, 64, 3), dtype = "uint8") 
                cv2.imwrite(str("users/"+user_name + "/profile_pic.jpg"), img)
                if returning_user:
                    printbot(str('hey '+user_name +' good to see you back'))
                else:
                    printbot(str('hi '+user_name))
                printbot('I am Chris Ziegler. Welcome to my world.')
                emotion = emotion_queue.get()
                if emotion['emotion'] == 'angry':
                    printbot('You seem a bit upset. I think meeting my mysterious friend will cheer you up.')
                elif emotion['emotion'] == 'disgust':
                    printbot('You seem a bit upset. I think meeting my mysterious friend will cheer you up.')
                elif emotion['emotion'] == 'scared':
                    printbot('Do not be scared my friend. I have someone who will cheer you up. Get ready to meet my mysterious friend.')
                elif emotion['emotion'] == 'happy':
                    printbot('It seems to be a great day today. I have surprise for you. Meet my mysterious friend.')
                elif emotion['emotion'] == 'sad':
                    printbot('Do not be sad. Life is hard, but you can fight it. I think meeting my mysterious friend will cheer you up.')
                elif emotion['emotion'] == 'surprised':
                    printbot('I looks like you have got a lot of surprises today. I have asweet surprise for you. Meet my mysterious friend.')
                else:
                    printbot('It seems like everything is fine and boring with you. \nWhat we are about to do next is not boring. Meet my mysterious friend. ')
                
                printbot('Just be careful to not talk like a grown up with him!!')
                time.sleep(3)
                printbot('Ohh, he is here. Type hi and he will respond.')
                #printbot(str('Your age and gender '+ emotion['age_gender']))

            try:
                user_input = input('>>')
                chatbot.chat_history.append(user_input)
                user_intent.put({'intent': user_input, 'story_progress': chatbot.story_progress})
                while output_intent.empty():
                    stopping = False
                intent_match = output_intent.get()
                intent = intent_match['intent']
                #print("intent received",intent)
                if(intent == 'bye'):
                    #l = len(chatbot.intents[intent].responses)
                    #chatbot.story_progress = chatbot.intents[intent].weight
                    #printbot(chatbot.intents[intent].responses[randrange(l)])
                    printbot('It was nice talking to you!!!')
                    if stop_detecting.empty():
                        pass
                    else:
                        stop = stop_detecting.get()
                    break
                elif(intent == 'no_matching_intent'):
                    printbot('I did not get you. But i have a poem for you')
                    request_poem.put({'haiku': intent})
                    while response_poem.empty():
                        stopping = False
                    poem = response_poem.get()
                    printbot(str(poem['line1']))
                    printbot(str(poem['line2']))
                    printbot(str(poem['line3']))
                    
                    if emotion_queue.empty():
                        pass
                    else:
                        emotion = emotion_queue.get()
                        printbot(str('You are '+ emotion['emotion']))
                elif(intent == 'GIVE_POETRY'):
                    request_poem.put({'haiku': intent})
                    while response_poem.empty():
                        stopping = False
                    poem = response_poem.get()
                    printbot(str(poem['line1']))
                    printbot(str(poem['line2']))
                    printbot(str(poem['line3']))
                    
                    if emotion_queue.empty():
                        pass
                    else:
                        emotion = emotion_queue.get()
                        printbot(str('You are '+ emotion['emotion']))
                elif "transition" in intent:
                    next_story = intent.split("_")[2]
                    chatbot.change_story(next_story)
                    l = len(chatbot.intents[intent].responses)
                    if l > 0:
                        chatbot.story_progress = chatbot.intents[intent].weight
                        printbot(chatbot.intents[intent].responses[randrange(l)])
                    else:    
                        request_poem.put({'haiku': intent})
                        while response_poem.empty():
                            stopping = False
                        poem = response_poem.get()
                        printbot(str(poem['line1']))
                        printbot(str(poem['line2']))
                        printbot(str(poem['line3']))
                else:
                    l = len(chatbot.intents[intent].responses)
                    if l > 0:
                        chatbot.story_progress = chatbot.intents[intent].weight
                        printbot(chatbot.intents[intent].responses[randrange(l)])
                    else:    
                        request_poem.put({'haiku': intent})
                        while response_poem.empty():
                            stopping = False
                        poem = response_poem.get()
                        printbot(str(poem['line1']))
                        printbot(str(poem['line2']))
                        printbot(str(poem['line3']))

            except Exception as e:
                print('Exception Generated', str(e))
                request_poem.put({'haiku': intent})
                while response_poem.empty():
                    stopping = False
                poem = response_poem.get()
                printbot(poem['line1'])
                printbot(poem['line2'])
                printbot(poem['line3'])
                if stop_detecting.empty():
                    pass
                else:
                    stop = stop_detecting.get()
                break

    print('Closing Chatbot prompt')

def get_data_from_max():
    print('trying to get data')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
    server_address = ('192.168.43.104', 5501) #put your system ip adderess here
    try:
        sock.bind(server_address)
        print('here')
        data, address = sock.recvfrom(4096)
        print('got data')
        print(data)
        if data:
            printbot(str('MAX:'+data))
            return data
    finally:
        sock.close()

def send_data_to_max(data):
    printbot(str('Bot:'+data))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
    server_address = ('192.168.43.243', 5500) #put your system ip adderess here
    
    try:

        # Send data
        sent = sock.sendto(data.encode(), server_address)

        # Receive response
        #data, server = sock.recvfrom(4096)
        # #print(data)
        # y = json.loads(data)
        # if y['Gender'] == 'man':
        #     print("The client is a handsome " +y['Gender'] + " approximately " + str(y["Age"]) + " years old and seems " + y['Emotion'])
        # else:
        #     print("The client is a georgeous " +y['Gender'] + " approximately " + str(y["Age"]) + " years old and seems " + y['Emotion'])

    finally:
        sock.close()


def max_process(emotion_queue, total_faces, stop_detecting, chatbot, user_intent, output_intent, request_poem, response_poem):
    import socket
    import sys

    users = False
    faces_count = 0
    chat_start = True

    print('started Max Process')
    while stop_detecting.empty() == False:
        returning_user = False
        ask_user_name = True
        try:
            os.mkdir("users")
        except:
            users = True
            #print('users directory already exists')
            
        while total_faces.empty() == False:
            faces_count = total_faces.get()['faces_count']
        while emotion_queue.empty() == False:   
            emotion_queue.get()

        if chat_start:
            chat_start = False
            print('\n')
            print('\n')
            print('\n')
            print('Waiting for input from Max')

        while faces_count > 0:
            if total_faces.empty() == False:
                face_count = total_faces.get()
            if ask_user_name:
                ask_user_name = False
                index = np.random.randint(0,2)
                salutations = ["\nMay I know your good name please", "\nWhat is your good name", "\nCan I have your good name, please"]
                send_data_to_max(salutations[index])
                user_name = get_data_from_max()
                dir_name = ''.join(e for e in user_name if e.isalnum())
                dir_name = dir_name.capitalize()
                try:
                    os.mkdir("users/"+dir_name)
                except:
                    returning_user = True
                
                img = np.zeros((64, 64, 3), dtype = "uint8") 
                cv2.imwrite(str("users/"+user_name + "/profile_pic.jpg"), img)
                if returning_user:
                    send_data_to_max(str('hey '+user_name +' good to see you back'))
                else:
                    send_data_to_max(str('hi'+user_name))
                emotion = emotion_queue.get()
                send_data_to_max(str('You are '+ emotion['emotion']))

            try:
                user_input = get_data_from_max()
                chatbot.chat_history.append(user_input)
                user_intent.put({'intent': user_input})
                while output_intent.empty():
                    stopping = False
                intent_match = output_intent.get()
                intent = intent_match['intent']
                if(intent == 'BYE'):
                    l = len(chatbot.intents[intent]['response'])
                    send_data_to_max(chatbot.intents[intent]['response'][randrange(l)])
                    if stop_detecting.empty():
                        pass
                    else:
                        stop = stop_detecting.get()
                    break
                elif(intent == 'GIVE_POETRY'):
                    request_poem.put({'haiku': intent})
                    while response_poem.empty():
                        stopping = False
                    poem = response_poem.get()
                    send_data_to_max(str(poem['line1']))
                    send_data_to_max(str(poem['line2']))
                    send_data_to_max(str(poem['line3']))
                    
                    if emotion_queue.empty():
                        pass
                    else:
                        emotion = emotion_queue.get()
                        send_data_to_max(str('You are '+ emotion['emotion']))
                else:
                    l = len(chatbot.intents[intent]['response'])
                    if l > 0:
                        send_data_to_max(chatbot.intents[intent]['response'][randrange(l)])
                    else:
                        request_poem.put({'haiku': intent})
                        while response_poem.empty():
                            stopping = False
                        poem = response_poem.get()
                        send_data_to_max(str(poem['line1']))
                        send_data_to_max(str(poem['line2']))
                        send_data_to_max(str(poem['line3']))
            except:
                print('Exception Generated')
                request_poem.put({'haiku': intent})
                while response_poem.empty():
                    stopping = False
                poem = response_poem.get()
                send_data_to_max(poem['line1'])
                send_data_to_max(poem['line2'])
                send_data_to_max(poem['line3'])
                if stop_detecting.empty():
                    pass
                else:
                    stop = stop_detecting.get()
                break


def main():

    warnings.filterwarnings("ignore")
    logging.disable(logging.CRITICAL)

    tf_session = tf.Session()
    K.set_session(tf_session)
    #haiku_bot = Haiku_Bot(tf_session)
    chatbot = Chatbot(tf_session)
    univEncoder = UnivEncoder(tf_session, chatbot.intents)


    output_dir = Path('models/poem_generator')
    # Get the parameters used for creating the model
    latent_dim, n_tokens, max_line_length, tokenizer = joblib.load(output_dir / 'metadata.pkl')
    # Create the new placeholder model
    training_model, lstm, lines, inputs, outputs = create_training_model(latent_dim, n_tokens)
    # Load the specified weights
    training_model.load_weights(output_dir / 'poem_generator_weights.hdf5')
    haiku_bot = Generator(lstm, lines, tf_session, tokenizer, n_tokens, max_line_length)

    face_recognizer = Face_Recognizer(False)
    prev_emotion = None
    print('started camera')
    stop_detecting.put({'stop_detecting': False, 'time': time.time()})
    fn = sys.stdin.fileno() #get original file descriptor
    if USE_MAX:
        processB = Process(target = max_process, args = (emotion_queue, total_faces, stop_detecting, chatbot, user_intent, output_intent, request_poem, response_poem))
        processB.start()
    else:
        processA = Process(target = chatbot_process, args = (emotion_queue, total_faces, stop_detecting, chatbot, fn, user_intent, output_intent, request_poem, response_poem))
        processA.start()

    
    
    while stop_detecting.empty() == False:
        # Detect Emotion
        try:
            face_recognizer.start_detection()
            #print(face_recognizer.current_emotion)
            emotion_detected = face_recognizer.current_emotion
        except:
            print("Detection Error")
        if prev_emotion is None:
            emotion_queue.put({'emotion': face_recognizer.current_emotion, 'time': time.time(), 'age_gender':face_recognizer.age_gender})
        elif emotion_detected != 'neutral':
            emotion_queue.put({'emotion': emotion_detected, 'time': time.time(), 'age_gender':face_recognizer.age_gender})
            prev_emotion = emotion_detected
        else :
            emotion_queue.put({'emotion': prev_emotion, 'time': time.time(), 'age_gender':face_recognizer.age_gender})
        
        total_faces.put({'faces_count': face_recognizer.total_faces, 'time': time.time()})
        #This receives user input and outputs matching intent
        if user_intent.empty() == False:
            try:
                intent_match = user_intent.get()
                intent_user = intent_match['intent']
                story_progress = intent_match['story_progress']
                if intent_user.lower() == 'bye':
                    output_intent.put({'intent': 'bye'})

                intent = univEncoder.match_intent(intent_user,story_progress)
                if "transition" in intent:
                    next_story = intent.split("_")[2]
                    #print("transitioning to :",next_story)
                    chatbot.change_story(next_story)
                    univEncoder.set_intent(chatbot.intents)
                output_intent.put({'intent': intent})
            except:
                request_poem.put({'haiku': 'Generate_Poetry'})
        
        #This receives request for a poem and outputs a hiku
        if request_poem.empty() == False:
            request = request_poem.get()
            poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
            poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
            line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
            line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
            line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
            response_poem.put({'line1':line1, 'line2':line2, 'line3': line3})
    try:
        print('Closing Camera')
        face_recognizer.stop_detection()
    except:
        print('unable to close camera')
    if USE_MAX:
        processB.terminate()
        processB.join()
        print("UDP process terminated")
    else:
        processA.terminate()
        processA.join()
        print("Chatbot process terminated")

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
