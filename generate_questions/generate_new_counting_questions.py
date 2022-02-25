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
from generate_questions.new_questions import CountQuestion
from generate_questions.reachability import are_reachable


import constants

all_object_classes = constants.QUESTION_OBJECT_CLASS_LIST

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
        if not os.path.exists(prefix + dataset_type + '/data_counting'):
            os.makedirs(prefix + dataset_type + '/data_counting')

        h5 = h5py.File(prefix + dataset_type + '/data_counting/Counting_Questions_' + time_str + '.h5', 'w')
        h5.create_dataset('questions/question', (num_record, 4), dtype=np.int32)
        print('Generating %d counting questions' % num_record)

        # Generate counting questions
        data_ind = 0
        episode = Episode()
        scene_number = random.randint(0, len(scene_numbers) - 1)
        while data_ind < num_record:
            k = 0

            scene_number += 1
            scene_num = scene_numbers[scene_number % len(scene_numbers)]

            scene_name = 'FloorPlan%d' % scene_num
            episode.initialize_scene(scene_name)
            num_tries = 0
            while num_tries < num_samples_per_scene:
                # randomly pick a pickable object in the scene
                object_class = random.choice(all_object_classes)
                question = CountQuestion(object_class)  # randomly generate a general counting question
                generated = [None] * (constants.MAX_COUNTING_ANSWER + 1)
                generated_counts = set()

                num_tries += 1

                positions = episode.env.step(
                    action="GetReachablePositions"
                ).metadata["actionReturn"]
                reachable_points = np.array([[p['x'], p['z']] for p in positions])
                xray_graph = graph_obj.Graph(reachable_points, use_gt=True, construct_graph=False)

                for i in range(100):
                    if DEBUG:
                        print('starting try ', i)
                    scene_seed = random.randint(0, 999999999)
                    episode.initialize_episode(scene_seed=scene_seed)
                    answer = question.get_answer(episode)
                    object_target = constants.OBJECT_CLASS_TO_ID[object_class]

                    if 0 < answer < len(generated) and answer not in generated_counts:
                        if DEBUG:
                            print('target', str(question), object_target, answer)

                        # Make sure findable
                        objectIds = [obj['objectId'] for obj in episode.event.metadata['objects'] if
                                     obj['objectType'] == object_class]
                        if not are_reachable(episode, xray_graph, objectIds=objectIds, search_for='all', DEBUG=DEBUG):
                            answer = None

                    print(str(question), answer)

                    if answer is not None and answer < len(generated) and answer not in generated_counts:
                        generated[answer] = [scene_num, scene_seed, constants.OBJECT_CLASS_TO_ID[object_class], answer]
                        generated_counts.add(answer)
                        print('\tcounts', sorted(list(generated_counts)))

                    if len(generated_counts) == len(generated):
                        for q in generated:
                            if data_ind >= h5['questions/question'].shape[0]:
                                num_tries = 2**32
                                break
                            h5['questions/question'][data_ind, :] = np.array(q)
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
            procs.append(proc)
            proc.start()
            time.sleep(1)
        for proc in procs:
            proc.join()


if __name__ == '__main__':
    main('train')
    main('val/unseen_scenes')
    main('val/seen_scenes')
