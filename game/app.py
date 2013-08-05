import pygame
import io
import random

clock = pygame.time.Clock()

pygame.init()

pygame.display.init()

pygame.font.init()
font = pygame.font.Font("resources/Verdana Bold.ttf", 12)

TILE_SIZE = 32
LEVEL = 1

screen = pygame.display.set_mode(
    (10*TILE_SIZE, 22*TILE_SIZE),
    pygame.DOUBLEBUF,
    16
)

DIMENSIONS = (10, 22)
border = pygame.image.load('resources/border.png')

SCORE = 0
calculations_per_frame = 0


class Tile(pygame.Surface):
    bound = False
    surface = None
    # expect (r,g,b,a,)
    color = None
    position = [None, None]

    def __init__(self, color, background=True):
        super(Tile, self).__init__((TILE_SIZE, TILE_SIZE,))
        self.erase_me = False
        self.color = color
        self.fill(self.color)
        if not background:
            self.blit(border, (0, 0,))
        self.position = [None, None]

    def tilecopy(self):
        new_item = Tile(self.color, background=False)
        return new_item

    def calc_bound(self):
        bound = False
        if self.position[1]+TILE_SIZE >= TILE_SIZE * 20:
            bound = True
        else:
            for t in game_status['placed_tiles']:
                tl, tr = t.position[0], t.position[0]+TILE_SIZE
                sl, sr = self.position[0], self.position[0]+TILE_SIZE
                tt = t.position[1]
                sb = self.position[1] + TILE_SIZE
                if t != self and tl == sl and tr == sr and sb == tt:
                    bound = True
        self.bound = bound

    def should_delete(self):
        return self.erase_me

    def __repr__(self):
        return self.unicode()

    def __str__(self):
        return self.unicode()

    def unicode(self):
        return u"Tile %s at %s\n" % (self.color, self.position)


red_tile = Tile(pygame.Color(255, 0, 0))
yellow_tile = Tile(pygame.Color(255, 255, 0))
green_tile = Tile(pygame.Color(0, 255, 0))
blue_tile = Tile(pygame.Color(0, 0, 255))
magenta_tile = Tile(pygame.Color(255, 0, 255))
cyan_tile = Tile(pygame.Color(0, 255, 255))
black_tile = Tile(pygame.Color(32, 32, 32, 20))

tiles = [red_tile, green_tile, blue_tile,
         cyan_tile, magenta_tile, yellow_tile]

level_file = io.open('levels/blank_level.txt').read()

code_to_tile = {
    'R': red_tile,
    'G': green_tile,
    'B': blue_tile,
    'C': cyan_tile,
    'M': magenta_tile,
    'Y': yellow_tile,
    'K': black_tile
}

tiles = 'RGBCMY'


def get_level_surface(lf):
    surface = pygame.Surface((10*TILE_SIZE, 20*TILE_SIZE))
    level = lf.split("\n")
    for x in xrange(0, len(level)):
        for y in xrange(0, len(level[x])):
            tile = code_to_tile.get(level[x][y], None)
            if tile:
                surface.blit(tile, (y*TILE_SIZE, x*TILE_SIZE))
    return surface


def random_level():
    surface = pygame.Surface((10*TILE_SIZE, 20*TILE_SIZE))
    for x in xrange(0, 20):
        for y in xrange(0, 10):
            tile = code_to_tile[random.choice(tiles)]
            surface.blit(tile, (y*TILE_SIZE, x*TILE_SIZE))
    return surface

level_surface = get_level_surface(level_file)
game_status = {
    'block_falling': False,
    'score': 0,
    'placed_tiles': [],
    'current': None,
    'next': None,
    'block_pos': [TILE_SIZE*4, 0],
    'move_cool': True,
    'drop_cool': True,
    'rotate_cool': True,
}


def shutdown():
    pygame.font.quit()
    pygame.display.quit()
    pygame.quit()


def generate_block():
    return [
        [random.choice(tiles), random.choice(tiles)],
        [random.choice(tiles), random.choice(tiles)]
    ]


def rotate_block(b, counter=False):
    o = b[0][0]
    if counter:
        b[0][0] = b[0][1]
        b[0][1] = b[1][1]
        b[1][1] = b[1][0]
        b[1][0] = o
    else:
        b[0][0] = b[1][0]
        b[1][0] = b[1][1]
        b[1][1] = b[0][1]
        b[0][1] = o


def get_block_surface(block):
    s = pygame.Surface((2*TILE_SIZE, 2*TILE_SIZE))
    for x in xrange(len(block)):
        for y in xrange(len(block[x])):
            z = None
            z = code_to_tile[block[x][y]].tilecopy()
            if x is not None:
                s.blit(z, (y*TILE_SIZE, x*TILE_SIZE))
    return s


def create_block():
    if game_status['next'] is not None:
        block = game_status['next']
        game_status['next'] = generate_block()
        return block
    else:
        game_status['next'] = generate_block()
        return generate_block()


def block_grounded():
    for b in game_status['placed_tiles']:
        b = b.position
        left_side = game_status['block_pos'][0]
        right_side = game_status['block_pos'][0] + TILE_SIZE * 2
        tl = b[0]
        tr = b[0] + TILE_SIZE
        if tl >= left_side and tr <= right_side:
            if game_status['block_pos'][1] == b[1]:
                return True
    if game_status['block_pos'][1] >= TILE_SIZE * 20:
        return True
    else:
        return False


def cooldown():
    if game_status['rotate_cool'] > 0:
        game_status['rotate_cool'] -= 1
    if game_status['move_cool'] > 0:
        game_status['move_cool'] -= 1
    if game_status['drop_cool'] > 0:
        game_status['drop_cool'] -= 1


def decompose_current_block():
    tiles = []
    for x in range(0, len(game_status['current'])):
        for y in range(0, len(game_status['current'][x])):
            tile = code_to_tile[game_status['current'][x][y]].tilecopy()
            tile.position[0] = (
                game_status['block_pos'][0] + TILE_SIZE * y
            )
            tile.position[1] = (
                game_status['block_pos'][1] + TILE_SIZE * x
            )
            tiles.append(tile)
    return tiles

while True:
    screen.fill(0)
    fps = clock.get_fps()
    for event in pygame.event.get([pygame.QUIT]):
        if event.type == pygame.QUIT:
            shutdown()
            break
    keys = pygame.key.get_pressed()
    push_left, push_right = False, False
    if keys[pygame.K_ESCAPE]:
        shutdown()
        break
    if keys[pygame.K_j] and game_status['move_cool'] == 0:
        push_left = True
        game_status['move_cool'] = 6
    if keys[pygame.K_l] and game_status['move_cool'] == 0:
        push_right = True
        game_status['move_cool'] = 6
    if keys[pygame.K_a] and game_status['rotate_cool'] == 0:
        rotate_block(game_status['current'], counter=True)
        game_status['rotate_cool'] = 9
    if keys[pygame.K_s] and game_status['rotate_cool'] == 0:
        rotate_block(game_status['current'])
        game_status['rotate_cool'] = 9
    drop = False
    if keys[pygame.K_SPACE] and game_status['drop_cool'] == 0:
        drop = True
        game_status['drop_cool'] = 18

    if game_status['block_falling'] is False:
        game_status['current'] = create_block()
        game_status['block_falling'] = True

    game_status['block_pos'][1] += TILE_SIZE / 16

    if push_left:
        if game_status['block_pos'][0] > 0:
            game_status['block_pos'][0] -= TILE_SIZE
        else:
            game_status['block_pos'][0] = 0

    if push_right:
        if game_status['block_pos'][0] < TILE_SIZE * 8:
            game_status['block_pos'][0] += TILE_SIZE
        else:
            game_status['block_pos'][0] = TILE_SIZE * 8

    bs = get_block_surface(game_status['current'])

    next_surface = get_block_surface(game_status['next'])
    next_surface = pygame.transform.scale(next_surface, (TILE_SIZE, TILE_SIZE))

    if drop is True:
        while not block_grounded():
            game_status['block_pos'][1] += 1

    if block_grounded():
        # calculate which are white here.
        game_status['block_pos'][1] -= TILE_SIZE * 2
        game_status['block_falling'] = False
        game_status['placed_tiles'] += decompose_current_block()
        game_status['block_pos'] = [TILE_SIZE * 4, 0]
        game_status['current'] = None

    # clean up bound tiles that should be gone.

    for t in game_status['placed_tiles']:
        if t.bound and t.should_delete():
            i = game_status['placed_tiles'].index(t)
            del (game_status['placed_tiles'][i])
            SCORE += 1

    #move the unbound tiles
    for t in game_status['placed_tiles']:
        was_bound = t.bound
        t.calc_bound()
        if t.bound is False:
            t.position[1] += 1

    status_surface = font.render(
        u"SCORE: %s CPF: %s Placed: %s:  " % (
            SCORE,
            calculations_per_frame,
            len(game_status['placed_tiles'])
        ),
        1,
        (255, 255, 255, 0)
    )
    cooldown()

    screen.blit(level_surface, (0, 64))
    screen.blit(bs, game_status['block_pos'])
    for t in game_status['placed_tiles']:
        screen.blit(
            t,
            (t.position[0], t.position[1]+TILE_SIZE*2,)
        )
    screen.fill(0, rect=pygame.Rect(0, 0, 640, 64))
    screen.blit(status_surface, (0, 0,))
    screen.blit(
        font.render("Next", 1, (255, 255, 255, 255)),
        (TILE_SIZE*9, TILE_SIZE)
    )
    screen.blit(next_surface, (TILE_SIZE*9, 0))
    pygame.display.flip()
    clock.tick(60)
    calculations_per_frame = 0
