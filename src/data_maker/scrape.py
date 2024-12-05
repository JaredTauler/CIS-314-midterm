import re
from .fetch import cache_fetch

URL_PROGRAMS = 'https://catalog.shepherd.edu/content.php?catoid=19&navoid=3646'
URL_PREVIEW = 'https://catalog.shepherd.edu/preview_program.php?poid='

# Scraping is combined with the model. It just seems easier to understand this way.

# Get list of all programs from Shepherd website
def get_program_list():
    # Get list of programs
    html = cache_fetch(URL_PROGRAMS)

    # Capture ID and name
    pattern = r'<a href="[^"]*poid=(\d+)[^"]*">([^<]+)</a>'
    matches = re.findall(pattern, html)

    l = []
    for program in matches:
        l.append(
            ProgramNode(program[0], program[1])
        )

    return l

# Nodes that contain other nodes inherit this
class BaseCollectionNode():
    def __init__(self):
        self.nodes = []

    def append(self, node):
        self.nodes.append(node)

    def __iter__(self):
        for n in self.nodes:
            yield n

    def __repr__(self):
        return str([i for i in self.nodes])

# Programs contain cores
class ProgramNode(BaseCollectionNode):
    def __init__(self, _id: str, name: str):
        super().__init__()

        self._id = _id
        self.name = name

        html = cache_fetch(URL_PREVIEW + self._id)
        self.find_cores(html)


    def __repr__(self):
        return self.name    

    def __str__(self):
        return self.name

    # Find all of the cores
    def find_cores(self, html):
        pattern = r'class="acalog-core">(.*?)<\/div>'
        list_core_html = re.findall(pattern, html)


        for html in list_core_html:
            new = CoreNode(html)
            self.nodes.append(new)
        # FIXME I cannot figure this out. For now, cores will not have hierarchy.
        # Frontend core name bug is related to this.

        # Cores are nested, the way we tell how is by looking at the heading number and grouping them by that:
        # Example:
        # 2 |-> 3 -|-> 4
        #   |      |-> 4
        #   |-> 3

# Cores contain courses (As well as other cores)
class CoreNode(BaseCollectionNode):
    def __init__(self, html: str):
        super().__init__()

        # self.parent = parent

        self.name = self.find_name(html)
        if self.name.isspace():
            raise ValueError

        self.heading = self.find_heading(html)

        self.find_courses(html)


    def __repr__(self):
        return f'{self.name}: {str(self.nodes)}'

    # Find the core's heading number
    def find_heading(self, html):
        pattern = r'<h(\d)>'
        heading_value = re.findall(pattern, html)

        return heading_value[0]

    def find_name(self, html: str) -> str:
        # h\d finds h1-h5 headings, which are used to denote core
        a = re.findall(
            '\/a>([^<]+)(?:.(?!\/a))+h\d',  # FIXME backtracking will blow it up on big htmls
            html
        )

        if a == []:
            raise ValueError
            # return 'BROKEN'
        else:
            return a[0] # TODO Testcase for more than 1

    # TODO This feels like it can be done recurisvely
    def find_courses(self, html: str):
        pattern = r'acalog-course.*?<\/li>'
        list_course_html = re.findall(pattern, html)

        master = self.nodes
        current_coll = master
        was_or = False
        for index, course_html in enumerate(list_course_html):
            new_course = CourseNode(course_html)

            # The goal of this is to get the next HTML.
            def next_course_html():
                c = list_course_html

                i = index + 1  # Index starts at 0
                if i > len(c) - 1:  # Len starts counting at 1
                    return None
                else:
                    return list_course_html[i]

            def find_is_or():
                html = next_course_html()
                pattern = r'>OR<'

                if html is None:  # Last course of core
                    return False
                else:
                    x = re.findall(pattern, html)

                    # regex returns a list.
                    return x  # Empty lists evaluate to False, while non-empty evaluates to True

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
                current_coll = master

            # No OR
            else:
                current_coll.append(new_course)


# This is to store relationships between courses.
class RelationshipNode(BaseCollectionNode):
    conditions = {
        'OR',
        # 'AND',
        # None
    }

    def __init__(self, condition):
        super().__init__()

        self.condition = condition


class CourseNode():
    def __init__(self, html: str):
        find = lambda pattern: re.findall(pattern, html)

        # Course name
        # Get between the a tags
        self.name = find(r'<a[^>]*>([^<]+)<\/a>')[0]  # TODO test case test for more than 1 here

        # TODO Course credit amount

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name