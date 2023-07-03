import pygame
from pygame.locals import *
import sys, os
import math
import button
import random
import pygame.freetype
import time

pygame.mixer.init()
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional
jetPackFire = pygame.image.load('fire.png')
laser_sound = pygame.mixer.Sound(os.path.join('sounds', 'laser.wav'))
alien_death = pygame.mixer.Sound(os.path.join('sounds', 'alien_death.mp3'))
jetpack_active = pygame.mixer.Sound(os.path.join('sounds', 'jetpack_active.mp3'))
jetpack_active.set_volume(0.25)
HEIGHT = 450
WIDTH = 600
ACC = 0.5
FRIC = -0.12
FPS = 70
x = 400
y = 200
vector = -1.6
start_game = False
shoot = False
font = pygame.freetype.Font(None, 32)
restart_font = pygame.freetype.Font(None, 50)
score = 0
score_multiplier = 1
elapsed_time = 0
spawn_time = 0
powerup_spawn_time = 0
CAMERA_SPEED = 0.1
player_hits =  1
powerup_length = 250
elapsed = 0
show_start_button = True
show_controls = False
restart = False
art_height = 225/3
art_w = 225
art_x = 250
art_y = 100
clock = pygame.time.Clock()
fire_rate = 250
fired_time = 0
pickup_time = 0

data = pygame.image.load(os.path.join('images', 'data.png'))
data = pygame.transform.scale(data, (300,30))

player_idle = pygame.image.load('playerIdle.png')

start_button = pygame.image.load('start_button.png')
start_rect = start_button.get_rect()
restart_img = pygame.image.load(os.path.join('images','restart_button.png'))
restart_rect = restart_img.get_rect()
help_button = pygame.image.load(os.path.join('images', 'help_button.jpg'))
help_rect = help_button.get_rect()

bullet_img = pygame.image.load(os.path.join('images', 'bullet.png'))

control_art = pygame.image.load(os.path.join('images', 'controls.png'))
control_art = pygame.transform.scale(control_art, (350, 250))
data = pygame.image.load(os.path.join('images', 'data.png'))
data = pygame.transform.scale(data, (300,30))



#load power up images
firerate_img = pygame.image.load(os.path.join('images','fire_rate.png'))
speedboost_img = pygame.image.load(os.path.join('images','speed_boost.png'))
increasescore_img = pygame.image.load(os.path.join('images','extra_score.png'))
extralife_img = pygame.image.load(os.path.join('images','extra_hit.png'))

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))

bg_img = pygame.image.load('bg.jpg')
bg_img = pygame.transform.scale(bg_img,(WIDTH,HEIGHT))


pygame.display.set_caption("Space Cowboy")


class Camera():
  def __init__(self, width, height):
    self.camera = pygame.Rect(0,0,width,height)
    self.width = width
    self.height = height

  def apply(self, entity):
    return entity.rect.move(self.camera.topleft)
  
  def update(self, target):
    x = -target.rect.x + int(WIDTH/2 - 200)
    y = -target.rect.y + int((HEIGHT/2) + 21)

    self.camera = pygame.Rect(x, y, self.width, self.height)
    self.camera.x += int(target.vel.x * CAMERA_SPEED)

    self.camera.x = lerp(self.camera.x, x, CAMERA_SPEED)

def lerp(a, b, t):
  return a + (b-a) * t

class Player(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    pRect = player_idle.get_rect()
    pRect.center = (x, y)

    self.surf = player_idle
    self.rect = pRect

    self.pos = vec((10, 385))
    self.vel = vec(0, 0)
    self.acc = vec(0, 0)
    self.direction = 1


  def move(self):
    self.acc = vec(0, 0.5)

    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[K_LEFT]:
      self.acc.x = -ACC
      self.flip = True
      self.direction = -1
    if pressed_keys[K_RIGHT]:
      self.acc.x = ACC
      self.direction = 1

    self.acc.x += self.vel.x * FRIC
    self.vel += self.acc
    self.pos += self.vel + 0.5 * self.acc
    self.rect.midbottom = self.pos

  def update(self):
    global restart
    hit_platform = pygame.sprite.spritecollide(P1, platforms, False)
    hit_alien = pygame.sprite.spritecollide(self, aliens, False)
    global player_hits
    if hit_platform:
      self.pos.y = hit_platform[0].rect.top + 1
      self.vel.y = 0
    
    if hit_alien and player_hits == 1:
      self.kill()
      restart = True
    pRect = player_idle.get_rect()
    self.surf = player_idle


    

  def jump(self):
    self.acc = vec(0, 0.5)

    self.acc.y = -1

    self.acc.y += self.vel.y * FRIC
    self.vel += self.acc
    self.pos += self.vel + 0.5 * self.acc


class Bullet(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    self.image = pygame.Surface((10, 20))
    self.image = bullet_img
    self.surf = bullet_img
    self.rect = self.image.get_rect()
    self.rect.centerx = x
    self.rect.bottom = y
    self.speedy = 10

  def update(self):
    self.rect.x += self.speedy
    # Remove the bullet if it goes off the screen
    if self.rect.bottom < 0:
      self.kill()
    
def increase_score():
  global score
  score += 1 * score_multiplier

class platform(pygame.sprite.Sprite):

  def __init__(self, width, height):
    super().__init__()
    ground = pygame.image.load(os.path.join('images', 'ground.png'))
    self.width = width
    self.height = height
    self.surf = ground
    self.rect = self.surf.get_rect(center=(self.width, self.height))


class groundAlien(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    gAlien = (pygame.image.load_extended('alien.png'))
    gRect = gAlien.get_rect()
    gRect.center = (x, y)
    self.surf = gAlien
    self.rect = gRect
    self.vector = vector
    self.pos = vec((x, y))
    self.vel = vec(0, 0)
    self.acc = vec(0, 0)

  def update(self, player_pos, accel_rate):
    dist = player_pos - self.pos
    dir = dist.normalize()
    self.acc = dir * accel_rate
    self.vel += self.acc
    max_speed = 2
    self.val = self.vel.normalize() * min(self.vel.length(), max_speed)
    self.pos += self.vel
    self.rect.center = self.pos
    
    hitB = pygame.sprite.spritecollide(self, bullet_group, False)
    if hitB:
      self.kill()
      hitB[0].kill()
      global score; score += 100
      self.rect.x = 1000
      self.rect.y = -1000
      alien_death.play()

class powerUp(pygame.sprite.Sprite):

  def __init__(self, x, y, img, effectNum):
    super().__init__()
    imgRect = img.get_rect()
    imgRect.center = (x,y)
    self.surf = img
    self.rect = imgRect
    self.vector = vector
    self.pos = vec((x,y))
    self.effectNum = effectNum

  def collide(self, entity):
    pickup = pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(player), False)
    if pickup:
      self.kill()
      self.rect.x = 1000
      self.rect.y = -1000
      return True
    

  def apply(self, entity):
    if self.effectNum == 1:
      global ACC; ACC = 1
    elif self.effectNum == 2:
      global fire_rate; fire_rate = 125
    elif self.effectNum == 3:
      global score_multiplier; score_multiplier = 5
    elif self.effectNum == 4:
      global player_hits; player_hits += 1

  def end(self, entity):
    global fire_rate, score_multiplier, ACC
    ACC = 0.5
    fire_rate = 250
    score_multiplier = 1
    







PT1 = platform(WIDTH/2, HEIGHT - 10)
P1 = Player(200, 200)
A1 = groundAlien(random.randint(WIDTH/2,WIDTH-20), random.randint(70,HEIGHT-100))
camera = Camera(WIDTH, HEIGHT)

start_button = button.Button(165, 100, start_button, 0.40)
help_button = button.Button(260, 350, help_button, .15)
restart_button = button.Button(165, 100, restart_img, 0.40)

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
all_sprites.add(A1)

#create sprite groups
platforms = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
aliens = pygame.sprite.Group()
player = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player.add(P1)
platforms.add(PT1)
aliens.add(A1)

run = True

while run:
  delta_time = clock.tick(FPS)
  pygame.display.update()
  # update and draw groups
  bullet_group.update()
  bullet_group.draw(displaysurface)

  if start_game == False:
    for event in pygame.event.get():
      if event.type == pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      displaysurface.blit(bg_img,(0,0))
      if show_start_button:
        start_button.draw(displaysurface)
      help_button.draw(displaysurface)
      if show_controls:
        displaysurface.blit(control_art, (120, 100))
        displaysurface.blit(data, (160,413))

      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          pos = pygame.mouse.get_pos()
          if start_button.is_clicked(pos) and show_start_button == True:
            start_game = True
          elif help_button.is_clicked(pos):
            pygame.draw.rect(displaysurface, (0,0,0), start_rect)
            pygame.display.update()
            show_start_button = not(show_start_button)
            show_controls = not(show_controls)

  elif restart:
    for event in pygame.event.get():
      if event.type == pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      for entity in all_sprites:
        entity.kill()
      displaysurface.blit(bg_img,(0,0))
      restart_button.draw(displaysurface)
      restart_font.render_to(displaysurface, (155, 300), 'You Failed!', (255, 255, 255))
      font.render_to(displaysurface, (175, 350), 'Final Score: ' + str(score), (255, 255, 255))


      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          pos = pygame.mouse.get_pos()
          if restart_button.is_clicked(pos):
            PT1 = platform(WIDTH/2, HEIGHT - 10)
            P1 = Player(200, 200)
            A1 = groundAlien(random.randint(WIDTH/2,WIDTH-20), random.randint(70,HEIGHT-100))

            all_sprites.add(PT1)
            all_sprites.add(P1)
            all_sprites.add(A1)
            
            player.add(P1)
            platforms.add(PT1)
            aliens.add(A1)
            
            score = 0
            restart = False



  else:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
        pygame.quit()
        sys.exit()

    displaysurface.blit(bg_img,(0,0))
    font.render_to(displaysurface, (10, 10), 'Score: ' + str(score), (255, 255, 255))

    current_time = pygame.time.get_ticks()

    elapsed_time += delta_time
    if elapsed_time >= 70:
      increase_score()
      elapsed_time = 0
    
    spawn_time += delta_time #if commented out alien spawning is disabled for testing
    if spawn_time >= 3000:
      A1 = groundAlien(random.randint(int(P1.pos.x) + WIDTH/2, int(P1.pos.x) + (WIDTH-20)), random.randint(70,HEIGHT-100))
      aliens.add(A1)
      all_sprites.add(A1)
      spawn_time = 0

    powerup_spawn_time += delta_time
    if powerup_spawn_time >= 1000:
      chance = random.randint(1,5)
      if chance == 1:
        type = random.randint(1,3)
        if type == 1:
          PU1 = powerUp(random.randint(int(P1.pos.x) + WIDTH/2, int(P1.pos.x) + (WIDTH-20)), random.randint(70,HEIGHT-100), speedboost_img, 1)
        elif type == 2:
          PU1 = powerUp(random.randint(int(P1.pos.x) + WIDTH/2, int(P1.pos.x) + (WIDTH-20)), random.randint(70,HEIGHT-100), firerate_img, 2)
        elif type ==3:
          PU1 = powerUp(random.randint(int(P1.pos.x) + WIDTH/2, int(P1.pos.x) + (WIDTH-20)), random.randint(70,HEIGHT-100), increasescore_img, 3)
      try:
        all_sprites.add(PU1)
        powerups.add(PU1)
        powerup_spawn_time = 0
      except NameError:
        pass

    for powerup in powerups:
      if powerup.collide(P1):
        elapsed = 0
        powerup.apply(P1)
    

      if powerup_length - elapsed > 0:
        elapsed += 1
      elif powerup_length - elapsed == 0:
          powerup.end(P1)



    camera.update(P1)

    for entity in all_sprites:
      displaysurface.blit(entity.surf, camera.apply(entity))

    P1.move()

    key = pygame.key.get_pressed()
    if key[pygame.K_UP]:
      P1.jump()
      P1.pRect = jetPackFire.get_rect()
      P1.surf = jetPackFire
      jetpack_active.play()
    else:
      P1.update()
      jetpack_active.stop()
      

    
    if current_time - fired_time >= fire_rate:
      if key[pygame.K_SPACE]:
        bullet = Bullet(P1.pos.x + 22, P1.pos.y - 24)
        bullet_group.add(bullet)
        all_sprites.add(bullet)
        fired_time = current_time
        laser_sound.play()


    aliens.update(P1.pos, 0.0000001)
    if 0 == len(aliens.sprites()):
      pass 
    else:
      aliens.update(P1.pos, 0.1) # if number is really small alien movement is disabled default value = .05

    if P1.pos.x > (PT1.width - 40):
      PT1 = platform((PT1.width + WIDTH + 400), HEIGHT - 10)
      platforms.add(PT1)
      all_sprites.add(PT1)
    if A1.pos.x < 0:
      A1.kill()
    