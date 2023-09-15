from thefuzz import fuzz
from thefuzz import process
name = "hand bags"
full_name = "ShoulderBags"


def check(search: str, category: str ):
    print(f"Token sort ratio similarity score: {fuzz.token_sort_ratio(search, category)}")



if __name__ == '__main__':
    check('handbags', 'crossbodybags')