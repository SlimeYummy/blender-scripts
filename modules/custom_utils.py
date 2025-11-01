import math

class ActionMeta:
    raw_start: int
    raw_finish: int
    raw_duration: int
    start: int
    finish: int
    duration: int
    frame_map: dict[int, float]

    def __init__(self, start, finish, remap = [], delete = []):
        self.raw_start = start
        self.raw_finish = finish
        self.raw_duration = finish - start

        frame_map = {}
        counter = 0
        for frame in range(start, finish + 1):
            if frame not in delete:
                self.finish = counter
                frame_map[frame] = counter
            for rng, scale in remap:
                if frame in rng:
                    counter += scale
                    break
            else:
                counter += 1
            counter = ActionMeta.try_int(counter)

        self.start = 0
        self.duration = self.finish - self.start
        self.frame_map = frame_map
    
    def try_int(num: int | float) -> int | float:
        near = round(num)
        if math.isclose(num, near, rel_tol=1e-7, abs_tol=1e-8):
            return near
        return num


action_metas = {
    'RunStart_L90_Empty': ActionMeta(0, 68, [[range(0, 69), 0.5]], [*range(13, 69, 2)]),
    'RunStart_L180_Empty': ActionMeta(0, 72, [[range(0, 73), 0.5]], [*range(17, 73, 2)]),
    'RunStart_R90_Empty': ActionMeta(0, 68, [[range(0, 69), 0.5]], [*range(13, 69, 2)]),
    'RunStart_R180_Empty': ActionMeta(0, 72, [[range(0, 73), 0.5]], [*range(17, 73, 2)]),
    'RunStop_L_Empty': ActionMeta(0, 78, [[range(0, 79), 2 /3]]),
    'RunStop_R_Empty': ActionMeta(0, 78, [[range(0, 79), 2 /3]]),
    'WalkStart_L90_Empty': ActionMeta(0, 68, [[range(0, 69), 0.5]], [*range(15, 69, 2)]),
    'WalkStart_L180_Empty': ActionMeta(0, 72, [[range(0, 73), 0.5]], [*range(19, 73, 2)]),
    'WalkStart_R90_Empty': ActionMeta(0, 68, [[range(0, 69), 0.5]], [*range(15, 69, 2)]),
    'WalkStart_R180_Empty': ActionMeta(0, 72, [[range(0, 73), 0.5]], [*range(19, 73, 2)]),

    'Idle_Axe': ActionMeta(0, 180, [[range(0, 181), 0.5]]),
    'Attack_Idle_L': ActionMeta(0, 40),
    'Attack_Idle_R': ActionMeta(0, 40),
    # 'Attack_1_1': ActionMeta(0, 46, [[range(23, 32), 2/3], [range(38, 44), 1.5]]),
    # 'Attack_1_2': ActionMeta(0, 46, [[range(18, 27), 2/3]]),
    # 'Attack_2_1': ActionMeta(0, 50, []),
    # 'Attack_2_2': ActionMeta(0, 50, []),
    'Attack_01A': ActionMeta(0, 91),
    'Attack_02A': ActionMeta(0, 91),
    'Attack_03A': ActionMeta(0, 85),
    'Attack_04A': ActionMeta(0, 85),
}

def find_action_meta(name):
    meta = action_metas.get(name)
    if not meta:
        raise Exception(f'Meta not found "{name}"')
    return meta
