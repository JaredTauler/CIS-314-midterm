from scrape import getProgram
from factory import processCourseData


for name, html in getProgram('2531'):
    print(name)
    course_data = processCourseData(html)



# for node in c.nodes:
#     print(node)