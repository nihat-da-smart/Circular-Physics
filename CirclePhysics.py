import pygame
import sys
from pygame.math import Vector2

SCREEN_WIDTH, SCREEN_HEIGHT = 640*2, 480*1.75
BG_COLOR = (0, 0, 0)
GRAVITY = (0, 9.81 * 2)
FRICTION = 0.8
MAX_UPDATES_PER_FRAME = 99999
TIME_STEP = 1 / 60.0

class Circle:
    def __init__(self, pos, radius, color=(255, 255, 255), mass=1):
        self.pos = Vector2(pos)
        self.radius = float(radius)
        self.color = color
        self.mass = float(mass)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def update(self, dt):
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt
        self.acceleration = Vector2(0, 0)

    def apply_force(self, force):
        self.acceleration += force

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def detect_collision(self, other_obj):
        distance = self.pos.distance_to(other_obj.pos)
        collision_radius = self.radius + other_obj.radius
        if distance < collision_radius:
            normal = (other_obj.pos - self.pos).normalize()
            return normal
        else:
            return None

    def handle_collision(self, normal, other_obj):
        relative_velocity = other_obj.velocity - self.velocity
        if relative_velocity.dot(normal) >= 0:
            return

        total_mass = self.mass + other_obj.mass
        impulse = (2 * relative_velocity.dot(normal)) / total_mass

        self.velocity += impulse * normal * other_obj.mass
        other_obj.velocity -= impulse * normal * self.mass

        self.velocity *= FRICTION
        other_obj.velocity *= FRICTION

        overlap = self.radius + other_obj.radius - self.pos.distance_to(other_obj.pos)
        if overlap > 0:
            move = normal * overlap
            self.pos -= move * (1.5 * other_obj.mass / total_mass)
            other_obj.pos += move * (1.5 * self.mass / total_mass)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
Title = 'Physics sim'
pygame.display.set_caption(Title)

class PhysicsEngine:
    def __init__(self, gravity=GRAVITY):
        self.gravity = Vector2(gravity)
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def update(self, dt, keys_pressed):
        for obj in self.objects:
            obj.apply_force(self.gravity)

            if obj == big_circle:
                if keys_pressed[pygame.K_LEFT]:
                    obj.velocity.x -= 10 * dt
                if keys_pressed[pygame.K_RIGHT]:
                    obj.velocity.x += 10 * dt
                if keys_pressed[pygame.K_UP]:
                    obj.velocity.y -= 10 * dt
                if keys_pressed[pygame.K_DOWN]:
                    obj.velocity.y += 10 * dt

            obj.update(dt)

            if obj.pos.x - obj.radius < 0:
                obj.velocity.x = abs(obj.velocity.x)
                obj.pos.x = obj.radius
            if obj.pos.x + obj.radius > SCREEN_WIDTH:
                obj.velocity.x = -abs(obj.velocity.x)
                obj.pos.x = SCREEN_WIDTH - obj.radius
            if obj.pos.y - obj.radius < 0:
                obj.velocity.y = abs(obj.velocity.y)
                obj.pos.y = obj.radius
            if obj.pos.y + obj.radius > SCREEN_HEIGHT:
                obj.velocity.y = -abs(obj.velocity.y)
                obj.pos.y = SCREEN_HEIGHT - obj.radius

            for other_obj in self.objects:
                if obj != other_obj:
                    normal = obj.detect_collision(other_obj)
                    if normal:
                        other_obj.handle_collision(normal, obj)
                        obj.handle_collision(normal, other_obj)

physics_engine = PhysicsEngine()
circles = []

big_circle = Circle((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 40, (255, 0, 0), mass=3)
other_circle = Circle((SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 100), 30, (0, 255, 0), mass=1.5)
smol_circle = Circle((SCREEN_WIDTH/3, SCREEN_HEIGHT/3), 10, (125, 20, 255), mass=0.5)


circles.append(big_circle)
circles.append(other_circle)
circles.append(smol_circle)

for circle in circles:
    physics_engine.add_object(circle)

time_since_last_update = 0
FPS = 60
SIM_FPS = 60
TIME_PER_UPDATE = 1 / SIM_FPS

while True:
    dt = clock.tick(FPS) / 1000.0
    time_since_last_update += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    updates = 0
    while time_since_last_update >= TIME_PER_UPDATE and updates < MAX_UPDATES_PER_FRAME:
        keys_pressed = pygame.key.get_pressed()
        physics_engine.update(TIME_PER_UPDATE, keys_pressed)
        time_since_last_update -= TIME_PER_UPDATE
        updates += 1

    screen.fill(BG_COLOR)
    for circle in circles:
        circle.draw(screen)
    pygame.display.update()
