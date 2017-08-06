import ugfx
lenny = __import__(__file__.rsplit('/', 1)[0] + '/lenny')

def setup():
    pass

def draw(at_y):
    (x, y, w, h) = lenny.render_creation(
            lambda w, h: (lenny.BADGE_EINK_WIDTH // 2 - w // 2, at_y - h),
            lenny.creation)
    return [10*60*1000, h]
