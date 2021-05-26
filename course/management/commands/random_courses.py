import random
from configparser import ConfigParser

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from course.models import *

config = ConfigParser()
config.read("config/config.ini")


class Command(BaseCommand):
    help = "Create random users"

    def add_arguments(self, parser):
        parser.add_argument(
            "total", type=int, help="Indicates the number of users to be created"
        )

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        prefix = kwargs["prefix"]
        admin = kwargs["admin"]
        courseware = kwargs["courseware"]

        for i in range(total):

            course_data = {
                "course_code": "x",
                "instructors": ["mfhodges"],
                "course_schools": [course_school],
                "course_subject": course["course_department"],
                "course_term": term[-1],
                "course_activity": course["activity"],
                "course_number": course["course_number"],
                "course_section": course["section_number"],
                "course_name": course["course_title"],
                "year": term[:-1],
                "requested": False,
                "course_primary_subject": primary_subj,
            }


titles = [
    "What [Keyword] Can Teach You About [Alternate keyword]",
    "[Number] Crucial Tactics for [Keyword]",
    "Why Your [Keyword] is Missing the Mark (And How You Can Fix It)",
    "Back to Basics in [Keyword]",
    "[Number] Creative Ways to [Solution] [Keyword]",
    "Do You Recognize the [Number] Early Warning Signs of [blank]?",
    "Ultimate guide to [Keyword]",
    "The Modern Rules of [Keyword]",
    "[Number] Reasons [Keyword] is Better Than [Alternate keyword]",
]


def get_random(word):
    movies = [
        "'The Shawshank Redemption'",
        "'The Godfather'",
        "'The Godfather: Part II'",
        "'Pulp Fiction'",
        "'The Good, the Bad and the Ugly'",
        "'The Dark Knight'",
        "'12 Angry Men'",
        "'Schindler"
        "s List"
        ", "
        "The Lord of the Rings: The Return of the King"
        ", "
        "Fight Club"
        ", "
        "Star Wars: Episode V - The Empire Strikes Back"
        ", "
        "The Lord of the Rings: The Fellowship of the Ring"
        ", "
        "One Flew Over the Cuckoo's Nest"
        ", "
        "Inception"
        ", "
        "Goodfellas"
        ", "
        "Star Wars"
        ", "
        "Seven Samurai"
        ", "
        "Forrest Gump"
        ", "
        "The Matrix"
        ", "
        "The Lord of the Rings: The Two Towers"
        ", "
        "City of God"
        ", "
        "Se7en"
        ", "
        "The Silence of the Lambs"
        ", "
        "Once Upon a Time in the West"
        ", "
        "Casablanca"
        ", "
        "The Usual Suspects"
        ", "
        "Raiders of the Lost Ark"
        ", "
        "Rear Window"
        ", "
        "It's a Wonderful Life"
        ", "
        "Psycho"
        ", "
        "Léon: The Professional"
        ", "
        "Sunset Blvd."
        ", "
        "American History X"
        ", "
        "Apocalypse Now"
        ", "
        "Terminator 2: Judgment Day"
        ", "
        "Saving Private Ryan"
        ", "
        "Memento"
        ", "
        "City Lights"
        ", "
        "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb"
        ", "
        "Alien"
        ", "
        "Modern Times"
        ", "
        "Spirited Away"
        ", "
        "North by Northwest"
        ", "
        "Back to the Future"
        ", "
        "Life Is Beautiful"
        ", "
        "The Shining"
        ", "
        "The Pianist"
        ", "
        "Citizen Kane"
        ", "
        "The Departed"
        ", "
        "M"
        ", "
        "Paths of Glory"
        ", "
        "Vertigo"
        ", "
        "Django Unchained"
        ", "
        "Double Indemnity"
        ", "
        "The Dark Knight Rises"
        ", "
        "Aliens"
        ", "
        "Taxi Driver"
        ", "
        "American Beauty"
        ", "
        "The Green Mile"
        ", "
        "Gladiator"
        ", "
        "The Intouchables"
        ", "
        "WALL·E"
        ", "
        "The Lives of Others"
        ", "
        "Toy Story 3"
        ", "
        "The Great Dictator"
        ", "
        "The Prestige"
        ", "
        "A Clockwork Orange"
        ", "
        "Lawrence of Arabia"
        ", "
        "Amélie"
        ", "
        "To Kill a Mockingbird"
        ", "
        "Reservoir Dogs"
        ", "
        "Das Boot"
        ", "
        "The Lion King"
        ", "
        "Cinema Paradiso"
        ", "
        "Star Wars: Episode VI - Return of the Jedi"
        ", "
        "The Treasure of the Sierra Madre"
        ", "
        "The Third Man"
        ", "
        "Once Upon a Time in America"
        ", "
        "Requiem for a Dream"
        ", "
        "Eternal Sunshine of the Spotless Mind"
        ", "
        "Full Metal Jacket"
        ", "
        "Oldboy"
        ", "
        "Braveheart"
        ", "
        "L.A. Confidential"
        ", "
        "Bicycle Thieves"
        ", "
        "Chinatown"
        ", "
        "Singin in the Rain"
        ", "
        "Princess Mononoke"
        ", "
        "Monty Python and the Holy Grail"
        ", "
        "Metropolis"
        ", "
        "Rashomon"
        ", "
        "Some Like It Hot"
        ", "
        "Amadeus"
        ", "
        "2001: A Space Odyssey"
        ", "
        "All About Eve"
        ", "
        "Witness for the Prosecution"
        ", "
        "The Sting"
        ", "
        "The Apartment"
        ", "
        "Grave of the Fireflies"
        ", "
        'Indiana Jones and the Last Crusade"',
    ]
    terms = ["Anything", "Everything", "Nothing", "Life"]
    solve = ["solve", "fix", "make", "learn"]
    blank = ["failure", "death", "madness", "ASMR"]
    subjects = [
        "Mathematics",
        "History",
        "Physics",
        "Computer Science",
        "French",
        "German",
        "Gender Studies",
    ]

    lookup = {
        "Keyword": random.choice(
            [random.choice(subjects), random.choice(terms), random.choice(movies)]
        ),
        "Alternate keyword": random.choice(subjects + terms + movies),
        "Number": random.choice(["2", "3", "4", "5", "6", "7", "8", "9", "10"]),
        "Solution": random.choice(solve),
        "blank": random.choice(blank),
    }
    ans = lookup[word]
    return ans


def create_name(template):
    variables = [
        "Keyword",
        "Alternate keyword",
        "Number",
        "Solution",
        "world-class example",
        "blank",
    ]
    t = template
    choosen_words = []
    for var in variables:
        # print(var)
        start = t.find(var)
        end = start + len(var)
        if start != -1:
            # exists
            # print(t)
            new = get_random(var)
            while new in choosen_words:
                # print("getting new word")
                new = get_random(var)

            choosen_words.append(new)
            t = t.replace(var, new)
            # print(t)
    t = t.replace("[", "")
    t = t.replace("]", "")
    return t


# once all variables have been replaced remove the brackets


def random_name():
    titles = [
        "What [Keyword] Can Teach You About [Alternate keyword]",
        "[Number] Crucial Tactics for [Keyword]",
        "Why Your [Keyword] is Missing the Mark (And How You Can Fix It)",
        "Back to Basics in [Keyword]",
        "[Number] Creative Ways to [Solution] [Keyword]",
        "Do You Recognize the [Number] Early Warning Signs of [blank]?",
        "Ultimate guide to [Keyword]",
        "The Modern Rules of [Keyword]",
        "[Number] Reasons [Keyword] is Better Than [Alternate keyword]",
    ]
    return create_name(random.choice(titles))
