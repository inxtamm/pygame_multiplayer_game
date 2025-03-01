import pygame, random, sys, math, json
from network import Network
from player import Player, Animation, Camera, World, ParticleManager


class Window:
    def __init__(self):
        self.dimensions = [600, 400]
        self.dt = 0.01
        self.window = pygame.display.set_mode(self.dimensions)
        self.display = pygame.Surface((self.dimensions[0] // 2, self.dimensions[1] // 2))
        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()


    def update(self):
        self.window.blit(pygame.transform.scale(self.display, self.dimensions), (0, 0))
        pygame.display.update()
        self.display.fill((255, 255, 255))#28, 30, 45 :: 13, 32, 43
        self.clock.tick(60)

class Input:
    def __init__(self):
        self.mouse_pos = [0, 0]
        self.mouse = {
            'left_mouse_button_down': False,
            'left_mouse_button_up': False,
            'left_click': False
        }
        self.weapon_angle = 0

    def update(self):
        x, y = pygame.mouse.get_pos()
        self.mouse_pos[0] = int(x / 2)
        self.mouse_pos[1] = int(y / 2)        

        self.mouse['left_click'] = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse['left_mouse_button_down'] = True
                self.mouse['left_mouse_button_up'] = False
                self.mouse['left_click'] = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse['left_mouse_button_up'] = True
                self.mouse['left_mouse_button_down'] = False

class Client:
    def __init__(self):
        
        self._id = str(random.random()).split('.')[-1][:-6]
        self.input = Input()
        self.window = Window()
        with open('data/map.json') as f:
            d = json.load(f)
        self.world = World(d)
        self.particle_manager = ParticleManager()
        self.start_pos = [100, 100]
        self.player = Player(self.start_pos, (9, 13), (255, 0, 0), self._id)
        self.camera = Camera(self.player)
        self.network = Network(self.player)
        self.player.level = self.world.map
        self.animations = {}
        self.weapons = {'shotgun': pygame.image.load('data/images/gun.png').convert_alpha()}

    def run(self):
        len_old_player_list = 0
        while True:
            # player movement
            self.player.move(self.window.dt)
            if not self.player.alive:
                self.player.pos = self.start_pos
                self.player.health = self.player.max_health
                self.player.alive = True
            # player weapon rotation & shooting
            if self.player.weapon:
                self.player.weapon.rotation = math.degrees(math.atan2(self.input.mouse_pos[1] - self.player.pos[1] + self.camera.pos[1], self.input.mouse_pos[0] - self.player.pos[0] + self.camera.pos[0]))
            if self.input.mouse['left_mouse_button_down']:
                player.weapon.shoot()
            #camera
            self.camera.update(self.window.dt)
            #update active player list
            player_list = self.network.send(self.player)
            if len_old_player_list != len(player_list):
                self.animations = {}
            for i in player_list:
                if i not in self.animations:
                    self.animations[i] = Animation('player')
            len_old_player_list = len(player_list)
            
            # Particles
            self.particle_manager.update_render(self.window.display, self.camera.pos)


            for player_index in player_list:
                # render animations
                anim = self.animations[player_index]

                anim.update(self.window.dt)
                player = player_list[player_index]
                anim.flip = player.flip
                anim.set_action(player.action)
                self.window.display.blit(anim.img, (player.pos[0] - self.camera.pos[0] - 3, player.pos[1] - self.camera.pos[1] - 3))
                # damage effect on player
                if player.hurt:
                    mask = pygame.mask.from_surface(anim.img)
                    mask_img = mask.to_surface(setcolor=(255, 255, 255, int(player.hurt * 255)), unsetcolor=(0, 0, 0, 0))
                    self.window.display.blit(mask_img, ((player.pos[0] - self.camera.pos[0]) // 1 - 3, (player.pos[1] - self.camera.pos[1]) // 1 - 3))

                if player.weapon:
                    # update weapons
                    player.weapon.update(player_list, self.particle_manager, self.window.dt)

                    #render projectiles
                    player.weapon.render_projectiles(self.window.display, self.camera.pos)

                    # render weapons
                    weapon_img = self.weapons[player.weapon.type]
                    weapon_img = pygame.transform.flip(weapon_img.copy(), False, player.weapon.flip)
                    weapon_img = pygame.transform.rotate(weapon_img, -player.weapon.rotation)
                    self.window.display.blit(weapon_img, (player.pos[0] - self.camera.pos[0] - weapon_img.get_width() // 2 + 5, player.pos[1] - self.camera.pos[1] - weapon_img.get_height() // 2 + 5))
                
                player_list[player_index].update(self.window.dt)
            
            #render world
            self.world.render(self.window.display, self.camera.pos)

            #render player health bar
            pygame.draw.rect(self.window.display, (255, 0, 0), pygame.Rect(0, 0, 100, 20))
            pygame.draw.rect(self.window.display, (0, 255, 0), pygame.Rect(0, 0, (player.health / player.max_health) * 100, 20))

            self.input.update()
            self.window.update()


client = Client()
client.run()


