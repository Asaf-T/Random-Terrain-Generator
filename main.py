import pygame
import sys
import random
import numpy as np
from perlin_noise import PerlinNoise
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP
import os

################################################################

# general
SCREEN_W, SCREEN_H = 800, 600
MAP_H = 10
scale = 1
seed_num = random.randint(10000000, 99999999)
map_num = 0

# map position
MAP_SHIFT_X, MAP_SHIFT_Y = 0, 0
MAP_SHIFT_INITIAL_X, MAP_SHIFT_INITIAL_Y = SCREEN_W/2, SCREEN_H/2
MAP_MIDDLE_X, MAP_MIDDLE_Y = SCREEN_W/2, SCREEN_H/2
moving_map = False

# save map
vertex_dict = {}
saved_map_obj = ''
animation_loading_num = 0
savingProcess_counter = 0
vertex = 0
savingProcess = False

# height plane
layer = 0
moving_height_plane = False

# zoom
zoom = 1
zoom_temp = 1
ZOOM_SHIFT_X, ZOOM_SHIFT_Y = 0, 0
ZOOM_SHIFT_INITIAL_X, ZOOM_SHIFT_INITIAL_Y = 0, 0
changing_zoom = False

# real time generation
GEN_SQUARE_SIZE = 50
generated_chunks = [(0, 0)]
gen_mode = False

# biomes
water, grass, dark_grass, sand, stone, snow = (0, 0, 255), (0, 255, 0), (0, 170, 0), (255,255,0),(128,128,128), (245,245,245)
biomeRanges = {stone:((0,1), (0,0.3)), grass:((0.2,0.6), (0.2,0.4)), dark_grass:((0.2,0.6), (0.4,0.6)), sand:((0.7,1), (0,1)), snow:((0,0.2), (0.5,1))}
colors = [water, grass, dark_grass, sand, stone, snow]

################################################################

pygame.display.set_caption('Map Generator')
pygame.init()
screen=pygame.display.set_mode((SCREEN_W,SCREEN_H), pygame.RESIZABLE)
running=True
k=pygame.key
clock=pygame.time.Clock()
surf=pygame.surface.Surface((SCREEN_W,SCREEN_H))

################################################################

def generate_perlin_noise(octaves = 4, seed = 0, start_coordinates = (0,0)):
    noise = PerlinNoise(octaves,seed)
    data = np.zeros((GEN_SQUARE_SIZE*scale, GEN_SQUARE_SIZE*scale))
    for y in range(0, GEN_SQUARE_SIZE*scale):
        for x in range(0, GEN_SQUARE_SIZE*scale):
            data[y, x] = noise([(x + start_coordinates[1])/(GEN_SQUARE_SIZE*scale), (y + start_coordinates[0])/(GEN_SQUARE_SIZE*scale)])  # Normalize to 0-1
    # Normalize to 0-1 range
    data = (data - data.min())/(data.max() - data.min())
    return data

def generate_map(seed_num, start_coordinates):
    map = []
    noise_list = []

    for i in range(4):
        noise_list.append(generate_perlin_noise(octaves=[3,3,2,6][i], seed=int(str(seed_num)[i*2:(i+1)*2]), start_coordinates = start_coordinates))
        '''
        0 = temperature
        1 = humidity
        2 = primary height
        3 = secondary height
        '''

    for y in range(GEN_SQUARE_SIZE*scale):
        for x in range(GEN_SQUARE_SIZE*scale):


            # set height
            z=(noise_list[2][x,y] - 0.5)*MAP_H/2 + noise_list[3][x,y]*MAP_H*scale - MAP_H/5 - 2.5

            # assign biomes
            currentBiome = grass
            for biome in biomeRanges:
                if biomeRanges[biome][0][0] <= noise_list[0][x,y] <= biomeRanges[biome][0][1] and biomeRanges[biome][1][0] <= noise_list[1][x,y] <= biomeRanges[biome][1][1]:
                    currentBiome = biome

            # if 0<=noise_list[0][x,y]<=0.2 and 0<=noise_list[1][x,y]<=1:
            #     biome=snow
            # elif 0.2<noise_list[0][x,y]<=0.6 and 0<=noise_list[1][x,y]<=0.2:
            #     biome=grass
            # elif 0.6<noise_list[0][x,y]<=1 and 0<=noise_list[1][x,y]<=0.1:
            #     biome=sand
            # else:
            #     biome=stone

            if z <= 0:
                currentBiome = water


            # add to map
            map.append([(currentBiome),(start_coordinates[0] + x, start_coordinates[1] + y, z)])

    return map

def draw_text(text = 'TEXT', text_pos = (0, 0), text_size = 10, text_color = (0, 0, 0), text_rotation = 0, text_font = 'Arial'):
    text_final = pygame.font.SysFont(text_font, text_size).render(text, True, text_color)
    text_final = text = pygame.transform.rotate(text_final, text_rotation)
    screen.blit(text_final, text_pos)

################################################################

map = generate_map(seed_num, (0, 0))
map_updated = False

while running:

    MOUSE_X, MOUSE_Y = pygame.mouse.get_pos()

    for event in pygame.event.get():

        # quit
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False

        # # generate map
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
        #     print('generating')
        #     map = generate_map()
        #     map_updated = False


        if gen_mode and not savingProcess:

            # exit generation mode
            if event.type == pygame.KEYDOWN and event.key == pygame.K_g and gen_mode:
                gen_mode = False

            # enter generation mode
            else:
                gen_mode = True

            if event.type == MOUSEBUTTONDOWN:

                # generate more land
                if event.button == 1 and not (np.floor((MOUSE_X - MAP_SHIFT_X)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE - MAP_MIDDLE_X, np.ceil((MOUSE_Y - MAP_SHIFT_Y)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE - MAP_MIDDLE_Y - GEN_SQUARE_SIZE) in generated_chunks:
                    map_temp = generate_map(seed_num, (np.floor((MOUSE_X - MAP_SHIFT_X)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE - MAP_MIDDLE_X, np.ceil((MOUSE_Y - MAP_SHIFT_Y)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE - MAP_MIDDLE_Y - GEN_SQUARE_SIZE))
                    map += map_temp
                    generated_chunks.append((np.floor((MOUSE_X - MAP_SHIFT_X)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE - MAP_MIDDLE_X, np.ceil((MOUSE_Y - MAP_SHIFT_Y)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE - MAP_MIDDLE_Y - GEN_SQUARE_SIZE))

                # # change size of generation square
                # if event.button == 4:
                #     GEN_SQUARE_SIZE += 5
                #     print(GEN_SQUARE_SIZE)
                # elif event.button == 5:
                #     GEN_SQUARE_SIZE -= 5

            map_updated = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_g and not savingProcess: # pygame.key.get_pressed()[pygame.K_g]:
            gen_mode = True

        elif not gen_mode and not savingProcess:
            if event.type == MOUSEBUTTONDOWN:

                # change height plane
                if screen.get_width()*0.025 <= MOUSE_X <= screen.get_width()*0.025 + screen.get_width()*0.95 and screen.get_height()*(1-1/16) <= MOUSE_Y <= screen.get_height()*(1-1/16) + screen.get_height()/64:
                    moving_height_plane = True

                # zoom in/out
                if event.button == 4 or event.button == 5 and zoom > 0:
                    if event.button == 4:
                        zoom += 1
                    elif event.button == 5:
                        zoom -= 1

                    map_updated = False
                    changing_zoom = True

                else:
                    # zoom = 1

                    map_updated = False
                    changing_zoom = True

                # move the map
                if event.button == 1 and not (screen.get_width()*0.025 <= MOUSE_X <= screen.get_width()*0.025 + screen.get_width()*0.95 and screen.get_height()*(1-1/16) <= MOUSE_Y <= screen.get_height()*(1-1/16) + screen.get_height()/64):
                    MAP_SHIFT_INITIAL_X = MOUSE_X
                    MAP_SHIFT_INITIAL_Y = MOUSE_Y
                    moving_map = True

            # release mouse
            if event.type == MOUSEBUTTONUP:
                moving_map = False
                moving_height_plane = False

            # update map shift
            if moving_map:
                MAP_SHIFT_X += MOUSE_X - MAP_SHIFT_INITIAL_X
                MAP_SHIFT_Y += MOUSE_Y - MAP_SHIFT_INITIAL_Y

                MAP_SHIFT_INITIAL_X = MOUSE_X
                MAP_SHIFT_INITIAL_Y = MOUSE_Y

                map_updated = False

            # update height plane
            if moving_height_plane:
                layer = (MAP_H*2)*(MOUSE_X - screen.get_width()*0.025)/(screen.get_width()*0.95) - MAP_H
                map_updated = False

            # update zoom shift
            if changing_zoom:
                # ZOOM_SHIFT_X = (MAP_SHIFT_X - MOUSE_X)*(zoom - 1)
                # ZOOM_SHIFT_Y = (MAP_SHIFT_Y - MOUSE_Y)*(zoom - 1)

                # zoom_temp = zoom

                # print(ZOOM_SHIFT_X, ZOOM_SHIFT_Y)

                # MAP_SHIFT_X += ZOOM_SHIFT_X
                # MAP_SHIFT_Y += ZOOM_SHIFT_Y

                # ZOOM_SHIFT_X, ZOOM_SHIFT_Y = 0, 0
                # ZOOM_SHIFT_INITIAL_X, ZOOM_SHIFT_INITIAL_Y = 0, 0
                changing_zoom = False


    # save map as obj
    if pygame.key.get_pressed()[pygame.K_c] and not savingProcess:
        savingProcess_counter = 0
        vertex_dict = {}
        saved_map_obj = ''
        vertex = 0
        savingProcess = True

    if savingProcess:
        if savingProcess_counter < len(map):
            pixel = map[savingProcess_counter]
            vertex += 1
            saved_map_obj += f'v {pixel[1][0]} {pixel[1][2]} {pixel[1][1]}\n'
            vertex_dict[(pixel[1][0], pixel[1][1])] = vertex
            savingProcess_counter += 1

        elif savingProcess_counter == len(map):
            saved_map_obj += f'v {min(generated_chunks)[0]} 0 {min(generated_chunks)[1]}\n'
            saved_map_obj += f'v {max(generated_chunks)[0] + GEN_SQUARE_SIZE} 0 {max(generated_chunks)[1] + GEN_SQUARE_SIZE}\n'
            saved_map_obj += f'v {max(generated_chunks)[0] + GEN_SQUARE_SIZE} 0 {min(generated_chunks)[1]}\n'
            saved_map_obj += f'v {min(generated_chunks)[0]} 0 {max(generated_chunks)[1] + GEN_SQUARE_SIZE}\n'

            vertex = 0
            saved_map_obj += '\n'
            savingProcess_counter += 1

        elif savingProcess_counter < 2*len(map):
            pixel = map[savingProcess_counter - len(map) - 1]
            vertex += 1
            savingProcess_counter += 1
            # for i in [1,-1]:
            #     for j in [1,-1]:
            #         for ii in [-1,1]:
            #             for jj in [-1,1]:
            #                 if (pixel[1][0] + i, pixel[1][1] + j) in vertex_dict and (pixel[1][0] + ii, pixel[1][1] + jj) in vertex_dict:
            #                     face= f'f {vertex_dict[(pixel[1][0], pixel[1][1])]} {vertex_dict[(pixel[1][0] + i, pixel[1][1] + j)]} {vertex_dict[(pixel[1][0] + ii, pixel[1][1] + jj)]}'
            #                     if not face in saved_map_obj:
            #                         saved_map_obj += face + '\n'

            for i in [((1,0),(0,1)), ((1,0),(0,-1)), ((-1,0),(0,1)), ((-1,0),(0,-1))]: #,  ((0,1),(1,0)),((0,1),(-1,0)),  ((0,-1),(1,0)),((0,-1),(-1,0))]:
                if (pixel[1][0] + i[0][0], pixel[1][1] + i[0][1]) in vertex_dict and (pixel[1][0] + i[1][0], pixel[1][1] + i[1][1]) in vertex_dict:
                    face= f'f {vertex_dict[(pixel[1][0], pixel[1][1])]} {vertex_dict[(pixel[1][0] + i[0][0], pixel[1][1] + i[0][1])]} {vertex_dict[(pixel[1][0] + i[1][0], pixel[1][1] + i[1][1])]}'
                    if not face in saved_map_obj:
                        saved_map_obj += face + '\n'

        else:

            saved_map_obj += f'f {len(map) + 1} {len(map) + 2} {len(map) + 3}\n'
            saved_map_obj += f'f {len(map) + 1} {len(map) + 2} {len(map) + 4}\n'

            # pyperclip.copy(saved_map_obj)

            # os.system("c:/Desktop>map.obj","w")
            # open('map.obj').write(saved_map_obj)

            # Step 1: Create a .txt file and write some content
            txt_file_path = "map.txt"
            with open(txt_file_path, "w") as txt_file:
                txt_file.write(saved_map_obj)

            # Step 2: Read the .txt content and write it to an .obj file
            obj_file_path = "map.obj"
            with open(txt_file_path, "r") as txt_file:
                content = txt_file.read()

            with open(obj_file_path, "w") as obj_file:
                obj_file.write(content)

            # Verify file creation
            if os.path.exists(obj_file_path):
                print(f"Successfully converted {txt_file_path} to {obj_file_path}")
            else:
                print("Conversion failed.")

            savingProcess = False

        if pygame.key.get_pressed()[pygame.K_x]:
            savingProcess = False

        map_updated = False


    ####################
    SCREEN_W, SCREEN_H = screen.get_width(), screen.get_height()
    # draw
    if True: #not map_updated:
        map_updated = True

        screen.fill([0,0,255])
        for pixel in map:
            pos_size = [pixel[1][0]*zoom + MAP_MIDDLE_X + MAP_SHIFT_X + ZOOM_SHIFT_X, pixel[1][1]*zoom + MAP_MIDDLE_Y + MAP_SHIFT_Y + ZOOM_SHIFT_Y, zoom, zoom]

            # map
            pygame.draw.rect(screen, (pixel[0][0], pixel[0][1], pixel[0][2]), pos_size) # (pixel[0][0] + 0.01*pixel[1][2],pixel[0][1] + 0.01*pixel[1][2],pixel[0][2] + 0.01*pixel[1][2]), pos_size)

            # height plane
            if pixel[1][2]<layer:
                pygame.draw.rect(screen, (255,0,255), pos_size)

        # plane slider
        pygame.draw.rect(screen, (255, 255, 255), [SCREEN_W*0.025, SCREEN_H*(1-1/16), SCREEN_W*0.95, SCREEN_H/64])

        if MOUSE_X < screen.get_width()*0.025:
            pygame.draw.rect(screen, (0, 0, 0), [SCREEN_W*0.025, SCREEN_H*(1 - 1/16), 2, SCREEN_H/64])
        elif screen.get_width()*0.975 < MOUSE_X:
            pygame.draw.rect(screen, (0, 0, 0), [SCREEN_W*0.975, SCREEN_H*(1 - 1/16), 2, SCREEN_H/64])
        else:
            pygame.draw.rect(screen, (0, 0, 0), [(layer/MAP_H/2 + 0.5)*SCREEN_W*0.95 + SCREEN_W*0.025, SCREEN_H*(1 - 1/16), 2, SCREEN_H/64])

        if gen_mode:
            # square generation
            pygame.draw.rect(screen, (0, 0, 0), [np.floor(((MOUSE_X - MAP_SHIFT_X))/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_X, np.ceil((MOUSE_Y - MAP_SHIFT_Y)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_Y, GEN_SQUARE_SIZE, 2])
            pygame.draw.rect(screen, (0, 0, 0), [np.floor((MOUSE_X - MAP_SHIFT_X)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_X, np.ceil(((MOUSE_Y - MAP_SHIFT_Y) - GEN_SQUARE_SIZE)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_Y, 2, GEN_SQUARE_SIZE])
            pygame.draw.rect(screen, (0, 0, 0), [np.floor((MOUSE_X - MAP_SHIFT_X)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_X, np.ceil(((MOUSE_Y - MAP_SHIFT_Y) - GEN_SQUARE_SIZE)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_Y, GEN_SQUARE_SIZE, 2])
            pygame.draw.rect(screen, (0, 0, 0), [np.floor(((MOUSE_X - MAP_SHIFT_X) + GEN_SQUARE_SIZE)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_X, np.ceil(((MOUSE_Y - MAP_SHIFT_Y) - GEN_SQUARE_SIZE)/GEN_SQUARE_SIZE)*GEN_SQUARE_SIZE + MAP_SHIFT_Y, 2, GEN_SQUARE_SIZE + 2])

        if savingProcess:
            # draw "Saving map"
            if 30 * 0 <= animation_loading_num <= 30 * 1:
                draw_text('Saving map', (SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 10), 20)
                animation_loading_num += 1
            elif 30 * 1 < animation_loading_num <= 30 * 2:
                draw_text('Saving map.', (SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 10), 20)
                animation_loading_num += 1
            elif 30 * 2 < animation_loading_num <= 30 * 3:
                draw_text('Saving map..', (SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 10), 20)
                animation_loading_num += 1
            elif 30 * 3 < animation_loading_num <= 30 * 4:
                draw_text('Saving map...', (SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 10), 20)
                animation_loading_num += 1
                if animation_loading_num == 30 * 4:
                    animation_loading_num = 0

            # draw saving numbers
            draw_text(f'{savingProcess_counter}/{2*len(map)}', (SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 30), 10)

            # draw saving bar
            pygame.draw.rect(screen, (0, 0, 0),[SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 45, 100, 10])
            pygame.draw.rect(screen, (255, 255, 255),[SCREEN_W - 110, SCREEN_H*(1-1/16) - 70 + 45, 100*savingProcess_counter/(2*len(map)), 10])

            # draw saving percent
            draw_text(f'{np.floor(10*100*savingProcess_counter/(2*len(map)))/10}%', (SCREEN_W-110, SCREEN_H*(1-1/16) - 70 + 55), 10)


        # draw biome graph
        pygame.draw.rect(screen, (255, 255, 255), [0, 0, 220, 220])
        pygame.draw.rect(screen, grass, [20, 0, 200, 200])
        draw_text('Temperature', (0,130), 15, (0, 0, 0), 90)
        pygame.draw.rect(screen, (0, 0, 0), [20, 200, 200, 2])
        draw_text('Humidity', (20,200), 15)
        pygame.draw.rect(screen, (0, 0, 0), [20 - 2, 0, 2, 200 + 2])

        for biome in biomeRanges:
            # pygame.draw.rect(screen, biome, [biomeRanges[biome][1][0]*200 + 20, biomeRanges[biome][0][0]*200, (biomeRanges[biome][1][1] - biomeRanges[biome][1][0])*200, (biomeRanges[biome][0][1] - biomeRanges[biome][0][0])*200])
            pygame.draw.rect(screen, biome, [biomeRanges[biome][1][0]*200 + 20, (1-biomeRanges[biome][0][1])*200, (biomeRanges[biome][1][1] - biomeRanges[biome][1][0])*200, (biomeRanges[biome][0][1] - biomeRanges[biome][0][0])*200])



        # draw instructions
        pygame.draw.rect(screen, (255, 255, 255), [SCREEN_W - 380, 0, 380, 70])
        draw_text('esc = exit Map Generator', (SCREEN_W - 380 + 5, 0), 20)
        draw_text('c = save map as obj  x = stop map saving process', (SCREEN_W - 380 + 5, 20), 20)
        draw_text('g = enter/exit generation mode', (SCREEN_W - 380 + 5, 40), 20)


    clock.tick(60)
    pygame.display.flip()

pygame.quit()
sys.exit()
