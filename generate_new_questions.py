from generate_questions import combine_hdf5
from generate_questions import generate_new_existence_questions
from generate_questions import generate_new_logical_questions
from generate_questions import generate_new_counting_questions
from generate_questions import generate_new_material_questions
from generate_questions import generate_new_size_compare_questions
from generate_questions import generate_new_distance_compare_questions
from generate_questions import generate_new_material_compare_questions
from generate_questions import generate_new_preposition_questions

import new_question_to_text

for dataset_type in ['val/seen_scenes', 'val/unseen_scenes', 'train']:
    #generate_new_existence_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'existence')
    #generate_new_logical_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'logical')
    #generate_new_counting_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'counting')
    generate_new_preposition_questions.main(dataset_type)
    combine_hdf5.combine(dataset_type, 'preposition')
    #generate_new_material_compare_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'material_compare')
    #generate_new_material_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'material')
    #generate_new_size_compare_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'size_compare')
    #generate_new_distance_compare_questions.main(dataset_type)
    #combine_hdf5.combine(dataset_type, 'distance_compare')

for dataset_type in ['val/unseen_scenes', 'val/seen_scenes', 'train']:
    generate_new_material_compare_questions.main(dataset_type)
    combine_hdf5.combine(dataset_type, 'material_compare')

new_question_to_text.main()
