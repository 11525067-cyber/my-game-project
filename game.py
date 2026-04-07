import math
import os
import json
import pygame
import sys
import random
import cv2
import numpy as np
from itertools import combinations

class Circle:
    def __init__(self, x, y, vx, vy, radius, health, color, name, image=None, gun_image=None, character_type=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.health = health
        self.max_health = health
        self.color = color
        self.name = name
        self.character_type = character_type or name
        self.image = image
        self.gun_image = gun_image
        self.bullet_timer = 0.0
        self.target = None
        self.colliding = False
        self.bullet_count = 0
        self.ultimate_active = False
        self.burst_remaining = 0
        self.burst_timer = 0.0
        self.burst_is_ultimate = False
        self.attack_count = 0
        self.ultimate_duration_timer = 0.0
        self.ultimate_cooldown_timer = 5.0
        self.normal_image = image
        self.ultimate_image = None
        self.controller = "ai"
        self.impulse_vx = 0.0
        self.impulse_vy = 0.0
        self.impulse_wall_bounces_remaining = 0
        self.gojo_sequence_index = 0
        self.gojo_attack_count = 0
        self.gojo_hollow_purple_count = 0
        self.base_speed = math.hypot(vx, vy)
        self.gojo_ultimate_stage = None
        self.gojo_ultimate_timer = 0.0
        self.gojo_ultimate_hold_timer = 0.0
        self.gojo_ultimate_charge_duration = 0.0
        self.gojo_domain_freeze_timer = 0.0
        self.gojo_void_intro_timer = 0.0
        self.gojo_domain_banner_timer = 0.0
        self.damage = 0
        self.damage_bonus = 0
        self.faker_skill_cooldown_timer = 0.0
        self.faker_skill_state = None
        self.faker_blink_mark_active = False
        self.faker_blink_mark_x = 0.0
        self.faker_blink_mark_y = 0.0
        self.faker_blink_return_timer = 0.0
        self.faker_charmed_timer = 0.0
        self.faker_charmed_source_index = -1
        self.faker_combo_target_index = -1
        self.faker_combo_shots_remaining = 0
        self.faker_combo_shot_timer = 0.0
        self.faker_normal_attack_count = 0
        self.faker_ultimate_cooldown_timer = 0.0
        self.faker_invulnerable_timer = 0.0
        self.faker_last_stand_used = False
        self.faker_ultimate_banner_timer = 0.0

    def move(self, dt):
        self.x += (self.vx + self.impulse_vx) * dt
        self.y += (self.vy + self.impulse_vy) * dt
        if self.impulse_wall_bounces_remaining <= 0:
            impulse_damping = max(0.0, 1.0 - 3.0 * dt)
            self.impulse_vx *= impulse_damping
            self.impulse_vy *= impulse_damping

    def bounce_off_wall(self, width, height=None):
        h = height if height is not None else width
        if self.x - self.radius <= 0 and self.vx < 0:
            self.vx = -self.vx
            self.x = self.radius
        elif self.x + self.radius >= width and self.vx > 0:
            self.vx = -self.vx
            self.x = width - self.radius

        if self.y - self.radius <= 0 and self.vy < 0:
            self.vy = -self.vy
            self.y = self.radius
        elif self.y + self.radius >= h and self.vy > 0:
            self.vy = -self.vy
            self.y = h - self.radius

    def clamp_to_arena(self, width, height=None):
        h = height if height is not None else width
        self.x = max(self.radius, min(width - self.radius, self.x))
        self.y = max(self.radius, min(h - self.radius, self.y))

    def clamp_to_trapezoid(self, arena_left, arena_top, arena_width, arena_height):
        tube_w = max(120, int(arena_width * 0.4))
        top_center_x = arena_left + arena_width // 2
        tube_left = top_center_x - tube_w // 2
        tube_right = top_center_x + tube_w // 2
        
        bottom_y = arena_top + arena_height
        
        if self.y + self.radius > bottom_y:
            self.y = bottom_y - self.radius
        
        if self.y - self.radius < arena_top:
            self.y = arena_top + self.radius
        
        if self.x - self.radius < arena_left:
            self.x = arena_left + self.radius
        if self.x + self.radius > arena_left + arena_width:
            self.x = arena_left + arena_width - self.radius
        
        taper_height = arena_height * 0.3
        if taper_height > 0 and self.y < arena_top + taper_height:
            local_y = self.y - arena_top
            progress = local_y / taper_height
            progress = max(0, min(1, progress))
            
            left_boundary = tube_left + (arena_left - tube_left) * progress
            right_boundary = tube_right + (arena_left + arena_width - tube_right) * progress
            
            if self.x - self.radius < left_boundary:
                self.x = left_boundary + self.radius
            if self.x + self.radius > right_boundary:
                self.x = right_boundary - self.radius

    def bounce_impulse_off_wall(self, width, height=None):
        h = height if height is not None else width
        if self.x - self.radius <= 0 and self.impulse_vx < 0:
            self.impulse_vx = -self.impulse_vx * 0.92
            self.x = self.radius
            if self.impulse_wall_bounces_remaining > 0:
                self.impulse_wall_bounces_remaining -= 1
        elif self.x + self.radius >= width and self.impulse_vx > 0:
            self.impulse_vx = -self.impulse_vx * 0.92
            self.x = width - self.radius
            if self.impulse_wall_bounces_remaining > 0:
                self.impulse_wall_bounces_remaining -= 1

        if self.y - self.radius <= 0 and self.impulse_vy < 0:
            self.impulse_vy = -self.impulse_vy * 0.92
            self.y = self.radius
            if self.impulse_wall_bounces_remaining > 0:
                self.impulse_wall_bounces_remaining -= 1
        elif self.y + self.radius >= h and self.impulse_vy > 0:
            self.impulse_vy = -self.impulse_vy * 0.92
            self.y = h - self.radius
            if self.impulse_wall_bounces_remaining > 0:
                self.impulse_wall_bounces_remaining -= 1

    def hit(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.hypot(dx, dy)
        return distance <= self.radius + other.radius


class Bullet:
    def __init__(
        self,
        x,
        y,
        vx,
        vy,
        owner_index,
        color=(255, 220, 50),
        size=5,
        image=None,
        is_ultimate=False,
        source="default",
        damage=None,
        attack_type=None,
        crit_chance=0.0,
        crit_damage=0,
        bounce_forever=False,
        expires_with_owner_ultimate=False,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner_index = owner_index
        self.color = color
        self.size = size
        self.image = image
        self.is_ultimate = is_ultimate
        self.source = source
        self.damage = damage
        self.attack_type = attack_type
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage
        self.bounce_forever = bounce_forever
        self.expires_with_owner_ultimate = expires_with_owner_ultimate
        self.field_radius = 0
        self.field_strength = 0.0
        self.pushes_projectiles = False
        self.pushes_characters = False
        self.hold_timer = 0.0
        self.hold_duration = 0.0
        self.blue_charging = False
        self.hold_offset = 0.0
        self.release_speed = None
        self.pending_vx = vx
        self.pending_vy = vy
        self.target_index = -1
        self.turn_rate = 0.0
        self.field_damage_per_second = 0.0
        self.hit_targets = set()
        self.pull_strength = 0.0
        self.push_strength = 0.0
        self.inner_push_radius = 0.0
        self.field_activation_delay = 0.0

    def move(self, dt):
        if self.hold_timer > 0:
            self.hold_timer = max(0.0, self.hold_timer - dt)
            if self.hold_timer == 0.0:
                # Bullet released - blue no longer charging
                self.blue_charging = False
                if self.source == "gojo_blue":
                    self.field_activation_delay = 0.6
                release_speed = self.release_speed if self.release_speed is not None else math.hypot(self.pending_vx, self.pending_vy)
                pending_length = math.hypot(self.pending_vx, self.pending_vy)
                if pending_length > 0 and release_speed > 0:
                    self.vx = (self.pending_vx / pending_length) * release_speed
                    self.vy = (self.pending_vy / pending_length) * release_speed
                else:
                    self.vx = self.pending_vx
                    self.vy = self.pending_vy
            return
        if self.field_activation_delay > 0:
            self.field_activation_delay = max(0.0, self.field_activation_delay - dt)
        self.x += self.vx * dt
        self.y += self.vy * dt

    def bounce_off_wall(self, width, height=None):
        h = height if height is not None else width
        bounced = False
        if self.x <= 0 and self.vx < 0:
            self.vx = -self.vx
            self.x = 0
            bounced = True
        elif self.x >= width and self.vx > 0:
            self.vx = -self.vx
            self.x = width
            bounced = True

        if self.y <= 0 and self.vy < 0:
            self.vy = -self.vy
            self.y = 0
            bounced = True
        elif self.y >= h and self.vy > 0:
            self.vy = -self.vy
            self.y = h
            bounced = True
        return bounced

    def draw(self, surface, offset_x=0, offset_y=0):
        display_size = self.size
        if self.hold_duration > 0 and self.hold_timer > 0:
            growth = 1.0 - (self.hold_timer / self.hold_duration)
            display_size = max(1, int(self.size * growth))
        if self.source == "faker_charm":
            heart_surface = pygame.Surface((display_size * 4, display_size * 4), pygame.SRCALPHA)
            cx = heart_surface.get_width() // 2
            cy = heart_surface.get_height() // 2
            r = max(4, int(display_size * 0.6))
            pygame.draw.circle(heart_surface, (255, 135, 220, 210), (cx - r // 2, cy - r // 4), r)
            pygame.draw.circle(heart_surface, (255, 135, 220, 210), (cx + r // 2, cy - r // 4), r)
            pygame.draw.polygon(
                heart_surface,
                (255, 165, 230, 220),
                [(cx - r * 2 // 1, cy), (cx + r * 2 // 1, cy), (cx, cy + r * 2)],
            )
            surface.blit(heart_surface, heart_surface.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y))))
            return
        if self.source == "faker_orb" and self.image:
            glow_surface = pygame.Surface((display_size * 6, display_size * 6), pygame.SRCALPHA)
            center = glow_surface.get_width() // 2
            pygame.draw.circle(glow_surface, (120, 220, 255, 55), (center, center), max(6, int(display_size * 2.3)))
            pygame.draw.circle(glow_surface, (205, 245, 255, 95), (center, center), max(4, int(display_size * 1.55)))
            surface.blit(glow_surface, glow_surface.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y))))
        if self.image:
            draw_image = self.image
            if display_size != self.size:
                draw_image = pygame.transform.smoothscale(draw_image, (display_size * 2, display_size * 2))
            angle = math.degrees(math.atan2(self.pending_vy if self.hold_timer > 0 else self.vy, self.pending_vx if self.hold_timer > 0 else self.vx)) + 360
            rotated = pygame.transform.rotate(draw_image, -angle)
            image_rect = rotated.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y)))
            surface.blit(rotated, image_rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x + offset_x), int(self.y + offset_y)), display_size)


class Meteor:
    def __init__(self, x, y, vx, vy, size, owner_index=-1, target_index=-1, damage=6, attack_type="skill", is_crit=True, max_bounces=3, turn_rate=math.pi, color=(255, 20, 147), image=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.owner_index = owner_index
        self.target_index = target_index
        self.damage = damage
        self.attack_type = attack_type
        self.is_crit = is_crit
        self.max_bounces = max_bounces
        self.turn_rate = turn_rate
        self.color = color
        self.image = image
        self.bounce_count = 0

    def move(self, dt, circles):
        if 0 <= self.target_index < len(circles):
            target = circles[self.target_index]
            if target.health > 0:
                speed = math.hypot(self.vx, self.vy)
                if speed > 0:
                    dx = target.x - self.x
                    dy = target.y - self.y
                    distance = math.hypot(dx, dy)
                    if distance > 0:
                        desired_angle = math.atan2(dy, dx)
                        current_angle = math.atan2(self.vy, self.vx)
                        angle_delta = (desired_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                        max_turn = self.turn_rate * dt
                        if angle_delta > max_turn:
                            angle_delta = max_turn
                        elif angle_delta < -max_turn:
                            angle_delta = -max_turn
                        new_angle = current_angle + angle_delta
                        self.vx = math.cos(new_angle) * speed
                        self.vy = math.sin(new_angle) * speed
        self.x += self.vx * dt
        self.y += self.vy * dt

    def bounce_off_wall(self, width, height=None):
        h = height if height is not None else width
        if self.x - self.size <= 0 and self.vx < 0:
            self.vx = -self.vx
            self.x = self.size
            self.bounce_count += 1
        elif self.x + self.size >= width and self.vx > 0:
            self.vx = -self.vx
            self.x = width - self.size
            self.bounce_count += 1

        if self.y - self.size <= 0 and self.vy < 0:
            self.vy = -self.vy
            self.y = self.size
            self.bounce_count += 1
        elif self.y + self.size >= h and self.vy > 0:
            self.vy = -self.vy
            self.y = h - self.size
            self.bounce_count += 1

    def draw(self, surface, offset_x=0, offset_y=0):
        if self.image:
            angle = math.degrees(math.atan2(self.vy, self.vx))
            rotated = pygame.transform.rotate(self.image, -angle)
            image_rect = rotated.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y)))
            surface.blit(rotated, image_rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x + offset_x), int(self.y + offset_y)), self.size)


def get_font(size):
    font_names = ["Segoe UI", "Arial", "Tahoma", "Verdana", "Microsoft YaHei", None]
    for name in font_names:
        if name is None:
            font = pygame.font.SysFont(None, size)
            font.set_bold(True)
            return font
        font_path = pygame.font.match_font(name)
        if font_path:
            font = pygame.font.Font(font_path, size)
            font.set_bold(True)
            return font
    font = pygame.font.SysFont(None, size)
    font.set_bold(True)
    return font


def draw_text(surface, text, x, y, color=(255, 255, 255), size=20):
    font = get_font(size)
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))


def draw_text_lines(surface, lines, x, y, color=(255, 255, 255), size=20, line_gap=8):
    font = get_font(size)
    line_height = font.get_height() + line_gap
    for idx, line in enumerate(lines):
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y + idx * line_height))




def add_damage_text(damage_texts, target_circle, damage, is_crit):
    color = (255, 255, 0) if is_crit else (255, 255, 255)
    offset_x = random.uniform(-target_circle.radius * 0.4, target_circle.radius * 0.4)
    offset_y = random.uniform(-target_circle.radius * 0.4, target_circle.radius * 0.4)
    damage_texts.append(
        {
            "x": target_circle.x + offset_x,
            "y": target_circle.y + offset_y,
            "vy": -40.0,
            "ttl": 0.6,
            "text": f"-{damage}",
            "color": color,
        }
    )


def apply_damage_to_circle(damage_texts, circle, damage, is_crit):
    if getattr(circle, "faker_invulnerable_timer", 0.0) > 0:
        return 0.0
    if circle.character_type == "T1 Faker" and getattr(circle, "faker_skill_state", None) is not None:
        return 0.0
    final_damage = damage
    if circle.character_type == "Gojo Satoru" and circle.ultimate_active:
        final_damage *= 0.5
    if circle.character_type == "T1 Faker" and circle.ultimate_active:
        final_damage *= 0.45
    final_damage = max(0.0, final_damage)
    circle.health = max(circle.health - final_damage, 0)
    if (
        circle.character_type == "T1 Faker"
        and circle.ultimate_active
        and circle.health <= 0
        and not getattr(circle, "faker_last_stand_used", False)
    ):
        circle.health = 1
        circle.faker_last_stand_used = True
        circle.faker_invulnerable_timer = 0.8
    shown_damage = max(1, int(round(final_damage))) if final_damage > 0 else 0
    if shown_damage > 0:
        add_damage_text(damage_texts, circle, shown_damage, is_crit)
    return final_damage


def apply_explosion_splash_damage(damage_texts, circles, owner_index, center_x, center_y, radius, damage, require_hostile=True):
    owner_circle = circles[owner_index] if 0 <= owner_index < len(circles) else None
    for idx, circle in enumerate(circles):
        if circle.health <= 0 or idx == owner_index:
            continue
        if require_hostile and not circles_are_hostile(owner_circle, circle):
            continue
        if math.hypot(circle.x - center_x, circle.y - center_y) <= radius + circle.radius:
            apply_damage_to_circle(damage_texts, circle, damage, False)


def get_faker_damage_bonus(circle, attack_type):
    if circle is None or circle.character_type != "T1 Faker" or not circle.ultimate_active:
        return 0
    return 60 if attack_type == "skill" else 24


def get_faker_skill_cooldown_rate(circle):
    if circle is None or circle.character_type != "T1 Faker" or not circle.ultimate_active:
        return 1.0
    return 1.5


def make_tinted_glow_image(image, color):
    if image is None:
        return None
    tinted = image.copy()
    tinted.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    tinted.fill((*color, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


def add_gojo_technique_explosion(explosions, x, y, base_radius, colors):
    particles = []
    particle_count = 24
    for _ in range(particle_count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(base_radius * 2.8, base_radius * 7.0)
        particles.append(
            {
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "radius": random.uniform(base_radius * 0.16, base_radius * 0.34),
                "ttl": random.uniform(0.22, 0.42),
                "max_ttl": 0.42,
                "color": random.choice(colors["particle"]),
            }
        )

    explosions.append(
        {
            "x": x,
            "y": y,
            "ttl": 0.36,
            "max_ttl": 0.36,
            "ring_radius": max(18.0, base_radius * 0.9),
            "ring_growth": max(70.0, base_radius * 5.5),
            "core_radius": max(10.0, base_radius * 0.65),
            "particles": particles,
            "ring_color": colors["ring"],
            "core_color": colors["core"],
            "core_highlight_color": colors["core_highlight"],
        }
    )


def update_gojo_technique_explosions(explosions, dt):
    alive_explosions = []
    for explosion in explosions:
        explosion["ttl"] -= dt
        if explosion["ttl"] <= 0:
            continue

        alive_particles = []
        for particle in explosion["particles"]:
            particle["ttl"] -= dt
            if particle["ttl"] <= 0:
                continue
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vx"] *= max(0.0, 1.0 - 3.2 * dt)
            particle["vy"] *= max(0.0, 1.0 - 3.2 * dt)
            alive_particles.append(particle)
        explosion["particles"] = alive_particles
        alive_explosions.append(explosion)

    return alive_explosions


def draw_gojo_technique_explosions(surface, explosions, offset_x=0, offset_y=0):
    for explosion in explosions:
        progress = 1.0 - (explosion["ttl"] / explosion["max_ttl"]) if explosion["max_ttl"] > 0 else 1.0
        ring_radius = explosion["ring_radius"] + explosion["ring_growth"] * progress
        ring_alpha = max(0, int(220 * (1.0 - progress)))
        ring_width = max(2, int(10 * (1.0 - progress) + 2))
        glow_size = max(1, int(ring_radius * 2 + 40))
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        center = glow_size // 2

        pygame.draw.circle(
            glow_surface,
            (*explosion["core_color"], max(0, int(95 * (1.0 - progress)))),
            (center, center),
            max(1, int(explosion["core_radius"] * (1.3 + progress * 0.8))),
        )
        pygame.draw.circle(
            glow_surface,
            (*explosion["core_highlight_color"], max(0, int(135 * (1.0 - progress)))),
            (center, center),
            max(1, int(explosion["core_radius"] * (0.75 + progress * 0.25))),
        )
        pygame.draw.circle(
            glow_surface,
            (*explosion["ring_color"], ring_alpha),
            (center, center),
            max(1, int(ring_radius)),
            ring_width,
        )
        surface.blit(
            glow_surface,
            glow_surface.get_rect(center=(int(explosion["x"] + offset_x), int(explosion["y"] + offset_y))),
        )

        for particle in explosion["particles"]:
            particle_progress = 1.0 - (particle["ttl"] / particle["max_ttl"]) if particle["max_ttl"] > 0 else 1.0
            particle_alpha = max(0, int(255 * (1.0 - particle_progress)))
            particle_surface_size = max(2, int(particle["radius"] * 4))
            particle_surface = pygame.Surface((particle_surface_size, particle_surface_size), pygame.SRCALPHA)
            particle_center = particle_surface_size // 2
            pygame.draw.circle(
                particle_surface,
                (*particle["color"], particle_alpha),
                (particle_center, particle_center),
                max(1, int(particle["radius"])),
            )
            surface.blit(
                particle_surface,
                particle_surface.get_rect(center=(int(particle["x"] + offset_x), int(particle["y"] + offset_y))),
            )


def draw_button(surface, rect, text, fill_color=(70, 130, 220), border_color=(220, 220, 255)):
    pygame.draw.rect(surface, (30, 30, 40), rect, border_radius=14)
    pygame.draw.rect(surface, fill_color, rect, 3, border_radius=14)
    text_surface = get_font(32).render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def load_optional_sound(base_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ("", ".ogg", ".wav", ".mp3"):
        path = os.path.join(base_dir, f"{base_name}{ext}")
        if os.path.isfile(path):
            try:
                return pygame.mixer.Sound(path)
            except pygame.error:
                return None
    return None


def amplify_sound(sound, factor):
    if sound is None or factor == 1.0:
        return sound
    try:
        samples = pygame.sndarray.array(sound)
    except (pygame.error, ValueError):
        return sound
    original_dtype = samples.dtype
    amplified = samples.astype(np.float32) * factor
    if np.issubdtype(original_dtype, np.integer):
        limits = np.iinfo(original_dtype)
        amplified = np.clip(amplified, limits.min, limits.max)
    else:
        amplified = np.clip(amplified, -1.0, 1.0)
    try:
        return pygame.sndarray.make_sound(amplified.astype(original_dtype))
    except pygame.error:
        return sound


def create_circle(name, character_type, x, y, image, gun_image, color, radius, health=1000):
    angle = random.uniform(0, math.tau)
    speed = random.uniform(220, 300)
    circle = Circle(
        x=x,
        y=y,
        vx=math.cos(angle) * speed,
        vy=math.sin(angle) * speed,
        radius=radius,
        health=health,
        color=color,
        name=name,
        image=image,
        gun_image=gun_image,
        character_type=character_type,
    )
    circle.bullet_timer = random.uniform(0.5, 1.0)
    return circle


def is_zombie_side(circle):
    return circle.controller == "zombie" or circle.character_type in ("Green Mob", "Giorno Mambo")


def circles_are_hostile(source_circle, target_circle):
    if source_circle is None or target_circle is None or source_circle is target_circle:
        return False
    source_is_zombie = is_zombie_side(source_circle)
    target_is_zombie = is_zombie_side(target_circle)
    if source_is_zombie or target_is_zombie:
        return source_is_zombie != target_is_zombie
    return True


def get_hostile_opponents(source_circle, circles):
    return [
        other
        for other in circles
        if other.health > 0 and circles_are_hostile(source_circle, other)
    ]


def is_player_controlled_human(circle):
    return circle.controller in ("player1", "player2") and not is_zombie_side(circle)


def get_apocalypse_damage_bonus(circle, damage_kind):
    if circle is None or not is_player_controlled_human(circle):
        return 0
    if damage_kind == "skill":
        return getattr(circle, "skill_damage_bonus", 0)
    if damage_kind == "normal":
        return getattr(circle, "normal_attack_damage_bonus", 0)
    return 0


def scale_apocalypse_damage(owner_circle, base_damage, attack_type):
    return base_damage + get_apocalypse_damage_bonus(owner_circle, attack_type)


def normalize_velocity(circle, target_speed):
    speed = math.hypot(circle.vx, circle.vy)
    if speed > 0:
        scale = target_speed / speed
        circle.vx *= scale
        circle.vy *= scale


def resolve_circle_collision(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    distance = math.hypot(dx, dy)
    min_dist = a.radius + b.radius
    if distance == 0 or distance >= min_dist:
        return

    nx = dx / distance
    ny = dy / distance
    overlap = min_dist - distance

    a.x -= nx * (overlap / 2)
    a.y -= ny * (overlap / 2)
    b.x += nx * (overlap / 2)
    b.y += ny * (overlap / 2)

    rel_vel = (a.vx - b.vx) * nx + (a.vy - b.vy) * ny
    if rel_vel > 0:
        return

    impulse = -rel_vel
    a.vx += impulse * nx
    a.vy += impulse * ny
    b.vx -= impulse * nx
    b.vy -= impulse * ny


def get_lead_unit_vector(shooter, target, projectile_speed, max_prediction_time=0.8, samples=28):
    rx = target.x - shooter.x
    ry = target.y - shooter.y
    tvx = target.vx
    tvy = target.vy
    direct_length = math.hypot(rx, ry)
    if direct_length <= 0:
        return None

    direct_x = rx / direct_length
    direct_y = ry / direct_length

    best_t = 0.0
    best_error = float("inf")
    best_aim_x = rx
    best_aim_y = ry

    for i in range(1, samples + 1):
        t = (max_prediction_time * i) / samples
        target_x = rx + tvx * t
        target_y = ry + tvy * t
        target_dist = math.hypot(target_x, target_y)
        bullet_dist = projectile_speed * t
        error = abs(target_dist - bullet_dist)

        if error < best_error:
            best_error = error
            best_t = t
            best_aim_x = target_x
            best_aim_y = target_y

    lead_len = math.hypot(best_aim_x, best_aim_y)
    if lead_len <= 0:
        return direct_x, direct_y

    lead_x = best_aim_x / lead_len
    lead_y = best_aim_y / lead_len

    # Blend lead and direct aim. Long prediction times are less reliable in a bounce-heavy arena.
    lead_weight = 0.85 - 0.45 * (best_t / max_prediction_time if max_prediction_time > 0 else 0.0)
    lead_weight = max(0.45, min(0.9, lead_weight))
    aim_x = direct_x * (1.0 - lead_weight) + lead_x * lead_weight
    aim_y = direct_y * (1.0 - lead_weight) + lead_y * lead_weight
    final_len = math.hypot(aim_x, aim_y)
    if final_len <= 0:
        return direct_x, direct_y
    return aim_x / final_len, aim_y / final_len


def apply_radial_push(source_x, source_y, target_x, target_y, radius, strength):
    dx = target_x - source_x
    dy = target_y - source_y
    distance = math.hypot(dx, dy)
    if distance <= 0 or distance > radius:
        return None
    falloff = 1.0 - (distance / radius)
    push = strength * falloff
    return (dx / distance) * push, (dy / distance) * push


def curve_bullet_toward_target(bullet, circles, dt, arena_size=None, arena_height=None):
    if bullet.hold_timer > 0 or bullet.turn_rate <= 0 or not (0 <= bullet.target_index < len(circles)):
        return

    target = circles[bullet.target_index]
    speed = math.hypot(bullet.vx, bullet.vy)
    if speed <= 0:
        return

    desired_dx = 0.0
    desired_dy = 0.0

    if target.health > 0:
        desired_dx += target.x - bullet.x
        desired_dy += target.y - bullet.y

    if bullet.source == "gojo_blue" and arena_size is not None:
        ah = arena_height if arena_height is not None else arena_size
        wall_margin = max(90.0, bullet.size * 10.0)
        center_x = arena_size * 0.5
        center_y = ah * 0.5

        if bullet.x < wall_margin:
            desired_dx += (wall_margin - bullet.x) * 2.6 + (center_x - bullet.x) * 0.35
        elif bullet.x > arena_size - wall_margin:
            desired_dx -= (bullet.x - (arena_size - wall_margin)) * 2.6 + (bullet.x - center_x) * 0.35

        if bullet.y < wall_margin:
            desired_dy += (wall_margin - bullet.y) * 2.6 + (center_y - bullet.y) * 0.35
        elif bullet.y > ah - wall_margin:
            desired_dy -= (bullet.y - (ah - wall_margin)) * 2.6 + (bullet.y - center_y) * 0.35

    distance = math.hypot(desired_dx, desired_dy)
    if distance <= 0:
        return

    desired_angle = math.atan2(desired_dy, desired_dx)
    current_angle = math.atan2(bullet.vy, bullet.vx)
    angle_delta = (desired_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
    max_turn = bullet.turn_rate * dt
    angle_delta = max(-max_turn, min(max_turn, angle_delta))
    new_angle = current_angle + angle_delta
    bullet.vx = math.cos(new_angle) * speed
    bullet.vy = math.sin(new_angle) * speed


def apply_blue_pull_to_circle(bullet, circle, dt):
    dx = circle.x - bullet.x
    dy = circle.y - bullet.y
    distance = math.hypot(dx, dy)
    if distance <= 0 or distance > bullet.field_radius:
        return False

    effective_pull_radius = max(circle.radius * 2.6, bullet.size * 24.0)
    if distance > effective_pull_radius:
        return True

    nx = dx / distance
    ny = dy / distance
    settle_distance = bullet.size * 0.65 + circle.radius * 0.3
    distance_to_settle = max(0.0, distance - settle_distance)
    pull_strength = 1.0 - min(1.0, distance / effective_pull_radius)
    base_pull_step = getattr(bullet, "pull_strength", 0.0)
    if base_pull_step > 0:
        pull_step = min(distance_to_settle, base_pull_step * dt)
    else:
        pull_step = min(distance_to_settle, (120.0 + 420.0 * pull_strength) * dt)

    circle.x -= nx * pull_step
    circle.y -= ny * pull_step

    velocity_damping = max(0.0, 1.0 - 7.0 * dt)
    circle.impulse_vx *= velocity_damping
    circle.impulse_vy *= velocity_damping
    circle.vx *= max(0.0, 1.0 - 2.2 * dt)
    circle.vy *= max(0.0, 1.0 - 2.2 * dt)
    circle.impulse_wall_bounces_remaining = 0
    return True


def apply_purple_lock_to_circle(bullet, circle, dt):
    dx = circle.x - bullet.x
    dy = circle.y - bullet.y
    distance = math.hypot(dx, dy)
    if distance <= 0 or distance > bullet.field_radius:
        return False

    effective_pull_radius = max(circle.radius * 3.0, bullet.size * 9.6)
    if distance > effective_pull_radius:
        return True

    nx = dx / distance
    ny = dy / distance
    settle_distance = bullet.size * 0.22 + circle.radius * 0.18
    distance_to_settle = max(0.0, distance - settle_distance)
    lock_strength = 1.0 - min(1.0, distance / effective_pull_radius)
    pull_step = min(distance_to_settle, (300.0 + 900.0 * lock_strength) * dt)

    circle.x -= nx * pull_step
    circle.y -= ny * pull_step

    velocity_damping = max(0.0, 1.0 - 10.0 * dt)
    circle.impulse_vx *= velocity_damping
    circle.impulse_vy *= velocity_damping
    circle.vx *= max(0.0, 1.0 - 5.0 * dt)
    circle.vy *= max(0.0, 1.0 - 5.0 * dt)
    circle.impulse_wall_bounces_remaining = 0
    return True


def draw_gojo_blue_black_hole(surface, bullet, elapsed_time, offset_x=0, offset_y=0):
    if bullet.source != "gojo_blue":
        return

    field_radius = max(bullet.size * 3.5, bullet.field_radius * 0.18)
    glow_size = max(2, int(field_radius * 2.4))
    glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    center = glow_size // 2
    cx = int(bullet.x + offset_x)
    cy = int(bullet.y + offset_y)

    pygame.draw.circle(glow_surface, (30, 40, 60, 115), (center, center), int(field_radius))
    pygame.draw.circle(glow_surface, (85, 170, 255, 70), (center, center), int(field_radius * 0.82), max(2, int(field_radius * 0.1)))
    pygame.draw.circle(glow_surface, (150, 225, 255, 80), (center, center), int(field_radius * 0.56), max(2, int(field_radius * 0.08)))
    pygame.draw.circle(glow_surface, (8, 12, 22, 220), (center, center), max(2, int(field_radius * 0.34)))
    pygame.draw.circle(glow_surface, (155, 225, 255, 70), (center, center), max(2, int(field_radius * 0.18)))

    for orbit_index in range(5):
        angle = elapsed_time * (2.2 + orbit_index * 0.35) + orbit_index * (math.tau / 5)
        orbit_radius = field_radius * (0.45 + orbit_index * 0.11)
        px = center + math.cos(angle) * orbit_radius
        py = center + math.sin(angle) * orbit_radius * 0.58
        particle_radius = max(2, int(bullet.size * (0.18 + orbit_index * 0.02)))
        pygame.draw.circle(glow_surface, (170, 235, 255, 165), (int(px), int(py)), particle_radius)

    surface.blit(glow_surface, glow_surface.get_rect(center=(cx, cy)))


def add_gojo_purple_trail(trails, x, y, size):
    trails.append(
        {
            "x": x,
            "y": y,
            "ttl": 0.45,
            "max_ttl": 0.45,
            "radius": size * random.uniform(0.5, 0.9),
            "spark_angle": random.uniform(0, math.tau),
        }
    )


def update_gojo_purple_trails(trails, dt):
    alive = []
    for trail in trails:
        trail["ttl"] -= dt
        if trail["ttl"] > 0:
            alive.append(trail)
    return alive


def draw_gojo_purple_trails(surface, trails, offset_x=0, offset_y=0):
    for trail in trails:
        progress = 1.0 - (trail["ttl"] / trail["max_ttl"])
        radius = trail["radius"] * (1.0 + progress * 1.7)
        alpha = max(0, int(185 * (1.0 - progress)))
        size = max(4, int(radius * 3.0))
        trail_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        pygame.draw.circle(trail_surface, (210, 130, 255, alpha), (center, center), max(2, int(radius)))
        pygame.draw.circle(trail_surface, (255, 220, 255, max(0, int(alpha * 0.7))), (center, center), max(1, int(radius * 0.45)))
        spark_length = radius * 0.85
        angle = trail["spark_angle"] + progress * 2.4
        x1 = center + math.cos(angle) * spark_length
        y1 = center + math.sin(angle) * spark_length
        x2 = center - math.cos(angle) * spark_length
        y2 = center - math.sin(angle) * spark_length
        pygame.draw.line(trail_surface, (255, 245, 255, max(0, int(alpha * 0.9))), (x1, y1), (x2, y2), max(1, int(radius * 0.18)))
        surface.blit(trail_surface, trail_surface.get_rect(center=(int(trail["x"] + offset_x), int(trail["y"] + offset_y))))


def add_faker_dust_trail(trails, x, y, radius):
    trails.append(
        {
            "x": x,
            "y": y,
            "ttl": 0.32,
            "max_ttl": 0.32,
            "radius": radius,
        }
    )


def update_faker_dust_trails(trails, dt):
    alive = []
    for trail in trails:
        trail["ttl"] -= dt
        if trail["ttl"] > 0:
            alive.append(trail)
    return alive


def draw_faker_dust_trails(surface, trails, offset_x=0, offset_y=0):
    for trail in trails:
        progress = 1.0 - (trail["ttl"] / trail["max_ttl"])
        radius = trail["radius"] * (0.8 + progress * 1.4)
        alpha = max(0, int(120 * (1.0 - progress)))
        dust_surface = pygame.Surface((int(radius * 4), int(radius * 4)), pygame.SRCALPHA)
        center = dust_surface.get_width() // 2
        pygame.draw.circle(dust_surface, (216, 185, 120, alpha), (center, center), max(2, int(radius)))
        pygame.draw.circle(dust_surface, (250, 220, 170, max(0, int(alpha * 0.65))), (center, center), max(1, int(radius * 0.55)))
        surface.blit(dust_surface, dust_surface.get_rect(center=(int(trail["x"] + offset_x), int(trail["y"] + offset_y))))


def add_faker_magic_flame(flames, x, y, radius, color):
    flames.append(
        {
            "x": x,
            "y": y,
            "radius": radius,
            "ttl": 0.26,
            "max_ttl": 0.26,
            "color": color,
        }
    )


def update_faker_magic_flames(flames, dt):
    alive = []
    for flame in flames:
        flame["ttl"] -= dt
        if flame["ttl"] <= 0:
            continue
        alive.append(flame)
    return alive


def draw_faker_magic_flames(surface, flames, offset_x=0, offset_y=0):
    for flame in flames:
        progress = 1.0 - (flame["ttl"] / flame["max_ttl"]) if flame["max_ttl"] > 0 else 1.0
        radius = flame["radius"] * (0.8 + progress * 1.1)
        alpha = max(0, int(200 * (1.0 - progress)))
        flame_surface = pygame.Surface((int(radius * 5), int(radius * 5)), pygame.SRCALPHA)
        center = flame_surface.get_width() // 2
        r, g, b = flame["color"]
        pygame.draw.circle(flame_surface, (r, g, b, max(0, int(alpha * 0.32))), (center, center), max(3, int(radius * 1.7)))
        pygame.draw.circle(flame_surface, (r, g, b, alpha), (center, center), max(2, int(radius)))
        pygame.draw.circle(flame_surface, (255, 245, 255, max(0, int(alpha * 0.78))), (center, center), max(1, int(radius * 0.45)))
        surface.blit(flame_surface, flame_surface.get_rect(center=(int(flame["x"] + offset_x), int(flame["y"] + offset_y))))


def move_circle_toward(circle, target_x, target_y, max_step):
    dx = target_x - circle.x
    dy = target_y - circle.y
    distance = math.hypot(dx, dy)
    if distance <= max_step or distance <= 1e-6:
        circle.x = target_x
        circle.y = target_y
        return True
    circle.x += (dx / distance) * max_step
    circle.y += (dy / distance) * max_step
    return False


def update_faker_skill_actions(circles, dt, waves, dust_trails):
    dash_speed = (300.0 * 3.0) / 1.3
    shake_strength = 0.0

    for circle in circles:
        state = getattr(circle, "faker_skill_state", None)
        if circle.character_type != "T1 Faker" or not state:
            continue
        if circle.health <= 0:
            circle.faker_skill_state = None
            continue

        circle.vx = 0.0
        circle.vy = 0.0
        circle.impulse_vx = 0.0
        circle.impulse_vy = 0.0
        circle.impulse_wall_bounces_remaining = 0
        state["phase_timer"] = max(0.0, state.get("phase_timer", 0.0) - dt)

        destination_x = state["dash_out_x"] if state["phase"] == "dash_out" else state["origin_x"]
        destination_y = state["dash_out_y"] if state["phase"] == "dash_out" else state["origin_y"]
        reached = move_circle_toward(circle, destination_x, destination_y, dash_speed * dt)
        timed_out = state["phase_timer"] <= 0.0

        trail_radius = max(circle.radius * 0.32, 10.0)
        add_faker_dust_trail(dust_trails, circle.x - state["push_dir_x"] * circle.radius * 0.4, circle.y - state["push_dir_y"] * circle.radius * 0.4, trail_radius)
        shake_strength = max(shake_strength, 5.0 if state["phase"] == "dash_out" else 3.0)

        if state["phase"] == "dash_out" and (reached or timed_out):
            circle.x = destination_x
            circle.y = destination_y
            waves.append(
                {
                    "owner_index": state["owner_index"],
                    "primary_target_index": state["target_index"],
                    "origin_x": state["wall_start_x"],
                    "origin_y": state["wall_start_y"],
                    "center_x": state["wall_start_x"],
                    "center_y": state["wall_start_y"],
                    "dir_x": state["push_dir_x"],
                    "dir_y": state["push_dir_y"],
                    "perp_x": -state["push_dir_y"],
                    "perp_y": state["push_dir_x"],
                    "length": state["wall_length"],
                    "thickness": state["wall_thickness"],
                    "start_offset": 0.0,
                    "travel_distance": state["wall_travel_distance"],
                    "windup": 0.0,
                    "move_duration": state["wall_move_duration"],
                    "linger_duration": 4.0,
                    "total_duration": state["wall_move_duration"] + 4.0,
                    "age": 0.0,
                    "push_strength": 2400.0,
                    "push_speed": dash_speed * 0.95,
                    "damage": 100,
                    "barrier_padding": max(10.0, circle.radius * 0.3),
                    "hit_targets": set(),
                }
            )
            state["phase"] = "dash_back"
            state["phase_timer"] = state.get("dash_back_duration", 0.18)
        elif state["phase"] == "dash_back" and (reached or timed_out):
            circle.x = destination_x
            circle.y = destination_y
            circle.faker_skill_state = None

    return shake_strength


def update_faker_soldier_waves(waves, circles, dt, damage_texts, dust_trails):
    alive = []
    shake_strength = 0.0
    for wave in waves:
        wave["age"] += dt
        age = wave["age"]
        windup = wave["windup"]
        move_duration = wave.get("move_duration", wave.get("dash_duration", 0.0))
        linger_duration = wave.get("linger_duration", max(0.0, wave["total_duration"] - windup - move_duration))
        total_duration = wave["total_duration"]

        if age >= total_duration:
            continue

        center_x = wave["origin_x"]
        center_y = wave["origin_y"]
        if age >= windup:
            if move_duration > 0:
                progress = min(1.0, (age - windup) / move_duration)
            else:
                progress = 1.0
            travel = wave["start_offset"] + wave["travel_distance"] * progress
            center_x += wave["dir_x"] * travel
            center_y += wave["dir_y"] * travel
            is_moving = age < windup + move_duration
            if is_moving:
                dust_x = center_x - wave["dir_x"] * (wave["thickness"] * 0.45)
                dust_y = center_y - wave["dir_y"] * (wave["thickness"] * 0.45)
                add_faker_dust_trail(dust_trails, dust_x, dust_y, wave["thickness"] * 0.18)
                shake_strength = max(shake_strength, 6.0 * (1.0 - min(1.0, progress)) + 1.5)
            elif linger_duration > 0:
                linger_progress = min(1.0, (age - windup - move_duration) / linger_duration)
                shake_strength = max(shake_strength, 1.5 * (1.0 - linger_progress))

            owner_circle = circles[wave["owner_index"]] if 0 <= wave["owner_index"] < len(circles) else None
            for idx, circle in enumerate(circles):
                if idx == wave["owner_index"] or circle.health <= 0:
                    continue
                if not circles_are_hostile(owner_circle, circle):
                    continue
                rel_x = circle.x - center_x
                rel_y = circle.y - center_y
                local_forward = rel_x * wave["dir_x"] + rel_y * wave["dir_y"]
                local_side = rel_x * wave["perp_x"] + rel_y * wave["perp_y"]
                max_forward = wave["thickness"] * 0.5 + circle.radius
                max_side = wave["length"] * 0.5 + circle.radius
                if abs(local_forward) > max_forward or abs(local_side) > max_side:
                    continue

                penetration = max(0.0, max_forward - local_forward + wave.get("barrier_padding", 0.0))
                push_step = max(0.0, wave.get("push_speed", 280.0) * dt + penetration * 0.75)
                circle.x += wave["dir_x"] * push_step
                circle.y += wave["dir_y"] * push_step
                circle.impulse_vx += wave["dir_x"] * wave["push_strength"] * dt
                circle.impulse_vy += wave["dir_y"] * wave["push_strength"] * dt
                circle.vx *= max(0.0, 1.0 - 4.5 * dt)
                circle.vy *= max(0.0, 1.0 - 4.5 * dt)
                circle.impulse_wall_bounces_remaining = max(circle.impulse_wall_bounces_remaining, 2)

                if idx not in wave["hit_targets"]:
                    wave["hit_targets"].add(idx)
                    damage = scale_apocalypse_damage(owner_circle, wave["damage"], "skill")
                    if damage > 0:
                        apply_damage_to_circle(damage_texts, circle, damage, False)

        wave["center_x"] = center_x
        wave["center_y"] = center_y
        alive.append(wave)
    return alive, shake_strength


def draw_faker_soldier_waves(surface, waves, elapsed_time, offset_x=0, offset_y=0):
    for wave in waves:
        age = wave["age"]
        progress = min(1.0, age / wave["total_duration"]) if wave["total_duration"] > 0 else 1.0
        cx = wave.get("center_x", wave["origin_x"]) + offset_x
        cy = wave.get("center_y", wave["origin_y"]) + offset_y
        dir_x = wave["dir_x"]
        dir_y = wave["dir_y"]
        perp_x = wave["perp_x"]
        perp_y = wave["perp_y"]
        length = wave["length"]
        thickness = wave["thickness"]

        wall_surface = pygame.Surface((int(length + thickness * 3), int(length + thickness * 3)), pygame.SRCALPHA)
        center = wall_surface.get_width() // 2
        wall_rect = pygame.Rect(
            int(center - thickness * 0.5),
            int(center - length * 0.5),
            int(thickness),
            int(length),
        )

        if age < wave["windup"]:
            windup_progress = age / wave["windup"] if wave["windup"] > 0 else 1.0
            glow_radius = int(thickness * (0.7 + windup_progress * 0.45))
            pygame.draw.circle(wall_surface, (245, 210, 110, 90), (center, center), glow_radius)
            pygame.draw.circle(wall_surface, (255, 230, 165, 140), (center, center), max(8, int(glow_radius * 0.55)), 3)
        else:
            move_duration = wave.get("move_duration", wave.get("dash_duration", 0.0))
            moving = age < wave["windup"] + move_duration
            trail_len = max(12, int(thickness * 2.4))
            if moving:
                shock_rect = pygame.Rect(int(center - trail_len), int(center - length * 0.52), trail_len, int(length * 1.04))
                pygame.draw.rect(wall_surface, (225, 188, 110, 78), shock_rect, border_radius=max(6, int(trail_len * 0.2)))
            pygame.draw.rect(wall_surface, (255, 225, 150, 125), wall_rect, border_radius=max(8, int(thickness * 0.22)))
            edge_rect = pygame.Rect(wall_rect.x + max(2, wall_rect.width - max(8, int(thickness * 0.18))), wall_rect.y, max(8, int(thickness * 0.18)), wall_rect.height)
            pygame.draw.rect(wall_surface, (255, 245, 205, 170), edge_rect, border_radius=max(4, int(thickness * 0.12)))

            soldier_count = 7
            for i in range(soldier_count):
                t = 0 if soldier_count == 1 else i / (soldier_count - 1)
                sy = wall_rect.y + int(t * wall_rect.height)
                phase = elapsed_time * 8.0 + i * 0.55
                body_h = max(10, int(thickness * 0.34))
                body_w = max(8, int(thickness * 0.16))
                bob = math.sin(phase) * 3.0
                soldier_x = edge_rect.x - body_w - 4
                soldier_y = sy - body_h // 2 + bob
                pygame.draw.rect(wall_surface, (90, 70, 35, 155), (soldier_x, soldier_y, body_w, body_h), border_radius=max(3, body_w // 3))
                pygame.draw.circle(wall_surface, (248, 214, 132, 185), (soldier_x + body_w // 2, int(soldier_y - body_w * 0.2)), max(3, body_w // 2))

        angle = math.degrees(math.atan2(dir_y, dir_x))
        rotated = pygame.transform.rotate(wall_surface, -angle)
        surface.blit(rotated, rotated.get_rect(center=(int(cx), int(cy))))


def draw_faker_blink_marks(surface, circles, elapsed_time, offset_x=0, offset_y=0):
    for circle in circles:
        if circle.character_type != "T1 Faker" or not getattr(circle, "faker_blink_mark_active", False):
            continue
        pulse = 0.78 + 0.22 * math.sin(elapsed_time * 10.0)
        outer_radius = max(18, int(circle.radius * 1.18 * pulse))
        inner_radius = max(8, int(circle.radius * 0.5))
        mark_surface = pygame.Surface((outer_radius * 5, outer_radius * 5), pygame.SRCALPHA)
        center = mark_surface.get_width() // 2
        pygame.draw.circle(mark_surface, (70, 170, 255, 55), (center, center), outer_radius + 22)
        pygame.draw.circle(mark_surface, (110, 215, 255, 85), (center, center), outer_radius + 10)
        pygame.draw.circle(mark_surface, (160, 235, 255, 210), (center, center), outer_radius, 4)
        pygame.draw.circle(mark_surface, (235, 250, 255, 210), (center, center), inner_radius, 3)
        pygame.draw.circle(mark_surface, (180, 240, 255, 150), (center, center), max(5, inner_radius // 2 + 1))
        surface.blit(
            mark_surface,
            mark_surface.get_rect(center=(int(circle.faker_blink_mark_x + offset_x), int(circle.faker_blink_mark_y + offset_y))),
        )


def draw_faker_charm_status(surface, circles, elapsed_time, offset_x=0, offset_y=0):
    for circle in circles:
        if getattr(circle, "faker_charmed_timer", 0.0) <= 0:
            continue
        pulse = 0.82 + 0.18 * math.sin(elapsed_time * 12.0)
        heart_size = max(18, int(circle.radius * 0.95 * pulse))
        heart_surface = pygame.Surface((heart_size * 4, heart_size * 4), pygame.SRCALPHA)
        cx = heart_surface.get_width() // 2
        cy = heart_surface.get_height() // 2
        left = (cx - heart_size * 0.35, cy - heart_size * 0.2)
        right = (cx + heart_size * 0.35, cy - heart_size * 0.2)
        bottom = (cx, cy + heart_size * 0.7)
        pygame.draw.circle(heart_surface, (255, 120, 215, 170), (int(left[0]), int(left[1])), max(4, int(heart_size * 0.38)))
        pygame.draw.circle(heart_surface, (255, 120, 215, 170), (int(right[0]), int(right[1])), max(4, int(heart_size * 0.38)))
        pygame.draw.polygon(
            heart_surface,
            (255, 150, 225, 185),
            [
                (int(cx - heart_size * 0.7), int(cy - heart_size * 0.05)),
                (int(cx + heart_size * 0.7), int(cy - heart_size * 0.05)),
                (int(bottom[0]), int(bottom[1])),
            ],
        )
        surface.blit(
            heart_surface,
            heart_surface.get_rect(center=(int(circle.x + offset_x), int(circle.y - circle.radius - 18 + offset_y))),
        )

def draw_gojo_hollow_purple_charge(surface, circle, target, elapsed_time, match_assets, arena_left=0, arena_top=0):
    if circle.gojo_ultimate_stage not in ("merge", "hold"):
        return
    blue_image = match_assets.get("gojo_blue_merge_image") or match_assets.get("gojo_blue_projectile_image")
    red_image = match_assets.get("gojo_red_projectile_image")
    purple_image = match_assets.get("gojo_hollow_purple_image")
    if blue_image is None or red_image is None or purple_image is None:
        return

    if target:
        dx = target.x - circle.x
        dy = target.y - circle.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            ux = dx / distance
            uy = dy / distance
        else:
            ux, uy = 1.0, 0.0
    else:
        ux, uy = 1.0, 0.0
    perp_x = -uy
    perp_y = ux
    hand_x = circle.x + ux * (circle.radius + 24)
    hand_y = circle.y + uy * (circle.radius + 24)

    blue_size = max(blue_image.get_width(), blue_image.get_height())
    if circle.gojo_ultimate_stage == "merge":
        charge_duration = circle.gojo_ultimate_charge_duration if circle.gojo_ultimate_charge_duration > 0 else 2.0
        progress = 1.0 - (circle.gojo_ultimate_timer / charge_duration if circle.gojo_ultimate_timer > 0 else 0.0)
        side_offset = max(0.0, (1.0 - progress) * 100.0)
        left_center = (hand_x - perp_x * side_offset, hand_y - perp_y * side_offset)
        right_center = (hand_x + perp_x * side_offset, hand_y + perp_y * side_offset)
        blue_glow_size = max(blue_image.get_width(), blue_image.get_height()) + 36
        blue_glow = pygame.Surface((blue_glow_size, blue_glow_size), pygame.SRCALPHA)
        blue_glow_center = blue_glow_size // 2
        pygame.draw.circle(blue_glow, (120, 210, 255, 90), (blue_glow_center, blue_glow_center), max(8, blue_glow_size // 2 - 6))
        pygame.draw.circle(blue_glow, (185, 240, 255, 130), (blue_glow_center, blue_glow_center), max(4, blue_glow_size // 3))
        surface.blit(blue_glow, blue_glow.get_rect(center=(int(left_center[0] + arena_left), int(left_center[1] + arena_top))))
        surface.blit(blue_image, blue_image.get_rect(center=(int(left_center[0] + arena_left), int(left_center[1] + arena_top))))
        surface.blit(red_image, red_image.get_rect(center=(int(right_center[0] + arena_left), int(right_center[1] + arena_top))))
        purple_scale = 1.0 + progress * 3.0
    else:
        purple_scale = 4.0

    purple_size = max(8, int(blue_size * purple_scale))
    charge_image = pygame.transform.smoothscale(purple_image, (purple_size, purple_size))
    aura_surface = pygame.Surface((purple_size + 30, purple_size + 30), pygame.SRCALPHA)
    aura_center = aura_surface.get_width() // 2
    aura_alpha = 120 + int(60 * math.sin(elapsed_time * 10.0))
    pygame.draw.circle(aura_surface, (180, 110, 255, max(40, aura_alpha)), (aura_center, aura_center), max(6, purple_size // 2 + 8), max(2, purple_size // 14))
    surface.blit(aura_surface, aura_surface.get_rect(center=(int(hand_x + arena_left), int(hand_y + arena_top))))
    surface.blit(charge_image, charge_image.get_rect(center=(int(hand_x + arena_left), int(hand_y + arena_top))))


def draw_infinite_void_background(surface, rect, elapsed_time):
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((18, 10, 38, 170))
    center_x = rect.width // 2
    center_y = rect.height // 2
    for ring_index in range(7):
        pulse = (elapsed_time * (0.7 + ring_index * 0.09) + ring_index * 0.45) % 1.0
        radius = int((0.15 + pulse * 0.85) * min(rect.width, rect.height) * 0.55)
        alpha = max(18, int(105 * (1.0 - pulse)))
        color = (145 + ring_index * 10, 120 + ring_index * 8, 255, alpha)
        pygame.draw.circle(overlay, color, (center_x, center_y), max(12, radius), max(2, int(min(rect.width, rect.height) * 0.008)))
    for star_index in range(42):
        angle = star_index * 0.61 + elapsed_time * (0.12 + (star_index % 5) * 0.02)
        orbit = min(rect.width, rect.height) * (0.16 + (star_index % 9) * 0.055)
        x = center_x + math.cos(angle) * orbit
        y = center_y + math.sin(angle * 1.35) * orbit * 0.78
        radius = 1 + (star_index % 3)
        pygame.draw.circle(overlay, (225, 220, 255, 145), (int(x), int(y)), radius)
    surface.blit(overlay, rect.topleft)


def load_video_background(path, width, height):
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.isfile(path):
        return None
    capture = cv2.VideoCapture(path)
    if not capture.isOpened():
        return None
    fps = capture.get(cv2.CAP_PROP_FPS)
    return {
        "capture": capture,
        "fps": fps if fps and fps > 0 else 30.0,
        "frame_time": 0.0,
        "width": width,
        "height": height,
        "surface": None,
    }


def restart_video_background(video_state):
    if video_state is None:
        return
    video_state["capture"].set(cv2.CAP_PROP_POS_FRAMES, 0)
    video_state["frame_time"] = 0.0
    video_state["surface"] = None


def update_video_background(video_state, dt):
    if video_state is None:
        return None
    video_state["frame_time"] += dt
    frame_interval = 1.0 / max(1.0, video_state["fps"])
    while video_state["surface"] is None or video_state["frame_time"] >= frame_interval:
        if video_state["surface"] is not None:
            video_state["frame_time"] -= frame_interval
        ok, frame = video_state["capture"].read()
        if not ok:
            video_state["capture"].set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = video_state["capture"].read()
            if not ok:
                return video_state["surface"]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (video_state["width"], video_state["height"]), interpolation=cv2.INTER_AREA)
        frame = frame.swapaxes(0, 1)
        video_state["surface"] = pygame.surfarray.make_surface(frame).convert()
        if frame_interval <= 0:
            break
    return video_state["surface"]


def simulate():
    print("GAME STARTED!")  # Debug output
    _game_dir = os.path.dirname(os.path.abspath(__file__))
    pygame.init()
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
    except pygame.error:
        pass
    display_info = pygame.display.Info()
    desktop_width = display_info.current_w
    desktop_height = display_info.current_h
    radius = 50
    ui_panel_height = 220
    arena_margin = 20
    window_height = max(720, desktop_height - 80)
    base_square_size = window_height - ui_panel_height - arena_margin * 2
    square_size = base_square_size
    window_width = max(1100, min(desktop_width - 120, square_size + 260))
    screen_width = window_width
    screen_height = window_height
    arena_width = base_square_size
    arena_height = base_square_size
    arena_left = (window_width - square_size) // 2
    arena_top = arena_margin
    tube_top_height = 0
    zombie_spawn_timer = 0.0
    window_size = window_width
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Two Circle Health Simulation")
    clock = pygame.time.Clock()
    # Full-window domain background (video file in game folder, same dir as game.py)
    infinite_void_video = load_video_background("infinte void domain image.mp4", window_width, window_height)

    def load_image(path):
        full = path if os.path.isabs(path) else os.path.join(_game_dir, path)
        try:
            return pygame.image.load(full).convert_alpha()
        except pygame.error:
            print(f"Warning: {full} not found.")
            return None

    def scale_to_fit(image, width, height):
        if image is None:
            return None
        orig_width, orig_height = image.get_size()
        scale = min(width / orig_width, height / orig_height)
        if scale == 1.0:
            return image
        return pygame.transform.smoothscale(image, (max(1, int(orig_width * scale)), max(1, int(orig_height * scale))))

    mika_original = load_image("Mika swimsuit png.png")
    vu_original = load_image("vu a vu png.png")
    mika_ue_original = load_image("Mika swimsuit UE.png.webp")
    mika_meteor_original = load_image("meteor misono mika.png")
    mika_bullet_original = load_image("pink bullet mika.png")
    vu_projectile_original = load_image("ba mia.png")
    vu_ultimate_projectile_original = load_image("ba mia real.png")
    vu_ultimate_original = load_image("pharatay ultimate.png")
    gojo_original = load_image("gomen amanai.png")
    gojo_red_original = load_image("cursed technique red.png")
    gojo_blue_original = make_tinted_glow_image(gojo_red_original, (135, 206, 250))
    gojo_purple_original = load_image("hollow purple.png")
    do_mixi_win_loser_original = load_image("meo cam kho ga.png")
    mika_ultimate_xd_original = load_image("mika ultimate XD.png")
    mambo_original = load_image("mambo face.png")
    giorno_mambo_original = load_image("giorno mambo.png")
    faker_original = load_image("T1 Faker.png")
    faker_normal_attack_original = load_image("Faker normal attack.png")
    faker_call_original = load_image("faker call.png")
    mika_image = scale_to_fit(mika_original, radius * 2, radius * 2)
    vu_image = scale_to_fit(vu_original, int(radius * 2 * 1.4), radius * 2)
    vu_ultimate_image = scale_to_fit(vu_ultimate_original, int(radius * 2 * 1.4 * 1.2), int(radius * 2 * 1.2))
    gojo_image = scale_to_fit(gojo_original, radius * 2, radius * 2)
    gojo_red_projectile_image = scale_to_fit(gojo_red_original, int(radius * 1.1), int(radius * 1.1))
    gojo_blue_projectile_image = scale_to_fit(gojo_blue_original, int((radius * 1.1) / 1.3), int((radius * 1.1) / 1.3))
    gojo_blue_merge_image = scale_to_fit(gojo_blue_original, int(radius * 1.1), int(radius * 1.1))
    gojo_hollow_purple_image = scale_to_fit(gojo_purple_original, int((radius * 1.1) / 1.3), int((radius * 1.1) / 1.3))
    do_mixi_win_loser_image = scale_to_fit(do_mixi_win_loser_original, int(radius * 2 * 1.4), radius * 2)
    mambo_image = scale_to_fit(mambo_original, int(radius * 2 * 1.4), radius * 2)
    giorno_mambo_image = scale_to_fit(giorno_mambo_original, int(radius * 2 * 1.4), radius * 2)
    faker_image = scale_to_fit(faker_original, int(radius * 2.2 * 1.3), int(radius * 2.2 * 1.3))
    faker_normal_attack_image = scale_to_fit(faker_normal_attack_original, int(radius * 1.2), int(radius * 1.2))
    faker_call_image = scale_to_fit(faker_call_original, int(radius * 1.15), int(radius * 1.15))
    mika_gun_image = scale_to_fit(mika_ue_original, int(radius * 2.2), radius * 2)
    mika_meteor_image = scale_to_fit(mika_meteor_original, radius, radius)
    mika_ultimate_finish_meteor_image = scale_to_fit(mika_meteor_original, radius * 4, radius * 4)
    mika_bullet_image = scale_to_fit(mika_bullet_original, 56, 56)
    mika_bullet_ultimate_image = scale_to_fit(mika_bullet_original, 56, 56)
    vu_projectile_image = scale_to_fit(vu_projectile_original, int(46 * 1.5 * 1.5), int(46 * 1.5 * 1.5))
    vu_ultimate_projectile_image = scale_to_fit(vu_ultimate_projectile_original, int(46 * 1.5 * 1.5), int(46 * 1.5 * 1.5))
    if mika_image:
        base_w, base_h = mika_image.get_size()
    else:
        base_w, base_h = radius * 2, radius * 2
    mika_ultimate_xd_image = scale_to_fit(
        mika_ultimate_xd_original,
        max(1, int(base_w * 2 / 1.5 * 1.3)),
        max(1, int(base_h * 2 / 1.5 * 1.3)),
    )
    mika_ultimate_body_image = None
    mika_ultimate_halo_image = None
    if mika_ultimate_xd_image:
        uw, uh = mika_ultimate_xd_image.get_size()
        halo_h = max(1, int(uh * 0.18))
        mika_ultimate_body_image = mika_ultimate_xd_image.copy()
        pygame.draw.rect(mika_ultimate_body_image, (0, 0, 0, 0), pygame.Rect(0, 0, uw, halo_h + 2))
        mika_ultimate_halo_image = pygame.Surface((uw, halo_h), pygame.SRCALPHA)
        mika_ultimate_halo_image.blit(mika_ultimate_xd_image, (0, 0), pygame.Rect(0, 0, uw, halo_h))
    mika_ultimate_voice_bases = [
        "Mika_Swimsuit_ExSkill_1_2",
        "Mika_Swimsuit_ExSkill_1_3",
        "Mika_Swimsuit_ExSkill_2_1",
        "Mika_Swimsuit_ExSkill_2_2",
    ]
    mika_ultimate_voice_sounds = [snd for snd in (load_optional_sound(name) for name in mika_ultimate_voice_bases) if snd is not None]
    vu_bamia_sound = load_optional_sound("may chua tay dau")
    vu_ultimate_sound = load_optional_sound("alo vu ha em mp3")
    do_mixi_win_sound = load_optional_sound("an do mixi")
    gojo_win_sound = load_optional_sound("yowai mo")
    gojo_infinite_void_sound = amplify_sound(load_optional_sound("infinite void"), 2.0)
    gojo_lapse_blue_sound = amplify_sound(load_optional_sound("gojo lapse blue audio"), 2.0)
    gojo_reversal_red_sound = amplify_sound(load_optional_sound("gojo reversal red audio"), 2.0)
    gojo_hollow_purple_sound = amplify_sound(load_optional_sound("hollow purple audio"), 2.0)
    hachimi_sound = load_optional_sound("hachimi")
    hachimi_on_your_lawn_sound = load_optional_sound("hachimi on your lawn")
    hachimi_high_on_life_sound = load_optional_sound("hachimi high on life")
    golden_wind_mambo_sound = load_optional_sound("golden wind mambo")
    faker_call_sound = load_optional_sound("faker call audio")
    if gojo_infinite_void_sound:
        gojo_infinite_void_sound.set_volume(1.0)
    if gojo_lapse_blue_sound:
        gojo_lapse_blue_sound.set_volume(1.0)
    if gojo_reversal_red_sound:
        gojo_reversal_red_sound.set_volume(1.0)
    if gojo_hollow_purple_sound:
        gojo_hollow_purple_sound.set_volume(1.0)
    if faker_call_sound:
        faker_call_sound.set_volume(1.0)
    voice_primary_channel = pygame.mixer.Channel(0) if pygame.mixer.get_init() else None
    voice_secondary_channel = pygame.mixer.Channel(1) if pygame.mixer.get_init() else None
    music_channel = pygame.mixer.Channel(2) if pygame.mixer.get_init() else None
    zombie_music_mode = None
    
    def play_music_sound(sound):
        if sound is None or music_channel is None:
            return
        if music_channel.get_busy():
            music_channel.stop()
        music_channel.play(sound)

    def ensure_zombie_wave_music(mode):
        nonlocal zombie_music_mode
        if music_channel is None or zombie_music_mode == mode:
            return
        zombie_music_mode = mode
        music_channel.stop()
        if mode == "golden":
            if golden_wind_mambo_sound:
                music_channel.play(golden_wind_mambo_sound)
        else:
            opener = hachimi_on_your_lawn_sound or hachimi_sound
            if opener:
                music_channel.play(opener)
                if hachimi_high_on_life_sound and opener is not hachimi_high_on_life_sound:
                    music_channel.queue(hachimi_high_on_life_sound)
            elif hachimi_high_on_life_sound:
                music_channel.play(hachimi_high_on_life_sound)

    def stop_all_audio():
        nonlocal zombie_music_mode
        zombie_music_mode = None
        try:
            pygame.mixer.stop()
        except pygame.error:
            pass

    def play_voice_sound(sound, *, preferred="secondary", priority=False, block_if_primary=False):
        if sound is None:
            return
        if voice_primary_channel is None or voice_secondary_channel is None:
            sound.play()
            return
        if block_if_primary and voice_primary_channel.get_busy():
            return

        channel = voice_primary_channel if preferred == "primary" else voice_secondary_channel
        other_channel = voice_secondary_channel if channel is voice_primary_channel else voice_primary_channel

        if priority:
            channel.stop()
            channel.set_volume(1.0)
            if other_channel.get_busy():
                other_channel.set_volume(0.55)
            channel.play(sound)
            return

        if other_channel.get_busy():
            other_channel.set_volume(0.65)
            channel.set_volume(0.65)
        else:
            other_channel.set_volume(1.0)
            channel.set_volume(1.0)
        channel.play(sound)
    menu_state = "mode"
    game_mode = "sim"
    bot_difficulty = "medium"
    custom_count_input = ""
    zombie_count_input = ""
    mambo_count_input = ""
    current_wave = 1
    mambos_spawned_in_wave = 0
    mambos_to_spawn = 0
    wave_in_progress = False
    wave_complete = False
    player_count = 0
    selected_players = []
    circles = []
    bullets = []
    meteors = []
    damage_texts = []
    red_explosions = []
    purple_trails = []
    faker_waves = []
    faker_dust_trails = []
    faker_magic_flames = []
    screen_shake_timer = 0.0
    screen_shake_strength = 0.0
    faker_ultimate_hitstop_timer = 0.0
    gojo_red_colors = {
        "particle": [
            (255, 90, 90),
            (255, 50, 50),
            (255, 140, 140),
            (255, 210, 210),
        ],
        "ring": (255, 110, 110),
        "core": (255, 70, 70),
        "core_highlight": (255, 210, 210),
    }
    gojo_blue_colors = {
        "particle": [
            (120, 205, 255),
            (95, 185, 255),
            (160, 225, 255),
            (220, 245, 255),
        ],
        "ring": (130, 210, 255),
        "core": (90, 180, 255),
        "core_highlight": (220, 245, 255),
    }
    gojo_purple_colors = {
        "particle": [
            (180, 110, 255),
            (210, 140, 255),
            (235, 200, 255),
            (150, 80, 230),
        ],
        "ring": (195, 120, 255),
        "core": (125, 70, 210),
        "core_highlight": (240, 215, 255),
    }
    faker_blue_explosion_colors = {
        "particle": [
            (150, 230, 255),
            (110, 210, 255),
            (215, 245, 255),
            (245, 252, 255),
        ],
        "ring": (185, 238, 255),
        "core": (120, 210, 255),
        "core_highlight": (255, 255, 255),
    }
    colliding_pairs = set()
    running = True
    elapsed_time = 0.0
    battle_time = 0.0
    result_winner_name = ""
    result_show_options = False
    result_special_click_needed = False
    zombie_save_path = os.path.join(_game_dir, "mambo_apocalypse_save.json")
    pending_zombie_resume_data = None

    mode_rects = [
        pygame.Rect(screen_width // 2 - 290, screen_height // 2 - 160, 180, 150),
        pygame.Rect(screen_width // 2 - 90, screen_height // 2 - 160, 180, 150),
        pygame.Rect(screen_width // 2 + 110, screen_height // 2 - 160, 180, 150),
        pygame.Rect(screen_width // 2 - 290, screen_height // 2 + 20, 180, 150),
        pygame.Rect(screen_width // 2 - 90, screen_height // 2 + 20, 180, 150),
        pygame.Rect(screen_width // 2 + 110, screen_height // 2 + 20, 180, 150),
    ]
    zombie_count_rect = pygame.Rect(screen_width // 2 - 180, screen_height // 2 - 30, 360, 70)
    option_rects = [
        pygame.Rect(24, 140, 195, 285),
        pygame.Rect(243, 140, 195, 285),
        pygame.Rect(462, 140, 195, 285),
        pygame.Rect(681, 140, 195, 285),
    ]
    difficulty_rects = [
        pygame.Rect(screen_width // 2 - 380, screen_height // 2 - 75, 170, 150),
        pygame.Rect(screen_width // 2 - 190, screen_height // 2 - 75, 170, 150),
        pygame.Rect(screen_width // 2, screen_height // 2 - 75, 170, 150),
        pygame.Rect(screen_width // 2 + 190, screen_height // 2 - 75, 170, 150),
    ]
    info_card_rects = [
        pygame.Rect(30, 138, 200, 150),
        pygame.Rect(245, 138, 200, 150),
        pygame.Rect(460, 138, 200, 150),
        pygame.Rect(675, 138, 200, 150),
    ]
    info_detail_rect = pygame.Rect(30, 310, screen_width - 60, screen_height - 340)
    custom_input_rect = pygame.Rect(screen_width // 2 - 180, screen_height // 2 - 30, 360, 70)
    select_back_rect = pygame.Rect(screen_width - 220, 30, 180, 54)
    result_button_rects = [
        pygame.Rect(arena_left + arena_width // 2 - 220, arena_top + arena_height // 2 + 120, 200, 72),
        pygame.Rect(arena_left + arena_width // 2 + 20, arena_top + arena_height // 2 + 120, 200, 72),
    ]

    def initial_positions(count, current_radius):
        margin = current_radius + 5
        if count == 2:
            return [
                (margin, square_size / 2),
                (square_size - margin, square_size / 2),
            ]
        if count == 3:
            return [
                (margin, square_size / 2),
                (square_size / 2, margin),
                (square_size - margin, square_size / 2),
            ]
        if count == 4:
            return [
                (margin, margin),
                (square_size - margin, margin),
                (margin, square_size - margin),
                (square_size - margin, square_size - margin),
            ]
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)
        usable_w = max(1.0, square_size - margin * 2)
        usable_h = max(1.0, square_size - margin * 2)
        x_step = usable_w / max(1, cols - 1) if cols > 1 else 0
        y_step = usable_h / max(1, rows - 1) if rows > 1 else 0
        positions = []
        for idx in range(count):
            row = idx // cols
            col = idx % cols
            x = margin + col * x_step
            y = margin + row * y_step
            positions.append((x, y))
        return positions

    def initial_positions_zombie(count, current_radius, w, h):
        margin = current_radius + 5
        if count == 1:
            return [(w / 2, h - margin)]
        return [(margin, h - margin), (w - margin, h - margin)]

    available_colors = [
        (255, 0, 0),
        (255, 255, 0),
        (0, 200, 255),
        (255, 100, 255),
    ]
    bot_health_multipliers = {
        "easy": 0.8,
        "medium": 1.0,
        "hard": 2.0,
        "impossible": 4.0,
    }

    def get_match_radius():
        if game_mode != "custom":
            return radius
        shrink_steps = max(0, player_count - 1) // 10
        return max(8, int(radius / (1.5 ** shrink_steps)))

    def build_match_assets(match_radius):
        match_mika_image = scale_to_fit(mika_original, match_radius * 2, match_radius * 2)
        match_vu_image = scale_to_fit(vu_original, int(match_radius * 2 * 1.4), match_radius * 2)
        match_vu_ultimate_image = scale_to_fit(vu_ultimate_original, int(match_radius * 2 * 1.4 * 1.2), int(match_radius * 2 * 1.2))
        match_gojo_image = scale_to_fit(gojo_original, match_radius * 2, match_radius * 2)
        match_gojo_red_projectile_image = scale_to_fit(
            gojo_red_original,
            max(20, int(radius * 1.1 * (match_radius / radius))),
            max(20, int(radius * 1.1 * (match_radius / radius))),
        )
        match_gojo_blue_projectile_image = scale_to_fit(
            gojo_blue_original,
            max(16, int((radius * 1.1 * (match_radius / radius)) / 1.3)),
            max(16, int((radius * 1.1 * (match_radius / radius)) / 1.3)),
        )
        match_gojo_blue_merge_image = scale_to_fit(
            gojo_blue_original,
            max(20, int(radius * 1.1 * (match_radius / radius))),
            max(20, int(radius * 1.1 * (match_radius / radius))),
        )
        match_do_mixi_win_loser_image = scale_to_fit(do_mixi_win_loser_original, int(match_radius * 2 * 1.4), match_radius * 2)
        match_mambo_image = scale_to_fit(mambo_original, int(match_radius * 2 * 1.4), match_radius * 2)
        match_giorno_mambo_image = scale_to_fit(giorno_mambo_original, int(match_radius * 2 * 1.4), match_radius * 2)
        match_mika_gun_image = scale_to_fit(mika_ue_original, int(match_radius * 2.2), match_radius * 2)
        match_mika_meteor_image = scale_to_fit(mika_meteor_original, match_radius, match_radius)
        match_mika_finish_meteor_image = scale_to_fit(mika_meteor_original, match_radius * 4, match_radius * 4)
        match_mika_bullet_image = scale_to_fit(mika_bullet_original, max(20, int(56 * (match_radius / radius))), max(20, int(56 * (match_radius / radius))))
        match_mika_bullet_ultimate_image = scale_to_fit(mika_bullet_original, max(20, int(56 * (match_radius / radius))), max(20, int(56 * (match_radius / radius))))
        match_vu_projectile_image = scale_to_fit(vu_projectile_original, max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))), max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))))
        match_vu_ultimate_projectile_image = scale_to_fit(vu_ultimate_projectile_original, max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))), max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))))
        match_faker_normal_attack_image = scale_to_fit(faker_normal_attack_original, max(18, int(radius * 1.2 * (match_radius / radius))), max(18, int(radius * 1.2 * (match_radius / radius))))
        match_faker_call_image = scale_to_fit(faker_call_original, max(18, int(radius * 1.15 * (match_radius / radius))), max(18, int(radius * 1.15 * (match_radius / radius))))
        if match_mika_image:
            base_w, base_h = match_mika_image.get_size()
        else:
            base_w, base_h = match_radius * 2, match_radius * 2
        match_mika_ultimate_xd_image = scale_to_fit(
            mika_ultimate_xd_original,
            max(1, int(base_w * 2 / 1.5 * 1.3)),
            max(1, int(base_h * 2 / 1.5 * 1.3)),
        )
        match_mika_body_image = None
        match_mika_halo_image = None
        if match_mika_ultimate_xd_image:
            uw, uh = match_mika_ultimate_xd_image.get_size()
            halo_h = max(1, int(uh * 0.18))
            match_mika_body_image = match_mika_ultimate_xd_image.copy()
            pygame.draw.rect(match_mika_body_image, (0, 0, 0, 0), pygame.Rect(0, 0, uw, halo_h + 2))
            match_mika_halo_image = pygame.Surface((uw, halo_h), pygame.SRCALPHA)
            match_mika_halo_image.blit(match_mika_ultimate_xd_image, (0, 0), pygame.Rect(0, 0, uw, halo_h))
        return {
            "radius": match_radius,
            "mika_image": match_mika_image,
            "vu_image": match_vu_image,
            "vu_ultimate_image": match_vu_ultimate_image,
            "gojo_image": match_gojo_image,
            "faker_image": scale_to_fit(faker_original, max(1, int(radius * 2.2 * 1.3 * (match_radius / radius))), max(1, int(radius * 2.2 * 1.3 * (match_radius / radius)))),
            "gojo_red_projectile_image": match_gojo_red_projectile_image,
            "gojo_blue_projectile_image": match_gojo_blue_projectile_image,
            "gojo_blue_merge_image": match_gojo_blue_merge_image,
            "gojo_hollow_purple_image": scale_to_fit(gojo_purple_original, max(16, int((radius * 1.1 * (match_radius / radius)) / 1.3)), max(16, int((radius * 1.1 * (match_radius / radius)) / 1.3))),
            "do_mixi_win_loser_image": match_do_mixi_win_loser_image,
            "mambo_image": match_mambo_image,
            "giorno_mambo_image": match_giorno_mambo_image,
            "mika_gun_image": match_mika_gun_image,
            "mika_meteor_image": match_mika_meteor_image,
            "mika_finish_meteor_image": match_mika_finish_meteor_image,
            "mika_bullet_image": match_mika_bullet_image,
            "mika_bullet_ultimate_image": match_mika_bullet_ultimate_image,
            "vu_projectile_image": match_vu_projectile_image,
            "vu_ultimate_projectile_image": match_vu_ultimate_projectile_image,
            "faker_normal_attack_image": match_faker_normal_attack_image,
            "faker_call_image": match_faker_call_image,
            "mika_body_image": match_mika_body_image,
            "mika_halo_image": match_mika_halo_image,
        }

    match_assets = build_match_assets(radius)

    def get_character_label(character_id):
        if character_id == "Mika":
            return "Misono Mika"
        if character_id == "Gojo":
            return "Gojo Satoru"
        if character_id == "Faker":
            return "T1 Faker"
        return "Do Mixi"

    def build_display_names(character_ids):
        totals = {}
        for character_id in character_ids:
            label = get_character_label(character_id)
            totals[label] = totals.get(label, 0) + 1

        counts = {}
        names = []
        for character_id in character_ids:
            label = get_character_label(character_id)
            counts[label] = counts.get(label, 0) + 1
            if totals[label] > 1:
                names.append(f"{label} {counts[label]}")
            else:
                names.append(label)
        return names

    character_info_selected = "Mika"
    character_info_entries = {
        "Mika": {
            "title": "Misono Mika",
            "subtitle": "Crit-heavy burst carry",
            "overview": [
                "Normal Attack: Fires a 5-shot burst every 1.5s.",
                "Each bullet deals 4 damage, always crits, and heals Mika for 2 HP.",
                "Meteor Volley: Every burst also calls 4 meteors for 6 damage each.",
                "Meteors always crit, so each one lands for 12 damage.",
                "Ultimate - Heavenly Meteor: 6s cooldown.",
                "Mika enters a powered-up firing state and ends with a giant meteor.",
                "Final meteor deals 200 damage and always crits for 400.",
            ],
        },
        "Gojo": {
            "title": "Gojo Satoru",
            "subtitle": "Control mage with chained finishers",
            "overview": [
                "Technique Cycle: Fires every 2.5s, alternating Blue and Red.",
                "Lapse Blue: 50 damage on release and 30 damage per second in the field.",
                "Blue starts pulling 0.6s after release and uses a huge pull radius.",
                "Reversal Red: 100 damage with a heavy outward shockwave push.",
                "Hollow Purple: Unleashes after every 2 Blue or Red casts.",
                "Purple deals 300 on contact, 200 on wall explosion, and heals Gojo",
                "for 10% max HP when it connects.",
                "Ultimate - Domain Expansion: 15s cooldown and only unlocks after",
                "5s of battle time. Infinite Void opens a 4s domain state.",
            ],
        },
        "Vu": {
            "title": "Do Mixi",
            "subtitle": "Straight-line pressure and barrage zoning",
            "overview": [
                "Normal Skill - Ba Mia: Fires every 1.0s.",
                "Each projectile deals 36 skill damage in a direct line.",
                "Ultimate - Ba Mia Real: 7s cooldown with a 6s active window.",
                "Do Mixi launches a 6-projectile spread instead of a single shot.",
                "Each ultimate projectile deals 36 damage and has a 36% crit chance",
                "to spike to 72 damage.",
                "Ultimate shots keep bouncing while the form is active, making the",
                "arena much harder to cross safely.",
            ],
        },
        "Faker": {
            "title": "T1 Faker",
            "subtitle": "Mobile control fighter with clutch windows",
            "overview": [
                "Normal Attack: Throws Faker Call every 1.0s for 18 damage.",
                "Normal attacks have 15% crit chance for 30 damage.",
                "Skill Q - Emperor's Divide: 10s cooldown.",
                "Faker dashes through the target line, builds a soldier wall, and",
                "the wall slams enemies for 100 damage while blocking them for 4s.",
                "Faker cannot take damage while unleashing Q and can walk through it.",
                "Skill E - Spirit Rush Combo: 8s cooldown.",
                "A short dash launches an auto-aim charm, then 3 blue orbs follow up.",
                "Charm lasts 2s and burns for 60 damage per second.",
                "Each orb deals 80 damage and explodes for half splash damage.",
                "Ultimate R - Unkillable Demon King: 12s cooldown, 6s duration,",
                "and only unlocks after 5s of battle time.",
                "While active, Faker gains 1.5x move speed, bonus damage, damage",
                "reduction, 50% faster Q/E cooldown recovery, and one 1 HP last stand.",
            ],
        },
    }

    def load_zombie_progress():
        if not os.path.exists(zombie_save_path):
            return None
        try:
            with open(zombie_save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("game_mode") != "zombie":
                return None
            if not isinstance(data.get("selected_players"), list) or not data["selected_players"]:
                return None
            return data
        except (OSError, ValueError, TypeError):
            return None

    def delete_zombie_progress():
        try:
            if os.path.exists(zombie_save_path):
                os.remove(zombie_save_path)
        except OSError:
            pass

    def save_zombie_progress():
        if game_mode != "zombie" or not circles:
            return False
        player_circles = [c for c in circles if is_player_controlled_human(c)]
        if not player_circles:
            return False
        player_circles.sort(key=lambda c: 0 if c.controller == "player1" else 1)
        data = {
            "game_mode": "zombie",
            "player_count": player_count,
            "selected_players": list(selected_players),
            "current_wave": current_wave,
            "players": [
                {
                    "controller": circle.controller,
                    "character_type": circle.character_type,
                    "max_health": circle.max_health,
                    "health": circle.health,
                    "skill_damage_bonus": getattr(circle, "skill_damage_bonus", 0),
                    "normal_attack_damage_bonus": getattr(circle, "normal_attack_damage_bonus", 0),
                }
                for circle in player_circles
            ],
        }
        try:
            with open(zombie_save_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return True
        except OSError:
            return False

    def start_match():
        nonlocal menu_state, circles, bullets, meteors, damage_texts, red_explosions, purple_trails, faker_waves, faker_dust_trails, faker_magic_flames, screen_shake_timer, screen_shake_strength, faker_ultimate_hitstop_timer, elapsed_time, battle_time, result_winner_name, result_show_options, result_special_click_needed, square_size, arena_left, arena_top, arena_width, arena_height, result_button_rects, match_assets, tube_top_height, zombie_spawn_timer, current_wave, mambos_spawned_in_wave, mambos_to_spawn, wave_in_progress, wave_complete, zombie_music_mode, pending_zombie_resume_data
        menu_state = "play"
        if game_mode == "zombie":
            tube_top_height = 80
            square_size = int(min(base_square_size * 2.0, screen_width - arena_margin * 2))
            max_arena_h = max(400, screen_height - tube_top_height - ui_panel_height - arena_margin * 2)
            arena_height = min(square_size * 1.5, max_arena_h)
            arena_width = square_size
            arena_left = (window_width - arena_width) // 2
            arena_top = tube_top_height
            if pending_zombie_resume_data is not None:
                current_wave = max(1, int(pending_zombie_resume_data.get("current_wave", 1)))
                zombie_spawn_timer = 0.0
                mambos_spawned_in_wave = 0
                mambos_to_spawn = current_wave
            else:
                zombie_spawn_timer = 9999.0
                current_wave = 1
                mambos_spawned_in_wave = 1
                mambos_to_spawn = 1
            wave_in_progress = True
            wave_complete = False
            
            ensure_zombie_wave_music("normal")
        else:
            tube_top_height = 0
            square_size = min(base_square_size * 1.2, screen_width - arena_margin * 2) if game_mode == "sim" else base_square_size
            square_size = int(square_size)
            arena_width = square_size
            arena_height = square_size
            arena_left = (window_width - square_size) // 2
            arena_top = arena_margin
            zombie_spawn_timer = 0.0
        match_assets = build_match_assets(get_match_radius())
        result_button_rects = [
            pygame.Rect(arena_left + arena_width // 2 - 220, arena_top + arena_height // 2 + 120, 200, 72),
            pygame.Rect(arena_left + arena_width // 2 + 20, arena_top + arena_height // 2 + 120, 200, 72),
        ]
        circles = []
        bullets = []
        meteors = []
        damage_texts = []
        red_explosions = []
        purple_trails = []
        faker_waves = []
        faker_dust_trails = []
        faker_magic_flames = []
        screen_shake_timer = 0.0
        screen_shake_strength = 0.0
        faker_ultimate_hitstop_timer = 0.0
        colliding_pairs.clear()
        elapsed_time = 0.0
        battle_time = 0.0
        result_winner_name = ""
        result_show_options = False
        result_special_click_needed = False

    def reset_to_home():
        nonlocal menu_state, game_mode, bot_difficulty, custom_count_input, zombie_count_input, player_count, selected_players, circles, bullets, meteors, damage_texts, red_explosions, purple_trails, faker_waves, faker_dust_trails, faker_magic_flames, screen_shake_timer, screen_shake_strength, faker_ultimate_hitstop_timer, elapsed_time, battle_time, result_winner_name, result_show_options, result_special_click_needed, square_size, arena_left, arena_top, arena_width, arena_height, result_button_rects, match_assets, tube_top_height, zombie_spawn_timer, zombie_music_mode
        if game_mode == "zombie":
            stop_all_audio()
        menu_state = "mode"
        game_mode = "sim"
        bot_difficulty = "medium"
        custom_count_input = ""
        zombie_count_input = ""
        square_size = base_square_size
        arena_width = base_square_size
        arena_height = base_square_size
        arena_left = (window_width - square_size) // 2
        arena_top = arena_margin
        tube_top_height = 0
        zombie_spawn_timer = 0.0
        zombie_music_mode = None
        match_assets = build_match_assets(radius)
        result_button_rects = [
            pygame.Rect(arena_left + arena_width // 2 - 220, arena_top + arena_height // 2 + 120, 200, 72),
            pygame.Rect(arena_left + arena_width // 2 + 20, arena_top + arena_height // 2 + 120, 200, 72),
        ]
        player_count = 0
        selected_players = []
        circles = []
        bullets = []
        meteors = []
        damage_texts = []
        red_explosions = []
        purple_trails = []
        faker_waves = []
        faker_dust_trails = []
        faker_magic_flames = []
        screen_shake_timer = 0.0
        screen_shake_strength = 0.0
        faker_ultimate_hitstop_timer = 0.0
        colliding_pairs.clear()
        elapsed_time = 0.0
        battle_time = 0.0
        result_winner_name = ""
        result_show_options = False
        result_special_click_needed = False

    def show_result_screen():
        nonlocal menu_state, result_winner_name, result_show_options, result_special_click_needed
        if game_mode == "zombie":
            stop_all_audio()
        alive = [c for c in circles if c.health > 0 and c.character_type not in ("Zombie", "Green Mob", "Giorno Mambo")]
        winner_circle = alive[0] if alive else None
        if game_mode == "zombie" and not alive:
            result_winner_name = "GAME OVER"
        else:
            result_winner_name = winner_circle.name if winner_circle else "No one"
        menu_state = "result"
        result_special_click_needed = bool(winner_circle) and winner_circle.character_type == "Do Mixi"
        result_show_options = not result_special_click_needed
        if result_special_click_needed:
            for circle in circles:
                if circle.health <= 0:
                    circle.image = match_assets["do_mixi_win_loser_image"]
                    circle.ultimate_active = False
            if do_mixi_win_sound:
                play_voice_sound(do_mixi_win_sound, preferred="secondary")
        elif winner_circle and winner_circle.character_type == "Gojo Satoru" and gojo_win_sound:
            play_voice_sound(gojo_win_sound, preferred="secondary")

    def activate_ultimate(circle):
        if circle.character_type == "Gojo Satoru":
            activate_gojo_domain(circle)
            return
        if circle.character_type == "T1 Faker":
            activate_faker_demon_king(circle)
            return
        if circle.health <= 0 or circle.ultimate_active:
            return
        if circle.character_type != "Gojo Satoru" and circle.ultimate_cooldown_timer > 0:
            return
        if circle.character_type == "Misono Mika":
            circle.ultimate_active = True
            circle.ultimate_duration_timer = 5.0
            if mika_ultimate_voice_sounds:
                play_voice_sound(random.choice(mika_ultimate_voice_sounds), preferred="secondary")
        elif circle.character_type == "Do Mixi":
            circle.ultimate_active = True
            circle.ultimate_duration_timer = 6.0
            if vu_ultimate_sound:
                play_voice_sound(vu_ultimate_sound, preferred="secondary")

    def begin_gojo_domain_phase(circle):
        circle.gojo_ultimate_stage = "domain"
        circle.ultimate_duration_timer = 4.0
        circle.gojo_ultimate_timer = 4.0
        circle.gojo_ultimate_hold_timer = 0.0
        circle.gojo_ultimate_charge_duration = 0.0
        circle.gojo_domain_freeze_timer = 4.0
        circle.gojo_void_intro_timer = 0.0
        circle.gojo_sequence_index = 0
        circle.bullet_timer = 0.0
        restart_video_background(infinite_void_video)

    def activate_gojo_domain(circle):
        if circle.health <= 0 or circle.ultimate_active or circle.ultimate_cooldown_timer > 0:
            return
        if battle_time < 10.0:
            return
        circle.ultimate_active = True
        circle.gojo_ultimate_stage = "infinite_void_intro"
        intro_len = gojo_infinite_void_sound.get_length() if gojo_infinite_void_sound else 0.0
        circle.gojo_void_intro_timer = intro_len
        circle.gojo_domain_banner_timer = 1.8
        circle.ultimate_cooldown_timer = 15.0
        if gojo_infinite_void_sound:
            play_voice_sound(gojo_infinite_void_sound, preferred="primary", priority=True)
        if circle.gojo_void_intro_timer <= 0.0:
            begin_gojo_domain_phase(circle)

    def activate_gojo_hollow_purple(circle):
        nonlocal bullets
        if circle.health <= 0 or circle.ultimate_active or circle.gojo_attack_count < 5 or circle.target is None or circle.target.health <= 0:
            return
        owner_index = circles.index(circle) if circle in circles else -1
        bullets = [
            bullet
            for bullet in bullets
            if not (
                bullet.owner_index == owner_index
                and bullet.source in ("gojo_red", "gojo_blue")
            )
        ]
        circle.ultimate_active = True
        circle.gojo_ultimate_stage = "merge"
        circle.gojo_ultimate_charge_duration = 1.1
        circle.gojo_ultimate_timer = circle.gojo_ultimate_charge_duration
        audio_length = gojo_hollow_purple_sound.get_length() if gojo_hollow_purple_sound else 0.0
        circle.gojo_ultimate_hold_timer = max(0.15, audio_length - 2.0) if audio_length > 0 else circle.gojo_ultimate_charge_duration
        circle.gojo_domain_freeze_timer = 0.0
        if gojo_hollow_purple_sound:
            play_voice_sound(gojo_hollow_purple_sound, preferred="primary", priority=True)

    def activate_faker_first_skill(circle):
        nonlocal faker_waves, screen_shake_timer, screen_shake_strength
        if circle.health <= 0 or circle.faker_skill_cooldown_timer > 0 or circle.faker_skill_state is not None:
            return
        target = circle.target if circle.target and circle.target.health > 0 and circles_are_hostile(circle, circle.target) else None
        if target is None:
            opponents = get_hostile_opponents(circle, circles)
            if opponents:
                target = min(opponents, key=lambda other: math.hypot(other.x - circle.x, other.y - circle.y))
                circle.target = target

        if target is not None:
            dx = target.x - circle.x
            dy = target.y - circle.y
            target_radius = target.radius
        elif abs(circle.vx) + abs(circle.vy) > 0:
            dx = circle.vx
            dy = circle.vy
            target_radius = circle.radius
        else:
            dx = 1.0
            dy = 0.0
            target_radius = circle.radius
        distance = math.hypot(dx, dy)
        if distance <= 0:
            return
        dir_x = dx / distance
        dir_y = dy / distance
        push_dir_x = -dir_x
        push_dir_y = -dir_y
        owner_index = circles.index(circle)
        target_index = circles.index(target) if target is not None else -1
        wall_thickness = max(circle.radius * 3.2, 82.0)
        wall_length = max(circle.radius * 10.0, 240.0)
        dash_gap = target_radius + circle.radius + 16.0
        anchor_x = target.x if target is not None else circle.x + dir_x * max(circle.radius * 3.0, 120.0)
        anchor_y = target.y if target is not None else circle.y + dir_y * max(circle.radius * 3.0, 120.0)
        dash_out_x = anchor_x + dir_x * dash_gap
        dash_out_y = anchor_y + dir_y * dash_gap
        desired_enemy_x = circle.x + push_dir_x * (circle.radius + target_radius + 22.0)
        desired_enemy_y = circle.y + push_dir_y * (circle.radius + target_radius + 22.0)
        wall_start_x = anchor_x + dir_x * (target_radius + wall_thickness * 0.75 + 18.0)
        wall_start_y = anchor_y + dir_y * (target_radius + wall_thickness * 0.75 + 18.0)
        wall_end_x = desired_enemy_x - push_dir_x * (wall_thickness * 0.58 + target_radius + 6.0)
        wall_end_y = desired_enemy_y - push_dir_y * (wall_thickness * 0.58 + target_radius + 6.0)
        wall_travel_distance = math.hypot(wall_end_x - wall_start_x, wall_end_y - wall_start_y)
        wall_speed = (300.0 * 3.0) / 1.3
        dash_out_distance = math.hypot(dash_out_x - circle.x, dash_out_y - circle.y)
        dash_back_distance = math.hypot(circle.x - circle.x, circle.y - circle.y)

        circle.faker_skill_state = {
            "phase": "dash_out",
            "owner_index": owner_index,
            "target_index": target_index,
            "origin_x": circle.x,
            "origin_y": circle.y,
            "dash_out_x": dash_out_x,
            "dash_out_y": dash_out_y,
            "push_dir_x": push_dir_x,
            "push_dir_y": push_dir_y,
            "wall_start_x": wall_start_x,
            "wall_start_y": wall_start_y,
            "wall_length": wall_length,
            "wall_thickness": wall_thickness,
            "wall_travel_distance": wall_travel_distance,
            "wall_move_duration": max(0.12, wall_travel_distance / wall_speed),
            "phase_timer": max(0.14, dash_out_distance / wall_speed) + 0.06,
            "dash_back_duration": max(0.14, math.hypot(dash_out_x - circle.x, dash_out_y - circle.y) / wall_speed) + 0.06,
        }
        circle.faker_skill_cooldown_timer = 10.0
        screen_shake_timer = max(screen_shake_timer, 0.35)
        screen_shake_strength = max(screen_shake_strength, 8.0)

    def activate_faker_second_skill(circle):
        nonlocal screen_shake_timer, screen_shake_strength, faker_dust_trails, faker_magic_flames, bullets
        if circle.health <= 0 or circle.ultimate_cooldown_timer > 0 or circle.faker_skill_state is not None:
            return

        target = circle.target if circle.target and circle.target.health > 0 and circles_are_hostile(circle, circle.target) else None
        if target is None:
            opponents = get_hostile_opponents(circle, circles)
            if not opponents:
                return
            target = min(opponents, key=lambda other: math.hypot(other.x - circle.x, other.y - circle.y))
            circle.target = target

        dx = target.x - circle.x
        dy = target.y - circle.y
        distance = math.hypot(dx, dy)
        if distance <= 0:
            return
        dir_x = dx / distance
        dir_y = dy / distance
        dash_distance = min(max(circle.radius * 3.2, 120.0), max(80.0, distance - target.radius - circle.radius - 18.0))
        origin_x = circle.x
        origin_y = circle.y
        end_x = circle.x + dir_x * dash_distance
        end_y = circle.y + dir_y * dash_distance

        circle.x = end_x
        circle.y = end_y
        circle.vx = 0.0
        circle.vy = 0.0
        circle.impulse_vx = 0.0
        circle.impulse_vy = 0.0
        circle.impulse_wall_bounces_remaining = 0
        add_faker_dust_trail(faker_dust_trails, origin_x, origin_y, max(circle.radius * 0.6, 16.0))
        add_faker_dust_trail(faker_dust_trails, end_x, end_y, max(circle.radius * 0.75, 18.0))
        add_faker_magic_flame(faker_magic_flames, origin_x, origin_y, max(circle.radius * 0.75, 18.0), (120, 220, 255))
        add_faker_magic_flame(faker_magic_flames, end_x, end_y, max(circle.radius * 0.9, 22.0), (255, 120, 220))
        add_faker_magic_flame(faker_magic_flames, end_x, end_y, max(circle.radius * 1.35, 34.0), (135, 205, 255))
        screen_shake_timer = max(screen_shake_timer, 0.11)
        screen_shake_strength = max(screen_shake_strength, 6.2)

        charm_speed = 660.0
        charm_bullet = Bullet(
            end_x,
            end_y,
            dir_x * charm_speed,
            dir_y * charm_speed,
            circles.index(circle),
            color=(255, 135, 215),
            size=max(10, int(13 * (match_assets["radius"] / radius))),
            source="faker_charm",
            damage=0,
            attack_type="skill",
        )
        charm_bullet.target_index = circles.index(target)
        charm_bullet.turn_rate = 9.0
        bullets.append(charm_bullet)
        circle.ultimate_cooldown_timer = 8.0

    def activate_faker_demon_king(circle):
        nonlocal screen_shake_timer, screen_shake_strength, faker_ultimate_hitstop_timer
        if circle.health <= 0 or circle.ultimate_active or circle.faker_ultimate_cooldown_timer > 0:
            return
        if battle_time < 5.0:
            return
        circle.ultimate_active = True
        circle.ultimate_duration_timer = 6.0
        circle.faker_ultimate_cooldown_timer = 12.0
        circle.faker_last_stand_used = False
        circle.faker_invulnerable_timer = 0.0
        circle.faker_ultimate_banner_timer = 1.6
        faker_ultimate_hitstop_timer = max(faker_ultimate_hitstop_timer, 0.2)
        add_faker_magic_flame(faker_magic_flames, circle.x, circle.y, max(circle.radius * 1.4, 34.0), (255, 70, 120))
        add_faker_magic_flame(faker_magic_flames, circle.x, circle.y, max(circle.radius * 2.0, 48.0), (175, 90, 255))
        screen_shake_timer = max(screen_shake_timer, 0.24)
        screen_shake_strength = max(screen_shake_strength, 11.0)

    def get_controlled_velocity(keys, up_key, left_key, down_key, right_key, speed=280.0):
        move_x = float(keys[right_key]) - float(keys[left_key])
        move_y = float(keys[down_key]) - float(keys[up_key])
        if move_x == 0.0 and move_y == 0.0:
            return 0.0, 0.0
        length = math.hypot(move_x, move_y)
        return (move_x / length) * speed, (move_y / length) * speed

    while running:
        real_dt = clock.tick(60) / 1000.0
        sim_dt = real_dt
        if menu_state == "play":
            if faker_ultimate_hitstop_timer > 0:
                faker_ultimate_hitstop_timer = max(0.0, faker_ultimate_hitstop_timer - real_dt)
                sim_dt *= 0.18
            for c in circles:
                if (
                    c.character_type == "Gojo Satoru"
                    and c.ultimate_active
                    and c.gojo_ultimate_stage == "infinite_void_intro"
                ):
                    c.gojo_void_intro_timer = max(0.0, c.gojo_void_intro_timer - real_dt)
                    if c.gojo_void_intro_timer <= 0:
                        begin_gojo_domain_phase(c)
            gojo_voice_intro_active = any(
                c.character_type == "Gojo Satoru"
                and c.ultimate_active
                and c.gojo_ultimate_stage == "infinite_void_intro"
                for c in circles
            )
            if gojo_voice_intro_active:
                sim_dt = 0.0
        else:
            gojo_voice_intro_active = False
        elapsed_time += sim_dt if menu_state == "play" else real_dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu_state == "play" and game_mode == "zombie":
                        menu_state = "pause"
                    elif menu_state == "pause":
                        menu_state = "play"
                    else:
                        running = False
                elif menu_state == "custom_count":
                    if event.key == pygame.K_RETURN:
                        if custom_count_input.isdigit() and int(custom_count_input) > 0:
                            player_count = int(custom_count_input)
                            selected_players = []
                            menu_state = "select"
                    elif event.key == pygame.K_BACKSPACE:
                        custom_count_input = custom_count_input[:-1]
                    elif event.unicode.isdigit() and len(custom_count_input) < 3:
                        custom_count_input += event.unicode
                elif menu_state == "zombie_count":
                    if event.key == pygame.K_RETURN:
                        if zombie_count_input in ("1", "2"):
                            player_count = int(zombie_count_input)
                            selected_players = []
                            menu_state = "select"
                    elif event.key == pygame.K_BACKSPACE:
                        zombie_count_input = ""
                    elif event.unicode in ("1", "2"):
                        zombie_count_input = event.unicode
                elif menu_state == "play":
                    if not gojo_voice_intro_active:
                        for circle in circles:
                            if circle.controller == "player1" and event.key == pygame.K_e and circle.character_type == "T1 Faker":
                                activate_faker_second_skill(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_r and circle.character_type == "T1 Faker":
                                activate_ultimate(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_e:
                                activate_ultimate(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_q and circle.character_type == "T1 Faker":
                                activate_faker_first_skill(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_o and circle.character_type == "T1 Faker":
                                activate_faker_second_skill(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_p and circle.character_type == "T1 Faker":
                                activate_ultimate(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_o:
                                activate_ultimate(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_u and circle.character_type == "T1 Faker":
                                activate_faker_first_skill(circle)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if menu_state == "mode":
                    if mode_rects[0].collidepoint(mx, my):
                        game_mode = "sim"
                        player_count = 2
                        selected_players = []
                        menu_state = "select"
                    elif mode_rects[1].collidepoint(mx, my):
                        game_mode = "bot"
                        player_count = 2
                        selected_players = []
                        menu_state = "bot_difficulty"
                    elif mode_rects[2].collidepoint(mx, my):
                        game_mode = "pvp"
                        player_count = 2
                        selected_players = []
                        menu_state = "select"
                    elif mode_rects[3].collidepoint(mx, my):
                        game_mode = "custom"
                        player_count = 0
                        custom_count_input = ""
                        selected_players = []
                        menu_state = "custom_count"
                    elif mode_rects[4].collidepoint(mx, my):
                        saved_run = load_zombie_progress()
                        if saved_run is not None:
                            game_mode = "zombie"
                            player_count = int(saved_run.get("player_count", len(saved_run.get("selected_players", [])) or 1))
                            selected_players = list(saved_run.get("selected_players", []))
                            pending_zombie_resume_data = saved_run
                            start_match()
                        else:
                            game_mode = "zombie"
                            player_count = 0
                            zombie_count_input = ""
                            selected_players = []
                            menu_state = "zombie_count"
                    elif mode_rects[5].collidepoint(mx, my):
                        character_info_selected = "Mika"
                        menu_state = "character_info"
                elif menu_state == "bot_difficulty":
                    difficulty_names = ["easy", "medium", "hard", "impossible"]
                    for idx, rect in enumerate(difficulty_rects):
                        if rect.collidepoint(mx, my):
                            bot_difficulty = difficulty_names[idx]
                            selected_players = []
                            menu_state = "select"
                            break
                elif menu_state == "character_info":
                    if select_back_rect.collidepoint(mx, my):
                        menu_state = "mode"
                    elif info_card_rects[0].collidepoint(mx, my):
                        character_info_selected = "Mika"
                    elif info_card_rects[1].collidepoint(mx, my):
                        character_info_selected = "Gojo"
                    elif info_card_rects[2].collidepoint(mx, my):
                        character_info_selected = "Vu"
                    elif info_card_rects[3].collidepoint(mx, my):
                        character_info_selected = "Faker"
                elif menu_state == "select":
                    if select_back_rect.collidepoint(mx, my):
                        if game_mode == "bot":
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                menu_state = "bot_difficulty"
                        elif game_mode == "custom":
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                menu_state = "custom_count"
                        elif game_mode == "pvp":
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                menu_state = "mode"
                        elif game_mode == "zombie":
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                menu_state = "zombie_count"
                        else:
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                menu_state = "mode"
                    elif option_rects[0].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Mika")
                    elif option_rects[1].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Gojo")
                    elif option_rects[2].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Vu")
                    elif option_rects[3].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Faker")

                    if len(selected_players) == player_count:
                        start_match()
                elif menu_state == "result":
                    if result_special_click_needed:
                        result_special_click_needed = False
                        result_show_options = True
                    elif result_show_options:
                        if result_button_rects[0].collidepoint(mx, my):
                            reset_to_home()
                        elif result_button_rects[1].collidepoint(mx, my):
                            start_match()
                elif menu_state == "pause":
                    pause_rect = pygame.Rect(arena_left + arena_width // 2 - 180, arena_top + arena_height // 2 - 120, 360, 240)
                    pause_buttons = [
                        pygame.Rect(pause_rect.x + 40, pause_rect.y + 60, pause_rect.width - 80, 42),
                        pygame.Rect(pause_rect.x + 40, pause_rect.y + 112, pause_rect.width - 80, 42),
                        pygame.Rect(pause_rect.x + 40, pause_rect.y + 164, pause_rect.width - 80, 42),
                    ]
                    if pause_buttons[0].collidepoint(mx, my):
                        menu_state = "play"
                    elif pause_buttons[1].collidepoint(mx, my):
                        if save_zombie_progress():
                            reset_to_home()
                    elif pause_buttons[2].collidepoint(mx, my):
                        delete_zombie_progress()
                        reset_to_home()
        screen.fill((15, 18, 28))

        if menu_state == "mode":
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(screen, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(screen, "Battle Mode", title_rect.x + 20, title_rect.y + 20, size=44)
            draw_text(screen, "Choose how you want to play.", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            pygame.draw.rect(screen, (50, 55, 80), mode_rects[0], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), mode_rects[0], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), mode_rects[1], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), mode_rects[1], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), mode_rects[2], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), mode_rects[2], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), mode_rects[3], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), mode_rects[3], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), mode_rects[4], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), mode_rects[4], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), mode_rects[5], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), mode_rects[5], 3, border_radius=18)

            draw_text(screen, "2 Characters", mode_rects[0].x + 10, mode_rects[0].y + 20, size=30)
            draw_text(screen, "Simulation", mode_rects[0].x + 22, mode_rects[0].y + 60, size=30)
            draw_text(screen, "Vs Bot", mode_rects[1].x + 40, mode_rects[1].y + 45, size=34)
            draw_text(screen, "Vs Player", mode_rects[2].x + 18, mode_rects[2].y + 45, size=34)
            draw_text(screen, "Custom", mode_rects[3].x + 36, mode_rects[3].y + 28, size=32)
            draw_text(screen, "Simulation", mode_rects[3].x + 18, mode_rects[3].y + 68, size=28)
            draw_text(screen, "Mambo", mode_rects[4].x + 32, mode_rects[4].y + 18, size=26)
            draw_text(screen, "Apocalypse", mode_rects[4].x + 16, mode_rects[4].y + 54, size=24)
            draw_text(screen, "Characters", mode_rects[5].x + 12, mode_rects[5].y + 28, size=28)
            draw_text(screen, "Info", mode_rects[5].x + 56, mode_rects[5].y + 72, (220, 220, 255), size=28)
        elif menu_state == "character_info":
            header_rect = pygame.Rect(20, 20, screen_width - 40, 90)
            pygame.draw.rect(screen, (40, 45, 70), header_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), header_rect, 3, border_radius=16)
            draw_button(screen, select_back_rect, "Back", fill_color=(160, 110, 70))
            draw_text(screen, "Characters Info", header_rect.x + 20, header_rect.y + 18, size=36)
            draw_text(screen, "Click a character card to read the full kit.", header_rect.x + 20, header_rect.y + 58, (220, 220, 255), size=22)

            info_order = ["Mika", "Gojo", "Vu", "Faker"]
            info_titles = ["Mika", "Gojo", "Do Mixi", "Faker"]
            info_subtitles = ["Misono Mika", "Gojo Satoru", "Vu A Vu", "T1 Faker"]
            info_previews = [mika_original, gojo_original, vu_original, faker_original]
            info_sizes = [(100, 100), (100, 100), (140, 100), (125, 125)]
            info_centers = [250, 250, 248, 252]
            for idx, rect in enumerate(info_card_rects):
                is_selected = character_info_selected == info_order[idx]
                border_color = (255, 230, 150) if is_selected else (120, 160, 230)
                fill_color = (66, 72, 104) if is_selected else (50, 55, 80)
                pygame.draw.rect(screen, fill_color, rect, border_radius=18)
                pygame.draw.rect(screen, border_color, rect, 3, border_radius=18)
                draw_text(screen, info_titles[idx], rect.x + 16, rect.y + 14, size=28)
                draw_text(screen, info_subtitles[idx], rect.x + 16, rect.y + 50, (220, 220, 255), size=19)
                preview_source = info_previews[idx]
                if preview_source:
                    preview = pygame.transform.smoothscale(preview_source, info_sizes[idx])
                    screen.blit(preview, preview.get_rect(center=(rect.centerx, rect.y + info_centers[idx] - rect.y)))

            pygame.draw.rect(screen, (40, 45, 70), info_detail_rect, border_radius=20)
            pygame.draw.rect(screen, (120, 160, 230), info_detail_rect, 3, border_radius=20)
            entry = character_info_entries.get(character_info_selected, character_info_entries["Mika"])
            draw_text(screen, entry["title"], info_detail_rect.x + 24, info_detail_rect.y + 20, size=36)
            draw_text(screen, entry["subtitle"], info_detail_rect.x + 24, info_detail_rect.y + 62, (220, 220, 255), size=22)
            draw_text_lines(screen, entry["overview"], info_detail_rect.x + 24, info_detail_rect.y + 110, size=20, line_gap=7)
        elif menu_state == "zombie_count":
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(screen, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(screen, "Mambo Apocalypse", title_rect.x + 20, title_rect.y + 20, size=40)
            draw_text(screen, "How many players? (1-2 players)", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            pygame.draw.rect(screen, (50, 55, 80), zombie_count_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), zombie_count_rect, 3, border_radius=16)
            zc_text = zombie_count_input if zombie_count_input else "Type 1 or 2 and press Enter"
            zc_color = (255, 255, 255) if zombie_count_input else (180, 180, 200)
            draw_text(screen, zc_text, zombie_count_rect.x + 18, zombie_count_rect.y + 20, color=zc_color, size=28)
        elif menu_state == "bot_difficulty":
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(screen, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(screen, "Bot Difficulty", title_rect.x + 20, title_rect.y + 20, size=44)
            draw_text(screen, "Choose the bot HP strength.", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            difficulty_labels = ["Easy", "Medium", "Hard", "Impossible"]
            difficulty_hps = ["0.8x HP", "1.0x HP", "2.0x HP", "4.0x HP"]
            for idx, rect in enumerate(difficulty_rects):
                pygame.draw.rect(screen, (50, 55, 80), rect, border_radius=18)
                pygame.draw.rect(screen, (120, 160, 230), rect, 3, border_radius=18)
                draw_text(screen, difficulty_labels[idx], rect.x + 22, rect.y + 28, size=30)
                draw_text(screen, difficulty_hps[idx], rect.x + 32, rect.y + 82, (220, 220, 255), size=22)
        elif menu_state == "custom_count":
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(screen, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(screen, "Custom Character Simulation", title_rect.x + 20, title_rect.y + 20, size=40)
            draw_text(screen, "How many characters?", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            pygame.draw.rect(screen, (50, 55, 80), custom_input_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), custom_input_rect, 3, border_radius=16)
            input_text = custom_count_input if custom_count_input else "Type a number and press Enter"
            input_color = (255, 255, 255) if custom_count_input else (180, 180, 200)
            draw_text(screen, input_text, custom_input_rect.x + 18, custom_input_rect.y + 20, color=input_color, size=28)
            draw_text(screen, "Every 10 extra characters shrinks the ball size by 1.5x.", custom_input_rect.x - 10, custom_input_rect.bottom + 24, (220, 220, 255), size=20)
        elif menu_state == "select":
            display_names = build_display_names(selected_players)
            header_rect = pygame.Rect(20, 20, screen_width - 40, 90)
            pygame.draw.rect(screen, (40, 45, 70), header_rect, border_radius=16)
            pygame.draw.rect(screen, (120, 160, 230), header_rect, 3, border_radius=16)
            draw_button(screen, select_back_rect, "Back", fill_color=(160, 110, 70))
            draw_text(screen, "Choose Your Fighters", header_rect.x + 20, header_rect.y + 18, size=36)
            if game_mode == "bot" and len(selected_players) == 0:
                choose_prompt = "Choose Player"
            elif game_mode == "bot":
                choose_prompt = "Choose Bot"
            elif game_mode == "custom":
                choose_prompt = f"Choose character {len(selected_players) + 1} of {player_count}"
            else:
                choose_prompt = f"Player {len(selected_players) + 1}: choose your character."
            draw_text(screen, choose_prompt, header_rect.x + 20, header_rect.y + 52, (200, 200, 220), size=22)

            for idx, player_name in enumerate(display_names):
                draw_text(
                    screen,
                    f"{idx + 1}. {player_name}",
                    20,
                    header_rect.bottom + 12 + idx * 24,
                    (220, 220, 220),
                    size=20,
                )

            pygame.draw.rect(screen, (50, 55, 80), option_rects[0], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), option_rects[0], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), option_rects[1], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), option_rects[1], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), option_rects[2], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), option_rects[2], 3, border_radius=18)
            pygame.draw.rect(screen, (50, 55, 80), option_rects[3], border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), option_rects[3], 3, border_radius=18)

            draw_text(screen, "Mika", option_rects[0].x + 20, option_rects[0].y + 18, size=28)
            draw_text(screen, "Gojo", option_rects[1].x + 20, option_rects[1].y + 18, size=28)
            draw_text(screen, "Do Mixi", option_rects[2].x + 20, option_rects[2].y + 18, size=28)
            draw_text(screen, "Faker", option_rects[3].x + 20, option_rects[3].y + 18, size=28)
            draw_text(screen, "Misono Mika", option_rects[0].x + 20, option_rects[0].y + 52, (220, 220, 255), size=20)
            draw_text(screen, "Gojo Satoru", option_rects[1].x + 20, option_rects[1].y + 52, (220, 220, 255), size=20)
            draw_text(screen, "Vu A Vu", option_rects[2].x + 20, option_rects[2].y + 52, (220, 220, 255), size=20)
            draw_text(screen, "T1 Faker", option_rects[3].x + 20, option_rects[3].y + 52, (220, 220, 255), size=20)

            if mika_original:
                preview = pygame.transform.smoothscale(mika_original, (180, 180))
                rect = preview.get_rect(center=(option_rects[0].centerx, option_rects[0].y + 208))
                screen.blit(preview, rect)
            if gojo_original:
                preview = pygame.transform.smoothscale(gojo_original, (180, 180))
                rect = preview.get_rect(center=(option_rects[1].centerx, option_rects[1].y + 208))
                screen.blit(preview, rect)
            if vu_original:
                preview = pygame.transform.smoothscale(vu_original, (252, 180))
                rect = preview.get_rect(center=(option_rects[2].centerx, option_rects[2].y + 208))
                screen.blit(preview, rect)
            if faker_original:
                preview = pygame.transform.smoothscale(faker_original, (220, 220))
                rect = preview.get_rect(center=(option_rects[3].centerx, option_rects[3].y + 220))
                screen.blit(preview, rect)
        elif menu_state == "play":
            battle_time += sim_dt
            red_explosions = update_gojo_technique_explosions(red_explosions, sim_dt)
            purple_trails = update_gojo_purple_trails(purple_trails, sim_dt)
            faker_dust_trails = update_faker_dust_trails(faker_dust_trails, sim_dt)
            faker_magic_flames = update_faker_magic_flames(faker_magic_flames, sim_dt)
            added_skill_shake = update_faker_skill_actions(circles, sim_dt, faker_waves, faker_dust_trails)
            if added_skill_shake > 0:
                screen_shake_timer = max(screen_shake_timer, 0.08)
                screen_shake_strength = max(screen_shake_strength, added_skill_shake)
            if screen_shake_timer > 0:
                screen_shake_timer = max(0.0, screen_shake_timer - sim_dt)
                if screen_shake_timer == 0.0:
                    screen_shake_strength = 0.0
            
            wave_damage_bonus = (current_wave - 1) * 20 if game_mode == "zombie" else 0
            
            # Apply damage bonus from killing mambos to players
            for circle in circles:
                if game_mode == "zombie" and circle.character_type not in ("Green Mob", "Giorno Mambo"):
                    wave_damage_bonus += getattr(circle, 'damage_bonus', 0)
                    break
            
            def spawn_mambo():
                rz = max(25, int(match_assets["radius"] * 0.7))
                sx = random.uniform(0.2, 0.8) * arena_width
                sy = rz + 10
                sp = 100.0 * 1.5
                
                z = Circle(
                    sx,
                    sy,
                    random.uniform(-30, 30),
                    120,
                    rz,
                    1000 + (current_wave - 1) * 500,
                    (255, 255, 255),
                    "Green Mob",
                    match_assets.get("mambo_image"),
                    None,
                    character_type="Green Mob",
                )
                z.controller = "zombie"
                z.base_speed = sp
                z.bullet_timer = 9999.0
                z.damage = 20 + (current_wave - 1) * 0.5
                circles.append(z)

            def spawn_giorno_mambo():
                rz = max(35, int(match_assets["radius"] * 0.9))
                sx = random.uniform(0.3, 0.7) * arena_width
                sy = rz + 10
                sp = 80.0 * 1.5
                golden_stage = max(1, current_wave // 5)
                
                z = Circle(
                    sx,
                    sy,
                    random.uniform(-20, 20),
                    100,
                    rz,
                    5000 + (golden_stage - 1) * 2000,
                    (255, 255, 255),
                    "Giorno Mambo",
                    match_assets.get("giorno_mambo_image"),
                    None,
                    character_type="Giorno Mambo",
                )
                z.controller = "zombie"
                z.base_speed = sp
                z.bullet_timer = 9999.0
                z.damage = 500 + (golden_stage - 1) * 2
                circles.append(z)
            
            active_gojo_domain = next(
                (
                    circle
                    for circle in circles
                    if circle.character_type == "Gojo Satoru"
                    and circle.ultimate_active
                    and circle.gojo_ultimate_stage == "domain"
                ),
                None,
            )
            if not circles:
                if game_mode == "zombie":
                    positions = initial_positions_zombie(player_count, match_assets["radius"], arena_width, arena_height)
                else:
                    positions = initial_positions(player_count, match_assets["radius"])
                display_names = build_display_names(selected_players)
                for idx, character in enumerate(selected_players):
                    if character == "Mika":
                        image = match_assets["mika_image"]
                        gun_image = match_assets["mika_gun_image"]
                        name = display_names[idx]
                        character_type = "Misono Mika"
                    elif character == "Gojo":
                        image = match_assets["gojo_image"]
                        gun_image = None
                        name = display_names[idx]
                        character_type = "Gojo Satoru"
                    elif character == "Faker":
                        image = match_assets["faker_image"]
                        gun_image = None
                        name = display_names[idx]
                        character_type = "T1 Faker"
                    else:
                        image = match_assets["vu_image"]
                        gun_image = None
                        name = display_names[idx]
                        character_type = "Do Mixi"

                    color = available_colors[idx % len(available_colors)]
                    x, y = positions[idx]
                    circle = create_circle(name, character_type, x, y, image, gun_image, color, match_assets["radius"])
                    if game_mode == "zombie":
                        circle.controller = "player1" if idx == 0 else "player2"
                        circle.health = 1000 + (current_wave - 1) * 100
                        circle.max_health = circle.health
                        circle.damage_bonus = 0  # Damage bonus from killing mambos
                        circle.skill_damage_bonus = 0
                        circle.normal_attack_damage_bonus = 0
                        if pending_zombie_resume_data is not None:
                            saved_players = pending_zombie_resume_data.get("players", [])
                            if idx < len(saved_players):
                                saved_player = saved_players[idx]
                                circle.max_health = saved_player.get("max_health", circle.max_health)
                                circle.health = min(saved_player.get("health", circle.max_health), circle.max_health)
                                circle.skill_damage_bonus = saved_player.get("skill_damage_bonus", 0)
                                circle.normal_attack_damage_bonus = saved_player.get("normal_attack_damage_bonus", 0)
                    elif game_mode == "bot":
                        circle.controller = "player1" if idx == 0 else "ai"
                    elif game_mode == "pvp":
                        circle.controller = "player1" if idx == 0 else "player2"
                    if game_mode == "bot" and idx == 1:
                        bot_health = int(circle.health * bot_health_multipliers[bot_difficulty])
                        circle.health = bot_health
                        circle.max_health = bot_health
                    if character_type == "Do Mixi":
                        circle.bullet_timer = 1.0
                        circle.ultimate_cooldown_timer = 6.0
                        circle.ultimate_image = match_assets["vu_ultimate_image"]
                    elif character_type == "Gojo Satoru":
                        circle.bullet_timer = 2.5
                        circle.gojo_sequence_index = 0
                        circle.gojo_attack_count = 0
                        circle.gojo_hollow_purple_count = 0
                        circle.ultimate_cooldown_timer = 15.0
                    elif character_type == "T1 Faker":
                        circle.bullet_timer = 1.0
                        circle.ultimate_cooldown_timer = 8.0
                        circle.faker_ultimate_cooldown_timer = 12.0
                    circles.append(circle)
                if game_mode == "zombie":
                    if pending_zombie_resume_data is not None:
                        if current_wave % 5 == 0:
                            giorno_count = current_wave // 5
                            for _ in range(giorno_count):
                                spawn_giorno_mambo()
                            mambos_spawned_in_wave = giorno_count
                        pending_zombie_resume_data = None
                    else:
                        spawn_mambo()
            if game_mode == "zombie" and len(circles) > 0:
                humans = [c for c in circles if c.health > 0 and c.character_type not in ("Green Mob", "Giorno Mambo")]
                
                # Check if wave is complete (all mambos dead)
                mambos = [c for c in circles if c.character_type in ("Green Mob", "Giorno Mambo") and c.health > 0]
                
                if not mambos and wave_in_progress and not wave_complete:
                    # Wave complete, start next wave after delay
                    wave_in_progress = False
                    wave_complete = True
                    zombie_spawn_timer = 3.0  # Delay before next wave
                    for human in humans:
                        human.max_health += 100
                        human.health = human.max_health
                        human.skill_damage_bonus = getattr(human, "skill_damage_bonus", 0) + 30
                        human.normal_attack_damage_bonus = getattr(human, "normal_attack_damage_bonus", 0) + 2
                elif not wave_in_progress and wave_complete:
                    # Start next wave
                    zombie_spawn_timer -= sim_dt
                    if zombie_spawn_timer <= 0:
                        current_wave += 1
                        wave_complete = False
                        wave_in_progress = True
                        
                        # Play appropriate wave music
                        if current_wave % 5 == 0:
                            ensure_zombie_wave_music("golden")
                        else:
                            ensure_zombie_wave_music("normal")
                        
                        # Calculate mambos to spawn (wave number)
                        mambos_to_spawn = current_wave
                        mambos_spawned_in_wave = 0
                        
                        # Check if this is a multiple of 5 for Giorno spawn
                        if current_wave % 5 == 0:
                            giorno_count = current_wave // 5
                            for _ in range(giorno_count):
                                spawn_giorno_mambo()
                            mambos_spawned_in_wave += giorno_count
                
                if wave_in_progress:
                    zombie_spawn_timer -= sim_dt
                    if zombie_spawn_timer <= 0 and mambos_spawned_in_wave < mambos_to_spawn:
                        remaining = mambos_to_spawn - mambos_spawned_in_wave
                        if current_wave % 5 == 0:
                            actual_spawn = remaining
                            for _ in range(actual_spawn):
                                spawn_giorno_mambo()
                        else:
                            # Spawn 2-3 regular mambos at a time on non-golden waves.
                            spawn_count = random.randint(2, 3)
                            actual_spawn = min(spawn_count, remaining)
                            for _ in range(actual_spawn):
                                spawn_mambo()
                        mambos_spawned_in_wave += actual_spawn
                        
                        # Random spawn delay between groups
                        zombie_spawn_timer = 1.0 + random.uniform(0, 1.0)

            for circle in circles:
                if active_gojo_domain is not None and circle is not active_gojo_domain and circle.health > 0:
                    circle.impulse_vx = 0.0
                    circle.impulse_vy = 0.0
                    continue
                if circle.character_type == "Misono Mika":
                    if circle.ultimate_active:
                        circle.ultimate_duration_timer -= sim_dt
                        if circle.ultimate_duration_timer <= 0:
                            circle.ultimate_active = False
                            circle.ultimate_cooldown_timer = 6.0
                            end_opponents = get_hostile_opponents(circle, circles)
                            if end_opponents:
                                if circle.target in end_opponents:
                                    end_target = circle.target
                                else:
                                    end_target = min(end_opponents, key=lambda c: math.hypot(c.x - circle.x, c.y - circle.y))
                                finish_meteor_speed = 260.0
                                finish_aim_unit = get_lead_unit_vector(circle, end_target, finish_meteor_speed)
                                if finish_aim_unit:
                                    fux, fuy = finish_aim_unit
                                    meteors.append(
                                        Meteor(
                                            circle.x,
                                            circle.y,
                                            fux * finish_meteor_speed,
                                            fuy * finish_meteor_speed,
                                            (match_assets["radius"] // 2) * 4,
                                            owner_index=circles.index(circle),
                                            target_index=circles.index(end_target),
                                            damage=200,
                                            is_crit=True,
                                            max_bounces=3,
                                            image=match_assets["mika_finish_meteor_image"],
                                        )
                                    )
                            if mika_ultimate_voice_sounds:
                                play_voice_sound(random.choice(mika_ultimate_voice_sounds), preferred="secondary")
                    else:
                        circle.ultimate_cooldown_timer -= sim_dt
                        if circle.controller == "ai" and circle.ultimate_cooldown_timer <= 0:
                            activate_ultimate(circle)
                elif circle.character_type == "Do Mixi":
                    if circle.ultimate_active:
                        circle.ultimate_duration_timer -= sim_dt
                        if circle.ultimate_duration_timer <= 0:
                            circle.ultimate_active = False
                            circle.ultimate_cooldown_timer = 7.0
                    else:
                        circle.ultimate_cooldown_timer -= sim_dt
                        if circle.controller == "ai" and circle.ultimate_cooldown_timer <= 0:
                            activate_ultimate(circle)
                elif circle.character_type == "Gojo Satoru":
                    if circle.ultimate_active:
                        circle.gojo_domain_banner_timer = max(0.0, circle.gojo_domain_banner_timer - sim_dt)
                        if circle.gojo_ultimate_stage == "domain":
                            circle.ultimate_duration_timer -= sim_dt
                            circle.gojo_ultimate_timer = max(0.0, circle.ultimate_duration_timer)
                            circle.gojo_domain_freeze_timer = max(0.0, circle.gojo_domain_freeze_timer - sim_dt)
                            if circle.ultimate_duration_timer <= 0:
                                circle.ultimate_active = False
                                circle.gojo_ultimate_stage = None
                                circle.gojo_ultimate_timer = 0.0
                                circle.gojo_ultimate_hold_timer = 0.0
                                circle.gojo_ultimate_charge_duration = 0.0
                                circle.gojo_domain_freeze_timer = 0.0
                                circle.gojo_void_intro_timer = 0.0
                                circle.gojo_domain_banner_timer = 0.0
                        elif circle.gojo_ultimate_stage == "merge":
                            circle.gojo_ultimate_timer = max(0.0, circle.gojo_ultimate_timer - sim_dt)
                            circle.gojo_ultimate_hold_timer -= sim_dt
                            if circle.gojo_ultimate_hold_timer <= 0:
                                if circle.target and circle.target.health > 0:
                                    red_speed = (300.0 * 3.0) / 1.3
                                    aim_unit = get_lead_unit_vector(circle, circle.target, red_speed)
                                    if aim_unit:
                                        ux, uy = aim_unit
                                        skill_bonus = get_apocalypse_damage_bonus(circle, "skill")
                                        purple_size = max(16, int(((18 * (match_assets["radius"] / radius)) / 1.3) * 4.0))
                                        purple_image = match_assets["gojo_hollow_purple_image"]
                                        if purple_image:
                                            purple_image = pygame.transform.smoothscale(purple_image, (purple_size * 2, purple_size * 2))
                                        purple_bullet = Bullet(
                                            circle.x,
                                            circle.y,
                                            ux * red_speed,
                                            uy * red_speed,
                                            circles.index(circle),
                                            size=purple_size,
                                            image=purple_image,
                                            source="gojo_purple",
                                            damage=300 + skill_bonus,
                                            attack_type="skill",
                                        )
                                        purple_bullet.pushes_projectiles = True
                                        purple_bullet.pushes_characters = True
                                        purple_bullet.field_radius = purple_bullet.size * 3.0
                                        purple_bullet.pull_strength = 40000.0 if current_wave % 5 == 0 else 600000.0
                                        purple_bullet.push_strength = 420000.0
                                        purple_bullet.inner_push_radius = purple_bullet.size * 0.9
                                        purple_bullet.turn_rate = 0  # Straight line
                                        purple_bullet.target_index = circles.index(circle.target)
                                        bullets.append(purple_bullet)
                                        circle.gojo_ultimate_stage = "purple_flight"
                                        circle.gojo_ultimate_charge_duration = 0.0
                                if circle.gojo_ultimate_stage != "purple_flight":
                                    circle.ultimate_active = False
                                    circle.gojo_ultimate_stage = None
                                    circle.gojo_attack_count = 0
                                    circle.gojo_sequence_index = 0
                                    circle.gojo_ultimate_charge_duration = 0.0
                    else:
                        circle.ultimate_cooldown_timer = max(0.0, circle.ultimate_cooldown_timer - sim_dt)
                        if circle.controller == "ai" and circle.ultimate_cooldown_timer <= 0 and random.random() < 0.01:
                            activate_ultimate(circle)
                elif circle.character_type == "T1 Faker":
                    if circle.ultimate_active:
                        circle.ultimate_duration_timer -= sim_dt
                        circle.faker_ultimate_banner_timer = max(0.0, circle.faker_ultimate_banner_timer - sim_dt)
                        circle.faker_invulnerable_timer = max(0.0, circle.faker_invulnerable_timer - sim_dt)
                        if abs(circle.vx) + abs(circle.vy) > 0:
                            add_faker_magic_flame(faker_magic_flames, circle.x, circle.y, max(circle.radius * 0.6, 16.0), random.choice([(255, 80, 120), (175, 90, 255), (255, 140, 210)]))
                        if circle.ultimate_duration_timer <= 0:
                            circle.ultimate_active = False
                            circle.faker_invulnerable_timer = 0.0
                            circle.faker_last_stand_used = False
                    else:
                        circle.faker_invulnerable_timer = max(0.0, circle.faker_invulnerable_timer - sim_dt)
                    cooldown_rate = get_faker_skill_cooldown_rate(circle)
                    circle.ultimate_cooldown_timer = max(0.0, circle.ultimate_cooldown_timer - sim_dt * cooldown_rate)
                    circle.faker_skill_cooldown_timer = max(0.0, circle.faker_skill_cooldown_timer - sim_dt * cooldown_rate)
                    circle.faker_ultimate_cooldown_timer = max(0.0, circle.faker_ultimate_cooldown_timer - sim_dt)
                    if circle.ultimate_active and circle.health <= 0 and not circle.faker_last_stand_used:
                        circle.health = 1
                        circle.faker_last_stand_used = True
                        circle.faker_invulnerable_timer = 0.8
                    if circle.faker_combo_shots_remaining > 0:
                        circle.faker_combo_shot_timer = max(0.0, circle.faker_combo_shot_timer - sim_dt)
                        if circle.faker_combo_shot_timer <= 0 and 0 <= circle.faker_combo_target_index < len(circles):
                            combo_target = circles[circle.faker_combo_target_index]
                            if combo_target.health > 0 and getattr(combo_target, "faker_charmed_timer", 0.0) > 0:
                                orb_speed = (300.0 * 3.0) / 1.3
                                aim_unit = get_lead_unit_vector(circle, combo_target, orb_speed)
                                if aim_unit:
                                    ux, uy = aim_unit
                                else:
                                    dx = combo_target.x - circle.x
                                    dy = combo_target.y - circle.y
                                    dist = math.hypot(dx, dy)
                                    ux, uy = ((dx / dist), (dy / dist)) if dist > 0 else (1.0, 0.0)
                                orb = Bullet(
                                    circle.x,
                                    circle.y - circle.radius * 0.2,
                                    ux * orb_speed,
                                    uy * orb_speed,
                                    circles.index(circle),
                                    color=(140, 215, 255),
                                    size=max(7, int(9 * (match_assets["radius"] / radius))),
                                    image=match_assets.get("faker_normal_attack_image"),
                                    source="faker_orb",
                                    damage=80 + get_faker_damage_bonus(circle, "skill"),
                                    attack_type="skill",
                                )
                                orb.target_index = circle.faker_combo_target_index
                                orb.turn_rate = 12.0
                                bullets.append(orb)
                                add_faker_magic_flame(faker_magic_flames, circle.x, circle.y, max(circle.radius * 0.45, 10.0), (120, 220, 255))
                            circle.faker_combo_shots_remaining -= 1
                            circle.faker_combo_shot_timer = 0.12
                    elif circle.faker_combo_target_index != -1:
                        circle.faker_combo_target_index = -1
                    if circle.faker_skill_state is not None:
                        circle.bullet_timer = max(circle.bullet_timer, 0.18)
                    if circle.controller == "ai" and not circle.ultimate_active and circle.faker_ultimate_cooldown_timer <= 0:
                        low_hp_gate = circle.max_health * 0.35
                        if circle.health <= low_hp_gate or random.random() < 0.0015:
                            activate_faker_demon_king(circle)
                if circle.health > 0:
                    if getattr(circle, "faker_charmed_timer", 0.0) > 0:
                        circle.faker_charmed_timer = max(0.0, circle.faker_charmed_timer - sim_dt)
                        if 0 <= circle.faker_charmed_source_index < len(circles):
                            charm_owner = circles[circle.faker_charmed_source_index]
                        else:
                            charm_owner = None
                        charm_tick_damage = scale_apocalypse_damage(
                            charm_owner,
                            60 + get_faker_damage_bonus(charm_owner, "skill"),
                            "skill",
                        ) * sim_dt
                        if charm_tick_damage > 0:
                            circle.health = max(circle.health - charm_tick_damage, 0)
                        if circle.faker_charmed_timer <= 0:
                            circle.faker_charmed_source_index = -1
                    is_faker_charmed = getattr(circle, "faker_charmed_timer", 0.0) > 0
                else:
                    is_faker_charmed = False
                if circle.health > 0 and not is_faker_charmed:
                    opponents = get_hostile_opponents(circle, circles)
                    if opponents:
                        if circle.controller != "ai":
                            circle.target = min(opponents, key=lambda c: math.hypot(c.x - circle.x, c.y - circle.y))
                        elif len(opponents) == 1:
                            circle.target = opponents[0]
                        elif circle.target not in opponents:
                            circle.target = random.choice(opponents)
                        elif random.random() < 0.002:
                            circle.target = random.choice(opponents)

                        if circle.character_type == "Misono Mika":
                            circle.bullet_timer -= sim_dt
                            if circle.bullet_timer <= 0 and circle.target and circle.target.health > 0:
                                speed = 380.0 * 1.2
                                aim_unit = get_lead_unit_vector(circle, circle.target, speed)
                                if aim_unit:
                                    ux, uy = aim_unit
                                    if circle.burst_remaining == 0:
                                        circle.burst_remaining = 5
                                        circle.burst_timer = 0.0
                                        circle.burst_is_ultimate = circle.ultimate_active
                                        circle.attack_count += 1
                                        for i in range(4):
                                            meteor_speed = 200.0
                                            meteor_aim_unit = get_lead_unit_vector(circle, circle.target, meteor_speed)
                                            if meteor_aim_unit:
                                                mux, muy = meteor_aim_unit
                                            else:
                                                mux, muy = ux, uy
                                            mx = mux * meteor_speed
                                            my = muy * meteor_speed
                                            perp_x = -muy * 20 * (i - 1.5)
                                            perp_y = mux * 20 * (i - 1.5)
                                            meteors.append(
                                                Meteor(
                                                    circle.x + perp_x,
                                                    circle.y + perp_y,
                                                    mx,
                                                    my,
                                                    match_assets["radius"] // 2,
                                                    owner_index=circles.index(circle),
                                                    target_index=circles.index(circle.target),
                                                    damage=6,
                                                    attack_type="skill",
                                                    is_crit=True,
                                                    max_bounces=3,
                                                    image=match_assets["mika_meteor_image"],
                                                )
                                            )
                                    circle.bullet_timer = 0.75 if circle.ultimate_active else 1.5

                            if circle.burst_remaining > 0:
                                circle.burst_timer -= sim_dt
                                if circle.burst_timer <= 0 and circle.target and circle.target.health > 0:
                                    speed = (380.0 * 1.2) * (2.0 if circle.burst_is_ultimate else 1.0)
                                    aim_unit = get_lead_unit_vector(circle, circle.target, speed)
                                    if aim_unit:
                                        ux, uy = aim_unit
                                        vx = ux * speed
                                        vy = uy * speed
                                        bullet_image = match_assets["mika_bullet_ultimate_image"] if circle.burst_is_ultimate else match_assets["mika_bullet_image"]
                                        bullets.append(
                                            Bullet(
                                                circle.x,
                                                circle.y,
                                                vx,
                                                vy,
                                                circles.index(circle),
                                                size=max(4, int(10 * (match_assets["radius"] / radius))),
                                                image=bullet_image,
                                                is_ultimate=circle.burst_is_ultimate,
                                                source="mika",
                                            )
                                        )
                                        circle.bullet_count += 1
                                    circle.burst_remaining -= 1
                                    circle.burst_timer = 0.08
                        elif circle.character_type == "Do Mixi":
                            circle.bullet_timer -= sim_dt
                            if circle.bullet_timer <= 0 and circle.target and circle.target.health > 0:
                                speed = 340.0
                                aim_unit = get_lead_unit_vector(circle, circle.target, speed)
                                if aim_unit:
                                    ux, uy = aim_unit
                                    if circle.ultimate_active:
                                        perp_x = -uy
                                        perp_y = ux
                                        ultimate_speed = speed * 1.1
                                        for i in range(6):
                                            offset = (i - 2.5) * 42
                                            bullets.append(
                                                Bullet(
                                                    circle.x + perp_x * offset,
                                                    circle.y + perp_y * offset,
                                                    ux * ultimate_speed,
                                                    uy * ultimate_speed,
                                                    circles.index(circle),
                                                    size=max(6, int(11 * 1.5 * 1.5 * (match_assets["radius"] / radius))),
                                                    image=match_assets["vu_ultimate_projectile_image"],
                                                    is_ultimate=True,
                                                    source="vu_bamia_ultimate",
                                                    damage=36 + wave_damage_bonus,
                                                    attack_type="skill",
                                                    crit_chance=0.36,
                                                    crit_damage=72,
                                                    bounce_forever=True,
                                                    expires_with_owner_ultimate=True,
                                                )
                                            )
                                    else:
                                        bullets.append(
                                            Bullet(
                                                circle.x,
                                                circle.y,
                                                ux * speed,
                                                uy * speed,
                                                circles.index(circle),
                                                    size=max(6, int(11 * 1.5 * 1.5 * (match_assets["radius"] / radius))),
                                                    image=match_assets["vu_projectile_image"],
                                                source="vu_bamia",
                                                attack_type="skill",
                                            )
                                        )
                                    if vu_bamia_sound and not circle.ultimate_active:
                                        play_voice_sound(vu_bamia_sound, preferred="secondary")
                                circle.bullet_timer = 1.0
                        elif circle.character_type == "Gojo Satoru":
                            if circle.ultimate_active and circle.gojo_ultimate_stage not in ("domain", "infinite_void_intro"):
                                continue
                            circle.bullet_timer -= sim_dt
                            if circle.bullet_timer <= 0 and circle.target and circle.target.health > 0:
                                red_speed = (300.0 * 3.0) / 1.3
                                if circle.gojo_ultimate_stage == "domain":
                                    technique = "blue" if circle.gojo_sequence_index == 0 else "red"
                                elif circle.gojo_sequence_index == 0:
                                    technique = "blue"
                                elif circle.gojo_sequence_index == 1:
                                    technique = "red"
                                else:
                                    technique = random.choice(("red", "blue"))

                                domain_mul = 2.0 if circle.gojo_ultimate_stage == "domain" else 1.0
                                skill_bonus = get_apocalypse_damage_bonus(circle, "skill")
                                if technique == "blue":
                                    speed = red_speed * 0.35 * 1.2
                                    projectile_image = match_assets["gojo_blue_projectile_image"]
                                    source = "gojo_blue"
                                    damage = int(50 * domain_mul) + skill_bonus
                                    field_strength = -40000.0
                                    turn_rate = 0  # No tracking
                                    field_damage_per_second = 30.0 * domain_mul
                                else:
                                    speed = red_speed
                                    projectile_image = match_assets["gojo_red_projectile_image"]
                                    source = "gojo_red"
                                    damage = int(100 * domain_mul) + skill_bonus
                                    field_strength = 55555.56  # Reduced by another factor of 3
                                    turn_rate = 0.0
                                    field_damage_per_second = 0.0

                                aim_unit = get_lead_unit_vector(circle, circle.target, speed)
                                if aim_unit:
                                    ux, uy = aim_unit
                                    technique_bullet = Bullet(
                                        circle.x,
                                        circle.y,
                                        ux * speed,
                                        uy * speed,
                                        circles.index(circle),
                                        size=max(8, int((18 * (match_assets["radius"] / radius)) / (1.3 if source == "gojo_blue" else 1.0))),
                                        image=projectile_image,
                                        source=source,
                                        damage=damage,
                                        attack_type="skill",
                                    )
                                    technique_bullet.vx = 0.0
                                    technique_bullet.vy = 0.0
                                    technique_bullet.pending_vx = ux * speed
                                    technique_bullet.pending_vy = uy * speed
                                    technique_bullet.release_speed = speed
                                    technique_bullet.target_index = circles.index(circle.target)
                                    technique_bullet.hold_timer = 1.0
                                    technique_bullet.hold_duration = 1.0
                                    technique_bullet.hold_offset = circle.radius + technique_bullet.size * 0.9
                                    technique_bullet.field_radius = (arena_width * 0.5) if source == "gojo_blue" else (technique_bullet.size * 5.0)
                                    technique_bullet.field_strength = field_strength
                                    if source == "gojo_blue":
                                        technique_bullet.pull_strength = 40000.0
                                    technique_bullet.turn_rate = turn_rate
                                    technique_bullet.field_damage_per_second = field_damage_per_second
                                    technique_bullet.pushes_projectiles = source != "gojo_purple"
                                    technique_bullet.pushes_characters = source != "gojo_purple"
                                    technique_bullet.blue_charging = (source == "gojo_blue")
                                    bullets.append(technique_bullet)
                                    if source == "gojo_blue" and gojo_lapse_blue_sound:
                                        play_voice_sound(gojo_lapse_blue_sound, preferred="secondary", block_if_primary=True)
                                    elif source == "gojo_red" and gojo_reversal_red_sound:
                                        play_voice_sound(gojo_reversal_red_sound, preferred="secondary", block_if_primary=True)
                                    if circle.gojo_ultimate_stage == "domain":
                                        if technique == "blue":
                                            circle.gojo_sequence_index = 1
                                            circle.bullet_timer = technique_bullet.hold_duration + 0.5
                                        else:
                                            circle.gojo_sequence_index = 0
                                            circle.bullet_timer = 1.0
                                    else:
                                        circle.gojo_sequence_index += 1
                                        circle.bullet_timer = 2.5
                                    circle.gojo_attack_count += 1
                                    if circle.gojo_attack_count >= 2:
                                        activate_gojo_hollow_purple(circle)
                        elif circle.character_type == "T1 Faker":
                            if (
                                circle.controller == "ai"
                                and circle.ultimate_cooldown_timer <= 0
                                and not circle.faker_blink_mark_active
                                and circle.faker_skill_state is None
                                and circle.target
                                and random.random() < 0.008
                            ):
                                activate_faker_second_skill(circle)
                            if (
                                circle.controller == "ai"
                                and circle.faker_skill_cooldown_timer <= 0
                                and circle.faker_skill_state is None
                                and circle.target
                                and random.random() < 0.01
                            ):
                                activate_faker_first_skill(circle)
                            if circle.faker_skill_state is None:
                                circle.bullet_timer -= sim_dt
                            if circle.faker_skill_state is None and circle.bullet_timer <= 0 and circle.target and circle.target.health > 0:
                                speed = 420.0
                                aim_unit = get_lead_unit_vector(circle, circle.target, speed)
                                if aim_unit:
                                    ux, uy = aim_unit
                                    circle.faker_normal_attack_count += 1
                                    bullets.append(
                                        Bullet(
                                            circle.x,
                                            circle.y,
                                            ux * speed,
                                            uy * speed,
                                            circles.index(circle),
                                            color=(255, 255, 255),
                                            size=max(5, int(11 * (match_assets["radius"] / radius))),
                                            image=match_assets.get("faker_call_image"),
                                            source="faker",
                                            damage=scale_apocalypse_damage(circle, 18 + get_faker_damage_bonus(circle, "normal"), "normal"),
                                            attack_type="normal",
                                            crit_chance=0.15,
                                            crit_damage=scale_apocalypse_damage(circle, 30 + get_faker_damage_bonus(circle, "normal"), "normal"),
                                        )
                                    )
                                    if faker_call_sound and circle.faker_normal_attack_count % 2 == 1:
                                        play_voice_sound(faker_call_sound, preferred="secondary")
                                circle.bullet_timer = 1.0
                        if not gojo_voice_intro_active:
                            if circle.character_type == "T1 Faker" and circle.faker_skill_state is not None:
                                circle.vx = 0.0
                                circle.vy = 0.0
                            elif getattr(circle, "faker_charmed_timer", 0.0) > 0:
                                if 0 <= circle.faker_charmed_source_index < len(circles):
                                    source_circle = circles[circle.faker_charmed_source_index]
                                    dx = source_circle.x - circle.x
                                    dy = source_circle.y - circle.y
                                    dist = math.hypot(dx, dy)
                                    if dist > 0:
                                        pull_speed = min(circle.base_speed * 0.75 if circle.base_speed > 0 else 120.0, 120.0)
                                        circle.vx = (dx / dist) * pull_speed
                                        circle.vy = (dy / dist) * pull_speed
                                    else:
                                        circle.vx = 0.0
                                        circle.vy = 0.0
                                else:
                                    circle.vx = 0.0
                                    circle.vy = 0.0
                                circle.impulse_vx *= max(0.0, 1.0 - 7.0 * sim_dt)
                                circle.impulse_vy *= max(0.0, 1.0 - 7.0 * sim_dt)
                            elif circle.character_type == "T1 Faker" and circle.ultimate_active:
                                if circle.controller == "player1":
                                    keys = pygame.key.get_pressed()
                                    circle.vx, circle.vy = get_controlled_velocity(keys, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, speed=420.0)
                                elif circle.controller == "player2":
                                    keys = pygame.key.get_pressed()
                                    circle.vx, circle.vy = get_controlled_velocity(keys, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, speed=420.0)
                                elif circle.controller == "ai" and circle.target and circle.target.health > 0:
                                    dx = circle.target.x - circle.x
                                    dy = circle.target.y - circle.y
                                    dist = math.hypot(dx, dy)
                                    if dist > 0:
                                        circle.vx = (dx / dist) * circle.base_speed * 1.5
                                        circle.vy = (dy / dist) * circle.base_speed * 1.5
                            elif circle.controller == "player1":
                                keys = pygame.key.get_pressed()
                                circle.vx, circle.vy = get_controlled_velocity(keys, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d)
                            elif circle.controller == "player2":
                                keys = pygame.key.get_pressed()
                                circle.vx, circle.vy = get_controlled_velocity(keys, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l)
                            elif circle.controller == "zombie" and circle.character_type in ("Green Mob", "Giorno Mambo"):
                                humans = [c for c in circles if c.health > 0 and c.character_type not in ("Green Mob", "Giorno Mambo")]
                                if humans:
                                    t = min(humans, key=lambda c: math.hypot(c.x - circle.x, c.y - circle.y))
                                    dx, dy = t.x - circle.x, t.y - circle.y
                                    d = math.hypot(dx, dy)
                                    if d > 0:
                                        circle.vx = (dx / d) * circle.base_speed
                                        circle.vy = (dy / d) * circle.base_speed
                                        circle.target = t
                                else:
                                    # No humans - move down toward arena
                                    circle.vx = 0
                                    circle.vy = circle.base_speed
                                # Keep moving constantly - don't let physics stop the mambo
                                # Only reset if not being pushed by gojo_red (check vx/vy magnitude)
                                if not (hasattr(circle, 'being_pushed_by_red') and circle.being_pushed_by_red):
                                    circle.impulse_vx = 0
                                    circle.impulse_vy = 0
                                circle.being_pushed_by_red = False
                        if game_mode == "zombie" and is_player_controlled_human(circle):
                            circle.impulse_vx = 0.0
                            circle.impulse_vy = 0.0
                            circle.impulse_wall_bounces_remaining = 0
                        circle.move(sim_dt)
                        
                        if game_mode == "zombie":
                            # Clamp to the full white funnel in local arena coordinates.
                            circle.clamp_to_trapezoid(0, 0, arena_width, arena_height)
                        else:
                            if circle.controller in ("ai", "zombie"):
                                circle.bounce_off_wall(arena_width, arena_height)
                            circle.bounce_impulse_off_wall(arena_width, arena_height)
                            circle.clamp_to_arena(arena_width, arena_height)
            faker_waves, added_shake = update_faker_soldier_waves(faker_waves, circles, sim_dt, damage_texts, faker_dust_trails)
            if added_shake > 0:
                screen_shake_timer = max(screen_shake_timer, 0.08)
                screen_shake_strength = max(screen_shake_strength, added_shake)

            for i in range(len(circles)):
                for j in range(i + 1, len(circles)):
                    if game_mode == "zombie" and (
                        is_player_controlled_human(circles[i]) or is_player_controlled_human(circles[j])
                    ):
                        continue
                    resolve_circle_collision(circles[i], circles[j])
                    if game_mode == "zombie":
                        circles[i].clamp_to_trapezoid(0, 0, arena_width, arena_height)
                        circles[j].clamp_to_trapezoid(0, 0, arena_width, arena_height)
                    else:
                        circles[i].bounce_impulse_off_wall(arena_width, arena_height)
                        circles[j].bounce_impulse_off_wall(arena_width, arena_height)
                        circles[i].clamp_to_arena(arena_width, arena_height)
                        circles[j].clamp_to_arena(arena_width, arena_height)

            if game_mode == "zombie":
                # Track mambos that die this frame
                mambos_before = [c for c in circles if c.character_type in ("Green Mob", "Giorno Mambo") and c.health > 0]
                
                for z in circles:
                    if z.character_type not in ("Green Mob", "Giorno Mambo") or z.health <= 0:
                        continue
                    for h in circles:
                        if h.character_type in ("Green Mob", "Giorno Mambo") or h.health <= 0:
                            continue
                        if z.hit(h):
                            # Use wave-based damage stored on zombie, or default
                            z_damage = getattr(z, 'damage', 20) * sim_dt
                            apply_damage_to_circle(damage_texts, h, z_damage, False)
                
                # Check for dead mambos and reward players
                mambos_after = [c for c in circles if c.character_type in ("Green Mob", "Giorno Mambo") and c.health > 0]
                mambos_before_ids = set(id(c) for c in mambos_before)
                mambos_after_ids = set(id(c) for c in mambos_after)
                dead_mambos = mambos_before_ids - mambos_after_ids
                
                if dead_mambos:
                    dead_count = len(dead_mambos)
                    # Reward all alive human players
                    for h in circles:
                        if h.health > 0 and h.character_type not in ("Green Mob", "Giorno Mambo"):
                            # Heal 100 HP per mambo killed
                            h.health = min(h.health + 100 * dead_count, h.max_health)
                            # Increase damage by 30 per mambo killed
                            if hasattr(h, 'damage'):
                                h.damage = getattr(h, 'damage', 20) + 30 * dead_count

            for circle in circles:
                if circle.health > 0 and circle.controller == "ai" and circle.base_speed > 0:
                    if gojo_voice_intro_active:
                        continue
                    if (
                        active_gojo_domain is not None
                        and circle is not active_gojo_domain
                        and active_gojo_domain.gojo_domain_freeze_timer > 0
                    ):
                        continue
                    normalize_velocity(circle, circle.base_speed)

            alive_circles = [c for c in circles if c.health > 0]
            new_bullets = []
            domain_gojo_index = circles.index(active_gojo_domain) if active_gojo_domain is not None else -1
            for bullet in bullets:
                if (
                    active_gojo_domain is not None
                    and active_gojo_domain.gojo_domain_freeze_timer > 0
                    and not (
                        domain_gojo_index >= 0
                        and bullet.owner_index == domain_gojo_index
                        and bullet.source in ("gojo_red", "gojo_blue", "gojo_purple")
                    )
                ):
                    new_bullets.append(bullet)
                    continue
                if bullet.expires_with_owner_ultimate:
                    owner_is_active = 0 <= bullet.owner_index < len(circles) and circles[bullet.owner_index].ultimate_active
                    if not owner_is_active:
                        continue
                if bullet.hold_timer > 0 and 0 <= bullet.owner_index < len(circles):
                    owner = circles[bullet.owner_index]
                    pending_speed = bullet.release_speed if bullet.release_speed is not None else math.hypot(bullet.pending_vx, bullet.pending_vy)
                    if 0 <= bullet.target_index < len(circles):
                        target = circles[bullet.target_index]
                        if target.health > 0 and pending_speed > 0:
                            aim_unit = get_lead_unit_vector(owner, target, pending_speed)
                            if aim_unit:
                                ux, uy = aim_unit
                                bullet.pending_vx = ux * pending_speed
                                bullet.pending_vy = uy * pending_speed
                    pending_length = math.hypot(bullet.pending_vx, bullet.pending_vy)
                    if pending_length > 0:
                        growth = 1.0 - (bullet.hold_timer / bullet.hold_duration) if bullet.hold_duration > 0 else 1.0
                        ux = bullet.pending_vx / pending_length
                        uy = bullet.pending_vy / pending_length
                        charge_offset = bullet.hold_offset * growth
                        bullet.x = owner.x + ux * charge_offset
                        bullet.y = owner.y + uy * charge_offset
                curve_bullet_toward_target(bullet, circles, sim_dt, arena_width, arena_height)
                bullet.move(sim_dt)
                if bullet.source == "gojo_purple":
                    add_gojo_purple_trail(purple_trails, bullet.x, bullet.y, bullet.size)
                elif bullet.source == "faker_charm":
                    add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(bullet.size * 0.8, 8.0), random.choice([(255, 120, 220), (120, 220, 255), (255, 190, 240)]))
                elif bullet.source == "faker_orb":
                    add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(bullet.size * 0.8, 8.0), random.choice([(110, 210, 255), (150, 230, 255), (210, 245, 255)]))
                if bullet.pushes_projectiles or bullet.pushes_characters:
                    if bullet.pushes_projectiles:
                        for other_bullet in bullets:
                            if other_bullet is bullet:
                                continue
                            if bullet.source == "gojo_purple":
                                pull = apply_radial_push(bullet.x, bullet.y, other_bullet.x, other_bullet.y, bullet.field_radius, -bullet.pull_strength * sim_dt)
                                if pull is not None:
                                    other_bullet.vx += pull[0]
                                    other_bullet.vy += pull[1]
                                continue
                            if bullet.source == "gojo_blue" and (bullet.hold_timer > 0 or bullet.field_activation_delay > 0):
                                continue
                            push = apply_radial_push(
                                bullet.x,
                                bullet.y,
                                other_bullet.x,
                                other_bullet.y,
                                bullet.field_radius,
                                bullet.field_strength * sim_dt,
                            )
                            if push is None:
                                continue
                            push_x, push_y = push
                            other_bullet.vx += push_x * 3
                            other_bullet.vy += push_y * 3
                            if bullet.source == "gojo_red":
                                other_bullet.impulse_wall_bounces_remaining = max(getattr(other_bullet, 'impulse_wall_bounces_remaining', 0), 2)
                    if bullet.pushes_characters:
                        owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                        for idx, circle in enumerate(circles):
                            if idx == bullet.owner_index or circle.health <= 0:
                                continue
                            if game_mode == "zombie" and is_player_controlled_human(circle):
                                continue
                            if bullet.source == "gojo_purple":
                                inside_field = apply_purple_lock_to_circle(bullet, circle, sim_dt)
                                if not inside_field:
                                    continue
                                continue
                            if bullet.source == "gojo_blue":
                                if bullet.hold_timer > 0 or bullet.field_activation_delay > 0:
                                    continue
                                inside_field = apply_blue_pull_to_circle(bullet, circle, sim_dt)
                                if not inside_field:
                                    continue
                                if bullet.field_damage_per_second > 0:
                                    owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                    damage = scale_apocalypse_damage(owner, bullet.field_damage_per_second, "skill") * sim_dt
                                    circle.health = max(circle.health - damage, 0)
                                continue
                            if bullet.source == "gojo_red" and not circles_are_hostile(owner_circle, circle):
                                continue
                            push = apply_radial_push(
                                bullet.x,
                                bullet.y,
                                circle.x,
                                circle.y,
                                bullet.field_radius,
                                bullet.field_strength * sim_dt * 1.35,
                            )
                            if push is None:
                                continue
                            push_x, push_y = push
                            if bullet.source == "gojo_red":
                                # Mark as being pushed by red so impulse isn't immediately reset
                                circle.being_pushed_by_red = True
                                # Apply a huge burst so hostile units ricochet hard across the arena.
                                circle.impulse_vx += push_x * 14
                                circle.impulse_vy += push_y * 14
                                circle.vx += push_x * 7
                                circle.vy += push_y * 7
                                circle.impulse_wall_bounces_remaining = max(circle.impulse_wall_bounces_remaining, 4)
                                if game_mode == "zombie" and idx not in bullet.hit_targets:
                                    owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                    red_field_damage = scale_apocalypse_damage(owner, 100, "skill")
                                    apply_damage_to_circle(damage_texts, circle, red_field_damage, False)
                                    bullet.hit_targets.add(idx)
                            else:
                                circle.impulse_vx += push_x * 2.4
                                circle.impulse_vy += push_y * 2.4
                            if bullet.field_damage_per_second > 0:
                                damage = bullet.field_damage_per_second * sim_dt
                                circle.health = max(circle.health - damage, 0)
                bounced = False
                if bullet.bounce_forever:
                    bounced = bullet.bounce_off_wall(arena_width, arena_height)

                touched_wall = (
                    bullet.x - bullet.size <= 0
                    or bullet.x + bullet.size >= arena_width
                    or bullet.y - bullet.size <= 0
                    or bullet.y + bullet.size >= arena_height
                )
                if bullet.source == "gojo_red" and touched_wall:
                    impact_x = min(max(bullet.x, 0), arena_width)
                    impact_y = min(max(bullet.y, 0), arena_height)
                    add_gojo_technique_explosion(red_explosions, impact_x, impact_y, bullet.size * 2.2, gojo_red_colors)
                    continue
                if bullet.source == "gojo_blue" and touched_wall:
                    continue
                if bullet.source in ("faker_charm", "faker_orb") and touched_wall:
                    splash_radius = max(bullet.size * (3.6 if bullet.source == "faker_orb" else 3.0), 36.0)
                    splash_damage = scale_apocalypse_damage(
                        circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None,
                        60 if bullet.source == "faker_orb" else 25,
                        "skill",
                    )
                    add_gojo_technique_explosion(red_explosions, bullet.x, bullet.y, splash_radius, faker_blue_explosion_colors)
                    apply_explosion_splash_damage(damage_texts, circles, bullet.owner_index, bullet.x, bullet.y, splash_radius, splash_damage)
                    add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(bullet.size * 1.2, 12.0), (255, 150, 225) if bullet.source == "faker_charm" else (120, 215, 255))
                    continue
                if bullet.source == "gojo_purple" and touched_wall:
                    impact_x = min(max(bullet.x, 0), arena_width)
                    impact_y = min(max(bullet.y, 0), arena_height)
                    ap_r = max(bullet.field_radius, bullet.size * 2.4)
                    add_gojo_technique_explosion(red_explosions, impact_x, impact_y, ap_r, gojo_purple_colors)
                    owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                    purple_explosion_damage = scale_apocalypse_damage(owner_circle, 200, "skill")
                    purple_hit_any = False
                    for idx, circle in enumerate(circles):
                        if idx == bullet.owner_index or circle.health <= 0:
                            continue
                        if not circles_are_hostile(owner_circle, circle):
                            continue
                        if math.hypot(circle.x - impact_x, circle.y - impact_y) <= ap_r:
                            apply_damage_to_circle(damage_texts, circle, purple_explosion_damage, True)
                            purple_hit_any = True
                    if purple_hit_any and owner_circle is not None and owner_circle.health > 0:
                        owner_circle.health = min(owner_circle.max_health, owner_circle.health + owner_circle.max_health * 0.1)
                    if 0 <= bullet.owner_index < len(circles):
                        owner = circles[bullet.owner_index]
                        owner.ultimate_active = False
                        owner.gojo_ultimate_stage = None
                        owner.gojo_ultimate_hold_timer = 0.0
                        owner.gojo_ultimate_charge_duration = 0.0
                        owner.gojo_hollow_purple_count += 1
                        owner.gojo_attack_count = 0
                        owner.gojo_sequence_index = 0
                    continue

                if 0 <= bullet.x <= arena_width and 0 <= bullet.y <= arena_height:
                    hit_any = False
                    owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                    for idx, circle in enumerate(circles):
                        if idx == bullet.owner_index or circle.health <= 0:
                            continue
                        if bullet.source in ("faker_charm", "faker_orb") and not circles_are_hostile(owner_circle, circle):
                            continue
                        if bullet.source == "gojo_purple" and not circles_are_hostile(owner_circle, circle):
                            continue
                        hit_radius = circle.radius + (bullet.size * 0.55 if bullet.source == "gojo_purple" else 0.0)
                        if math.hypot(circle.x - bullet.x, circle.y - bullet.y) <= hit_radius:
                            if bullet.source == "faker_charm":
                                if not circles_are_hostile(owner_circle, circle):
                                    continue
                                circle.faker_charmed_timer = 2.0
                                circle.faker_charmed_source_index = bullet.owner_index
                                circle.vx = 0.0
                                circle.vy = 0.0
                                circle.impulse_vx *= 0.25
                                circle.impulse_vy *= 0.25
                                if owner_circle is not None and owner_circle.health > 0:
                                    owner_circle.faker_combo_target_index = idx
                                    owner_circle.faker_combo_shots_remaining = 3
                                    owner_circle.faker_combo_shot_timer = 0.05
                                charm_splash_radius = max(circle.radius * 1.25, bullet.size * 3.0)
                                charm_splash_damage = scale_apocalypse_damage(owner_circle, 25, "skill")
                                add_gojo_technique_explosion(red_explosions, bullet.x, bullet.y, charm_splash_radius, faker_blue_explosion_colors)
                                apply_explosion_splash_damage(
                                    damage_texts,
                                    circles,
                                    bullet.owner_index,
                                    bullet.x,
                                    bullet.y,
                                    charm_splash_radius,
                                    charm_splash_damage,
                                )
                                add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(circle.radius * 0.85, 20.0), (255, 140, 220))
                                add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(circle.radius * 1.25, 28.0), (120, 220, 255))
                                hit_any = True
                                break
                            if bullet.source in ("gojo_blue", "gojo_purple") and idx in bullet.hit_targets:
                                continue
                            if bullet.damage is not None:
                                is_crit = random.random() < bullet.crit_chance
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = bullet.crit_damage if is_crit else bullet.damage
                                attack_type = bullet.attack_type or "skill"
                                damage = scale_apocalypse_damage(owner, base_damage, attack_type)
                            elif bullet.source == "mika":
                                is_crit = True
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = 4
                                damage = scale_apocalypse_damage(owner, base_damage, "normal")
                            elif bullet.source == "vu_bamia":
                                is_crit = False
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                damage = scale_apocalypse_damage(owner, 36, "skill")
                            elif bullet.size == 5 and bullet.color == (255, 220, 50):  # normal yellow bullets
                                is_crit = random.random() < 0.1
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = 2 if is_crit else 1
                                damage = scale_apocalypse_damage(owner, base_damage, "normal")
                            else:
                                is_crit = random.random() < 0.1
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = 30 if is_crit else 15
                                damage = scale_apocalypse_damage(owner, base_damage, "normal")
                            apply_damage_to_circle(damage_texts, circle, damage, is_crit)
                            if is_crit and 0 <= bullet.owner_index < len(circles):
                                owner = circles[bullet.owner_index]
                                if owner.character_type == "Misono Mika" and owner.health > 0:
                                    owner.health = min(owner.max_health, owner.health + 2)
                            if bullet.source == "gojo_red":
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    max(circle.radius * 0.9, bullet.size * 2.8),
                                    gojo_red_colors,
                                )
                            elif bullet.source == "faker_orb":
                                orb_splash_radius = max(circle.radius * 1.3, bullet.size * 4.2)
                                orb_splash_damage = scale_apocalypse_damage(owner, 60, "skill")
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    orb_splash_radius,
                                    faker_blue_explosion_colors,
                                )
                                apply_explosion_splash_damage(
                                    damage_texts,
                                    circles,
                                    bullet.owner_index,
                                    bullet.x,
                                    bullet.y,
                                    orb_splash_radius,
                                    orb_splash_damage,
                                )
                                add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(circle.radius * 1.05, 24.0), (255, 95, 30))
                                add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(circle.radius * 1.45, 32.0), (255, 210, 110))
                            elif bullet.source == "gojo_purple" and owner is not None and owner.health > 0:
                                owner.health = min(owner.max_health, owner.health + owner.max_health * 0.1)
                            if bullet.source in ("gojo_blue", "gojo_purple"):
                                bullet.hit_targets.add(idx)
                            else:
                                hit_any = True
                                break
                    if not hit_any:
                        new_bullets.append(bullet)
            bullets = new_bullets

            if active_gojo_domain is None:
                new_meteors = []
                for meteor in meteors:
                    meteor.move(sim_dt, circles)
                    meteor.bounce_off_wall(arena_width, arena_height)
                    if meteor.bounce_count <= meteor.max_bounces and 0 <= meteor.x <= arena_width and 0 <= meteor.y <= arena_height:
                        hit_any = False
                        for idx, circle in enumerate(circles):
                            if idx == meteor.owner_index or circle.health <= 0:
                                continue
                            if math.hypot(circle.x - meteor.x, circle.y - meteor.y) <= circle.radius:
                                is_crit = meteor.is_crit
                                owner = circles[meteor.owner_index] if 0 <= meteor.owner_index < len(circles) else None
                                attack_type = getattr(meteor, "attack_type", "skill")
                                damage = scale_apocalypse_damage(owner, meteor.damage, attack_type)
                                if is_crit:
                                    damage *= 2
                                apply_damage_to_circle(damage_texts, circle, damage, is_crit)
                                if is_crit and 0 <= meteor.owner_index < len(circles):
                                    owner = circles[meteor.owner_index]
                                    if owner.character_type == "Misono Mika" and owner.health > 0:
                                        owner.health = min(owner.max_health, owner.health + 2)
                                hit_any = True
                                break
                        if not hit_any:
                            new_meteors.append(meteor)
                meteors = new_meteors

            shake_x = int(random.uniform(-screen_shake_strength, screen_shake_strength)) if screen_shake_timer > 0 else 0
            shake_y = int(random.uniform(-screen_shake_strength, screen_shake_strength)) if screen_shake_timer > 0 else 0
            render_arena_left = arena_left + shake_x
            render_arena_top = arena_top + shake_y
            screen.fill((20, 20, 30))
            faker_ultimate_visual = any(circle.character_type == "T1 Faker" and circle.ultimate_active for circle in circles)
            if faker_ultimate_visual:
                dark_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                dark_surface.fill((26, 10, 32, 56 if faker_ultimate_hitstop_timer <= 0 else 96))
                screen.blit(dark_surface, (0, 0))
            border_rect = pygame.Rect(render_arena_left, render_arena_top, arena_width, arena_height)
            
            active_domain_visual = any(
                circle.character_type == "Gojo Satoru"
                and circle.ultimate_active
                and circle.gojo_ultimate_stage == "domain"
                for circle in circles
            )
            gojo_domain_banner_owner = next(
                (
                    circle
                    for circle in circles
                    if circle.character_type == "Gojo Satoru"
                    and circle.ultimate_active
                    and circle.gojo_ultimate_stage in ("infinite_void_intro", "domain")
                    and circle.gojo_domain_banner_timer > 0
                ),
                None,
            )
            if active_domain_visual:
                video_surface = update_video_background(infinite_void_video, sim_dt)
                if video_surface is not None:
                    screen.blit(video_surface, (0, 0))
                else:
                    draw_infinite_void_background(screen, screen.get_rect(), elapsed_time)
            
                # Zombie mode special rendering
            if game_mode == "zombie":
                # Draw tube opening - where zombies come from
                tube_w = max(120, int(arena_width * 0.4))
                top_center_x = render_arena_left + arena_width // 2
                tube_height = tube_top_height
                
                # Calculate tube opening positions
                tube_left = top_center_x - tube_w // 2
                tube_right = top_center_x + tube_w // 2
                
                # Small white dots at top of screen (funnel points)
                dot_radius = 6
                pygame.draw.circle(screen, (255, 255, 255), (tube_left, 0), dot_radius)
                pygame.draw.circle(screen, (255, 255, 255), (tube_right, 0), dot_radius)
                
                # Draw diagonal lines from dots to rectangle corners (funnel shape)
                pygame.draw.line(screen, (255, 255, 255), (tube_left, 0), (render_arena_left, render_arena_top), 3)
                pygame.draw.line(screen, (255, 255, 255), (tube_right, 0), (render_arena_left + arena_width, render_arena_top), 3)
                
                # Draw white lines to enclose the playable region (left, right, bottom)
                pygame.draw.line(screen, (255, 255, 255), (render_arena_left, render_arena_top), (render_arena_left, render_arena_top + arena_height), 3)
                pygame.draw.line(screen, (255, 255, 255), (render_arena_left + arena_width, render_arena_top), (render_arena_left + arena_width, render_arena_top + arena_height), 3)
                pygame.draw.line(screen, (255, 255, 255), (render_arena_left, render_arena_top + arena_height), (render_arena_left + arena_width, render_arena_top + arena_height), 3)
            else:
                pygame.draw.rect(screen, (200, 200, 200), border_rect, 3)

            draw_gojo_technique_explosions(screen, red_explosions, render_arena_left, render_arena_top)
            draw_gojo_purple_trails(screen, purple_trails, render_arena_left, render_arena_top)
            draw_faker_dust_trails(screen, faker_dust_trails, render_arena_left, render_arena_top)
            draw_faker_magic_flames(screen, faker_magic_flames, render_arena_left, render_arena_top)
            draw_faker_charm_status(screen, circles, elapsed_time, render_arena_left, render_arena_top)
            draw_faker_soldier_waves(screen, faker_waves, elapsed_time, render_arena_left, render_arena_top)
            faker_banner_owner = next((circle for circle in circles if circle.character_type == "T1 Faker" and circle.faker_ultimate_banner_timer > 0), None)
            if faker_banner_owner is not None:
                banner_rect = pygame.Rect(screen_width // 2 - 310, 32, 620, 76)
                pygame.draw.rect(screen, (45, 12, 38), banner_rect, border_radius=18)
                pygame.draw.rect(screen, (255, 105, 190), banner_rect, 3, border_radius=18)
                draw_text(screen, "UNKILLABLE DEMON KING", banner_rect.x + 40, banner_rect.y + 18, color=(255, 245, 255), size=34)
            if gojo_domain_banner_owner is not None:
                banner_rect = pygame.Rect(screen_width // 2 - 340, 118, 680, 72)
                pygame.draw.rect(screen, (34, 18, 54), banner_rect, border_radius=18)
                pygame.draw.rect(screen, (205, 125, 255), banner_rect, 3, border_radius=18)
                draw_text(screen, "Domain Expansion: Infinite Void", banner_rect.x + 34, banner_rect.y + 18, color=(248, 238, 255), size=32)

            for meteor in meteors:
                meteor.draw(screen, render_arena_left, render_arena_top)

            for idx, circle in enumerate(circles):
                if circle.health <= 0:
                    continue
                if (
                    circle.character_type == "Gojo Satoru"
                    and circle.ultimate_active
                    and circle.gojo_ultimate_stage in ("infinite_void_intro", "domain")
                ):
                    aura_surface = pygame.Surface((int(circle.radius * 8), int(circle.radius * 8)), pygame.SRCALPHA)
                    aura_center = aura_surface.get_width() // 2
                    pulse = 0.86 + 0.14 * math.sin(elapsed_time * 8.5)
                    outer_r = max(18, int(circle.radius * 2.3 * pulse))
                    inner_r = max(10, int(circle.radius * 1.45))
                    pygame.draw.circle(aura_surface, (150, 90, 255, 36), (aura_center, aura_center), outer_r + 24)
                    pygame.draw.circle(aura_surface, (195, 125, 255, 70), (aura_center, aura_center), outer_r + 10)
                    pygame.draw.circle(aura_surface, (225, 170, 255, 145), (aura_center, aura_center), outer_r, 4)
                    pygame.draw.circle(aura_surface, (250, 235, 255, 110), (aura_center, aura_center), inner_r, 2)
                    screen.blit(aura_surface, aura_surface.get_rect(center=(int(circle.x + render_arena_left), int(circle.y + render_arena_top))))
                if circle.character_type == "T1 Faker" and circle.ultimate_active:
                    aura_surface = pygame.Surface((int(circle.radius * 7), int(circle.radius * 7)), pygame.SRCALPHA)
                    aura_center = aura_surface.get_width() // 2
                    pulse = 0.82 + 0.18 * math.sin(elapsed_time * 9.0)
                    outer_r = max(16, int(circle.radius * 2.0 * pulse))
                    inner_r = max(10, int(circle.radius * 1.3))
                    pygame.draw.circle(aura_surface, (255, 70, 120, 36), (aura_center, aura_center), outer_r + 18)
                    pygame.draw.circle(aura_surface, (170, 90, 255, 68), (aura_center, aura_center), outer_r + 8)
                    pygame.draw.circle(aura_surface, (255, 120, 220, 132), (aura_center, aura_center), outer_r, 4)
                    pygame.draw.circle(aura_surface, (255, 235, 255, 110), (aura_center, aura_center), inner_r, 2)
                    screen.blit(aura_surface, aura_surface.get_rect(center=(int(circle.x + render_arena_left), int(circle.y + render_arena_top))))
                current_image = circle.image
                if circle.character_type == "Misono Mika" and circle.ultimate_active and match_assets["mika_body_image"]:
                    current_image = match_assets["mika_body_image"]
                elif circle.character_type == "Do Mixi" and circle.ultimate_active and circle.ultimate_image:
                    current_image = circle.ultimate_image

                # Draw health bar for mambo enemies.
                if circle.character_type in ("Zombie", "Green Mob", "Giorno Mambo"):
                    bar_width = 40
                    bar_height = 4
                    bar_x = int(circle.x + render_arena_left - bar_width // 2)
                    bar_y = int(circle.y + render_arena_top - circle.radius - 15)
                    
                    # Calculate health ratio
                    health_ratio = max(0.0, min(1.0, circle.health / circle.max_health))
                    
                    # Draw red background (damage taken)
                    pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                    # Draw green foreground (remaining health)
                    pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
                    
                    # Draw HP text above health bar
                    hp_text = f"{int(circle.health)}/{circle.max_health}"
                    font = get_font(12)
                    rendered = font.render(hp_text, True, (255, 255, 255))
                    text_rect = rendered.get_rect()
                    text_rect.centerx = bar_x + bar_width // 2
                    text_rect.y = bar_y - 12
                    screen.blit(rendered, text_rect)

                if current_image:
                    image_rect = current_image.get_rect()
                    image_rect.center = (int(circle.x + render_arena_left), int(circle.y + render_arena_top))
                    screen.blit(current_image, image_rect)
                else:
                    pygame.draw.circle(
                        screen,
                        circle.color,
                        (int(circle.x + render_arena_left), int(circle.y + render_arena_top)),
                        circle.radius,
                    )
                if circle.character_type == "T1 Faker" and circle.ultimate_active:
                    eye_y = int(circle.y + render_arena_top - circle.radius * 0.18)
                    eye_dx = max(4, int(circle.radius * 0.22))
                    pygame.draw.circle(screen, (255, 95, 125), (int(circle.x + render_arena_left - eye_dx), eye_y), max(2, int(circle.radius * 0.11)))
                    pygame.draw.circle(screen, (255, 95, 125), (int(circle.x + render_arena_left + eye_dx), eye_y), max(2, int(circle.radius * 0.11)))
                if (
                    circle.character_type == "Gojo Satoru"
                    and circle.ultimate_active
                    and circle.gojo_ultimate_stage in ("infinite_void_intro", "domain")
                ):
                    eye_y = int(circle.y + render_arena_top - circle.radius * 0.16)
                    eye_dx = max(4, int(circle.radius * 0.22))
                    pygame.draw.circle(screen, (220, 170, 255), (int(circle.x + render_arena_left - eye_dx), eye_y), max(2, int(circle.radius * 0.1)))
                    pygame.draw.circle(screen, (220, 170, 255), (int(circle.x + render_arena_left + eye_dx), eye_y), max(2, int(circle.radius * 0.1)))

                if circle.character_type == "Misono Mika" and circle.ultimate_active and match_assets["mika_halo_image"]:
                    halo_float = math.sin(elapsed_time * 8.0) * 6.0
                    halo_rect = match_assets["mika_halo_image"].get_rect(
                        center=(int(circle.x + render_arena_left), int(circle.y + render_arena_top - circle.radius - 10 + halo_float))
                    )
                    screen.blit(match_assets["mika_halo_image"], halo_rect)

                if circle.gun_image and circle.target and circle.target.health > 0:
                    dx = circle.target.x - circle.x
                    dy = circle.target.y - circle.y
                    distance = math.hypot(dx, dy)
                    if distance > 0:
                        angle = math.degrees(math.atan2(dy, dx))
                        gun_rotated = pygame.transform.rotate(circle.gun_image, -angle)
                        gun_rect = gun_rotated.get_rect()
                        base_offset = circle.radius * 0.9
                        size_offset = max(gun_rect.width, gun_rect.height) * 0.35
                        offset = base_offset + size_offset
                        x_offset = dx / distance * offset
                        y_offset = dy / distance * offset
                        gun_rect.center = (int(circle.x + render_arena_left + x_offset), int(circle.y + render_arena_top + y_offset))
                        screen.blit(gun_rotated, gun_rect)

                if circle.character_type == "Gojo Satoru":
                    draw_gojo_hollow_purple_charge(screen, circle, circle.target, elapsed_time, match_assets, render_arena_left, render_arena_top)

            for bullet in bullets:
                draw_gojo_blue_black_hole(screen, bullet, elapsed_time, render_arena_left, render_arena_top)

            for bullet in bullets:
                bullet.draw(screen, render_arena_left, render_arena_top)

            for meteor in meteors:
                meteor.draw(screen, render_arena_left, render_arena_top)

            new_damage_texts = []
            for dmg in damage_texts:
                dmg["y"] += dmg["vy"] * sim_dt
                dmg["ttl"] -= sim_dt
                if dmg["ttl"] > 0:
                    draw_text(screen, dmg["text"], int(dmg["x"] + render_arena_left), int(dmg["y"] + render_arena_top), color=dmg["color"], size=22)
                    new_damage_texts.append(dmg)
            damage_texts = new_damage_texts

            human_circles = [c for c in circles if c.character_type not in ("Green Mob", "Giorno Mambo")]
            
            if game_mode == "zombie":
                # Zombie mode UI in white bottom area
                panel_top = arena_top + arena_height + 20
                
                # Draw wave indicator at top of arena
                if wave_complete:
                    draw_text(screen, f"WAVE {current_wave} COMPLETED!", arena_left + arena_width // 2 - 140, arena_top + 40, (255, 255, 255), size=36)
                    countdown = max(0, zombie_spawn_timer)
                    draw_text(screen, f"Next wave in {int(countdown) + 1}s...", arena_left + arena_width // 2 - 100, arena_top + 80, (255, 255, 255), size=28)
                else:
                    draw_text(screen, f"WAVE {current_wave}", arena_left + arena_width // 2 - 60, arena_top + 20, (255, 255, 255), size=32)
                
                bar_x = arena_left + 50
                bar_width = max(300, screen_width - bar_x - 50)
                bar_height = 25
                bar_gap = 72
                
                for idx, circle in enumerate(human_circles):
                    y = panel_top + idx * bar_gap
                    health_ratio = 0.0 if circle.max_health <= 0 else max(0.0, min(1.0, circle.health / circle.max_health))
                    
                    # Draw health bar background (dark for contrast on white)
                    pygame.draw.rect(screen, (40, 40, 40), (bar_x, y, bar_width, bar_height), border_radius=6)
                    # Draw health bar fill
                    pygame.draw.rect(screen, circle.color, (bar_x, y, int(bar_width * health_ratio), bar_height), border_radius=6)
                    # Draw health bar border
                    pygame.draw.rect(screen, (0, 0, 0), (bar_x, y, bar_width, bar_height), 2, border_radius=6)
                    
                    # Player name and health text
                    draw_text(screen, circle.name, bar_x - 10, y - 25, color=(255, 255, 255), size=22)
                    draw_text(screen, f"HP: {circle.health}/{circle.max_health}", bar_x, y + 3, color=(255, 255, 255), size=16)
                    
                    # Ultimate cooldown text
                    if circle.ultimate_active:
                        if circle.character_type == "Gojo Satoru" and circle.gojo_ultimate_stage == "infinite_void_intro":
                            ult_text = "INFINITE VOID (VOICE)..."
                            ult_color = (0, 100, 200)
                        else:
                            ult_text = "ULTIMATE ACTIVE"
                            ult_color = (200, 0, 0)
                    elif circle.character_type == "Gojo Satoru":
                        purple_text = f"HP {min(circle.gojo_attack_count, 2)}/2"
                        gate_wait = max(0.0, 10.0 - battle_time)
                        if gate_wait > 0:
                            ult_text = f"ULT LOCK {gate_wait:.1f}s | {purple_text}"
                            ult_color = (100, 100, 100)
                        elif circle.ultimate_cooldown_timer <= 0:
                            ult_text = f"ULTIMATE READY | {purple_text}"
                            ult_color = (0, 150, 0)
                        else:
                            ult_text = f"ULT {circle.ultimate_cooldown_timer:.1f}s | {purple_text}"
                            ult_color = (100, 0, 150)
                    elif circle.character_type == "T1 Faker":
                        if circle.ultimate_active:
                            ult_text = "R: DEMON KING ACTIVE"
                            ult_color = (255, 110, 180)
                        elif circle.faker_ultimate_cooldown_timer <= 0:
                            ult_text = "R READY"
                            ult_color = (255, 120, 200)
                        else:
                            ult_text = f"R {circle.faker_ultimate_cooldown_timer:.1f}s"
                            ult_color = (180, 90, 170)
                    elif circle.ultimate_cooldown_timer <= 0:
                        ult_text = "ULTIMATE READY"
                        ult_color = (0, 150, 0)
                    else:
                        ult_text = f"ULTIMATE COOLDOWN: {circle.ultimate_cooldown_timer:.1f}s"
                        ult_color = (100, 0, 0)
                    
                    draw_text(screen, ult_text, bar_x, y + 30, color=ult_color, size=16)
                    if circle.character_type == "T1 Faker":
                        q_text = "Q READY" if circle.faker_skill_cooldown_timer <= 0 else f"Q {circle.faker_skill_cooldown_timer:.1f}s"
                        e_text = "E READY" if circle.ultimate_cooldown_timer <= 0 else f"E {circle.ultimate_cooldown_timer:.1f}s"
                        r_text = "R READY" if circle.faker_ultimate_cooldown_timer <= 0 else f"R {circle.faker_ultimate_cooldown_timer:.1f}s"
                        e_color = (120, 220, 255) if circle.ultimate_cooldown_timer <= 0 else (140, 160, 190)
                        r_color = (255, 120, 200) if circle.faker_ultimate_cooldown_timer <= 0 else (185, 120, 175)
                        q_color = (255, 225, 120) if circle.faker_skill_cooldown_timer <= 0 else (180, 165, 120)
                        draw_text(screen, q_text, bar_x, y + 50, color=q_color, size=15)
                        draw_text(screen, e_text, bar_x + 100, y + 50, color=e_color, size=15)
                        draw_text(screen, r_text, bar_x + 220, y + 50, color=r_color, size=15)
                    
                    # Ultimate ready indicator
                    if circle.character_type == "T1 Faker":
                        ult_ready = circle.faker_ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    else:
                        ult_ready = circle.ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    if circle.character_type == "Gojo Satoru":
                        ult_ready = ult_ready and battle_time >= 10.0
                    ready_color = (0, 200, 0) if ult_ready else (150, 150, 150)
                    pygame.draw.circle(screen, ready_color, (bar_x - 30, y + bar_height // 2), 10)
                pygame.draw.circle(screen, (255, 255, 255), (bar_x - 30, y + bar_height // 2), 10, 2)

                # Players alive counter (only human players, not zombies)
                alive_count = sum(1 for c in circles if c.health > 0 and c.character_type not in ("Zombie", "Green Mob"))
                draw_text(screen, f"Survivors: {alive_count}", arena_left + 24, panel_top + len(human_circles) * bar_gap + 20, (255, 255, 255), size=24)

            if game_mode == "zombie":
                # Check win condition: game ends when all human players are dead
                human_alive_count = sum(1 for c in circles if c.health > 0 and c.character_type not in ("Zombie", "Green Mob"))
                if human_alive_count <= 0:
                    show_result_screen()
            else:
                # Regular mode UI
                panel_top = arena_top + arena_height + 12
                bar_x = arena_left + 170
                bar_width = max(220, screen_width - bar_x - 30)
                bar_height = 20
                bar_gap = 68
                bar_targets = circles
                for idx, circle in enumerate(bar_targets):
                    y = panel_top + idx * bar_gap
                    health_ratio = 0.0 if circle.max_health <= 0 else max(0.0, min(1.0, circle.health / circle.max_health))
                    pygame.draw.rect(screen, (55, 55, 65), (bar_x, y, bar_width, bar_height), border_radius=8)
                    pygame.draw.rect(screen, circle.color, (bar_x, y, int(bar_width * health_ratio), bar_height), border_radius=8)
                    pygame.draw.rect(screen, (220, 220, 230), (bar_x, y, bar_width, bar_height), 2, border_radius=8)
                    draw_text(screen, circle.name, arena_left + 24, y - 1, color=(230, 230, 235), size=20)
                    draw_text(screen, f"{circle.health}/{circle.max_health}", bar_x + bar_width - 92, y - 1, color=(245, 245, 250), size=18)
                    if circle.ultimate_active:
                        if circle.character_type == "Gojo Satoru" and circle.gojo_ultimate_stage == "infinite_void_intro":
                            ult_text = "INFINITE VOID (VOICE)..."
                            ult_color = (180, 210, 255)
                        else:
                            ult_text = "ULT ACTIVE"
                            ult_color = (255, 140, 120)
                    elif circle.character_type == "Gojo Satoru":
                        purple_text = f"HP {min(circle.gojo_attack_count, 2)}/2"
                        gate_wait = max(0.0, 10.0 - battle_time)
                        if gate_wait > 0:
                            ult_text = f"ULT LOCK {gate_wait:.1f}s | {purple_text}"
                            ult_color = (160, 160, 190)
                        elif circle.ultimate_cooldown_timer <= 0:
                            ult_text = f"ULT READY | {purple_text}"
                            ult_color = (255, 220, 70)
                        else:
                            ult_text = f"ULT {circle.ultimate_cooldown_timer:.1f}s | {purple_text}"
                            ult_color = (205, 185, 255)
                    elif circle.character_type == "T1 Faker":
                        if circle.ultimate_active:
                            ult_text = "R: DEMON KING ACTIVE"
                            ult_color = (255, 120, 190)
                        elif circle.faker_ultimate_cooldown_timer <= 0:
                            ult_text = "R READY"
                            ult_color = (255, 140, 210)
                        else:
                            ult_text = f"R {circle.faker_ultimate_cooldown_timer:.1f}s"
                            ult_color = (215, 150, 205)
                    elif circle.ultimate_cooldown_timer <= 0:
                        ult_text = "ULT READY"
                        ult_color = (255, 220, 70)
                    else:
                        ult_text = f"ULT {circle.ultimate_cooldown_timer:.1f}s"
                        ult_color = (200, 220, 255)
                    draw_text(screen, ult_text, arena_left + 24, y + 20, color=ult_color, size=18)
                    if circle.character_type == "T1 Faker":
                        q_text = "Q READY" if circle.faker_skill_cooldown_timer <= 0 else f"Q {circle.faker_skill_cooldown_timer:.1f}s"
                        e_text = "E READY" if circle.ultimate_cooldown_timer <= 0 else f"E {circle.ultimate_cooldown_timer:.1f}s"
                        r_text = "R READY" if circle.faker_ultimate_cooldown_timer <= 0 else f"R {circle.faker_ultimate_cooldown_timer:.1f}s"
                        e_color = (120, 220, 255) if circle.ultimate_cooldown_timer <= 0 else (160, 180, 210)
                        r_color = (255, 140, 210) if circle.faker_ultimate_cooldown_timer <= 0 else (215, 160, 205)
                        q_color = (255, 220, 90) if circle.faker_skill_cooldown_timer <= 0 else (190, 175, 130)
                        draw_text(screen, q_text, arena_left + 24, y + 42, color=q_color, size=16)
                        draw_text(screen, e_text, arena_left + 122, y + 42, color=e_color, size=16)
                        draw_text(screen, r_text, arena_left + 220, y + 42, color=r_color, size=16)
                    if circle.character_type == "T1 Faker":
                        ult_ready = circle.faker_ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    else:
                        ult_ready = circle.ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    if circle.character_type == "Gojo Satoru":
                        ult_ready = ult_ready and battle_time >= 10.0
                    ready_sign_color = (255, 220, 70) if ult_ready else (110, 110, 120)
                    pygame.draw.circle(screen, ready_sign_color, (arena_left + 148, y + 9), 8)

                alive_count = sum(1 for c in circles if c.health > 0)
                draw_text(screen, f"Players alive: {alive_count}", arena_left + 24, panel_top + len(bar_targets) * bar_gap + 8, (220, 220, 220), size=20)

                # Regular mode win condition
                alive_count = sum(1 for c in circles if c.health > 0)
                if alive_count <= 1:
                    show_result_screen()
        elif menu_state == "pause":
            screen.fill((20, 20, 30))
            border_rect = pygame.Rect(arena_left, arena_top, arena_width, arena_height)
            pygame.draw.rect(screen, (200, 200, 200), border_rect, 3)

            pause_rect = pygame.Rect(arena_left + arena_width // 2 - 180, arena_top + arena_height // 2 - 120, 360, 240)
            pygame.draw.rect(screen, (40, 45, 70), pause_rect, border_radius=18)
            pygame.draw.rect(screen, (120, 160, 230), pause_rect, 3, border_radius=18)
            draw_text(screen, "RUN MENU", pause_rect.x + 102, pause_rect.y + 18, (255, 255, 255), size=34)

            pause_buttons = [
                (pygame.Rect(pause_rect.x + 40, pause_rect.y + 60, pause_rect.width - 80, 42), "Continue", (70, 130, 220)),
                (pygame.Rect(pause_rect.x + 40, pause_rect.y + 112, pause_rect.width - 80, 42), "Save Progress", (90, 170, 110)),
                (pygame.Rect(pause_rect.x + 40, pause_rect.y + 164, pause_rect.width - 80, 42), "Delete Run", (190, 90, 90)),
            ]
            for rect, label, fill in pause_buttons:
                draw_button(screen, rect, label, fill_color=fill)
        elif menu_state == "result":
            screen.fill((20, 20, 30))
            border_rect = pygame.Rect(arena_left, arena_top, arena_width, arena_height)
            pygame.draw.rect(screen, (200, 200, 200), border_rect, 3)

            result_title = result_winner_name if result_winner_name == "GAME OVER" else f"{result_winner_name} wins"
            win_surface = get_font(38).render(result_title, True, (255, 220, 70))
            win_rect = win_surface.get_rect(center=(arena_left + arena_width // 2, arena_top + 36))
            screen.blit(win_surface, win_rect)

            for circle in circles:
                current_image = circle.image
                if circle.character_type == "Misono Mika" and circle.ultimate_active and match_assets["mika_body_image"]:
                    current_image = match_assets["mika_body_image"]
                elif circle.character_type == "Do Mixi" and circle.ultimate_active and circle.ultimate_image:
                    current_image = circle.ultimate_image

                if current_image:
                    image_rect = current_image.get_rect(center=(int(circle.x + arena_left), int(circle.y + arena_top)))
                    screen.blit(current_image, image_rect)
                else:
                    pygame.draw.circle(screen, circle.color, (int(circle.x + arena_left), int(circle.y + arena_top)), circle.radius)

            if result_special_click_needed:
                prompt_surface = get_font(24).render("Click once to continue", True, (255, 245, 180))
                prompt_rect = prompt_surface.get_rect(center=(arena_left + arena_width // 2, arena_top + arena_height - 20))
                screen.blit(prompt_surface, prompt_rect)
            elif result_show_options:
                draw_button(screen, result_button_rects[0], "Home", fill_color=(190, 150, 60))
                draw_button(screen, result_button_rects[1], "Rematch", fill_color=(70, 130, 220))
                draw_text(screen, "Return to Home Screen", result_button_rects[0].x - 8, result_button_rects[0].bottom + 12, (230, 230, 235), size=20)
                draw_text(screen, "Rematch", result_button_rects[1].x + 48, result_button_rects[1].bottom + 12, (230, 230, 235), size=20)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    simulate()
