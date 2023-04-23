import openai
import requests
import os
import datetime
import re
from termcolor import colored

hostedonPublic = False # This setting is essentially redundant now. Keep it on False unless you want purposefully locked down functionality.

if hostedonPublic:
    print(colored('Welcome!', 'cyan', attrs=['bold']))
    print(colored('This script heavily depends on OpenAI\'s GPT-3 API and therefore, it is necessary to provide an API key to make it work. If you don\'t feel at ease entering your API key, you can always fork the script and enter it in an environment variable instead.', 'yellow'))
    print(colored('Let\'s get started!', 'white'))
    while True:
      OpenApIKey = input("Please enter your OpenAI API key: ")
      # Send a request to OpenAI's API. If we get a positive response back, we're good to go and know the user provided a valid API key.
      headers = {'Authorization': f'Bearer {OpenApIKey}'}
      response = requests.get("https://api.openai.com/v1/engines", headers=headers)
      if response.status_code != 200:
          print(colored("Invalid OpenAI token, please try again.", "red"))
      else:
          print(colored("Token is valid!", "green"))
          break

if not hostedonPublic:
    OpenApIKey = os.environ['openai'] # Input OpenAI API key here.

my_model = 'text-davinci-003' # Davinci 003 is what this was tested on but other models can be used if you so wish. text-curie-001 is a step down from Davinci and can usually hold its own with a significantly smaller cost, but may be a tad less bright at times. Model list: https://beta.openai.com/docs/models/gpt-3

my_tokenlimit = 240 # The most amount of tokens Super Mario can generate. Anything past the token limit will result in him getting forcefully cut off. Anything below 80 seems to result in very common cut off points. 100 usually works well enough, 240 is just in case. This is only if he needs the tokens, and he doesn't always. 1 token equals around 4 characters in English. https://beta.openai.com/tokenizer

AutomaticModelSwitch = False # Should the model automatically switch after a certain amount of tokens? This is in an effort to save on cost. The below value, 'MaxtokensBeforeModelSwitch' will indicate the number of tokens before the model is switched. True = yes, do this. False = no, dont do this.

MaxtokensBeforeModelSwitch = 600 # This value only does anything if the above value, "AutomaticModelSwitch" is enabled. If it isn't enabled, don't worry about this option. If it is, then this options controls the token threshold at which the program will switch to a lower model in order to generate text with less price. As a loose guide, every trade off between verses usually results in 50~ tokens being added to the total. To help visualize the token system: https://beta.openai.com/tokenizer

sendallConversation = True # Should the program send the entire conversation to the API for generation? If this is set to false, only the player's current verse will be sent to the API for Super Mario to acknowledge. True = yes, send entire conversation. False = no, only send player's current verse. This option is an effort to save on cost and tokens, but can obviously result in the rap battle feeling disconnected. Your choice.

damage_system = True # Should you and Super Mario take damage depending on the sicker the bars your opponent does? True is on, False is off.

player_health = 100 # The players health. This value doesn't matter if the damage system is disabled.

super_mario_health = 100 # Super Mario's health. This value doesn't matter if the damage system is disabled.


# Welcome message to the user
print(colored("Welcome to the epic rap battle vs Super Mario!", "green"))
if hostedonPublic:
        print(colored("Please note: saving is currently disabled. Please set hostedonPublic back to False if this wasn't intended.", "red"))

print(colored("Remember: Super Mario is NOT real and cannot hurt you. Make sure to follow OpenAI's TOS whenever interacting with this program. Whatever you say is on you. You can type 'save' to create a text file of your current rap battle with Super Mario anytime. You can type 'quit' to exit.", "green"))

# Set up variables
VERSES = "You are in a rap battle against the legendary video game character Super Mario. This rap battle will be extremely intense, so watch out!\n"
model_switch_message_printed = False


# Function to get sickness of the verse using GPT-3
def get_verse_sickness_score(verse):
    openai.api_key = OpenApIKey
    response = openai.Completion.create(engine="text-davinci-003", prompt=f"generate a score for the sickness of this verse: {verse}", max_tokens=20) # I would highly advise against changing this to another model. Davinci 003 seems to be the only one capable of doing this sort of prompt and its simply too illogcal with the others.
    score_text = response["choices"][0]["text"]
    # print(response["choices"][0]["text"])
    match = re.search(r'\d+', score_text)
    # print("match")
    # print(match)
    # print("score text")
    # print(score_text)
    if match:
        score = match.group()
        # print(score)
    else:
        score = 0
        # print("no")
    return score


# Function to calculate damage based on verse sentiment
def calculate_damage(score):
    damage = int(score)
    return damage

  
# Function to check if game is over
def check_game_over(player_health, super_mario_health):
    if player_health <= 0:
        print("\033[1;31mGAME OVER!\033[1;37m Super Mario has won. Yahoo!\033[1;0m")
        
        print("  _   _   _   _     _   _   _   _")
        print(" / \ / \ / \ / \   / \ / \ / \ / \ ")
        print("( S | u | p | e | r |   | M | a | r | i | o )")
        print(" \_/ \_/ \_/ \_/   \_/ \_/ \_/ \_/")
        return True
    elif super_mario_health <= 0:
        print("\033[1;32mVICTORY!\033[1;37m Super Mario has been defeated. Hooray!\033[1;0m")
        
        print("  _   _   _   _     _   _   _   _")
        print(" / \ / \ / \ / \   / \ / \ / \ / \ ")
        print("( V | i | c | t | o | r | y | ! )")
        print(" \_/ \_/ \_/ \_/   \_/ \_/ \_/ \_/")
        return True
    return False


# Create a function to draw the health bar
def draw_health_bar(name, health, max_health):
    percentage = int(health / max_health * 100)
    health_bar = "[" + "=" * int((health / max_health) * 10) + " " * int(((max_health - health) / max_health) * 10) + "] " + str(percentage) + "%"
    if health >= (max_health * 0.8):
        print(colored(f'{name} Health: \033[1m{health_bar}\033[0m', 'green'))
    elif health >= (max_health * 0.5):
        print(colored(f'{name} Health: \033[1m{health_bar}\033[0m', 'yellow'))
    else:
        print(colored(f'{name} Health: \033[1m{health_bar}\033[0m', 'red'))
  
# Keep on going until the user wants the rap battle to end
while (True):
    # Get user input
    print(colored("Input your rap verse:", "cyan"))
    USER_TEXT = input()
  
    if USER_TEXT == "quit":
        break

    if USER_TEXT.strip().lower() == "save":
      # If player is using the public hosted repl, disable saving.
      if hostedonPublic:
        print("\033[1;31mYou can't save a rap battle while being on the public server. Please fork the repl to unlock this functionality.\033[1;0m")
        break
      current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
      file_name = "rap_battle " + current_time + ".txt"
      while os.path.exists(file_name):
          file_name = "rap_battle " + current_time + "(1)" + ".txt"
      with open(file_name, "w") as f:
         f.write(VERSES)
      print("Rap battle saved to " + file_name)
      continue

    # Append user's verse to the prompt
    VERSES += "Player: " + USER_TEXT.strip() + "\n"

    if AutomaticModelSwitch and len(VERSES.split()) > MaxtokensBeforeModelSwitch:
      if not model_switch_message_printed:
        model_switch_message_printed = True
        my_model = 'text-curie-001' # Switch to a lower model. Curie is the step down from Davinci and can usually hold its on, but if you want to really cut the cost off you can use even cheaper models. But beware, coherency may go flying out the window! Model list: https://beta.openai.com/docs/models/gpt-3 Model pricing: https://openai.com/api/pricing/
        print(colored("\nMax token threshold reached. Switching model to "+my_model+"..\n", "red"))

        
    # Make API call
    API_ENDPOINT = 'https://api.openai.com/v1/completions'
    if sendallConversation:
      data = {
      'prompt': VERSES,
      'model': my_model,
      'max_tokens': my_tokenlimit,
      "stop": "Player:"
      }
    else:
      data = {
      'prompt': "You are in a rap battle against the legendary video game character Super Mario. This rap battle will be extremely intense, so watch out!\nPlayer: " + USER_TEXT + "\nSuper Mario:",
      'model': my_model,
      'max_tokens': my_tokenlimit,
      "stop": "Player:"
      }
    HEADERS = {
        'Authorization': 'Bearer ' + OpenApIKey
    }

    response = requests.post(url=API_ENDPOINT, json=data, headers=HEADERS)


    # Add OpenAI Moderation API and check if Super Mario was a bully (uncalled for)
    openai.api_key = OpenApIKey
    moderation_response = openai.Moderation.create(
        input=response.json()['choices'][0]['text']
    )
    moderation_result = moderation_response["results"][0]
    if moderation_result["flagged"] == False:
        print(colored("Super Mario's verse:", "magenta"))
        print(colored(response.json()['choices'][0]['text'].strip().replace("Super Mario:", "").strip().replace("Mario:", "").strip() + "\n", "yellow"))
        # Append Super Mario's verse to the prompt
        VERSES += response.json()['choices'][0]['text'].strip().replace("Super Mario:", "").strip() + "\n"
        # print(VERSES)
        # print(len(VERSES.split()))
        # print("model: " + my_model)
        # Calculate damage for player's verse
        if damage_system:
          player_verse_sentiment = get_verse_sickness_score(USER_TEXT)
          player_damage = calculate_damage(player_verse_sentiment)
          super_mario_health -= player_damage
          # print(player_verse_sentiment)
          # print(player_damage)
          # print(player_health)
        # Calculate damage for Super Mario's verse
        if damage_system:
            super_mario_verse_sentiment = get_verse_sickness_score(response.json()['choices'][0]['text'])
            super_mario_damage = calculate_damage(super_mario_verse_sentiment)
            player_health -= super_mario_damage
    
            if check_game_over(player_health, super_mario_health):
    
                break
        else:
            # Do other stuff here if damage system is off
            pass
        if damage_system:
          # Draw the player's health bar
          draw_health_bar("Player", player_health, 100)
          
          # Draw Super Mario's health bar
          draw_health_bar("Super Mario", super_mario_health, 100)
        continue
        # print("You are in a rap battle against the legendary video game character Super Mario. This rap battle will be extremely intense, so watch out!\nPlayer: " + USER_TEXT + "\nSuper Mario:")
    else:
        print(colored("\nSuper Mario's verse was detected as too aggressive by the OpenAI Moderation API and was refused. Please rewrite your rap verse.\n", "red"))
