import appglue
import ugfx
lenny = __import__(__file__.rsplit('/', 1)[0] + '/lenny')


cursor_position = 2


def render():
    ugfx.clear(ugfx.WHITE)
    lenny.render_creation(
            lambda w, h: (lenny.BADGE_EINK_WIDTH // 2 - w // 2, lenny.BADGE_EINK_HEIGHT // 2 - h // 2),
            lenny.creation,
            cursor_position)
    ugfx.flush()

def cursor_move(delta):
    global cursor_position
    cursor_position = (cursor_position + delta + 5) % 5
    render()

def rotate_selection(delta):
    comp_name = ["ears", "eyes", "mouth", "eyes", "ears"][cursor_position]
    i = lenny.creation[comp_name]
    n = len(lenny.font[comp_name])
    lenny.creation[comp_name] = (lenny.creation[comp_name] + delta + n) % n
    lenny.store_creation()
    render()


ugfx.init()
ugfx.input_init()

ugfx.input_attach(ugfx.JOY_LEFT, lambda pressed: cursor_move(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_RIGHT, lambda pressed: cursor_move(1) if pressed else ())
ugfx.input_attach(ugfx.JOY_UP, lambda pressed: rotate_selection(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_DOWN, lambda pressed: rotate_selection(1) if pressed else ())
ugfx.input_attach(ugfx.BTN_START, lambda pressed: appglue.home())

render()
