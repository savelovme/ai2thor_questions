# AI2-THOR Dataset

The dataset was generated in [AI2-THOR](https://github.com/allenai/ai2thor), a near photo-realistic 3D environment, using its Python API and is based on [IQUAD](https://github.com/danielgordon10/thor-iqa-cvpr-2018). 

## Data

The dataset is available [here](https://drive.google.com/drive/folders/1lR-z9C5rmmZ5pEHh-ici1l2r0aIU6-Vl?usp=sharing)

It totals 269489 questions and is split ted into three parts: train, val/seen_scenes and val/seen_scenes. 
25 kitchen scenes and 36 types of objects in them were used for 8 types of questions.
For single-object questions images and segmentation masks were generated.
Information about splits for questions an be found in Table.

| type                     | train |val/seen|val/unseen | total |
|--------------------------|-------|--------|-----------|-------|
| counting                 | 34257 | 4403   | 7226      | 45886 |
| distance_compare         | 16742 | 3822   | 4031      | 24595 |
| existence                | 12990 | 5251   | 7442      | 25683 |
| logical                  | 31951 | 4584   | 6015      | 42550 | 
| material                 | 16650 | 5431   | 5264      | 27345 |
| material_compare         | 23754 | 3174   | 4163      | 31091 |
| preposition              | 39095 | 1609   | 6083      | 46787 |
| size_compare             | 21341 | 720    | 3491      | 25552 |
