import glob
from utils import question_util
import h5py
import os
import random
import constants


def main():
    question_files = sorted(glob.glob('questions/*/*/*h5')+glob.glob('questions/*/*/*/*h5'))

    vocab = set()

    max_sentence_length = 0
    for file_name in question_files:
        out_file = open(os.path.splitext(file_name)[0] + '.csv', 'w')

        print('Processing file', file_name)
        out_file.write('question_type;scene_number;seed;question;answer;question_object_ids;container_id;image_path\n')
        if 'data_existence' in file_name:
            question_type = 'existence'
        elif 'data_logical' in file_name:
            question_type = 'logical'
        elif 'data_preposition' in file_name:
            question_type = 'preposition'
        elif 'data_counting' in file_name:
            question_type = 'counting'
        elif 'data_material_compare' in file_name:
            question_type= 'material_compare'
        elif 'data_material' in file_name:
            question_type = 'material'
        elif 'data_size_compare' in file_name:
            question_type= 'size_compare'
        elif 'data_distance_compare' in file_name:
            question_type= 'distance_compare'

        dataset = h5py.File(file_name)
        dataset_np = dataset['questions/question'][...]
        for line in dataset_np:
            question_objs = []
            container_ind = None
            image = None
            if question_type == 'existence':
                scene_num, scene_seed, object_ind, answer = line
                question_objs = [object_ind]
                answer = str(bool(answer))
                image = f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.OBJECTS[object_ind]}.png"

            elif question_type == 'logical':
                scene_num, scene_seed, object1_ind, operator_ind, object2_ind, answer = line
                question_objs = [object1_ind, operator_ind, object2_ind]
                answer = str(bool(answer))

            elif question_type == 'preposition':
                scene_num, scene_seed, container_ind, answer_ind = line
                question_objs = []
                answer = constants.OBJECTS[answer_ind]
                image = f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.RECEPTACLES[container_ind]}.png"

            elif question_type == 'counting':
                scene_num, scene_seed, object_ind, answer = line
                question_objs = [object_ind]
                answer = str(int(answer))

            elif question_type == 'material':
                scene_num, scene_seed, object_ind, answer_ind = line
                question_objs = [object_ind]
                answer = constants.QUESTION_MATERIALS[answer_ind]
                image = f"images/{question_type}/FloorPlan{scene_num}/{scene_seed}_{constants.OBJECTS[object_ind]}.png"

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

            question_str = question_util.get_question_str(question_type, question_objs, container_ind, seed=scene_seed)
            parsed_question = question_str.replace('.', '').replace('?', '').lower().split(' ')
            max_sentence_length = max(len(parsed_question), max_sentence_length)
            vocab.update(parsed_question)

            if image and not os.path.exists(image):
                image = None

            if container_ind is None:
                container_ind = len(constants.OBJECTS)
            out_file.write('%s;%d;%d;%s;%s;%s;%d;%s\n' % (question_type, scene_num, scene_seed, question_str, answer, question_objs, container_ind, image))
            out_file.flush()
        print('Generated %d sentences for %s' % (dataset_np.shape[0], file_name))

    with open('vocabulary.txt', 'w') as ff:
        ff.write('\n'.join(sorted(list(vocab))))

    print('max sentence length', max_sentence_length)


if __name__ == '__main__':
    main()

