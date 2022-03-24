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
from generate_questions.reachability import get_object_cv2img


def main(question_type):

    question_files = sorted(glob.glob('questions/*/data_'+question_type+'/combined.h5')
                            + glob.glob('questions/*/*/data_'+question_type+'/combined.h5'))

    episode = Episode(image_gen=True)

    for file_name in question_files:
        print('Processing file', file_name)

        dataset = h5py.File(file_name)
        dataset_np = dataset['questions/question'][...]

        scene_name = None

        for line in dataset_np:
            if all(line == 0):
                continue
            question_objs = []
            container_ind = None
            if question_type == 'existence':
                scene_num, scene_seed, object_ind, answer = line
                question_objs = [object_ind]
                images = [f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.OBJECTS[object_ind]}.png"]
                masks = [f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.OBJECTS[object_ind]}_segmentation.png"]


            elif question_type == 'logical':
                scene_num, scene_seed, object1_ind, operator_ind, object2_ind, answer = line
                question_objs = [object1_ind, object2_ind]

            elif question_type == 'preposition':
                scene_num, scene_seed, container_ind, answer_ind = line
                question_objs = [answer_ind]
                images = [f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.RECEPTACLES[container_ind]}.png"]
                masks = [f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.RECEPTACLES[container_ind]}_segmentation.png"]

            #elif question_type == 'counting':
            #    scene_num, scene_seed, object_ind, answer = line
            #    question_objs = [object_ind]

            elif question_type == 'material':
                scene_num, scene_seed, object_ind, answer_ind = line
                question_objs = [object_ind]
                images = [f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.OBJECTS[object_ind]}.png"]
                masks = [f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.OBJECTS[object_ind]}_segmentation.png"]

            elif question_type == 'material_compare':
                scene_num, scene_seed, object1_ind, object2_ind, answer = line
                question_objs = [object1_ind, object2_ind]
                answer = str(bool(answer))

            elif question_type == 'size_compare':
                scene_num, scene_seed, object1_ind, object2_ind, answer = line
                question_objs = [object1_ind, object2_ind]
                answer = str(bool(answer))

            elif question_type == 'distance_compare':
                scene_num, scene_seed, object1_ind, object2_ind, object3_ind, answer = line
                question_objs = [object1_ind, object2_ind, object3_ind]
                answer = str(bool(answer))

            if scene_name != 'FloorPlan%d' % scene_num:
                scene_name = 'FloorPlan%d' % scene_num
                episode.initialize_scene(scene_name)
                #grid_file = 'layouts/%s-layout.npy' % scene_name
                positions = episode.env.step(
                    action="GetReachablePositions"
                ).metadata["actionReturn"]
                reachable_points = np.array([[p['x'], p['z']] for p in positions])

                xray_graph = graph_obj.Graph(reachable_points, use_gt=True, construct_graph=False)

            if any([object_ind==0 for object_ind in question_objs]):
                continue

            if all([os.path.exists(filename) for filename in images+masks]):
                continue

            episode.initialize_episode(scene_seed=scene_seed)

            for object_ind, image_name, mask_name in zip(question_objs, images, masks):
                if container_ind is not None:
                    image, masks = get_object_cv2img(episode, xray_graph, constants.OBJECTS[object_ind], constants.RECEPTACLES[container_ind])
                else:
                    image, masks = get_object_cv2img(episode, xray_graph, constants.OBJECTS[object_ind])
                cv2.imwrite(image_name, image)
                cv2.imwrite(mask_name, masks)

    episode.env.stop_unity()


if __name__ == '__main__':
    main('material')


