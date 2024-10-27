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


def id_coresHTMLs(_id) -> list[str]:
    # Get program details
    html = debug_fetch(URL_PREVIEW + _id)

    # Get cores
    # acalog-core(?:.(?!acalog-core))+\/ul
    pattern = r'acalog-core.*?<\/ul>'
    matches = re.findall(pattern, html)

    return matches

def find_core_name(html: str) -> str:
    a = re.findall(
        '/a>([^<]+)(?:.(?!/a))+h2', # FIXME god awful
        html
    )

    return a[0] # TODO what if more than 1? testcase

def cores_coursesHTMLs(htmls: list[str]) -> tuple[str, list[str]]:
    for core in htmls:
        # Get courses
        pattern = r'acalog-course.*?<\/li>'
        matches = re.findall(pattern, core)

        name = find_core_name(core) # FIXME evil dont care
        yield name, matches

def coursesHTMLs_data(htmls: list[str]) -> list[dict]:
    # TODO unit test number of courses with cores should be same total as without cores
    # Get list of courses
    course_list = []
    for string in htmls:
        new_course = {}

        find = lambda pattern: re.findall(pattern, string)

        # Course name
        # Get between the a tags
        new_course['name'] = find(r'<a[^>]*>([^<]+)<\/a>')[0]  # TODO test case test for more than 1 here

        # TODO Course credit amount

        # Add to the previous course, that this course is in a relationship with it.
        # Next step is easier this way.
        if find('>OR<'):
            course_list[-1]['or'] = True

        # TODO do ands even occur?
        if find('>AND<'):
            course_list[-1]['and'] = True

        course_list.append(new_course)
    return course_list



def getProgram(_id):
    cores = id_coresHTMLs(_id)

    htmls2 = cores_coursesHTMLs(cores)
    # print(list(htmls2))
    # print(list(htmls2)[0])
    # print(core)
    for name, core_htmls in htmls2:
        # print(name)
        data = coursesHTMLs_data(core_htmls)

        yield name, data
    # print(data)

# a = getProgram('2531')
# print(a)
# # print(list(program_to_cores(a)))