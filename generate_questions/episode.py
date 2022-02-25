"""A wrapper for engaging with the THOR environment."""
import random

import numpy as np

from utils import game_util
from constants import QUESTION_OBJECT_CLASS_LIST, BUGGED_SCENE_OBJ_PAIRS, MAX_COUNTING_ANSWER, IMAGE_SIZE


class Episode(object):
    """Manages an episode in the THOR env."""

    def __init__(self, image_gen=False):
        """Init function
           Inputs:
        """

        # Start the environment.
        self.env = self.start_env(image_gen)
        self.event = None
        self.is_initialized = False

    def start_env(self, image_gen):
        """Starts the environment."""
        if image_gen:
            env = game_util.create_env(width=IMAGE_SIZE, height=IMAGE_SIZE)
        else:
            env = game_util.create_env(quality='Very Low')
        return env

    def stop_env(self):
        """Stops the env."""
        self.env.stop()

    def get_objects(self):
        return self.event.metadata['objects']

    def initialize_scene(self, scene_name):
        self.scene_name = scene_name
        self.get_env_info()
        print("Initialized", scene_name)

    def get_env_info(self):
        """Get env specific information."""
        event = game_util.reset(self.env, self.scene_name,
                                render_depth_image=False,
                                render_class_image=False,
                                render_object_image=True)
        self.object_id_to_object_class = {
            obj['objectId']: obj['objectType'] for obj in event.metadata['objects']
        }

        self.pickable_object_classes = sorted(list(set([
            obj['objectType'] for obj in event.metadata['objects'] if
            obj['pickupable'] and obj['objectType'] != 'MiscObject'
        ])))
        print('# Pickable object_classes:',
              len(self.pickable_object_classes))

        # Find all receptacles.
        self.receptacles = sorted([
            obj['objectId'] for obj in event.metadata['objects']
            if obj['receptacle']
        ])
        print('# Receptacles:', len(self.receptacles))

        # Find all receptacle classes.
        self.receptacle_classes = list(set([item.split(
            '|')[0] for item in self.receptacles]))
        print('# Receptacle classes:', len(
            self.receptacle_classes))

        # Find all openable receptacles.
        self.openable_receptacles = sorted([
            obj['objectId'] for obj in event.metadata['objects']
            if obj['receptacle'] and obj['openable']
        ])
        print('# Openable Receptacles:', len(self.openable_receptacles))

        # Find all openable receptacle classes.
        self.openable_receptacle_classes = list(set([item.split(
            '|')[0] for item in self.openable_receptacles]))
        print('# Openable object classes:', len(
            self.openable_receptacle_classes))

        # Find all not openable receptacles.
        self.not_openable_receptacles = sorted([
            obj['objectId'] for obj in event.metadata['objects']
            if obj['receptacle'] and not obj['openable']
        ])
        print('# Not openable receptacles:', len(self.not_openable_receptacles))

        # Find all not openable receptacle classes.
        self.not_openable_receptacle_classes = list(set([item.split(
            '|')[0] for item in self.not_openable_receptacles]))
        print('# Not openable receptacles classes:', len(
            self.not_openable_receptacle_classes))

        self.agent_height = event.metadata['agent']['position']['y']

    def initialize_episode(self, scene_seed=None, agent_seed=None, num_duplicates=MAX_COUNTING_ANSWER,
                           max_num_repeats=10, remove_prob=0.25):
        """Initializes environment with given scene and random seed."""
        # Reset the scene with some random seed.
        if scene_seed is None:
            scene_seed = random.randint(0, 999999999)
        # print("Scene seed: ", scene_seed)
        if agent_seed is None:
            agent_seed = random.randint(0, 999999999)
        random.seed(scene_seed)
        self.event = game_util.reset(self.env, self.scene_name,
                                     render_depth_image=False,
                                     render_class_image=False,
                                     render_object_image=True)

        if num_duplicates is None:
            duplicates = None
        else:
            duplicates = [{"objectType": objType, "count": num_duplicates} for objType in QUESTION_OBJECT_CLASS_LIST if
                          random.random() < 1.0 / num_duplicates]
        self.event = self.env.step(action="InitialRandomSpawn", randomSeed=scene_seed,
                                   numDuplicatesOfType=duplicates, numPlacementAttempts=max_num_repeats)

        for obj in self.get_objects():
            if obj['pickupable'] and random.random() < remove_prob:
                if (self.scene_name, obj['objectType']) in BUGGED_SCENE_OBJ_PAIRS:
                    continue
                self.event = self.env.step(action="RemoveFromScene", objectId=obj['objectId'])
                #print("Removed", obj['objectId'])

        self.agent_height = self.event.metadata['agent']['position']['y']

        self.is_initialized = True

        return scene_seed, agent_seed

    def step(self, action_to_take, intercept=True, choose_object='closest', raise_for_failure=False):
        """Take required step and return reward, terminal, success flags.

           intercept: Whether to convert complex actions to basic ones.
           choose_object: When an object interaction command is given, how to
               select the object instance to interact with?
        """
        assert self.is_initialized, "Env not initialized."
        self.event, actual_action = self.env.step(
            action_to_take, intercept, choose_object)
        if raise_for_failure:
            assert self.event.metadata['lastActionSuccess']

    def get_agent_location(self):
        """Gets agent's location."""
        location = np.array([
            self.event.metadata['agent']['position']['x'],
            self.event.metadata['agent']['position']['y'],
            self.event.metadata['agent']['position']['z'],
            self.event.metadata['agent']['rotation']['y'],
            self.event.metadata['agent']['cameraHorizon']
        ])
        return location
