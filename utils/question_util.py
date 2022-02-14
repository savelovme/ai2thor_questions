import numpy as np
import constants
import random


def get_question_str(question_type, question_object_inds, question_container_ind=None, seed=None):

    object_articles = dict()
    for question_object_ind in question_object_inds:
        object_articles[question_object_ind] = 'a'
        if constants.OBJECTS_SINGULAR[question_object_ind][0] in {'a', 'e', 'i', 'o', 'u'}:
            object_articles[question_object_ind] = 'an'

    if question_container_ind is not None:
        container_article = 'a'
        if constants.OBJECTS_SINGULAR[question_container_ind][0] in {'a', 'e', 'i', 'o', 'u'}:
            container_article = 'an'
        if constants.OBJECTS_SINGULAR[question_container_ind] in {'fridge', 'microwave', 'sink'}:
            container_article = 'the'

        if constants.OBJECTS[question_container_ind] in {'Box', 'GarbageCan', 'Pot', 'Sink', 'Pan'}:
            preposition = 'in'
        else:
            preposition = 'on'

    if seed is not None:
        random.seed(seed)

    if question_type == 'existence':
        question_object_ind = question_object_inds[0]
        object_article = object_articles[question_object_ind]

        template_ind = random.randint(0,5)
        if template_ind == 0:
            return 'Is there %s %s in the room?' % (object_article, constants.OBJECTS_SINGULAR[question_object_ind])
        elif template_ind == 1:
            return 'Please tell me if there is %s %s somewhere in the room.' % (object_article, constants.OBJECTS_SINGULAR[question_object_ind])
        elif template_ind == 2:
            return 'Is there %s %s somewhere in the room?' % (object_article, constants.OBJECTS_SINGULAR[question_object_ind])
        elif template_ind == 3:
            return 'Is there %s %s somewhere nearby?' % (object_article, constants.OBJECTS_SINGULAR[question_object_ind])
        elif template_ind == 4:
            return 'I think %s %s is in the room. Is that correct?' % (object_article, constants.OBJECTS_SINGULAR[question_object_ind])
        elif template_ind == 5:
            return 'Do we have any %s?' % (constants.OBJECTS_PLURAL[question_object_ind])
        else:
            raise Exception('No template')

    elif question_type == 'logical':
        question_object1_ind, operator_ind, question_object2_ind = question_object_inds
        object1_article = object_articles[question_object1_ind]
        object2_article = object_articles[question_object2_ind]

        template_ind = random.randint(0, 4)
        if template_ind == 0:
            return 'Is there %s %s %s %s %s in the room?' \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      constants.LOGICAL_OPERATORS[operator_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])
        elif template_ind == 1:
            return 'Please tell me if there is %s %s %s %s %s  somewhere in the room.' \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      constants.LOGICAL_OPERATORS[operator_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])
        elif template_ind == 2:
            return 'Is there %s %s %s %s %s somewhere in the room?' \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      constants.LOGICAL_OPERATORS[operator_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])
        elif template_ind == 3:
            return 'Is there %s %s %s %s %s somewhere nearby?' \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      constants.LOGICAL_OPERATORS[operator_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])
        elif template_ind == 4:
            return 'I think %s %s %s %s %s is in the room. Is that correct?' \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      constants.LOGICAL_OPERATORS[operator_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])

    elif question_type == 'counting':
        question_object_ind = question_object_inds[0]

        template_ind = random.randint(0, 4)
        if template_ind == 0:
            return 'How many %s are there in the room?' % constants.OBJECTS_PLURAL[question_object_ind]
        elif template_ind == 1:
            return 'There are between 0 and %d %s in the room. How many are there?' % (constants.MAX_COUNTING_ANSWER, constants.OBJECTS_PLURAL[question_object_ind])
        elif template_ind == 2:
            return 'Please tell me how many %s there are somewhere in the room?' % constants.OBJECTS_PLURAL[question_object_ind]
        elif template_ind == 3:
            return 'Please tell me how many %s are around here?' % constants.OBJECTS_PLURAL[question_object_ind]
        elif template_ind == 4:
            return 'Count the number of %s in this room.' % constants.OBJECTS_PLURAL[question_object_ind]
        else:
            raise Exception('No template')

    elif question_type == 'preposition':
        if question_container_ind is None:
            raise Exception('No container for preposition question')

        template_ind = random.randint(0, 1)
        if template_ind == 0:
            return "What is %s %s %s?" % (preposition, container_article, constants.OBJECTS_SINGULAR[question_container_ind])
        elif template_ind == 1:
            return "There is something %s %s %s. What is it?" % (preposition, container_article, constants.OBJECTS_SINGULAR[question_container_ind])

    elif question_type == 'material':

        question_object_ind = question_object_inds[0]
        object_article = object_articles[question_object_ind]

        template_ind = random.randint(0, 1)
        if question_container_ind is None:
            if template_ind == 0:
                return "What material is the %s in the room made of?" \
                       % (constants.OBJECTS_SINGULAR[question_object_ind])
            elif template_ind == 1:
                return "There is %s %s somewhere in the room. What material is it made of?" \
                       % (object_article, constants.OBJECTS_SINGULAR[question_object_ind])
        else:
            if template_ind == 0:
                return "What material is the %s %s %s %s made of?" \
                       % (constants.OBJECTS_SINGULAR[question_object_ind], preposition, container_article,
                          constants.OBJECTS_SINGULAR[question_container_ind])
            elif template_ind == 1:
                return "There must be %s %s %s %s %s. What material is it made of?" \
                       % (object_article, constants.OBJECTS_SINGULAR[question_object_ind], preposition, container_article,
                          constants.OBJECTS_SINGULAR[question_container_ind])

    elif question_type == 'material_compare':
        question_object1_ind, question_object2_ind = question_object_inds
        object1_article = object_articles[question_object1_ind]
        object2_article = object_articles[question_object2_ind]

        template_ind = random.randint(0, 1)
        if template_ind == 0:
            return "Does %s %s share same material as %s %s in the room?" \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])
        elif template_ind == 1:
            return "There is %s %s and a %s %s in the room. Are they made of the same material?" \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])

    elif question_type == 'distance_compare':
        question_object1_ind, question_object2_ind, question_object3_ind = question_object_inds
        object1_article = object_articles[question_object1_ind]
        object2_article = object_articles[question_object2_ind]
        object3_article = object_articles[question_object3_ind]

        template_ind = random.randint(0, 1)
        if template_ind == 0:
            return "Is %s %s closer to %s %s than %s %s in the room?" \
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind],
                      object3_article, constants.OBJECTS_SINGULAR[question_object3_ind])
        elif template_ind == 1:
            return "Is %s %s farther from %s %s than %s %s in the room?" \
                   % (object3_article, constants.OBJECTS_SINGULAR[question_object3_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind],
                      object1_article, constants.OBJECTS_SINGULAR[question_object1_ind])

    elif question_type == 'size_compare':
        question_object1_ind, question_object2_ind = question_object_inds
        object1_article = object_articles[question_object1_ind]
        object2_article = object_articles[question_object2_ind]

        template_ind = random.randint(0, 1)
        if template_ind == 0:
            return "Is %s %s smaller than %s %s in the room?"\
                   % (object1_article, constants.OBJECTS_SINGULAR[question_object1_ind],
                      object2_article, constants.OBJECTS_SINGULAR[question_object2_ind])
        elif template_ind == 1:
            return "Is %s %s bigger than %s %s in the room?" \
                   % (object2_article, constants.OBJECTS_SINGULAR[question_object2_ind],
                      object1_article, constants.OBJECTS_SINGULAR[question_object1_ind])


