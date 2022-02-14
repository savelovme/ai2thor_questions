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
from generate_questions.new_questions import MaterialQuestion
from generate_questions.check_reachability import are_reachable

import constants

all_object_classes = constants.OBJECTS #QUESTION_OBJECT_CLASS_LIST

DEBUG = True
if DEBUG:
    PARALLEL_SIZE = 1
else:
    PARALLEL_SIZE = 8


def main(dataset_type):
    if dataset_type == 'val/unseen_scenes':
        num_questions_per_scene = round(24.0 / PARALLEL_SIZE)
        scene_numbers = constants.TEST_SCENE_NUMBERS
        num_samples_per_scene = 4
    elif dataset_type == 'val/seen_scenes':
        num_questions_per_scene = round(12.0 / PARALLEL_SIZE)
        scene_numbers = constants.TRAIN_SCENE_NUMBERS
        num_samples_per_scene = 4
    elif dataset_type == 'train':
        num_questions_per_scene = round(24.0 / PARALLEL_SIZE)
        scene_numbers = constants.TRAIN_SCENE_NUMBERS
        num_samples_per_scene = 4
    else:
        raise Exception('No test set found')
    num_record = int(num_samples_per_scene * np.ceil(num_questions_per_scene * 1.0 / num_samples_per_scene) * len(scene_numbers))

    assert(num_samples_per_scene % 4 == 0)

    def create_dump():
        time_str = py_util.get_time_str()
        prefix = 'questions/'
        if not os.path.exists(prefix + dataset_type + '/data_material'):
            os.makedirs(prefix + dataset_type + '/data_material')

        h5 = h5py.File(prefix + dataset_type + '/data_material/Material_Questions_' + time_str + '.h5', 'w')
        h5.create_dataset('questions/question', (num_record, 4), dtype=np.int32)
        print('--------------------------------------')
        print('Generating %d material questions' % num_record)
        print('--------------------------------------')

        # Generate material questions
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
                object_class = random.choice(all_object_classes)
                question = MaterialQuestion(object_class)  # randomly generate a general material question

                num_tries += 1

                grid_file = 'layouts/%s-layout.npy' % scene_name
                xray_graph = graph_obj.Graph(grid_file, use_gt=True, construct_graph=False)
                scene_bounds = [xray_graph.xMin, xray_graph.yMin,
                    xray_graph.xMax - xray_graph.xMin + 1,
                    xray_graph.yMax - xray_graph.yMin + 1]

                for i in range(10):  # try 10 times
                    scene_seed = random.randint(0, 999999999)
                    episode.initialize_episode(scene_seed=scene_seed)  # randomly initialize the scene
                    answer = question.get_answer(episode)

                    if answer in constants.QUESTION_MATERIALS:
                        # Make sure findable
                        objectIds = [obj['objectId'] for obj in episode.event.metadata['objects'] if obj['objectType']==object_class]
                        if not are_reachable(episode, xray_graph, objectIds=objectIds, search_for='any', DEBUG=DEBUG):
                            answer = None

                    print(str(question), answer)

                    if answer in constants.QUESTION_MATERIALS:
                        h5['questions/question'][data_ind, :] = np.array([scene_num, scene_seed, constants.OBJECT_CLASS_TO_ID[object_class], constants.MATERIAL_TO_ID[answer]])
                        data_ind += 1
                        k += 1
                        h5.flush()
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
