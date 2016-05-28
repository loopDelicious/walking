"""Seed reviews with a Markov text generator based on Trump foreign policy speech.
https://www.donaldjtrump.com/press-releases/donald-j.-trump-foreign-policy-speech
"""

from random import choice


def open_and_read_file(file_path):
    """Read the entire contents of the file in as a string."""

    contents = open(file_path).read()
    return contents


def make_chains(text_string):
    """Create a dictionary of markov chains.  Each key will consist of a tuple of (word1, word2),
    and teh value will be a list of the word(s) that follow those 2 words."""

    words = text_string.split()
    chains = {}
    #Iterates over words list by index, up to and including the third from the last element
    for i in range(len(words) - 2):
        if (words[i], words[i + 1]) in chains:
            chains[(words[i], words[i + 1])].append(words[i + 2])
        else:
            chains[(words[i], words[i + 1])] = [words[i + 2]]

    return chains, words


def make_text(chains, words):
    """Takes dictionary of markov chains; returns random text."""

    text = ""
    current_key = None

    while True:
        # start with a randomly selected key
        current_key = choice(chains.keys())
        # checks if first item from tuple is capitalized 
        if current_key[0].istitle():
            # if so, concatenate tuple to string 
            text += current_key[0] + " " + current_key[1] + " "
            break

    punctuations = ["!","?","."]

    #Establish condition to terminate Markov Chain
    while current_key != tuple(words[-2:]):
        #Prevents the formation of new key that has a none value 
        chosen_word = choice(chains[current_key])
       # iterates through punctuations list to ensure chains ends with punctuation
        for punctuation in punctuations:
            if punctuation in chosen_word:
                break

        # body of the Markov chain concatenates chosen_word-value to string
        text += chosen_word + " "
        new_key = (current_key[1], chosen_word)
        current_key = new_key
        
    return text


# input_path = "fairy.txt"
# input_text = open_and_read_file(input_path)
# chains, words = make_chains(input_text)
# random_text = make_text(chains, words)

# print random_text