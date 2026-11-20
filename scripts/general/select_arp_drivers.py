import arp_ops
import importlib

importlib.reload(arp_ops)


# cfg_include_fingers = True
cfg_include_fingers = False

cfg_include_weapons = True
# cfg_include_weapons = False

arp_ops.select_arp_drivers(include_fingers=cfg_include_fingers, include_weapons=cfg_include_weapons)
