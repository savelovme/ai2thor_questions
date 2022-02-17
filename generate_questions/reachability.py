import numpy as np
from utils import game_util
import constants


def are_reachable(episode, xray_graph, objectIds=[], search_for='all', DEBUG=False):

    scene_bounds = [xray_graph.xMin, xray_graph.yMin,
                    xray_graph.xMax - xray_graph.xMin + 1,
                    xray_graph.yMax - xray_graph.yMin + 1]

    xray_graph.memory[:, :, 1:] = 0

    if len(objectIds) == 1:
        search_for = 'any'

    for obj in episode.get_objects():
        if obj['objectId'] not in objectIds or obj['parentReceptacles'] is None:
            continue
        if DEBUG:
            print(obj['objectId'], 'is in', obj['parentReceptacles'])
        if len(set(obj['parentReceptacles']) & set(episode.openable_receptacles)) > 0:
            if search_for == 'all':
                return False
            continue

        obj_point = game_util.get_object_point(obj, scene_bounds)
        xray_graph.memory[obj_point[1], obj_point[0],
                          constants.OBJECT_CLASS_TO_ID[obj['objectType']] + 1] = 1

    graph_points = xray_graph.points.copy()
    graph_points = graph_points[np.random.permutation(graph_points.shape[0]), :]
    num_checked_points = 0
    for start_point in graph_points:
        headings = np.random.permutation(4)
        for heading in headings:
            start_point = (start_point[0], start_point[1], heading)
            patch = xray_graph.get_graph_patch(start_point)[0]
            if patch[:, :, 1:].max() > 0:
                action = {'action': 'Teleport',
                            'x': start_point[0] * constants.AGENT_STEP_SIZE,
                            'y': episode.agent_height,
                            'z': start_point[1] * constants.AGENT_STEP_SIZE,
                            'rotation': start_point[2] * 90,
                            'horizon': 30,
                            'standing': True
                        }
                if DEBUG:
                    print(f"Teleporting to {action['x']}, {action['y']}, {action['z']}")

                event = episode.env.step(action)
                for obj in event.metadata['objects']:
                    if obj['objectId'] not in objectIds:
                        continue
                    if obj['visible']:
                        if search_for == 'any':
                            return True
                        elif search_for == 'all':
                            obj_point = game_util.get_object_point(obj, scene_bounds)
                            xray_graph.memory[
                                obj_point[1], obj_point[0], constants.OBJECT_CLASS_TO_ID[obj['objectType']] + 1] = 0

                event = episode.env.step(action="LookUp", degrees=60)
                for obj in event.metadata['objects']:
                    if obj['objectId'] not in objectIds:
                        continue
                    if obj['visible']:
                        if search_for == 'any':
                            return True
                        elif search_for == 'all':
                            obj_point = game_util.get_object_point(obj, scene_bounds)
                            xray_graph.memory[
                                obj_point[1], obj_point[0], constants.OBJECT_CLASS_TO_ID[obj['objectType']] + 1] = 0

                num_checked_points += 1
                if num_checked_points > 100:
                    return False
            if np.max(xray_graph.memory[:, :, 1:]) == 0:
                return True

    return False


def get_object_cv2img(episode, xray_graph, object_class):

    scene_bounds = [xray_graph.xMin, xray_graph.yMin,
                    xray_graph.xMax - xray_graph.xMin + 1,
                    xray_graph.yMax - xray_graph.yMin + 1]

    xray_graph.memory[:, :, 1:] = 0

    objectIds = []
    for obj in episode.get_objects():
        if obj['objectType'] != object_class:
            continue
        objectIds.append(obj['objectId'])
        obj_point = game_util.get_object_point(obj, scene_bounds)
        xray_graph.memory[obj_point[1], obj_point[0],
                          constants.OBJECT_CLASS_TO_ID[obj['objectType']] + 1] = 1

    if len(objectIds) == 0: #get image of another object in not_openable_receptacle
        for obj in episode.get_objects():
            if not obj['pickupable'] or obj['objectType'] not in constants.OBJECTS:
                continue
            if len(set(obj['parentReceptacles']) & set(episode.openable_receptacles)) > 0:
                continue
            objectIds.append(obj['objectId'])
            obj_point = game_util.get_object_point(obj, scene_bounds)
            xray_graph.memory[obj_point[1], obj_point[0],
                              constants.OBJECT_CLASS_TO_ID[obj['objectType']] + 1] = 1

    if len(objectIds) == 0:
        return episode.event.frame

    graph_points = xray_graph.points.copy()
    _, x_str, y_str, z_str = objectIds[0].split('|')
    x = float(x_str.replace(',', '.').replace('+', ''))
    z = float(z_str.replace(',', '.').replace('+', ''))
    distances = [abs(p[0]*constants.AGENT_STEP_SIZE - x) + abs(p[1]*constants.AGENT_STEP_SIZE - z) for p in graph_points]
    graph_points = graph_points[np.argsort(distances), :]
    for start_point in graph_points:
        headings = np.random.permutation(4)
        for heading in headings:
            start_point = (start_point[0], start_point[1], heading)
            patch = xray_graph.get_graph_patch(start_point)[0]
            if patch[:, :, 1:].max() > 0:
                action = {'action': 'Teleport',
                            'x': start_point[0] * constants.AGENT_STEP_SIZE,
                            'y': episode.agent_height,
                            'z': start_point[1] * constants.AGENT_STEP_SIZE,
                            'rotation': start_point[2] * 90,
                            'horizon': 30,
                            'standing': True
                        }
                event = episode.env.step(action)
                for obj in event.metadata['objects']:
                    if obj['objectId'] not in objectIds:
                        continue
                    if obj['visible']:
                        return event.cv2img

                event = episode.env.step(action="LookUp")
                for obj in event.metadata['objects']:
                    if obj['objectId'] not in objectIds:
                        continue
                    if obj['visible']:
                        return event.cv2img

    return None#episode.event.cv2img