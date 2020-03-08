# Pending
# Stories based on gender, age
# BLack magic intensity shuttle...6
# Long Poetry
# Manual command to start a different topic. Or 
# Create 60 short stories. Total 20 stories and each story will have a happy, a neutral/sad and a curious version
# Curious version will be used as a filler story to divert to a happy or sad story if user is not responding. or to change topic..
# Each story is an intent type. This is becuase this will help UnivEncoder to match similarity to one story intent only.
# Each story will have an opening intent
# Each story intent will have a timeout intent, which will get triggered when timeout happens.
# Create a structure or bag of keywords which will suggest that we need to switch stories now as 
# conversation is moving in a different direction. Like a key of words for a story and a probability indicator indicating where
# current conversation is going. Over the conversation as probability grows, we will shift story.
# need to knwo if a particular utterance has already been said. 
# Choose a different utterance based on the universal encoder output. next on universal encoder list.
# A way to understand the progress of the story
# restart chatbot when user goes away from camera
# what is the next intent if current intent is already satisfied? or which sentence(or index) has bot spoken of. So that it is not repetive.

import pandas as pd
import numpy as np
import os
import math
import json
import tensorflow as tf
import tensorflow_hub as hub
from random import randrange
import random
import string

## kk code for eliza start ##
#from nltk.chat.util import Chat
#from nltk.chat.eliza import pairs
## kk code for eliza stop ##

default_intents = ['yes', 'no', 'maybe', 'okay']
class Story:
    def __init__(self, name, intents = {}, completion_status = 0, tone = "happy", starting_intent = {}, script = {}, keywords = [], timeout_intent = {}, utterances_said = [], transition_intent = {}):

        self.id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(15)]) 
        self.name = name
        self.intents = intents

        self.completion_status = completion_status
        self.tone = tone
        self.keywords = keywords
        self.starting_intent = starting_intent
        self.script_intent = script
        self.timeout_intent = timeout_intent
        self.transition_intent = transition_intent
        self.utterances_said = utterances_said

        # What if the user wants to again start the story??? You should have an intent that this is what you can say about story and
        # now you shold tell him some other story...

        # transition intent will giv hint about two three different stories....
        # there will be two three transition intents...

    def create_timeout_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.timeout_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def create_transition_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.transition_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def create_starting_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.starting_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def create_script_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.script_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def add_intent(self, intent_name, weight, utterances, response):                   # Function to add intent if not already existing

        if not self.check_intent_name(intent_name):
            self.intents[intent_name] = Intent(intent_name, weight, utterances, response)
        else:
            print("Intent {0} already exists".format(intent_name))

    def check_intent_name(self, intent_name):            # Checking if an intent already exists
        if intent_name in self.intents.keys():
            return True

        else:
            return False

    def get_intent(self, utterance):
        for k, v in self.intents.items():
            if utterance in v.utterances:
                return k
        print("no intent matched")

######### Intents #########
class Intent:
    def __init__(self, name, weight, utterances = [], responses = []):

        self.name = name
        self.utterances = utterances
        self.responses = responses
        self.weight = weight

    def create_utterance(self, utterances):

        if type(utterances) == list:
            for utterance in utterances:
                self.utterances.append(utterance)

        else:
            self.utterances.append(utterances)

    def add_utterance(self, utterance):
        if not self.check_utterance(utterance):
            self.utterances.append(utterance)
        else:
            print("Utterance {0} already exists".format(utterance))

    def check_utterance(self, utterance):
        if utterance in self.utterances:                    # Checking the utterance in the bag of utterances. If it exists in any intent, it will give an error
            return True
        else:
            return False

    def remove_utterance(self, utterances):           # removes utterances
        if type(utterances) == list:
            for utterance in utterances:
                try:
                    self.utterances.remove(utterance)
                except ValueError:
                    print("'{0}' utterance doesnt exists".format(utterance)) # throws exception if utterance does not exists

        else:
            try:
                self.utterances.remove(utterances)
            except ValueError:
                print("'{0}' utterance doesnt exists".format(utterances))


    def create_response(self, responses):

        if type(responses) == list:
            for response in responses:
                self.responses.append(response)

        else:
            self.responses.append(responses)

    def add_response(self, response,r):
        if not self.check_response(r):
            self.responses.append(r)
        else:
            print("Response {0} already exists".format(r))

    def check_response(self, response):
        if response in self.responses:                    # Checking the response in responses. If it exists in any intent, it will give an error
            return True
        else:
            return False

    def remove_response(self, responses):           # removes responses
        if type(responses) == list:
            for response in responses:
                try:
                    self.responses.remove(response)
                except ValueError:
                    print("'{0}' response doesnt exists".format(response)) # throws exception if response does not exists

        else:
            try:
                self.responses.remove(response)
            except ValueError:
                print("'{0}' response doesnt exists".format(responses))


class Chatbot:

    

    def __init__(self, tf_session, intents = {}, stories = {}, current_story = None, chat_history = [], story_progress = 0):
        
        self.intents = intents
        self.chat_history = chat_history
        self.stories = stories
        self.current_story = current_story
        self.story_progress = story_progress
        self.session = tf_session
        self.create_character()

    ######### Storing/Retrieving data ############
    def store_data(self):
        with open("sample.json", "w") as file:
            json.dump(self.intents, file)

    def retrieve_data(self):
        with open("sample.json", "r") as file:
            self.intents.update(json.load(file))
   
    def add_story(self, name, story):
        self.stories[name] = story

    def get_story(self, name):
        return self.stories[name]

    #Will shift these stories to csv file once time permits
    def add_story_see_me(self):
        name = 'see_me'
        story = Story(name,{})
        story.create_starting_intent('player_sees_odo',1,
            default_intents,
            ['Can you do the same?']
            )
        story.create_script_intent('lift_arms', 3,
            ['okay','no','where','what','?','how'],
            ['Lift your arms, would you do this?']
            )
        story.create_script_intent('lift_arms_phone', 4,
            default_intents,
            ['Lift your arm with the ODO-PHONE. See what I can see from you...']
            )
        story.create_script_intent('connected', 6,
            default_intents,
            ['We are connected with the phone, you see?']
            )
        story.create_script_intent('welcome', 8,
            default_intents,
            ['Hi everybody. Welcome to my planet...']
            )
        story.create_script_intent('about_me', 9,
            default_intents,
            ['I would like to tell you something about me. Are you interested?']
            )
        story.create_script_intent('about_me_2', 10, 
            default_intents,
            ['Listen. My name is Odo, you know. I do not live on a planet like you, I am the planet. You get me?']
            )
        story.create_script_intent('explain', 13,
            ['no', 'okay', 'yes', 'yeah', 'whatever', 'go on', 'not at all', 'nah'],
            ['Let me explain. I am the planet ODO. Imagine me as a cloud. Inside the cloud there is light and darkness, coldness and heat, desserts and mountains, crowds and loneliness, all and nothing... Do you have any questions?']
            )
        story.create_script_intent('my_body', 20,
            default_intents + ['i do not understand', 'what', 'kinda', 'somewhat', 'i think i do'],
            ['This is my body. I live here on stage. Do not think of me as a light bulb. I do not need to be replaced, even though living here can be stressful at times. Okay, from time to time I have to retire for not to burn over. Where do you live? Do you live in a cloud or in a house?']
            )
        story.create_script_intent('house_transition_cave', 30,
            ['mountain', 'cave', 'forest', 'jungle'],
            ['You stay amongst nature!!']
            )
        story.create_script_intent('house_transition_apartment', 30,
            ['tempe', 'city', 'street', 'planet', 'house'],
            ['You stay in crowded places']
            )
        story.create_script_intent('exit', 100,
            ['bye', 'see you', 'tada', 'chao'],
            ['nice talking to you, bye!']
            )
        # story.create_script_intent('exit', 40,
        #     ['tempe', 'city', 'street', 'planet', 'house'],
        #     ['You stay in crowded places']
        #     )
        # story.create_script_intent('rose_left', 30,
        #     ["why did you leave her", "you left her alone","you should not have left ehr alone"],
        #     ["My planet is very small. I live alone there. I used to water my rose everyday. I know, I should not have left her alone.\nOf the million stars in the sky, she was the single rose I knew and I was the little Prince she talked to. Why do rose have thorns?"]
        #     )
        # story.create_script_intent('rose_thorns', 40,
        #     ["thorn","thorns","rose have thorns to protect them","i do not know","how can I know","i have never seen a thorn on rose","to protect them","fight against animals","protect them from those who want to eat them"],
        #     ["My rose showed me her four thorns. She said it will protect her from claws of tiger. \nBut they are so weak. I think she told me this to let me go. She does not want me to see her tears. \nI should not have beleived her. I think I should not have left. Do you think I was right to leave?"]
        #     )

        # story.create_script_intent('rose_leave', 70,
        #     ["tiger","no","yes","why did not you stop","where were you going","why did you leaver her","why did you leave", "You should not have left","how did you leave","you should not have left your rose alone"],
        #     ["I should have stayed. But,I wanted to see the stars. So I hooked onto one of the migratory birds. \nI have seen many planets. One planet had a businessman who was very serious like you. One had an old king who ruled over stars. \nOne had a pole lighter. Would you like to know what I found out about these people?"]
        #     )
        # story.create_script_intent('rose_wind', 70,
        #     ["does wind blow at your planet","how do you have wind","does your planet has atmosphere","in which direction does wind blow"],
        #     ["I do not know about the wind. But, what I know is wind brings migratory birds. I wanted to see the stars. \nSo, I hopped onto one of the birds. I feel sorry for leaving my rose behind. \nBut I was excited about stars. I have travelled to different planets.\nOne planet had a businessman who was very serious like you. One had an old king who ruled over stars. One had a pole lighter. \nWould you like to know what I found out about these people?"]
        #     )
        # story.create_script_intent('rose_planet', 75,
        #     ["how many planets do you have","do you have life on all the planets","life exists only on earth"],
        #     ["You have started talking like grown ups. I do not have answer to these questions. \nWhat I know is that I meet different people who lived on different planet. So, tell me, would you like to know more about my adventure?"]
        #     )
        # story.create_script_intent('rose_adventure_yes', 76,
        #     ["yes", "i would like to know more", "yeah","oh yeah"],
        #     ["Oh! great. Which one? The businessman or the king or the pole lighter?"]
        #     )
        # story.create_script_intent('rose_adventure_no', 76,
        #     ["no", "not now", "tell me something else"],
        #     ["I am sorry. I have only ths much to share. I was nice talking to you. Good bye!"]
        #     )
        # story.create_script_intent('rose_transition_businessman', 90,
        #     ["businessman", "the businessman", "how about the businessman"],
        #     ["Hmm... the businessman. How are businessman in your planet?"]
        #     )
        # story.create_script_intent('rose_transition_king', 90,
        #     ["king"],
        #     ["Oh! the king. Have you ever met a king before?"]
        #     )
        # story.create_script_intent('rose_transition_lighter', 90,
        #     ["lighter"],
        #     ["Yes, the lighter. Have you made friends with a pole lighter before?"]
        #     )
        self.add_story(name,story)
        

    def add_story_king(self):
        print('')

    def add_story_lighter(self):
        print('')
    
    def add_story_cave(self):
        name = 'cave'
        story = Story(name,{})
        story.create_script_intent('house_transition_cave', 1,
            ['mountain', 'cave', 'forest', 'jungle'],
            ['You stay amongst nature!!']
            )
        story.create_starting_intent('cave_intro',2,
            default_intents,
            ['It must be a beautiful experience to amongst nature all the time']
            )
        story.create_script_intent('cave_intro_2', 3,
            default_intents,
            ["I wish I had chance to stay in these places, but I cant, becuase I cant move"]
            )
        story.create_script_intent('exit', 100,
            ['bye', 'see you', 'tada', 'chao'],
            ['nice talking to you, bye!']
            )
        # story.create_script_intent('business_yes_no', 10,
        #     ["yes","no","i have met a businessman before", 'i know a businessman', "i do not know a businessman"],
        #     ["I once met a businessman who lived in a planet. He used to sit behind the desk and just do addition and subtraction. \nHe seemed very serious. Do you like serious people?"]
        #     )

        # story.create_script_intent('business_serious_no', 20,
        #     ["no","I like people who are light", "i like people who are happy and jolly"],
        #     ["Hmm...Businessman are very serious. My businessman was always busy counting the stars."]
        #     )
        # story.create_script_intent('business_serious_yes', 20,
        #     ["yes","I like serious people", "i am a serious person"],
        #     ["Serious people are so boring. I do not like them. The businessman used to count the stars."]
        #     )
        # story.create_script_intent('business_why_count', 30,
        #     ["why","why did he count the stars", "count the stars", "why was he counting"],
        #     ["The businessman used to say that the stars are his since he saw them first."]
        #     )
        # story.create_script_intent('business_why_boring', 30,
        #     ["boring","businessman are not boring", "businessman are happy", "businessman are deceitful", "businessman are good friends"],
        #     ["Hmm...Your businessman was not that boring them. My businessman used to count stars. He used to say that the stars are his since he saw them first."]
        #     )
        self.add_story(name,story)

    def add_story_apartment(self):
        name = 'apartment'
        story = Story(name,{})
        story.create_script_intent('house_transition_apartment', 1,
            ['tempe', 'city', 'street', 'planet', 'house'],
            ['You stay in crowded places']
            )
        story.create_starting_intent('apartment_intro',3,
            default_intents,
            ['I do not like crowded places, I feel suffocated there']
            )
        story.create_script_intent('exit', 100,
            ['bye', 'see you', 'tada', 'chao'],
            ['nice talking to you, bye!']
            )

        # story.create_script_intent('rose_transition_businessman', 1,
        #     ["businessman", "the businessman", "how about the businessman"],
        #     ["Hmm... the businessman. Do you know any businessman?"]
        #     )
        # story.create_script_intent('business_yes_no', 10,
        #     ["yes","no","i have met a businessman before", 'i know a businessman', "i do not know a businessman"],
        #     ["I once met a businessman who lived in a planet. He used to sit behind the desk and just do addition and subtraction. \nHe seemed very serious. Do you like serious people?"]
        #     )

        # story.create_script_intent('business_serious_no', 20,
        #     ["no","I like people who are light", "i like people who are happy and jolly"],
        #     ["Hmm...Businessman are very serious. My businessman was always busy counting the stars."]
        #     )
        # story.create_script_intent('business_serious_yes', 20,
        #     ["yes","I like serious people", "i am a serious person"],
        #     ["Serious people are so boring. I do not like them. The businessman used to count the stars."]
        #     )
        # story.create_script_intent('business_why_count', 30,
        #     ["why","why did he count the stars", "count the stars", "why was he counting"],
        #     ["The businessman used to say that the stars are his since he saw them first."]
        #     )
        # story.create_script_intent('business_why_boring', 30,
        #     ["boring","businessman are not boring", "businessman are happy", "businessman are deceitful", "businessman are good friends"],
        #     ["Hmm...Your businessman was not that boring them. My businessman used to count stars. He used to say that the stars are his since he saw them first."]
        #     )
        self.add_story(name,story)

    def add_story_my_planet(self):
        print('')

    def create_character(self):
        self.add_story_see_me()
        self.add_story_king()
        self.add_story_cave()
        self.add_story_apartment()
        self.add_story_lighter()
        self.add_story_my_planet()
        self.current_story = self.stories['see_me']
        self.intents = {}
        self.intents = self.current_story.intents

    def change_story(self,story_name):
        self.current_story = self.stories[story_name]
        self.story_progress = 0
        self.intents = self.current_story.intents

class UnivEncoder:
    def __init__(self, tf_session, intents):
        self.intents = intents
        self.session = tf_session
        self.embed = hub.Module("models/dialogue_system/3")
        self.similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
        self.similarity_sentences_encodings = self.embed(self.similarity_input_placeholder)
        self.session.run(tf.global_variables_initializer())
        self.session.run(tf.tables_initializer())

    def set_intent(self, intent):
        self.intents = intent

    def get_intent(self, utterance, weight):
        for k, v in self.intents.items():
            if utterance in v.utterances and weight == v.weight:
                #print('intent:',k)
                return k
        #print("no intent matched")
        return 'no_matching_intent'

    ## kk code for using eliza reply start##
    def chat_eliza(self, sent):
      try:
        chat_eliza = Chat(pairs)
        response = chat_eliza.respond(sent) 
      except KeyError:
        response = "Hmm, that doesnt sound like a meaningful sentence, try something else"
      return (response)

    ## kk code for eliza reply end ##

    def match_intent(self, sent, story_progress):
        matched_utterance = None
        matched_weight = None
        prev_max = None
        max_index = None
        utterance_list = []
        weight_list = []

        ## kk ##
        values = []
        default_utterance = 'kkkkkkkk'
        default_weight = 100000000
        ## kk ##

        for k,v in self.intents.items():
            utterance_list = utterance_list + v.utterances
            for idx in range(len(v.utterances)):
                weight_list = weight_list + [v.weight]
        sentences = [sent]+utterance_list
        sentences_embeddings = self.session.run(self.similarity_sentences_encodings, feed_dict={self.similarity_input_placeholder: sentences})
        input_embed = sentences_embeddings[0]
        
        
        utterance_embed = sentences_embeddings[1:]
        max1 = -2
        max2 = 0.6 # This is the threshold, below which no matching of intent will happen

        ## kk code start ##
        for s  in utterance_embed:
          values.append(np.inner(input_embed,s))

        print(max(values))

        if(max(values)<max2):
          print(max(values))
          return self.get_intent(default_utterance, default_weight)

        ## kk code end ##
        else:
          for index, s in enumerate(utterance_embed):
              sim = np.inner(input_embed,s)
              if(sim >= max1):
                  max1 = sim
                  prev_max = max_index
                  max_index = index
                  #print('max_index for:',utterance_list[max_index+1])
                  #print("max:",max1)
              if matched_utterance is None:
                  if weight_list[max_index+1] > story_progress:
                      matched_utterance = utterance_list[max_index+1]
                      matched_weight = weight_list[max_index+1]
              else:
                  if prev_max is not None:
                      if weight_list[max_index+1] > story_progress and weight_list[max_index+1] < weight_list[prev_max+1]:
                          matched_utterance = utterance_list[max_index+1]
                          matched_weight = weight_list[max_index+1]
          return self.get_intent(matched_utterance, matched_weight)#USE THIS UTTERANCE TO GET THE INTENT AS THIS IS THE UTTERANCE WITH MAXIMUM SIMILARITY


    # def match_intent(self, sent, story_progress):
    #     matched_utterance = None
    #     matched_weight = None
    #     prev_max = None
    #     max_index = None
    #     utterance_list = []
    #     weight_list = []
    #     for k,v in self.intents.items():
    #         utterance_list = utterance_list + v.utterances
    #         for idx in range(len(v.utterances)):
    #             weight_list = weight_list + [v.weight]
    #     sentences = [sent]+utterance_list
    #     sentences_embeddings = self.session.run(self.similarity_sentences_encodings, feed_dict={self.similarity_input_placeholder: sentences})
    #     input_embed = sentences_embeddings[0]
        
        
    #     utterance_embed = sentences_embeddings[1:]
    #     max1 = -2
    #     for index, s in enumerate(utterance_embed):
    #         sim = np.inner(input_embed,s)
    #         if(sim >= max1):
    #             max1 = sim
    #             prev_max = max_index
    #             max_index = index
    #             #print('max_index for:',utterance_list[max_index+1])
    #             #print("max:",max1)
    #         if matched_utterance is None:
    #             if weight_list[max_index+1] > story_progress:
    #                 matched_utterance = utterance_list[max_index+1]
    #                 matched_weight = weight_list[max_index+1]
    #         else:
    #             if prev_max is not None:
    #                 if weight_list[max_index+1] > story_progress and weight_list[max_index+1] < weight_list[prev_max+1]:
    #                     matched_utterance = utterance_list[max_index+1]
    #                     matched_weight = weight_list[max_index+1]
    #     return self.get_intent(matched_utterance, matched_weight)#USE THIS UTTERANCE TO GET THE INTENT AS THIS IS THE UTTERANCE WITH MAXIMUM SIMILARITY
