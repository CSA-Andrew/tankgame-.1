# -*- coding: utf-8 -*-
import pygame
from pygame import gfxdraw
from random import randint, random, randrange, choice
import math

# declare colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DGREEN = (0, 100, 0)
YELLOW = (255, 215, 0)
ORANGE = (255, 127, 80)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)
Quit = False

pygame.init()


# button class
class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, image='youtube.png'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.image.load(image)
        # This makes a rectangle around the entity, used for anything
        # from collision to moving around.
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.image = pygame.transform.scale(self.image,
                                            (self.width, self.height))
        self.entity_surface = pygame.transform.smoothscale(self.image,
                                                           self.rect.size)
        self.image_copy = self.entity_surface.copy()

    def rotate(self, angle, center):
        self.entity_surface = pygame.transform.rotate(self.image_copy, angle)
        self.rect = self.entity_surface.get_rect(center=center)

    def draw(self, surface):
        surface.blit(self.entity_surface, self.rect)


class Button:
    def __init__(self, color, w, h, x, y, caption):
        self.color = color
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.caption = caption
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surface):
        text = screen_font.render(self.caption, True, WHITE)
        pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(text, (self.x + self.w / 2 - text.get_rect().width / 2,
                            self.y + self.h / 2 - text.get_rect().height / 2))

    def click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos[0], mouse_pos[1])


class Text:
    def __init__(self, text, x, y, color=WHITE):
        self.text = text
        self.x = x
        self.y = y
        self.color = color

    def update(self, surface, text):
        text = screen_font.render(self.text + str(text), True, self.color)
        surface.blit(text, (self.x, self.y))


# class used for sound definition
class Sound:
    def __init__(self, sound):
        self.sound = pygame.mixer.Sound(sound)

    def play_sound(self):
        self.sound.play()


class Projectile(Entity):
    def __init__(self, x, y, launch_angle, width=20, height=20,
                 image='youtube.png', speed=-7):
        super().__init__(x, y, width, height, image)
        rad_angle = math.radians(launch_angle)
        self.angle = (math.cos(rad_angle), math.sin(rad_angle))
        self.speed = speed
        self.max_distance = 50
        self.grav = 9.8
        self.is_active = True

        self.vertvel = 0

    def update(self):
        self.vertvel = self.vertvel + self.grav * 0.01

        self.rect.x += self.angle[1] * self.speed
        self.rect.y += self.vertvel + 0.01 + (self.angle[0] * self.speed)

        if self.rect.y > 800:
            self.is_active = False

        if self.rect.x > 1200:
            self.is_active = False

        if self.rect.x < -100:
            self.is_active = False

    def draw(self, surface):
        self.update()
        if self.is_active:
            surface.blit(self.entity_surface, self.rect)

    def kill(self):
        self.is_active = False


class Tank(Entity):
    def __init__(self, x, y, ASL=650, width=100, height=50, max_distance=100,
                 image='youtube.png'):
        super().__init__(x, y, width, height, image)
        self.asl = ASL
        self.launch_angle = 0
        self.distance_moved = 0
        self.max_distance = max_distance

        self.rotate_left = False
        self.rotate_right = False

        self.move_left = False
        self.move_right = False

        self.max = False

        self.speed = 1

        self.mv_l = 1
        self.mv_r = 1

        self.health = 100

        self.pwr = 0
        self.max_pwr = 100
        self.pwr_dec = False

        self.shot_began = False

        self.cannon = Entity(self.rect.x, self.rect.y, 10, 100)

        self.projectiles = []

        self.healthBar = HealthBar(self)

    def update(self):
        self.gravity()
        self.cannon.rect.x = self.rect.x + (self.rect.w / 2) - \
                             (self.cannon.rect.w / 2)
        self.cannon.rect.y = self.rect.y - 30
        if self.rotate_left:
            self.launch_angle += 1
            if self.launch_angle > 80:
                self.launch_angle = 80
        if self.rotate_right:
            self.launch_angle -= 1
            if self.launch_angle < -80:
                self.launch_angle = -80

        if self.move_right:
            if self.rect.x < 1000:
                self.distance_moved += self.speed
                self.rect.x += (self.speed) * self.mv_r
                if self.distance_moved > self.max_distance:
                    self.distance_moved = self.max_distance
                    self.mv_r = 0
                else:
                    self.mv_r = 1

        if self.move_left:
            if self.rect.x > 0:
                self.distance_moved -= self.speed
                self.rect.x -= (self.speed) * self.mv_l
                if self.distance_moved < -self.max_distance:
                    self.distance_moved = -self.max_distance
                    self.mv_l = 0
                else:
                    self.mv_l = 1

        if self.shot_began:
            if not self.pwr_dec:
                self.pwr += 1
                if self.pwr > self.max_pwr:
                    self.pwr_dec = True
            else:
                self.pwr -= 1
                if self.pwr < -self.max_pwr:
                    self.pwr_dec = False

    def create_projectile(self, speed):
        self.projectiles.append(Projectile(self.rect.x + (self.rect.w / 2),
                                           self.rect.y - 40, self.launch_angle,
                                           speed=speed))

    def gravity(self):
        # figure out better way to calculate gravity in holes (using raycast??)
        if self.rect.y < self.asl:
            self.rect.y += 4

    def draw(self, surface):
        self.update()
        center = (self.rect.x + (self.rect.w / 2), self.rect.y)
        self.cannon.rotate(self.launch_angle, center)
        surface.blit(self.entity_surface, self.rect)
        surface.blit(self.cannon.entity_surface, self.cannon.rect)

        for item in self.projectiles.copy():
            item.draw(surface)
            if not item.is_active:
                self.projectiles.remove(item)
        self.healthBar.update()
        self.healthBar.draw(surface)


class HealthBar(Entity):
    def __init__(self, child_of):
        self.child_of = child_of
        self.x = child_of.rect.x
        self.y = child_of.rect.y - 50
        self.width = int(self.child_of.rect.width * 1.5)
        self.height = 10
        super().__init__(self.x, self.y, self.width, self.height)

        self.current_value = child_of.health
        self.total_value = child_of.health
        self.is_visible = True

    def update(self):
        self.rect.y = self.child_of.rect.y - 80
        self.rect.x = self.child_of.rect.x - (self.child_of.rect.width / 4)
        self.current_value = self.child_of.health

        self.rect.width = (self.current_value / self.total_value) * self.width

    def draw(self, surface):
        if self.is_visible:
            pygame.draw.rect(surface, RED, pygame.Rect(self.rect.x, self.rect.y,
                                                       self.width,
                                                       self.rect.height))
            pygame.draw.rect(surface, GREEN, self.rect)


class GameManager:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.now = 0
        self.last = 0
        self.turn_finished = False

    def check_collision(self):
        pass

    def check_keys(self, k_state, key, player: Tank):

        self.now = pygame.time.get_ticks()
        if key == pygame.K_UP:
            pass
        elif key == pygame.K_DOWN:
            pass
        elif key == pygame.K_a:
            player.move_left = k_state
        elif key == pygame.K_d:
            player.move_right = k_state
        elif key == pygame.K_SPACE and self.now - self.last >= 200:
            self.last = self.now
            if not player.shot_began:
                player.shot_began = True
            else:
                player.create_projectile(
                    -abs((player.pwr / player.max_pwr * 10)) - 1)
                player.shot_began = False
                self.turn_finished = True
        elif key == pygame.K_q:
            player.rotate_left = k_state
        elif key == pygame.K_e:
            player.rotate_right = k_state


class Terrain:
    def __init__(self, variety=0, width=1200, height=800, asl=100, hills=1,
                 steepness=5):
        self.variety = variety
        self.hills = hills
        self.height = height
        self.steepness = steepness
        self.width = width
        self.height = height
        self.t_height = asl

        self.surfaces = []

        inter = width // 10
        for x in range(0, self.width + 1, inter):
            self.surfaces.append((x, self.height - self.t_height))
        self.surfaces.append((self.width, self.height - self.t_height))
        self.surfaces.append((self.width, self.height))
        self.surfaces.append((self.width, self.height))
        self.surfaces.append((0, self.height))
        self.surfaces.append((0, self.height))

    def draw(self, surface):
        pygame.gfxdraw.filled_polygon(surface, self.surfaces, GREY)

    def destroy(self, x, y, radius):
        if y < (self.height - self.t_height) - 5:
            return
        radius = randrange(radius - 10, radius)
        min_left = min(self.surfaces, key=lambda v: abs(v[0] - (x - radius)))
        min_right = min(self.surfaces, key=lambda v: abs(v[0] - (x + radius)))
        indx1 = self.surfaces.index(min_left)
        indx2 = self.surfaces.index(min_right)

        for z in range(indx1, indx2 + 1):
            try:
                self.surfaces.pop(z)
            except:
                pass

        depth = radius + randint(1, 3) - 10
        for i in range(1, self.steepness + 1):
            half = self.steepness // 2
            if i == half + 1:
                self.surfaces.insert(indx1, (x, y + depth))
            elif i > half + 1:
                self.surfaces.insert(indx1, (x - radius - randint(3, 5),
                                             y - randint(1, 10) + depth - (
                                                         radius / (
                                                             self.steepness // 2)) * (
                                                         i // 2)))
            else:
                self.surfaces.insert(indx1, (
                x + radius + randint(3, 5), y + (radius / self.steepness) * i))


def write_highscore(c_score):
    file = open('assets/highscores.txt', 'a')
    file.write(str(c_score) + '\n')
    file.close()


def get_highscores():
    return [line.rstrip('\n') for line in open('assets/highscores.txt')]


def SEND_COLOR_BASED_ON_VALUE(val):
    if val > 0.9:
        return RED
    elif val > 0.7:
        return ORANGE
    elif val > 0.5:
        return YELLOW
    elif val > 0.3:
        return DGREEN
    else:
        return GREEN


# declare screen
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('TANKZ')
pygame.display.flip()
pygame.font.init()
screen_font = pygame.font.SysFont('Arial', 30)
terrain = Terrain()
highscores = []
manager = GameManager()
player_one = Tank(100, 600)

player_two = Tank(1000, 600)

clock = pygame.time.Clock()

FPS = 120

DISTANCE = Text('DISTANCE TRAVELLED', 30, 10, color=BLACK)

DISTANCE_TRAVELLED = pygame.Rect(30, 50, 330, 30)

POWER = Text('POWER', 1050, 10, color=BLACK)

POWER_BAR = pygame.Rect(1170, 50, -330, 30)

main_player = player_one

ACTIVE_PLAYER = Text('YOUR TURN', 0, 0, color=RED)

while not Quit:
    screen.fill(WHITE)
    terrain.draw(screen)
    player_one.draw(screen)
    player_two.draw(screen)

    ACTIVE_PLAYER.x, ACTIVE_PLAYER.y = main_player.rect.x - 40, main_player.rect.y - 130
    ACTIVE_PLAYER.update(screen, ' ')

    clock.tick(FPS)

    DISTANCE.update(screen, ' ')
    POWER.update(screen, ' ')

    DISTANCE_TRAVELLED.width = abs(
        (main_player.distance_moved / main_player.max_distance)) * 330

    value = abs((main_player.pwr / main_player.max_pwr))
    POWER_BAR.width = value * -330
    pygame.draw.rect(screen, BLACK, DISTANCE_TRAVELLED)
    pygame.draw.rect(screen, SEND_COLOR_BASED_ON_VALUE(value), POWER_BAR)

    for event in pygame.event.get():
        if event == pygame.QUIT:
            Quit = True
            pygame.quit()
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key_state = (event.type == pygame.KEYDOWN)
            manager.check_keys(key_state, event.key, main_player)
            if manager.turn_finished:
                manager.turn_finished = False
                main_player.distance_moved = 0
                main_player.pwr = 0
                if main_player == player_one:
                    main_player = player_two
                else:
                    main_player = player_one
        elif event.type == pygame.MOUSEBUTTONDOWN:
            m_pos = pygame.mouse.get_pos()
            terrain.destroy(m_pos[0], m_pos[1], 55)

    pygame.display.update()
