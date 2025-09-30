import math


def near_int(n, tolerance=1e-6):
    return abs(n - round(n)) < tolerance


def lerp(a, b, t):
    return a + t * (b - a)


def ease_func(mode: str, t: float) -> float:
    match mode:
        case 'zero': return 0
        case 'one': return 1
        case 'linear': return t
        case 'quadIn': return t * t
        case 'quadOut': return 1 - (1 - t) * (1 - t)
        case 'cubicIn': return t * t * t
        case 'cubicOut': return 1 - (1 - t) * (1 - t) * (1 - t)
        case 'quartIn': return t * t * t * t
        case 'quartOut': return 1 - (1 - t) * (1 - t) * (1 - t) * (1 - t)
        case 'sineIn': return 1 - math.cos(t * math.pi / 2)
        case 'sineOut': return math.sin(t * math.pi / 2)
        case 'expoIn': return 2 ** (10 * (t - 1))
        case 'expoOut': return 1 - 2 ** (-10 * t)
        case 'circleIn': return 1 - math.sqrt(1 - t * t)
        case 'circleOut': return math.sqrt(1 - pow(t - 1, 2))
        case _: raise Exception(f'Unknown ease mode: {mode}')
