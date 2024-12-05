import data_maker
import random
import os


# Clearing screen doesn't play nice with IDEs
try:
    # Try posix
    def clear_screen():
        os.system('clear')

    clear_screen()
except:
    try:
        # Try windows
        def clear_screen():
            os.system('cls')

        clear_screen()
    except:
        # Nothing worked. Don't bother clearing screen
        clear_screen = lambda : False




def yesno(message):
    while True:
        print(message)
        print('Choices: y/n')

        ans = input()
        if 'y' in ans:
            return True
        elif 'n' in ans:
            return False


answer = yesno(
    'Picking a major is so hard... Do you want help?',
)
while True:
    if not answer:
        print('\nFine.')
        break
    elif answer:
        programs = data_maker.get_program_list()
        my_program = random.choice(programs)


        print(f"\nYour randomly selected program: {my_program}")

        layer = 4
        for core in my_program:
            print(' '*layer + core.name)

            layer = 8
            for node in core:
                # FIXME core names are somehow being stored as part of COURSE names.
                # This is 100% a bug despite looking intentional

                # Print individual course
                if type(node) is data_maker.CourseNode:
                    print(' '*layer + node.name)

                # Print relationship courses
                elif type(node) is data_maker.RelationshipNode:
                    string = ' '*layer
                    for course in node:
                        string += course.name
                        string += ' OR '
                    string = string[:-4] # Remove last OR
                    print(string)

        # Give insult
        insult = random.choice(
            [
                'Embarassing...',
                'Good for you!',
                'Good luck with that.',
                'Damn.',
                '',
            ],
        )

        print('\n'+ insult)

        print('\n\n')
        answer = yesno(
            'Go again?',
        )
        clear_screen()