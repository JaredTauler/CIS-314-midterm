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

class ProgramNode:
    cores = []
    _id = None

    def __init__(self, _id: str):
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
    courseList = []

    def __init__(self, html: str):
        self.name = self.find_name(html)
        if self.name.isspace():
            raise ValueError
        print(html)
        print(self.name)
        self.find_courses(html)
        print(self.courseList)

    def find_courses(self, html:str):
        pattern = r'acalog-course.*?<\/li>'
        list_course_html = re.findall(pattern, html)

        for course_html in list_course_html:
            new_course = {}

            find = lambda pattern: re.findall(pattern, course_html)

            # Course name
            # Get between the a tags
            new_course['name'] = find(r'<a[^>]*>([^<]+)<\/a>')[0]  # TODO test case test for more than 1 here

            # TODO Course credit amount

            # Add to the previous course, that this course is in a relationship with it.
            # Next step is easier this way.
            if find('>OR<'):
                self.courseList[-1]['or'] = True

            # TODO do ands even occur?
            if find('>AND<'):
                self.courseList[-1]['and'] = True
                raise ValueError # FIXME to get my attention.

            self.courseList.append(new_course)

    def find_name(self, html: str) -> str:
        a = re.findall(
            '/a>([^<]+)(?:.(?!/a))+h2', # FIXME god awful
            html
        )

        return a[0] # TODO what if more than 1? testcase


a = ProgramNode('2531')
a.find_cores()
print(len(a.cores))


# def id_coresHTMLs(_id) -> list[str]:
#     # Get program details
#     html = debug_fetch(URL_PREVIEW + _id)
#
#     # Get cores
#     # acalog-core(?:.(?!acalog-core))+\/ul
#     pattern = r'acalog-core.*?<\/ul>'
#     matches = re.findall(pattern, html)
#
#     return matches



# def cores_coursesHTMLs(htmls: list[str]) -> tuple[str, list[str]]:
#     for core in htmls:
#         # Get courses
#         pattern = r'acalog-course.*?<\/li>'
#         matches = re.findall(pattern, core)
#
#         name = find_core_name(core) # FIXME evil dont care
#         yield name, matches

# def coursesHTMLs_data(htmls: list[str]) -> list[dict]:
#     # TODO unit test number of courses with cores should be same total as without cores
#     # Get list of courses
#     course_list = []
#     for string in htmls:
#         new_course = {}
#
#         find = lambda pattern: re.findall(pattern, string)
#
#         # Course name
#         # Get between the a tags
#         new_course['name'] = find(r'<a[^>]*>([^<]+)<\/a>')[0]  # TODO test case test for more than 1 here
#
#         # TODO Course credit amount
#
#         # Add to the previous course, that this course is in a relationship with it.
#         # Next step is easier this way.
#         if find('>OR<'):
#             course_list[-1]['or'] = True
#
#         # TODO do ands even occur?
#         if find('>AND<'):
#             course_list[-1]['and'] = True
#
#         course_list.append(new_course)
#     return course_list



# def getProgram(_id):
#     cores = id_coresHTMLs(_id)
#
#     htmls2 = cores_coursesHTMLs(cores)
#     # print(list(htmls2))
#     # print(list(htmls2)[0])
#     # print(core)
#     for name, core_htmls in htmls2:
#         # print(name)
#         data = coursesHTMLs_data(core_htmls)
#
#         yield name, data
    # print(data)

# a = getProgram('2531')
# print(a)
# # print(list(program_to_cores(a)))