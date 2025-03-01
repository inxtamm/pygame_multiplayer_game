import math, time, os, random
import pygame

ANIM_PATH = 'data/images/animations/'

def collided_tile_list(tile_list, rect):
    hit_list = []
    for tile in tile_list:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

class Player:
    def __init__(self, pos, size, color, id=""):
        self.pos = list(pos)
        self.size = list(size)
        self.color = color
        self.id = id
        self.rect_pos_offset = [0, 0]
        self.velocity = [0, 0]
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.action = 'idle'
        self.flip = False
        self.weapon = Weapon(self, 'shotgun')
        self.alive = True
        self.hurt = 0
        self.level = None
        self.max_health = 10
        self.health = self.max_health

    @property
    def center(self):
        return [self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2]
    
    @property
    def rect(self):
        return pygame.Rect(self.pos[0] - self.rect_pos_offset[0], self.pos[1] - self.rect_pos_offset[1], self.size[0], self.size[1])
    
    def damage(self, damage):
        self.hurt = 1
        self.health -= damage

    def get_tile_rects(self):
        #get only the tile rects that are close to player
        # * * *
        # * P *
        # * * *
        # P stands for player so, we get the closest 9 tiles to player in each direction
        rects = []
        directions = [
            [-1, 0],
            [0, 0],
            [1, 0],
            [-1, -1],
            [0, -1],
            [1, -1],
            [-1, 1],
            [0, 1],
            [1, 1],
        ]
        new_pos = (int(self.center[0] // 16), int(self.center[1] // 16))
        for direction in directions:
            tile_pos = str(new_pos[0] + direction[0]) + ';' + str(new_pos[1] + direction[1])
            if tile_pos in self.level:
                rects.append(pygame.Rect(int(tile_pos.split(';')[0]) * 16, int(tile_pos.split(';')[1]) * 16, 16, 16))
        return rects

    def check_collisions(self, velocity):
        self.pos[0] += velocity[0]
        player_rect = self.rect
        for tile_rect in self.get_tile_rects():
            if player_rect.colliderect(tile_rect):
                if velocity[0] > 0:
                    player_rect.right = tile_rect.left
                elif velocity[0] < 0:
                    player_rect.left = tile_rect.right
                self.pos[0] = player_rect.x

        self.pos[1] += velocity[1]
        player_rect = self.rect
        for tile_rect in self.get_tile_rects():
            if player_rect.colliderect(tile_rect):
                if velocity[1] > 0:
                    player_rect.bottom = tile_rect.top
                elif velocity[1] < 0:
                    player_rect.top = tile_rect.bottom
                self.pos[1] = player_rect.y

    def move(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.velocity[0] = -2
            self.action = 'run'
        elif keys[pygame.K_d]:
            self.velocity[0] = 2
            self.action = 'run'
        else:
            self.velocity[0] = 0
        if keys[pygame.K_w]:
            self.velocity[1] = -2
            self.action = 'run'
        elif keys[pygame.K_s]:
            self.velocity[1] = 2
            self.action = 'run'
        else:
            self.velocity[1] = 0
        if not self.velocity[0] and not self.velocity[1]:
            self.action = 'idle'
        self.check_collisions(self.velocity)
        self.update(dt)

    def update(self, dt):
        
        self.hurt = max(0, self.hurt - 3 * dt)
        if self.health <= 0:
            self.alive = False

class Weapon:
    def __init__(self, owner, type):
        self.owner = owner
        self.type = type
        self.rotation = 0
        self.cooldown = 0.2
        self.flip = False
        self.max_ammo = 100
        self.ammo = self.max_ammo
        self.projectiles = []
        self.shoot_time = time.time()

    def shoot(self):
        if time.time() - self.shoot_time >= self.cooldown:
            self.shoot_time = time.time()
            projectile = Projectile(self.owner.id, self.owner.center, self.rotation, 600)
            projectile.level = self.owner.level
            self.projectiles.append(projectile)
        
    def update(self, player_list, particle_manager, dt):
        #update weapon img rotation
        if (self.rotation % 360 < 270) and (self.rotation % 360 > 90):
            self.flip = True
        else:
            self.flip = False
        #uupdate projectiles
        for projectile in self.projectiles:
            alive = projectile.update(player_list, particle_manager, dt)
            if not alive:
                self.projectiles.remove(projectile)

    def render_projectiles(self, surf, offset=(0, 0)):
        for projectile in self.projectiles:
            projectile.render(surf, offset)

class Animation:
    def __init__(self, entity_name):
        self.anim_path = ANIM_PATH + '/' + entity_name
        self.action = 'idle'
        self.frames = []
        self.index = 0
        self.speed = 20
        self.flip = False
        self.load_frames()

    @property
    def img(self):
        return pygame.transform.flip(self.frames[int(self.index)], self.flip, False)

    def load_frames(self):
        self.frames = []
        for image in os.listdir(self.anim_path + '/' + self.action):
            self.frames.append(pygame.image.load(self.anim_path + '/' + self.action + '/' + image).convert_alpha())

    def set_action(self, action:str):
        if action != self.action:
            self.action = action
            self.load_frames()

    def update(self, dt):
        self.index += 1 * dt * self.speed
        if self.index >= len(self.frames):
            self.index = 0

def bullet_line_end_pos(pos, angle, length):
    pos = list(pos)
    pos[0] += math.cos(angle) * length
    pos[1] += math.sin(angle) * length
    return pos

class Projectile:
    def __init__(self, owner_id, pos, direction: float, speed):
        self.owner = owner_id
        self.pos = list(pos).copy()
        self.direction = math.radians(direction)
        self.speed = speed
        self.bullet_length = 7
        self.lifespan = 0.9
        self.start_time = time.time()
        self.alive = True
        self.level = None

    def update(self, player_list, particle_manager, dt):
        if self.level != None:
            if str(int(self.pos[0]) // 16) + ';' + str(int(self.pos[1]) // 16) in self.level:
                for i in range(10):
                    particle_manager.add_particle(self.pos.copy(), random.random() * math.pi * 2, random.randint(4, 6),random.randint(0, 3), color=random.choice(['#0b1016', '#212528', '#323230', '#4b4e4f']))
                self.alive = False
        for player_index in player_list:
            if player_list[player_index].rect.collidepoint(self.pos):
                if player_list[player_index].id != self.owner:
                    player_list[player_index].damage(1)
                    self.alive = False
                    for i in range(5):
                        particle_manager.add_particle(self.pos.copy(), self.direction + random.random(), random.randint(2, 5),random.randint(0, 2), color=random.choice(['#0b1016', '#212528', '#323230', '#4b4e4f']))
        if time.time() - self.start_time >= self.lifespan:
            self.alive = False
        self.pos[0] += math.cos(self.direction) * self.speed * dt
        self.pos[1] += math.sin(self.direction) * self.speed * dt
        return self.alive

    
    def render(self, surf, offset=(0, 0)):
        pygame.draw.line(surf, (0, 255, 255), (self.pos[0] - offset[0], self.pos[1] - offset[1]), bullet_line_end_pos((self.pos[0] - offset[0], self.pos[1] - offset[1]), self.direction, self.bullet_length), 4)



class Camera:
    def __init__(self, player, window_dimensions=[300, 200]):
        self.true_pos = [0, 0]
        self.win_dimensions = window_dimensions
        self.target_pos = [0, 0]
        self.rate = 0.3
        self.player = player
        self.pos = [0, 0]

    def update(self, dt):
        self.target_pos = [self.player.pos[0] - self.win_dimensions[0] // 2, self.player.pos[1] - self.win_dimensions[1] // 2]
        self.true_pos[0] += (self.target_pos[0] - self.true_pos[0]) / (self.rate / dt)
        self.true_pos[1] += (self.target_pos[1] - self.true_pos[1]) / (self.rate / dt)
        self.pos = [int(self.true_pos[0]), int(self.true_pos[1])]
    

def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

def load_tilesets(img, tile_size=16):
    final_images = {}
    index = 0
    for y in range(3):
        for x in range(3):
            final_images[index] = clip(img, x * tile_size, y * tile_size, tile_size, tile_size)
            index += 1
    return final_images

class World:
    def __init__(self, map):
        self.map = map
        self.tile_img = pygame.image.load('data/images/base_tiles.png').convert_alpha()
        self.tile_size = 16
        self.tile_images = load_tilesets(self.tile_img)
        
    def render(self, surf, offset):
        for tile in self.map:
            pos = (int(tile.split(';')[0]) * self.tile_size, int(tile.split(';')[1]) * self.tile_size)
            surf.blit(self.tile_images[self.map[tile]], (pos[0] - offset[0], pos[1] - offset[1]))

class Particle:
    def __init__(self, pos, angle, duration, speed=2, color=(255, 255, 255)):#duration also means the size
        self.pos = list(pos)
        self.angle = angle
        self.duration = duration
        self.particles = []
        self.speed = speed
        self.color = color

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        self.duration -= 0.3
        if self.duration > 0:
            return True
        else:
            return False

    def render(self, surf, offset):
        pygame.draw.circle(surf, self.color, (self.pos[0] - offset[0], self.pos[1] - offset[1]), self.duration)

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add_particle(self, pos, angle, duration, speed=2, color=(255, 255, 255)):
        self.particles.append(Particle(pos, angle, duration, speed, color))

    def update_render(self, surf, offset):
        for particle in self.particles:

            alive = particle.update()
            if not alive:
                self.particles.remove(particle)
            particle.render(surf, offset)