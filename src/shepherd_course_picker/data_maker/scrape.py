from .fetch import cache_fetch
from typing import Union
from bs4 import BeautifulSoup
import bs4
import re

URL_PROGRAMS = 'https://catalog.shepherd.edu/content.php?catoid=19&navoid=3646'
URL_PREVIEW = 'https://catalog.shepherd.edu/preview_program.php?poid='


# Check if element has a class
def soupHasClass(soup: BeautifulSoup, class_) -> bool:
    for c in soup.get('class'):
        if class_ in str(c):
            return True
    return False


# Find a parent of an element.
def findSoupParent(source_soup: BeautifulSoup, element: str, tries: int = 10) -> bs4.Tag:
    current = source_soup.parent
    while True:
        if current and current.name == element:
            return current
        elif tries < 0:
            raise RuntimeError  # TODO "scraping" error?
        else:
            tries -= 1
            current = current.parent


# General function to find an element with class within soup
def findElementWithClassInSoup(source_soup: BeautifulSoup, element: str, _class: str) -> BeautifulSoup:
    e = source_soup.find_all(element)

    # FIXME no idea why this cant be gotten the normal way with find_all. This is concerning
    # i think i was using _class not class_? (in funciton call)

    for td in e:
        if [_class] == td.get('class'):  # TODO what if multiple classes
            return td

    raise RuntimeError  # FIXME Get better error


# Get only DIRECT children.
def elemDirectChildren(elem: bs4.Tag, name: str = None) -> list[bs4.Tag]:
    """FIXME warning this has fidget brain"""
    if name:
        rows = elem.find_all(name, recursive=False)
    else:
        rows = elem.find_all(recursive=False)
    return rows


# Scraping is combined with the model. It just seems easier to understand this way.


class BaseNode():
    # This should be overwritten
    def render(self):
        raise RuntimeError

    # def propagate(self):
    #     self.render()


# Collection of nodes. Just for typing's sake
class NodeCollection(list):
    pass
    # def __init__(self):
    #     pass


# Nodes that contain other nodes inherit this
class BaseCollectionNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def __iter__(self):
        for n in self.nodes:
            yield n

    def __repr__(self):
        return str([i for i in self.nodes])

    def append(self, node: BaseNode):
        self.nodes.append(node)

    # # Render itself and its children. This way things can come apart and function without their parents
    # def propagate(self):
    #     super().propagate()
    #     for node in self.nodes:
    #         node.propagate()


class CourseNode(BaseNode):
    def __init__(self, html: str):
        super().__init__()
        find = lambda pattern: re.findall(pattern, html)

        # Course name
        # Get between the a tags
        self.name = find(r'<a[^>]*>([^<]+)<\/a>')[0]  # TODO test case test for more than 1 here

        # TODO Course credit amount

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


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


# Cores contain courses (As well as other cores)
class CoreNode(BaseCollectionNode):
    def __init__(self, html: str):
        super().__init__()

        # self.parent = parent

        self.name = self.find_name(html)
        if self.name.isspace():
            raise ValueError

        self.heading = self.find_heading(html)

        self.nodes = self.find_courses(html)

    def __repr__(self):
        return f'{self.name}: {str(self.nodes)}'

    # def propagate(self):

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
            raise RuntimeError
            # return 'BROKEN'
        else:
            return a[0]  # TODO Testcase for more than 1

    # TODO This feels like it can be done recurisvely
    def find_courses(self, html: str) -> list[Union[CourseNode, RelationshipNode]]:
        pattern = r'acalog-course.*?<\/li>'
        list_course_html = re.findall(pattern, html)

        master = []
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

        return master


# TODO I feel like this should live inside of CoreNode
# Recursively find cores
# This takes an HTML tag.
def recurseForCores(elem: bs4.Tag) -> NodeCollection:
    def nodeHasCoreChildren(node: bs4.Tag) -> bool:
        return c.find_all('div', class_='acalog-core') != []

    # We will be parsing cores and "lists" of cores.
    childs = elemDirectChildren(elem, 'div')  # Get all direct div children.
    new_nodes = NodeCollection()

    # "For tag every tag that is direct child of given HTML element"
    for c in childs:
        # If node has children,
        if nodeHasCoreChildren(c):
            f = recurseForCores(c)  # Recursively run this function and find it's children
            new_nodes.append(f)

        # TODO elif on finding core and else raise exception

        # Node is a core,
        else:
            new = CoreNode(str(c))  # FIXME pass tag not str
            new_nodes.append(new)

    return new_nodes


# Programs contain cores
class ProgramNode(BaseCollectionNode):
    def __init__(self, _id: str, name: str):
        super().__init__()

        self._id = _id
        self.name = name

        # html = self.make_html()

        # self.nodes = self.find_cores(html)

    def render(self):
        html = self.make_html()

        self.nodes = self.find_cores(html)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def make_html(self) -> str:
        return cache_fetch(URL_PREVIEW + self._id)

    # Find all of the cores
    def find_cores(self, html) -> list[CoreNode]:
        # FIXME evil awful partition this and make it testable
        soup = BeautifulSoup(
            html, 'html.parser'
        )

        # Everything we care about is in a big fat td element
        a = findElementWithClassInSoup(
            soup,
            "td",
            'block_content'
        )

        table = a.findChild()  # First child will be this table. (Have to be specific because tables are everywhere)
        if not soupHasClass(table, 'table_default'):
            raise RuntimeError

        table_rows = elemDirectChildren(table)

        a = table_rows[1]  # TODO override implement every row
        if a.name != 'tr':  # This should be a table row
            raise RuntimeError

        core_div = a.find('div')  # First div contains list of cores

        found_core = recurseForCores(core_div)

        return found_core


# Get list of all programs from Shepherd website
def get_program_list() -> list[ProgramNode]:
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
