import pygame, sys
import json

screen = pygame.display.set_mode((800, 600))
display = pygame.Surface((400, 300))
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
            final_images[index] = clip(img, x * tile_size, y * tile_size, 16, 16)
            index += 1
    return final_images

tile_img = pygame.image.load('data/images/base_tiles.png').convert_alpha()
tiles = load_tilesets(tile_img)
active_tile = None
left_mouse_hold_down = False
right_mouse_hold_down = False
click = False

with open('data/map.json') as f:
    d = json.load(f)
level = d
scroll = [0, 0]
speed = 10

while True:
    display.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()
    mx = int(mx / 2)
    my = int(my / 2)


    if active_tile != None:
        active_tile_image = tiles[active_tile].copy()
        active_tile_image.set_alpha(150)
        pos = (int(mx + scroll[0]) // 16, int(my + scroll[1]) // 16)
        display.blit(active_tile_image, (pos[0] * 16 - scroll[0], pos[1] * 16 - scroll[1]))

        string_tile_pos = str(pos[0]) + ';' + str(pos[1])
        if left_mouse_hold_down and mx > display.get_width() // 5:
            level[string_tile_pos] = active_tile

        if right_mouse_hold_down and mx > display.get_width() // 5:
            if string_tile_pos in level:
                del level[string_tile_pos]


    for raw_pos in level:
        tile_pos = (int(raw_pos.split(';')[0]) * 16, int(raw_pos.split(';')[1]) * 16)
        display.blit(tiles[level[raw_pos]], (tile_pos[0] - scroll[0], tile_pos[1] - scroll[1]))
        pygame.draw.rect(display, (32, 32, 32), pygame.Rect(0, 0, display.get_width() // 5, display.get_height()))


    for i, tile in enumerate(tiles):
        tile_rect = pygame.Rect(10, 10 + i * 20, 16, 16)
        if tile_rect.collidepoint(mx, my):
            display.blit(tiles[tile], (8, 10 + i * 20))
            if click:
                active_tile = tile
        else:
            display.blit(tiles[tile], (10, 10 + i * 20))
            
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            click = True
            if event.button == 1:
                left_mouse_hold_down = True
            if event.button == 3:
                right_mouse_hold_down = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_mouse_hold_down = False
            if event.button == 3:
                right_mouse_hold_down = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                scroll[1] -= speed
            if event.key == pygame.K_d:
                scroll[0] += speed
            if event.key == pygame.K_s:
                scroll[1] += speed
            if event.key == pygame.K_a:
                scroll[0] -= speed
            if event.key == pygame.K_f:
                with open("data/map.json", "w") as file:
                    json.dump(level, file)
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
    pygame.display.update()