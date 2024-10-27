import re
from fetch import fetch, debug_fetch

URL_PROGRAMS = 'https://catalog.shepherd.edu/content.php?catoid=19&navoid=3646'
URL_PREVIEW = 'https://catalog.shepherd.edu/preview_program.php?poid='

def get_program_list():
    # Get list of programs
    html = debug_fetch(
        URL_PROGRAMS
    )

    # Capture ID and name
    pattern = r'<a href="[^"]*poid=(\d+)[^"]*">([^<]+)</a>'
    matches = re.findall(pattern, html)

    program = matches[10]

class CollectionNode():
    # conditions = {
    #     'AND',
    #     'OR',
    #     None
    # }

    # def __init__(self, node, condition):
    #     pass
    def __init__(self):
        # self.condition = condition

        self.nodes = []  # Would overcomplicate things to add nodes on init

    def append(self, node):
        self.nodes.append(node)

    def __repr__(self):
        return str([i for i in self.nodes])


class RelationshipNode():
    conditions = {
        'AND',
        # 'OR',
        # None
    }
    def __init__(self, condition):
        # super().__init__()

        self.condition = condition

        self.nodes = []

    def append(self, node):
        self.nodes.append(node)

class ProgramNode:
    def __init__(self, _id: str):
        self.cores = []
        self._id = _id

    # Get Cores contained within Program
    def find_cores(self):
        html = debug_fetch(URL_PREVIEW + self._id)

        pattern = r'acalog-core.*?<\/ul>'
        list_core_html = re.findall(pattern, html)

        for core_html in list_core_html:
            new = CoreNode(core_html)
            self.cores.append(new)

class CoreNode:
    def __init__(self, html: str):
        self.courseList = []

        self.name = self.find_name(html)
        if self.name.isspace():
            raise ValueError

        self.find_courses(html)

    def find_name(self, html: str) -> str:
        a = re.findall(
            '/a>([^<]+)(?:.(?!/a))+h2', # FIXME god awful
            html
        )

        return a[0] # TODO what if more than 1? testcase


    def find_courses(self, html:str):
        pattern = r'acalog-course.*?<\/li>'
        list_course_html = re.findall(pattern, html)


        master = CollectionNode()
        current_coll = master
        was_or = False
        for index, course_html in enumerate(list_course_html):
            new_course = CourseNode(course_html)

            # find = lambda pattern:

            # Add to the previous course, that this course is in a relationship with it.
            # Next step is easier this way.

            # The goal of this is to get the next HTML.
            # Basically the same amount of work as not looking ahead. Easier to "grok" it this way.
            def next_course_html():
                c = list_course_html

                i = index + 1 # Index starts at 0
                if i > len(c) - 1: # Len starts counting at 1
                    return None
                else:
                    return list_course_html[i]


            def find_is_or():
                html = next_course_html()
                pattern = r'>OR<'

                if html is None: # Last course of core
                    return False
                else:
                    x = re.findall(pattern, html)

                    # regex returns a list.
                    return x # Empty lists evaluate to False, while non-empty evaluates to True

            is_or = find_is_or()

            # In the middle of an OR
            if is_or and was_or:
                current_coll.append(new_course)

            # Starting an OR
            elif is_or:
                was_or = True

                new_coll = RelationshipNode('or')

                current_coll.append(new_coll)
                current_coll = new_coll

                current_coll.append(new_course)

            # End of OR
            elif was_or:
                was_or = False
                current_coll.append(new_course)
                print([i.name for i in current_coll.nodes])
                current_coll = master

            # No OR
            else:
                current_coll.append(new_course)

            # # TODO do ands even occur?
            # if find('>AND<'):
            #     self.courseList[-1]['and'] = True
            #     raise ValueError # FIXME to get my attention.

            # self.courseList.append(
            #     CourseNode(course_html)
            # )
        # print(master)



class CourseNode():
    def __init__(self, html: str):
        find = lambda pattern: re.findall(pattern, html)

        # Course name
        # Get between the a tags
        self.name = find(r'<a[^>]*>([^<]+)<\/a>')[0]  # TODO test case test for more than 1 here

        # TODO Course credit amount


a = ProgramNode('2531')
a.find_cores()
