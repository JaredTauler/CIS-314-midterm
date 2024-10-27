
class CoreNode:
    def __init__(self, name: str):
        self.name = name

class CourseNode:
    # def link_AND(self):
    #     pass
    # def link_OR(self):
    #     pass
    # TODO id
    # TODO credits
    def __init__(self, name: str, **kwargs):
        self.name = name

    def __repr__(self):
        return self.name


class CollectionNode():
    conditions = {
        'AND',
        'OR',
        None
    }

    # def __init__(self, node, condition):
    #     pass
    def __init__(self, condition):
        self.condition = condition

        self.nodes = []  # Would overcomplicate things to add nodes on init

    def append(self, node):
        self.nodes.append(node)

    def __repr__(self):
        return str([i for i in self.nodes])


# TODO having OR is good enough I think.

# FIXME this feels like it can be done recursively.
master = CollectionNode(None)
current_coll = master
was_or = False
was_and = False
for course in course_list:
    is_or = course.get('or')

    new_course = CourseNode(
        **course
    )

    # In the middle of an OR
    if is_or and was_or:
        current_coll.append(new_course)

    # Starting an OR
    elif is_or:
        was_or = True

        new_coll = CollectionNode('or')

        current_coll.append(new_coll)
        current_coll = new_coll

        current_coll.append(new_course)

    # End of OR
    elif was_or:
        was_or = False
        current_coll.append(new_course)
        current_coll = master

    # No more OR
    else:
        current_coll.append(new_course)

