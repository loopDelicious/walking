"""Utility file to generate random ratings and reviews to seed database."""

from text_generator import open_and_read_file, make_chains, make_text
from random import choice, randint

def generate_ratings():
    """Use pseudo random number and Markov text generator to create text for sample ratings."""

    seed_ratings = []

    # rate ~900 landmarks in ascending order beginning with 1
    landmark_id = 1
    while landmark_id < 894:
    
        # from user base of ~100
        user_id = randint(1,100)

        # assign random score for up to 5-star ratings
        user_score = randint(1,5)

        # use markov chain generator to create reviews
        input_text = open_and_read_file("fairy.txt")
        chains, words = make_chains(input_text)
        random_text = make_text(chains, words)
        user_notes_for_landmark = choice(random_text)

        data = {
                "landmark_id": landmark_id,
                "user_id": user_id,
                "user_score": user_score,
                "user_notes_for_landmark": user_notes_for_landmark
                }

        seed_ratings.append(data)

        landmark_id +=1

    return seed_ratings

# how do I create a fil
generate_ratings()

        



