import json
import ugfx

BADGE_EINK_WIDTH  = 296
BADGE_EINK_HEIGHT = 128

font = {}

def resolve_file(rel_path):
    return __file__.rsplit('/', 1)[0] + '/' + rel_path

class Char(object):
    def __init__(self, char):
        self.char = char

    def width(self):
        return self.char["w"]

    def height(self):
        return self.char["h"]

    def __raster(self):
        return self.char["d"]

    def render(self, at_x, at_y):
        width = self.width()
        height = self.height()
        raster = self.__raster()
        for x in range(0, width):
            for y in range(0, height):
                i = y * width + x
                if raster[i // 8] & (1 << (i % 8)):
                    ugfx.pixel(at_x + x, at_y + y, ugfx.BLACK)

ugfx.init()

# Load our custom font.
for comp_name in ["ears", "eyes", "mouth"]:
    comp_list = []
    with open(resolve_file("lenny_%s.png" % comp_name), "rb") as f:
        comp = []
        while True:
            char_header = f.read(3)
            if len(char_header) == 0:
                break # EOF
            # Decode the number of bytes in the character.
            char_size = char_header[1] << 8 | char_header[2]

            # This bit indicates whether the character should be considered
            # part of a a collection.
            if not char_header[0] and len(comp) > 0:
                comp_list.append(comp)
                comp = []

            binary_raster = f.read(char_size)
            width = binary_raster[0] << 8 | binary_raster[1]
            height = binary_raster[2]
            comp.append(Char({
                "w": width,
                "h": height,
                "d": binary_raster[3:3 + width * height // 8],
            }))
    font[comp_name] = comp_list


creation = {
    "mouth": 1,
    "eyes": 24,
    "ears": 1,
}
cursor_position = 2
#cursor_hidden = False

def render():
    ugfx.clear(ugfx.WHITE)

    start_y = BADGE_EINK_HEIGHT // 2 - font["mouth"][0][0].height() // 2
    total_width = 0
    characters = []
    for (comp_name, comp_n) in [("ears", 0), ("eyes", 0), ("mouth", 0), ("eyes", 1), ("ears", 1)]:
        comp = font[comp_name][creation[comp_name]]
        char = comp[comp_n % len(comp)]
        total_width += char.width()
        characters.append(char)
    start_x = BADGE_EINK_WIDTH // 2 - total_width // 2

    advance_x = start_x
    for i, char in enumerate(characters):
        char.render(advance_x, start_y)
        if i == cursor_position:
            ugfx.fill_circle(advance_x + char.width() // 2, start_y + char.height() + 0, 5, ugfx.BLACK);
        advance_x += char.width()

    ugfx.string(0, BADGE_EINK_HEIGHT - 24, "http://textsmili.es", "PermanentMarker22", ugfx.BLACK)
    ugfx.flush()

def cursor_move(delta):
    cursor_position = (cursor_position + delta + 5) % 5
    render()

def rotate_selection(delta):
    comp_name = ["ears", "eyes", "mouth", "eyes", "ears"][cursor_position]
    i = creation[comp_name]
    n = len(font[comp_name])
    creation[creation[comp_name]] = (creation[creation[comp_name]] + delta + n) % n
    render()


render()

ugfx.input_init()
ugfx.input_attach(ugfx.JOY_LEFT, lambda pressed: cursor_move(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_RIGHT, lambda pressed: cursor_move(1) if pressed else ())
ugfx.input_attach(ugfx.JOY_UP, lambda pressed: rotate_selection(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_DOWN, lambda pressed: rotate_selection(1) if pressed else ())
