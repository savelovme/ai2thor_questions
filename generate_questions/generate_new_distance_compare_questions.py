import pdb
import os
import time
from generate_questions.episode import Episode
import random
import numpy as np
import h5py
import multiprocessing
from utils import game_util
from utils import py_util
from graph import graph_obj
from generate_questions.new_questions import DistanceCompareQuestion
from generate_questions.reachability import are_reachable

import constants

all_object_classes = constants.OBJECTS

DEBUG = False
if DEBUG:
    PARALLEL_SIZE = 1
else:
    PARALLEL_SIZE = 12


def main(dataset_type):
    if dataset_type == 'val/unseen_scenes':
        num_questions_per_scene = round(1000.0 / PARALLEL_SIZE)
        scene_numbers = constants.TEST_SCENE_NUMBERS
        num_samples_per_scene = 8
    elif dataset_type == 'val/seen_scenes':
        num_questions_per_scene = round(100.0 / PARALLEL_SIZE)
        scene_numbers = constants.TRAIN_SCENE_NUMBERS
        num_samples_per_scene = 4
    elif dataset_type == 'train':
        num_questions_per_scene = round(1000.0 / PARALLEL_SIZE)
        scene_numbers = constants.TRAIN_SCENE_NUMBERS
        num_samples_per_scene = 8
    else:
        raise Exception('No test set found')
    num_record = int(num_samples_per_scene * np.ceil(num_questions_per_scene * 1.0 / num_samples_per_scene) * len(scene_numbers))

    assert(num_samples_per_scene % 4 == 0)

    def create_dump():
        time_str = py_util.get_time_str()
        prefix = 'questions/'
        if not os.path.exists(prefix + dataset_type + '/data_distance_compare'):
            os.makedirs(prefix + dataset_type + '/data_distance_compare')

        h5 = h5py.File(prefix + dataset_type + '/data_distance_compare/Distance_Compare_Questions_' + time_str + '.h5', 'w')
        h5.create_dataset('questions/question', (num_record, 6), dtype=np.int32)
        print('--------------------------------------')
        print('Generating %d distance_compare questions' % num_record)
        print('--------------------------------------')

        # Generate distance_compare questions
        data_ind = 0
        episode = Episode()
        scene_number = -1
        while data_ind < num_record:
            k = 0

            scene_number += 1
            scene_num = scene_numbers[scene_number % len(scene_numbers)]

            scene_name = 'FloorPlan%d' % scene_num
            episode.initialize_scene(scene_name)
            num_tries = 0
            while k < num_samples_per_scene and num_tries < 10 * num_samples_per_scene:
                # randomly pick a pickable object in the scene
                object1_class, object2_class, object3_class = random.sample(all_object_classes, 3)
                question = DistanceCompareQuestion(object1_class, object2_class, object3_class)  # randomly generate a general distance_compare question

                num_tries += 1

                positions = episode.env.step(
                    action="GetReachablePositions"
                ).metadata["actionReturn"]
                reachable_points = np.array([[p['x'], p['z']] for p in positions])
                xray_graph = graph_obj.Graph(reachable_points, use_gt=True, construct_graph=False)

                for i in range(20):  # try 20 times
                    scene_seed = random.randint(0, 999999999)
                    episode.initialize_episode(scene_seed=scene_seed)#, num_duplicates=None, remove_prob=0)  # randomly initialize the scene
                    answer = question.get_answer(episode)

                    if answer is not None:
                        # Make sure findable
                        objectIds = [obj['objectId'] for obj in episode.event.metadata['objects'] if
                                      obj['objectType'] in (object1_class, object2_class, object3_class)]

                        if not are_reachable(episode, xray_graph, objectIds=objectIds, search_for='all', DEBUG=DEBUG):
                            answer = None

                    print(str(question), answer)

                    if answer is not None:
                        h5['questions/question'][data_ind, :] = np.array(
                            [scene_num, scene_seed, constants.OBJECT_CLASS_TO_ID[object1_class],
                             constants.OBJECT_CLASS_TO_ID[object2_class], constants.OBJECT_CLASS_TO_ID[object3_class], answer])
                        h5.flush()
                        data_ind += 1
                        k += 1
                        break
                print("# generated samples: {}".format(data_ind))

        h5.close()
        episode.env.stop_unity()

    if DEBUG:
        create_dump()
    else:
        procs = []
        for ps in range(PARALLEL_SIZE):
            proc = multiprocessing.Process(target=create_dump)
            proc.start()
            procs.append(proc)
            time.sleep(1)
        for proc in procs:
            proc.join()

if __name__ == '__main__':
    main('train')
    main('val/unseen_scenes')
    main('val/seen_scenes')
