import appglue
import badge
import ugfx

BADGE_EINK_WIDTH  = 296
BADGE_EINK_HEIGHT = 128

font = {}

def resolve_file(rel_path):
    return __file__.rsplit('/', 1)[0] + '/' + rel_path

class Char(object):
    def __init__(self, filename, fd):
        offset = fd.tell()
        metadata = f.read(3)
        self.__width = metadata[0] << 8 | metadata[1]
        self.__height = metadata[2]
        self.__filename = filename
        self.__offset = offset
        fd.seek(offset + 3 + self.width() * self.height() // 8)

    def width(self):
        return self.__width

    def height(self):
        return self.__height

    def __raster(self):
        with open(self.__filename, "rb") as f:
            f.seek(self.__offset + 3)
            return f.read(self.width() * self.height() // 8)

    def render(self, at_x, at_y):
        width = self.width()
        height = self.height()
        raster = self.__raster()
        for x in range(0, width):
            for y in range(0, height):
                i = y * width + x
                if raster[i // 8] & (1 << (i & 7)):
                    ugfx.pixel(at_x + x, at_y + y, ugfx.BLACK)

ugfx.init()

# Load our custom font.
for comp_name in ["ears", "eyes", "mouth"]:
    comp_list = []
    filename = resolve_file("lenny_%s.png" % comp_name)
    with open(filename, "rb") as f:
        comp = []
        while True:
            char_header = f.read(3)
            if len(char_header) == 0:
                break # EOF
            # Decode the number of bytes in the character.
            char_size = char_header[1] << 8 | char_header[2]
            char_offset = f.tell()

            # This bit indicates whether the character should be considered
            # part of a a collection.
            if not char_header[0] and len(comp) > 0:
                comp_list.append(comp)
                comp = []

            comp.append(Char(filename, f))
    font[comp_name] = comp_list

creation = {
    "mouth": int(badge.nvs_get_str("lenny_face", "mouth", "0")),
    "eyes": int(badge.nvs_get_str("lenny_face", "eyes", "0")),
    "ears": int(badge.nvs_get_str("lenny_face", "ears", "0")),
}
cursor_position = 2


def store_creation():
    global creation
    for comp_name, val in creation.items():
        badge.nvs_set_str("lenny_face", comp_name, str(val))

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
    global cursor_position
    cursor_position = (cursor_position + delta + 5) % 5
    render()

def rotate_selection(delta):
    global creation
    global cursor_position
    global font
    comp_name = ["ears", "eyes", "mouth", "eyes", "ears"][cursor_position]
    i = creation[comp_name]
    n = len(font[comp_name])
    creation[comp_name] = (creation[comp_name] + delta + n) % n
    store_creation()
    render()


render()

ugfx.input_init()
ugfx.input_attach(ugfx.JOY_LEFT, lambda pressed: cursor_move(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_RIGHT, lambda pressed: cursor_move(1) if pressed else ())
ugfx.input_attach(ugfx.JOY_UP, lambda pressed: rotate_selection(-1) if pressed else ())
ugfx.input_attach(ugfx.JOY_DOWN, lambda pressed: rotate_selection(1) if pressed else ())
ugfx.input_attach(ugfx.BTN_START, lambda pressed: appglue.home())
