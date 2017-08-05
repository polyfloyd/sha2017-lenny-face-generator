import appglue
import ugfx
lenny = __import__(__file__.rsplit('/', 1)[0] + '/lenny')

lenny.render()

ugfx.input_init()
ugfx.input_attach(ugfx.JOY_LEFT, lambda pressed: lenny.cursor_move(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_RIGHT, lambda pressed: lenny.cursor_move(1) if pressed else ())
ugfx.input_attach(ugfx.JOY_UP, lambda pressed: lenny.rotate_selection(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_DOWN, lambda pressed: lenny.rotate_selection(1) if pressed else ())
ugfx.input_attach(ugfx.BTN_START, lambda pressed: appglue.home())
