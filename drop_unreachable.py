import glob
from utils import question_util
import h5py
import cv2
import os
import numpy as np
import random
import constants

from generate_questions.episode import Episode
from graph import graph_obj
from generate_questions.reachability import are_reachable


def main(dataset_type, question_type):

    prefix = 'questions/'
    location = prefix + dataset_type + '/data_' + question_type + '/'

    question_file = location + 'combined.h5'
    checked_file = location + 'checked.h5'

    if not os.path.exists(question_file):
        print(f"File {question_file} not found")
        return
    if os.path.exists(checked_file):
        os.rename(checked_file, location + 'checked_old.h5')

    dataset = h5py.File(question_file)
    dataset_np = dataset['questions/question'][...]

    checked = h5py.File(location + '/checked.h5', 'w')
    checked.create_dataset('questions/question', dataset_np.shape, dtype=np.int32)

    scene_name = None
    data_ind = 0
    episode = Episode()

    for line in dataset_np:

        question_objs = []
        container_ind = None
        if question_type == 'existence':
            scene_num, scene_seed, object_ind, answer = line
            question_objs = [object_ind]
            search_for = 'any'

        elif question_type == 'logical':
            scene_num, scene_seed, object1_ind, operator_ind, object2_ind, answer = line
            question_objs = [object1_ind, object2_ind]
            search_for = 'any'

        elif question_type == 'preposition':
            scene_num, scene_seed, container_ind, answer_ind = line
            question_objs = [answer_ind]
            search_for = 'any'

        elif question_type == 'counting':
            scene_num, scene_seed, object_ind, answer = line
            question_objs = [object_ind]
            search_for = 'all'

        elif question_type == 'material':
            scene_num, scene_seed, object_ind, answer_ind = line
            question_objs = [object_ind]
            search_for = 'any'

        elif question_type == 'material_compare':
            scene_num, scene_seed, object1_ind, object2_ind, answer = line
            question_objs = [object1_ind, object2_ind]
            search_for = 'any'

        elif question_type == 'size_compare':
            scene_num, scene_seed, object1_ind, object2_ind, answer = line
            question_objs = [object1_ind, object2_ind]
            search_for = 'any'

        elif question_type == 'distance_compare':
            scene_num, scene_seed, object1_ind, object2_ind, object3_ind, answer = line
            question_objs = [object1_ind, object2_ind, object3_ind]
            search_for = 'all'

        if scene_name != 'FloorPlan%d' % scene_num:
            scene_name = 'FloorPlan%d' % scene_num
            episode.initialize_scene(scene_name)
            positions = episode.env.step(
                action="GetReachablePositions"
            ).metadata["actionReturn"]
            reachable_points = np.array([[p['x'], p['z']] for p in positions])

            xray_graph = graph_obj.Graph(reachable_points, use_gt=True, construct_graph=False)

        if any([object_ind==0 for object_ind in question_objs]):
            continue

        episode.initialize_episode(scene_seed=scene_seed)

        reachable = []
        for object_ind in question_objs:
            if container_ind is not None:
                parents = [parent for parent in episode.get_objects()
                           if parent['objectType'] == constants.RECEPTACLES[container_ind] and parent['receptacleObjectIds'] is not None]
                objectIds = [objId for parent in parents for objId in parent['receptacleObjectIds'] if
                             objId.split('|')[0] == constants.OBJECTS[object_ind]]
            else:
                objectIds = [obj['objectId'] for obj in episode.get_objects() if
                             obj['objectType'] == constants.OBJECTS[object_ind]]
            reachable.append(are_reachable(episode, xray_graph, objectIds, search_for))

        if question_type == 'existence':
            if bool(answer) != all(reachable):
                continue
        elif question_type == 'logical':
            if constants.LOGICAL_OPERATORS[operator_ind] == 'and' and not all(reachable):
                continue
            elif constants.LOGICAL_OPERATORS[operator_ind] == 'or' and not any(reachable):
                continue
        elif not all(reachable):
            continue

        checked['questions/question'][data_ind, :] = line
        data_ind += 1
        checked.flush()

    episode.env.stop_unity()


if __name__ == '__main__':
    for dataset_type in ['train', 'val/unseen_scenes', 'val/seen_scenes']:
        for question_type in ['existence', 'logical', 'counting', 'preposition',
                              'material', 'material_compare', 'size_compare', 'distance_compare']:
            main(dataset_type, question_type)



