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







def id_coresHTMLs(_id) -> []:
    # Get program details
    html = debug_fetch(URL_PREVIEW + _id)

    # Get cores
    # acalog-core(?:.(?!acalog-core))+\/ul
    pattern = r'acalog-core.*?<\/ul>'
    matches = re.findall(pattern, html)

    return matches

def cores_coursesHTMLs(htmls: list[str]) -> dict:
    for core in htmls:
        # Get courses
        pattern = r'acalog-course.*?<\/li>'
        matches = re.findall(pattern, core)

        yield matches

def coursesHTMLs_data(htmls: [str]):
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

        # TODO do ands occur?
        if find('>AND<'):
            course_list[-1]['and'] = True

        course_list.append(new_course)
    return course_list

def getProgram(_id):
    htmls1 = id_coresHTMLs(_id)
    # for core in htmls1:
    htmls2 = cores_coursesHTMLs(htmls1)
    # print(list(htmls2)[0])
    # print(core)
    for core_htmls in htmls2:
        data = coursesHTMLs_data(core_htmls)
        print(data)
    # print(data)

a = getProgram('2531')
print(a)
# print(list(program_to_cores(a)))