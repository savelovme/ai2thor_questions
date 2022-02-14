import pdb
import random
import numpy as np
from utils import game_util, question_util

from constants import OBJECT_CLASS_TO_ID, OBJECTS_SINGULAR, AGENT_STEP_SIZE, LOGICAL_OPERATOR_TO_ID, MIN_SIZE_DIFF


class Question(object):
    def __init__(self):
        pass
    def get_answer(self, episode):
        raise NotImplementedError
    def __str__(self):
        raise NotImplementedError


class ExistenceQuestion(Question):
    def __init__(self, object_class, parent_object_class = None):
        super(ExistenceQuestion, self).__init__()
        #assert parent_object_class is None or object_class.name in parent_object_class.children

        self.object_class = object_class
        self.parent_object_class = parent_object_class
        if parent_object_class == 'TableTop':
            self.preposition='on'
        else:
            self.preposition = 'in'

    def get_answer(self, episode):
        """ Get answer to the question given an episode """
        if self.parent_object_class is None:
            # parent_object_class is None. Question becomes "Is there an [object_class] in the room?"
            if self.object_class in [obj['objectType'] for obj in episode.get_objects()]:
                return True
            else:
                return False
        elif (self.parent_object_class in episode.not_openable_receptacle_classes):
            # parent_object_class is receptacle. Question becomes "Is there an [object_class] on/in [parent_object_class]?"
            # the question is valid only when the obj/parent_obj is a valid combination for this scene
            parent_objects = [obj for obj in episode.get_objects() if obj['objectType'] == self.parent_object_class]
            for parent_object in parent_objects:
                if self.object_class in [obj.split('|')[0] for obj in parent_object['receptacleObjectIds']]:
                    return True
            return False
        else:
            return None
            #raise Exception("Invalid combination: {} and {}!".format(self.object_class, self.parent_object_class))

    def __str__(self):
        """ Get the string representation of the question """
        if self.parent_object_class is None:
            return question_util.get_question_str('existence', [OBJECT_CLASS_TO_ID[self.object_class]])
        else:
            return question_util.get_question_str('existence', [OBJECT_CLASS_TO_ID[self.object_class]], OBJECT_CLASS_TO_ID[self.parent_object_class])

class LogicalQuestion(Question):
    def __init__(self, object1_class, operator, object2_class):
        super(LogicalQuestion, self).__init__()
        assert operator in ('and', 'or')

        self.object1_class = object1_class
        self.operator = operator
        self.object2_class = object2_class

    def get_answer(self, episode):
        """ Get answer to the question given an episode """
        #"Is there an [object1_class] and/or [object2_class] in the room?"
        episode_objects = [obj['objectType'] for obj in episode.get_objects()]
        if self.operator == 'and':
            return self.object1_class in episode_objects and self.object2_class in episode_objects
        elif self.operator == 'or':
            return self.object1_class in episode_objects or self.object2_class in episode_objects

    def __str__(self):
        """ Get the string representation of the question """
        return question_util.get_question_str('logical', [OBJECT_CLASS_TO_ID[self.object1_class], LOGICAL_OPERATOR_TO_ID[self.operator], OBJECT_CLASS_TO_ID[self.object2_class]])


class PrepositionQuestion(Question):
    def __init__(self, parent_object_class):
        super(PrepositionQuestion, self).__init__()
        #assert len(parent_object_class.children) == 1

        self.parent_object_class = parent_object_class
        if parent_object_class in {'Box', 'GarbageCan', 'Pot', 'Sink', 'Pan'}:
            self.preposition = 'in'
        else:
            self.preposition = 'on'

    def get_answer(self, episode):
        """ Get answer to the question given an episode """
        if self.parent_object_class in episode.not_openable_receptacle_classes:
            # " What is on/in [parent_object_class]?"
            parents = [parent for parent in episode.get_objects()
                       if parent['objectType'] == self.parent_object_class and parent['receptacleObjectIds'] is not None]
            children = [objId.split('|')[0] for parent in parents for objId in parent['receptacleObjectIds']]
            if len(children) == 1:
                return children[0]
            else:
                return None
                #Uncertainty or no children
        else:
            return None
            #raise Exception("Invalid combination: {} and {}!".format(self.object_class, self.parent_object_class))

    def __str__(self):
        """ Get the string representation of the question """
        return question_util.get_question_str('preposition', [], OBJECT_CLASS_TO_ID[self.parent_object_class])


class MaterialQuestion(Question):
    def __init__(self, object_class, parent_object_class = None):
        super(MaterialQuestion, self).__init__()
        #assert parent_object_class is None or object_class.name in parent_object_class.children

        self.object_class = object_class
        self.parent_object_class = parent_object_class

    def get_answer(self, episode):
        """ Get answer to the question given an episode """
        if self.parent_object_class is None:
            # "What material is [object_class] in the room made of"
            objects = [obj for obj in episode.get_objects() if obj['objectType'] == self.object_class]
            if len(objects) > 0:
                materials = objects[0]['salientMaterials']
                if materials is None:
                    return None
                if len(materials) == 1:
                    return materials[0]
            return None
            # Uncertainty or no valid objects

        elif self.parent_object_class in episode.not_openable_receptacle_classes:
            # parent_object_class is receptacle. Question becomes "What material is [object_class] on/in [parent_object_class]?"
            childIds = [objId for parent in episode.get_objects() for objId in parent['receptacleObjectIds']
                        if parent['objectType'] == self.parent_object_class]
            if len(childIds) == 1:
                obj = [obj for obj in episode.get_objects() if obj['objectId'] == childIds[0]][0]
                materials = obj['salientMaterials']
                if len(materials) == 1:
                    return materials[0]
            return None
                # Uncertainty or no valid objects
        else:
            return None
            #raise Exception("Invalid combination: {} and {}!".format(self.object_class, self.parent_object_class))

    def __str__(self):
        """ Get the string representation of the question """
        if self.parent_object_class is None:
            return question_util.get_question_str('material', [OBJECT_CLASS_TO_ID[self.object_class]])
        else:
            return question_util.get_question_str('material', [OBJECT_CLASS_TO_ID[self.object_class]], OBJECT_CLASS_TO_ID[self.parent_object_class])




class MaterialCompareQuestion(Question):
    def __init__(self, object1_class, object2_class):
        super(MaterialCompareQuestion, self).__init__()

        self.object1_class = object1_class
        self.object2_class = object2_class

    def get_answer(self, episode):
        # "Does [object1_class] share the same materials as [object2_class] in the room"
        objects1 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object1_class]
        objects2 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object2_class]

        if len(objects1) > 0 and len(objects2) > 0:
            materials1 = objects1[0]['salientMaterials']
            materials2 = objects2[0]['salientMaterials']
            if materials1 is None or materials2 is None:
                return None
            if len(materials1) > 0 and len(materials2) > 0:
                return set(materials1) == set(materials2)
        return None
            #Invalid objects

    def __str__(self):
        return question_util.get_question_str('material_compare', [OBJECT_CLASS_TO_ID[self.object1_class], OBJECT_CLASS_TO_ID[self.object2_class]])


class SizeCompareQuestion(Question):
    def __init__(self, object1_class, object2_class):
        super(SizeCompareQuestion, self).__init__()

        self.object1_class = object1_class
        self.object2_class = object2_class

    def get_answer(self, episode):
        # "Is [object1_class] smaller than [object2_class] in the room?"
        objects1 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object1_class]
        objects2 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object2_class]

        if objects1 and objects2:
            size1 = objects1[0]['axisAlignedBoundingBox']['size']
            size2 = objects2[0]['axisAlignedBoundingBox']['size']

            if (abs(size1['x'] - size2['x']) + abs(size1['y'] - size2['y']) + abs(size1['z'] - size2['z']) < MIN_SIZE_DIFF) \
                    or (abs(size1['x'] - size2['z']) + abs(size1['y'] - size2['y']) + abs(size1['z'] - size2['x']) < MIN_SIZE_DIFF):
                return None # Too close to differ
            elif (size1['x'] <= size2['x'] and size1['y'] <= size2['y'] and size1['z'] <= size2['z']) \
                    or (size1['x'] <= size2['z'] and size1['y'] <= size2['y'] and size1['z'] <= size2['x']):
                return True
            elif (size1['x'] >= size2['x'] and size1['y'] >= size2['y'] and size1['z'] >= size2['z']) \
                    or (size1['x'] >= size2['z'] and size1['y'] >= size2['y'] and size1['z'] >= size2['x']):
                return False

        return None
            #Uncertainty or invalid objects

    def __str__(self):
        return question_util.get_question_str('size_compare', [OBJECT_CLASS_TO_ID[self.object1_class], OBJECT_CLASS_TO_ID[self.object2_class]])


class DistanceCompareQuestion(Question):
    def __init__(self, object1_class, object2_class, object3_class):
        super(DistanceCompareQuestion, self).__init__()

        self.object1_class = object1_class
        self.object2_class = object2_class
        self.object3_class = object3_class

    def get_answer(self, episode):
        # "Is [object1_class] closer to [object2_class] than [object3_class] in the room?"
        objects1 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object1_class]
        objects2 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object2_class]
        objects3 = [obj for obj in episode.get_objects() if obj['objectType'] == self.object3_class]

        if objects1 is None or objects2 is None or objects3 is None:
            return None

        if len(objects1) == 1 and len(objects2) == 1 and len(objects3) == 1:
            dist_12 = game_util.euclidean_dist(objects1[0], objects2[0])
            dist_23 = game_util.euclidean_dist(objects2[0], objects3[0])

            if abs(dist_12 - dist_23) < MIN_SIZE_DIFF:
                return None #Too close to differ,
            return dist_12 < dist_23

        return None
            #Uncertainty or invalid objects

    def __str__(self):
        return question_util.get_question_str('distance_compare', [OBJECT_CLASS_TO_ID[self.object1_class],
                                                                   OBJECT_CLASS_TO_ID[self.object2_class],
                                                                   OBJECT_CLASS_TO_ID[self.object3_class]])


class CountQuestion(Question):
    def __init__(self, object_class, parent_object_class = None):
        super(CountQuestion, self).__init__()
        # assert(parent_object_class is None or object_class.name in parent_object_class.children)

        self.object_class = object_class
        self.parent_object_class = parent_object_class
        if parent_object_class is None:
            self.preposition = 'in'
        elif parent_object_class in {'Box', 'GarbageCan', 'Pot', 'Sink', 'Pan'}:
            self.preposition = 'in'
        else:
            self.preposition = 'on'

    def get_answer(self, episode):
        """ Get answer to the question given an episode """
        if self.parent_object_class is None:
            # parent_object_class is None. Question becomes "Is there an [object_class] in the room?"
            return len([obj for obj in episode.get_objects() if obj['objectType'] == self.object_class])
        elif self.parent_object_class.name in episode.not_openable_receptacle_classes:
            total_count = 0
            # parent_object_class is not openable. Question becomes "Is there an [object_class] on/in [parent_object_class]?"
            parent_objects = [obj for obj in episode.get_objects() if obj['objectType'] == self.parent_object_class.name]
            for parent_object in parent_objects:
                total_count += len([obj for obj in parent_object['receptacleObjectIds'] if obj.split('|')[0] == self.object_class.name])
            return total_count
        else:
            raise Exception("there is no {} in the scene!".format(self.parent_object_class.name))

    def __str__(self):
        """ Get the string representation of the question """
        if self.parent_object_class is None:
            return question_util.get_question_str('counting', [OBJECT_CLASS_TO_ID[self.object_class]])
        else:
            return game_util.get_question_str(1, OBJECT_CLASS_TO_ID[self.object_class], OBJECT_CLASS_TO_ID[self.parent_object_class])
