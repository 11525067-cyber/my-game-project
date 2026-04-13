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
        self.team_id = None
        self.damage_taken_multiplier = 1.0
        self.attack_speed_multiplier = 1.0
        self.stun_timer = 0.0
        self.martian_citizenship_timer = 0.0
        self.epstein_mark_timer = 0.0
        self.epstein_mark_owner_index = -1
        self.epstein_corruption_timer = 0.0
        self.epstein_corruption_type = None
        self.epstein_shadowstep_cooldown = 0.0
        self.epstein_blackmail_cooldown = 0.0
        self.epstein_network_cooldown = 0.0
        self.epstein_passive_timer = 0.0
        self.epstein_phase_two = False
        self.epstein_untargetable = False
        self.epstein_minor_attack_timer = 0.0
        self.epstein_ultimate_stage = None
        self.epstein_voice_intro_timer = 0.0
        self.epstein_banner_timer = 0.0
        self.epstein_titan_owner_index = -1
        self.titan_evolution_timer = 0.0
        self.titan_evolved = False
        self.titan_resistances = {"normal": 1.0, "skill": 1.0}
        self.titan_slam_timer = 0.0
        self.titan_aura_timer = 0.0
        self.titan_beam_timer = 0.0
        # Elon Musk attributes
        self.elon_skill_state = None  # Tracks current skill state (e.g., rocket punch flying)
        self.elon_rocket_punch_timer = 0.0
        self.elon_rocket_punch_cooldown = 0.0
        self.elon_cybertruck_active = False
        self.elon_cybertruck_timer = 0.0
        self.elon_cybertruck_cooldown = 0.0
        self.elon_ultimate_active = False
        self.elon_ultimate_timer = 0.0
        self.elon_ultimate_cooldown = 0.0
        self.elon_passive_stun_timer = 0.0
        self.elon_aura_color = (255, 255, 100)  # Yellow aura
        self.elon_normal_attack_speed = 0.8  # Attack speed for Dogecoin Toss
        self.elon_base_attack_speed = 1.0  # Base attack speed for reference

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
        wall_bounces_remaining=0,
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
        self.wall_bounces_remaining = wall_bounces_remaining
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
        self.gojo_blue_converted = False
        self.gojo_blue_border_color = (120, 220, 255)

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
        if bounced and self.wall_bounces_remaining > 0:
            self.wall_bounces_remaining -= 1
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
        if self.source in ("zomboss_pea", "zomboss_turret_pea", "zomboss_charged_pea"):
            glow_scale = 2.9 if self.source == "zomboss_charged_pea" else 2.1
            glow_surface = pygame.Surface((display_size * 8, display_size * 8), pygame.SRCALPHA)
            center = glow_surface.get_width() // 2
            outer_color = (125, 255, 150, 65) if self.source != "zomboss_charged_pea" else (255, 160, 110, 78)
            inner_color = (220, 255, 220, 135) if self.source != "zomboss_charged_pea" else (255, 235, 165, 145)
            pygame.draw.circle(glow_surface, outer_color, (center, center), max(8, int(display_size * glow_scale)))
            pygame.draw.circle(glow_surface, inner_color, (center, center), max(5, int(display_size * (glow_scale * 0.55))))
            surface.blit(glow_surface, glow_surface.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y))))
        if self.image:
            draw_image = self.image
            if display_size != self.size:
                draw_image = pygame.transform.smoothscale(draw_image, (display_size * 2, display_size * 2))
            draw_vx = self.pending_vx if self.hold_timer > 0 else self.vx
            draw_vy = self.pending_vy if self.hold_timer > 0 else self.vy
            angle = math.degrees(math.atan2(draw_vy, draw_vx))
            # Falcon 9 and SpaceX rocket sprites are authored nose-up, so use a nose-up offset.
            if self.source in ("elon_rocket_punch", "elon_mars_ultimate"):
                rotation = -angle - 90
            else:
                rotation = -angle
            rotated = pygame.transform.rotate(draw_image, rotation)
            image_rect = rotated.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y)))
            surface.blit(rotated, image_rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x + offset_x), int(self.y + offset_y)), display_size)
        if self.gojo_blue_converted:
            pygame.draw.circle(
                surface,
                self.gojo_blue_border_color,
                (int(self.x + offset_x), int(self.y + offset_y)),
                max(display_size + 3, int(display_size * 1.28)),
                max(2, int(display_size * 0.28)),
            )


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


def draw_soft_glow(surface, center_x, center_y, outer_radius, colors):
    glow_size = max(8, int(outer_radius * 4))
    glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    glow_center = glow_size // 2
    for radius, color, width in colors:
        pygame.draw.circle(glow_surface, color, (glow_center, glow_center), max(2, int(radius)), width)
    surface.blit(glow_surface, glow_surface.get_rect(center=(int(center_x), int(center_y))))




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


def add_status_text(damage_texts, target_circle, text, color=(255, 210, 120), ttl=0.9):
    offset_x = random.uniform(-target_circle.radius * 0.45, target_circle.radius * 0.45)
    offset_y = random.uniform(-target_circle.radius * 0.5, target_circle.radius * 0.15)
    damage_texts.append(
        {
            "x": target_circle.x + offset_x,
            "y": target_circle.y + offset_y,
            "vy": -28.0,
            "ttl": ttl,
            "text": text,
            "color": color,
        }
    )


def apply_damage_to_circle(damage_texts, circle, damage, is_crit):
    if getattr(circle, "faker_invulnerable_timer", 0.0) > 0:
        return 0.0
    if circle.character_type == "T1 Faker" and getattr(circle, "faker_skill_state", None) is not None:
        return 0.0
    if circle.character_type == "Epstein" and getattr(circle, "epstein_untargetable", False):
        return 0.0
    final_damage = damage
    final_damage *= getattr(circle, "damage_taken_multiplier", 1.0)
    if getattr(circle, "martian_citizenship_timer", 0.0) > 0:
        final_damage *= 0.85
    if circle.character_type == "Gojo Satoru" and circle.ultimate_active:
        final_damage *= 0.5
    if circle.character_type == "T1 Faker" and circle.ultimate_active:
        final_damage *= 0.45
    final_damage = max(0.0, final_damage)
    if circle.character_type == "Dummy Diddy":
        circle.dummy_damage_taken_total = getattr(circle, "dummy_damage_taken_total", 0.0) + final_damage
        shown_damage = max(1, int(round(final_damage))) if final_damage > 0 else 0
        if shown_damage > 0:
            add_damage_text(damage_texts, circle, shown_damage, is_crit)
        return final_damage
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
        if circle.character_type == "Dummy Diddy":
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


def is_epstein_unit(circle):
    return circle is not None and circle.character_type in ("Epstein", "Epstein Thrall", "Golden Titan")


def is_epstein_summon(circle):
    return circle is not None and circle.character_type in ("Epstein Thrall", "Golden Titan")


def apply_epstein_mark(owner_index, target_circle, duration=4.0):
    if target_circle is None:
        return
    target_circle.epstein_mark_timer = max(getattr(target_circle, "epstein_mark_timer", 0.0), duration)
    target_circle.epstein_mark_owner_index = owner_index


def consume_epstein_mark_bonus(owner_circle, target_circle, damage, bonus_damage=22.0):
    if owner_circle is None or target_circle is None:
        return damage
    if not circles_are_hostile(owner_circle, target_circle):
        return damage
    if getattr(target_circle, "epstein_mark_timer", 0.0) <= 0:
        return damage
    target_circle.epstein_mark_timer = 0.0
    target_circle.epstein_mark_owner_index = -1
    return damage + bonus_damage


def apply_titan_adaptive_resistance(target_circle, damage, attack_type):
    if target_circle is None or target_circle.character_type != "Golden Titan":
        return damage
    key = attack_type if attack_type in ("normal", "skill") else "skill"
    resistance = target_circle.titan_resistances.get(key, 1.0)
    adjusted_damage = damage * resistance
    target_circle.titan_resistances[key] = max(0.3, resistance * 0.88)
    return adjusted_damage


def make_tinted_glow_image(image, color):
    if image is None:
        return None
    tinted = image.copy()
    tinted.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    tinted.fill((*color, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


def add_gojo_technique_explosion(explosions, x, y, base_radius, colors):
    if isinstance(colors, dict):
        color_set = colors
    else:
        palette = list(colors) if colors else [(255, 255, 255)]
        color_set = {
            "particle": palette,
            "ring": palette[0],
            "core": palette[min(1, len(palette) - 1)],
            "core_highlight": palette[min(2, len(palette) - 1)],
        }
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
                "color": random.choice(color_set["particle"]),
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
            "ring_color": color_set["ring"],
            "core_color": color_set["core"],
            "core_highlight_color": color_set["core_highlight"],
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
    pygame.draw.rect(surface, (30, 30, 40), rect, border_radius=0)
    pygame.draw.rect(surface, fill_color, rect, 3, border_radius=0)
    text_surface = get_font(32).render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_media_toggle_button(surface, rect, is_paused):
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    top_color = (170, 220, 255) if is_paused else (145, 205, 255)
    bottom_color = (42, 138, 230) if is_paused else (30, 118, 212)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * t),
            255,
        )
        pygame.draw.line(button_surface, color, (0, y), (rect.width, y))

    gloss_rect = pygame.Rect(6, 6, rect.width - 12, max(12, rect.height // 3))
    pygame.draw.rect(button_surface, (255, 255, 255, 42), gloss_rect, border_radius=16)
    pygame.draw.rect(button_surface, (18, 40, 76), button_surface.get_rect(), 3, border_radius=18)
    pygame.draw.rect(button_surface, (235, 248, 255), button_surface.get_rect().inflate(-8, -8), 2, border_radius=16)

    icon_color = (8, 16, 28)
    if is_paused:
        triangle_left = rect.width * 0.34
        triangle_width = rect.width * 0.18
        triangle_height = rect.height * 0.34
        center_y = rect.height / 2
        points = [
            (triangle_left, center_y - triangle_height / 2),
            (triangle_left, center_y + triangle_height / 2),
            (triangle_left + triangle_width, center_y),
        ]
        pygame.draw.polygon(button_surface, icon_color, [(int(x), int(y)) for x, y in points])
    else:
        bar_height = rect.height * 0.38
        bar_width = max(10, int(rect.width * 0.08))
        gap = max(12, int(rect.width * 0.07))
        left_x = int(rect.width / 2 - gap / 2 - bar_width)
        top_y = int(rect.height / 2 - bar_height / 2)
        pygame.draw.rect(button_surface, icon_color, (left_x, top_y, bar_width, int(bar_height)), border_radius=3)
        pygame.draw.rect(button_surface, icon_color, (left_x + bar_width + gap, top_y, bar_width, int(bar_height)), border_radius=3)

    surface.blit(button_surface, rect.topleft)


def draw_lock_icon(surface, center_x, center_y, color=(220, 240, 220)):
    shackle_rect = pygame.Rect(0, 0, 20, 16)
    shackle_rect.center = (int(center_x), int(center_y - 8))
    pygame.draw.arc(surface, color, shackle_rect, math.pi, math.tau, 3)
    body_rect = pygame.Rect(0, 0, 18, 16)
    body_rect.center = (int(center_x), int(center_y + 6))
    pygame.draw.rect(surface, color, body_rect, border_radius=4)


def load_optional_sound(base_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ("", ".ogg", ".wav", ".mp3", ".m4a"):
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
    return circle.controller == "zombie" or circle.character_type in ("Green Mob", "Giorno Mambo", "Mambo Mario", "Mambo Zomboss")


def is_mambo_enemy(circle):
    return circle.character_type in ("Green Mob", "Giorno Mambo", "Mambo Mario", "Mambo Zomboss")


def circles_are_hostile(source_circle, target_circle):
    if source_circle is None or target_circle is None or source_circle is target_circle:
        return False
    source_team = getattr(source_circle, "team_id", None)
    target_team = getattr(target_circle, "team_id", None)
    if source_team is not None and source_team == target_team:
        return False
    source_is_zombie = is_zombie_side(source_circle)
    target_is_zombie = is_zombie_side(target_circle)
    if source_is_zombie or target_is_zombie:
        return source_is_zombie != target_is_zombie
    return True


def get_hostile_opponents(source_circle, circles):
    hostiles = [
        other
        for other in circles
        if other.health > 0 and circles_are_hostile(source_circle, other)
    ]
    if is_player_controlled_human(source_circle):
        zomboss_targets = [other for other in hostiles if other.character_type == "Mambo Zomboss"]
        if zomboss_targets:
            return zomboss_targets
    return hostiles


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


def apply_gojo_infinity_slow(gojo_circle, obj, velocity_attr_names, radius, slowdown_factor=3.0):
    if gojo_circle is None or obj is None or slowdown_factor <= 1.0:
        return False
    dx = gojo_circle.x - obj.x
    dy = gojo_circle.y - obj.y
    distance = math.hypot(dx, dy)
    if distance <= 0 or distance > radius:
        return False

    vx_name, vy_name = velocity_attr_names
    vx = getattr(obj, vx_name, 0.0)
    vy = getattr(obj, vy_name, 0.0)
    inward_speed = ((vx * dx) + (vy * dy)) / distance
    if inward_speed <= 0:
        return False

    reduction_scale = 1.0 - (1.0 / slowdown_factor)
    slow_x = (dx / distance) * inward_speed * reduction_scale
    slow_y = (dy / distance) * inward_speed * reduction_scale
    setattr(obj, vx_name, vx - slow_x)
    setattr(obj, vy_name, vy - slow_y)
    return True


def bullet_ignores_gojo_infinity(bullet, gojo_index):
    if bullet is None:
        return True
    if bullet.source in ("gojo_red", "gojo_purple"):
        return True
    if bullet.source == "gojo_blue" and bullet.owner_index == gojo_index and bullet.hold_timer > 0:
        return True
    return False


def convert_bullet_to_gojo_owner(bullet, gojo_index):
    if bullet is None or bullet.source == "gojo_blue":
        return False
    if bullet.owner_index == gojo_index and bullet.gojo_blue_converted:
        return False
    bullet.owner_index = gojo_index
    bullet.gojo_blue_converted = True
    bullet.gojo_blue_border_color = (120, 220, 255)
    return True


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
    global cap
    print("GAME STARTED!")  # Debug output
    _game_dir = os.path.dirname(os.path.abspath(__file__))
    pygame.init()
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        pygame.mixer.set_num_channels(max(8, pygame.mixer.get_num_channels()))
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
    padding = 200
    original_window_width = window_width
    window_width += 2 * padding
    screen_width = window_width
    screen_height = window_height
    arena_width = base_square_size
    arena_height = base_square_size
    arena_left = padding + (original_window_width - square_size) // 2
    arena_top = arena_margin
    tube_top_height = 0
    zombie_spawn_timer = 0.0
    zomboss_wave_summons_spawned = 0
    window_size = window_width
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Two Circle Health Simulation")
    fullscreen = False
    game_surface = pygame.Surface((window_width, window_height))
    draw_surface = game_surface
    clock = pygame.time.Clock()
    # Full-window domain background (video file in game folder, same dir as game.py)
    infinite_void_video = load_video_background("infinte void domain image.mp4", original_window_width, window_height)

    def load_image(path):
        full = path if os.path.isabs(path) else os.path.join(_game_dir, path)
        try:
            return pygame.image.load(full).convert_alpha()
        except pygame.error:
            print(f"Warning: {full} not found.")
            return None

    # Load mode selection images
    mode_images = {
        "title": load_image("Games Modes Lilith.png"),
        "character_info": load_image("character info.png"),
        "2p_simulation": load_image("2p simulation.png"),
        "vs_bot": load_image("Vs Bot.png"),
        "vs_player": load_image("vs player.png"),
        "custom_simulation": load_image("Custom simulation.png"),
        "mambo_apocalypse": load_image("mambo apocalypse.png"),
        "dummy_testing": load_image("dummy testing.png"),
    }

    def scale_to_fit(image, width, height):
        if image is None:
            return None
        orig_width, orig_height = image.get_size()
        scale = min(width / orig_width, height / orig_height)
        if scale == 1.0:
            return image
        return pygame.transform.smoothscale(image, (max(1, int(orig_width * scale)), max(1, int(orig_height * scale))))

    def scale_to_height(image, height):
        if image is None:
            return None
        orig_width, orig_height = image.get_size()
        if orig_height <= 0:
            return image
        scale = height / orig_height
        if scale == 1.0:
            return image
        return pygame.transform.smoothscale(
            image,
            (max(1, int(orig_width * scale)), max(1, int(orig_height * scale))),
        )

    def render_mode_tile(image, width, height):
        if image is None or width <= 0 or height <= 0:
            return None
        return scale_to_fit(image, width, height)

    def render_mode_tile_to_visible_box(image, visible_width, visible_height):
        if image is None or visible_width <= 0 or visible_height <= 0:
            return None
        visible_bounds = image.get_bounding_rect(min_alpha=1)
        if visible_bounds.width <= 0 or visible_bounds.height <= 0:
            scaled = scale_to_fit(image, visible_width, visible_height)
            if scaled is None:
                return None
            return scaled, scaled.get_rect()
        scale = min(visible_width / visible_bounds.width, visible_height / visible_bounds.height)
        scaled_width = max(1, int(round(image.get_width() * scale)))
        scaled_height = max(1, int(round(image.get_height() * scale)))
        scaled = pygame.transform.smoothscale(image, (scaled_width, scaled_height))
        scaled_bounds = pygame.Rect(
            int(round(visible_bounds.x * scale)),
            int(round(visible_bounds.y * scale)),
            max(1, int(round(visible_bounds.width * scale))),
            max(1, int(round(visible_bounds.height * scale))),
        )
        draw_rect = scaled.get_rect()
        draw_rect.x = (visible_width - scaled_bounds.width) // 2 - scaled_bounds.x
        draw_rect.y = (visible_height - scaled_bounds.height) // 2 - scaled_bounds.y
        return scaled, draw_rect

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
    arona_and_plana_original = load_image("arona and plana.png")
    do_mixi_win_loser_original = load_image("meo cam kho ga.png")
    mika_ultimate_xd_original = load_image("mika ultimate XD.png")
    mambo_original = load_image("mambo face.png")
    giorno_mambo_original = load_image("giorno mambo.png")
    mambo_mario_original = load_image("mambo mario.png")
    mambo_zomboss_original = load_image("mambo zomboss.png")
    epstein_original = load_image("epstein.png")
    titan_trump_original = load_image("mahora trump.png")
    lucky_box_mambo_mario_original = load_image("lucky box mario mambo.png")
    fire_flower_mambo_mario_original = load_image("fire flower mambo mario.png")
    fireball_mambo_mario_original = load_image("fireball mambo mario.png")
    faker_original = load_image("T1 Faker.png")
    faker_normal_attack_original = load_image("Faker normal attack.png")
    faker_call_original = load_image("faker call.png")
    dummy_diddy_original = load_image("dummy diddy.png")
    epstein_normal_attack_original = load_image("judaism normal attack.png")
    epstein_normal_attack_blue_original = make_tinted_glow_image(epstein_normal_attack_original, (90, 210, 255))
    epstein_classroom_original = load_image("epstein classroom.png")
    elon_musk_original = load_image("elon musk.png")
    dogecoin_original = load_image("doge coin elon musk.png")
    falcon_9_original = load_image("falcon 9.png")
    cybertruck_original = load_image("tesla cybertruck.png")
    space_x_rocket_original = load_image("space x rocket.png")
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
    mambo_mario_image = scale_to_fit(mambo_mario_original, int(radius * 2 * 3.6), int(radius * 2 * 2.5))
    mambo_zomboss_image = scale_to_fit(mambo_zomboss_original, int(radius * 2 * 4.5), int(radius * 2 * 4.5))
    lucky_box_mambo_mario_image = scale_to_fit(lucky_box_mambo_mario_original, int(radius * 2.1), int(radius * 2.1))
    fire_flower_mambo_mario_image = scale_to_fit(fire_flower_mambo_mario_original, int(radius * 1.8), int(radius * 1.8))
    fireball_mambo_mario_image = scale_to_fit(fireball_mambo_mario_original, int(radius * 1.2), int(radius * 1.2))
    green_shell_mambo_mario_original = load_image("green shell mambo mario.png")
    green_shell_mambo_mario_image = scale_to_fit(green_shell_mambo_mario_original, int(radius * 1.2), int(radius * 1.2))
    faker_image = scale_to_fit(faker_original, int(radius * 2.2 * 1.3), int(radius * 2.2 * 1.3))
    epstein_height = faker_image.get_height() if faker_image else int(radius * 2.2 * 1.3)
    epstein_image = scale_to_height(epstein_original, epstein_height)
    titan_trump_image = scale_to_height(titan_trump_original, epstein_height * 2)
    faker_normal_attack_image = scale_to_fit(faker_normal_attack_original, int(radius * 1.2), int(radius * 1.2))
    faker_call_image = scale_to_fit(faker_call_original, int(radius * 1.15), int(radius * 1.15))
    epstein_normal_attack_image = scale_to_fit(epstein_normal_attack_blue_original, int(radius * 1.35), int(radius * 1.35))
    mika_gun_image = scale_to_fit(mika_ue_original, int(radius * 2.2), radius * 2)
    
    # Elon Musk character scaling
    elon_musk_height = max(1, int(epstein_height * 1.2))
    elon_musk_image = scale_to_height(elon_musk_original, elon_musk_height)
    elon_display_height = elon_musk_image.get_height() if elon_musk_image else elon_musk_height
    
    dogecoin_size = max(1, int(elon_display_height * 0.5))
    dogecoin_image = scale_to_fit(dogecoin_original, dogecoin_size, dogecoin_size)
    
    falcon_9_size = max(1, int(elon_display_height * 3.0))
    falcon_9_image = scale_to_height(falcon_9_original, falcon_9_size)
    
    cybertruck_size = max(1, int(elon_display_height))
    cybertruck_image = scale_to_height(cybertruck_original, cybertruck_size)
    
    space_x_rocket_size = max(1, int(elon_display_height * 8.0))
    space_x_rocket_image = scale_to_height(space_x_rocket_original, space_x_rocket_size)
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
    epstein_summon_sound = amplify_sound(load_optional_sound("with this treasure i summon"), 2.0)
    epstein_jumpscare_sound = amplify_sound(load_optional_sound("epstein jumpscare"), 1.5)
    trump_jumpscare_original = load_image("trump jumpscare.png")
    hachimi_sound = load_optional_sound("hachimi")
    hachimi_on_your_lawn_sound = load_optional_sound("hachimi on your lawn")
    hachimi_high_on_life_sound = load_optional_sound("hachimi high on life")
    mambo_high_onlife_sound = load_optional_sound("mambo high onlife") or load_optional_sound("mambo high on life")
    golden_wind_mambo_sound = load_optional_sound("golden wind mambo")
    mambo_mario_sound = load_optional_sound("mambo mario audio")
    faker_call_sound = load_optional_sound("faker call audio")
    elon_skill_voice_sounds = [
        snd
        for snd in (
            load_optional_sound("this is elon musk"),
            load_optional_sound("yi long ma"),
        )
        if snd is not None
    ]
    elon_win_sound = load_optional_sound("this is elon musk win")
    epstein_win_sound = load_optional_sound("charlie kirk funk")

    # Background music
    maid_arisu_theme_file = "Maid Arisu theme.mp3"
    home_music_files = [
        "Hifumi Daisuki.mp3",
        "Jumping thoughts NEoYaM.mp3",
        "Koukatsu.mp3",
        "Uminaoshi.mp3",
        "New Darling.mp3"
    ]
    home_music_track_files = {maid_arisu_theme_file, *home_music_files}
    home_music_volume = 0.25
    home_music_track_volumes = {
        "Jumping thoughts NEoYaM.mp3": min(1.0, home_music_volume * 4.0),
    }
    initial_home_music = ["Maid Arisu theme.mp3", "Hifumi Daisuki.mp3", "Jumping thoughts NEoYaM.mp3"]
    def get_current_home_music_files():
        if has_finished_battle:
            return home_music_files
        else:
            return initial_home_music
    current_home_music_index = 0
    home_music_paused = False

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
    for snd in elon_skill_voice_sounds:
        snd.set_volume(1.0)
    if elon_win_sound:
        elon_win_sound.set_volume(1.0)
    voice_primary_channel = pygame.mixer.Channel(0) if pygame.mixer.get_init() else None
    voice_secondary_channel = pygame.mixer.Channel(1) if pygame.mixer.get_init() else None
    voice_extra_channels = [pygame.mixer.Channel(idx) for idx in (3, 4)] if pygame.mixer.get_init() else []
    voice_channels = [ch for ch in ([voice_primary_channel, voice_secondary_channel] + voice_extra_channels) if ch is not None]
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
        if mode == "zomboss":
            zomboss_track = mambo_high_onlife_sound or hachimi_high_on_life_sound or hachimi_on_your_lawn_sound or hachimi_sound
            if zomboss_track:
                music_channel.play(zomboss_track)
        elif mode == "boss":
            if mambo_mario_sound:
                music_channel.play(mambo_mario_sound)
        elif mode == "golden":
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

    def play_background_music(file):
        nonlocal home_music_paused
        try:
            pygame.mixer.music.load(os.path.join(_game_dir, file))
            if file in home_music_track_files:
                volume = home_music_track_volumes.get(file, home_music_volume)
            else:
                volume = 1.0
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1 if file in home_music_track_files else pygame.NOEVENT)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            home_music_paused = False
        except pygame.error:
            pass

    def play_next_home_music():
        nonlocal current_home_music_index
        current_files = get_current_home_music_files()
        if current_home_music_index >= len(current_files):
            current_home_music_index = 0
        play_background_music(current_files[current_home_music_index])
        current_home_music_index += 1

    def start_home_music():
        nonlocal current_home_music_index, home_music_paused
        current_home_music_index = 0
        home_music_paused = False
        play_next_home_music()

    def ensure_home_music_running():
        nonlocal home_music_paused
        if not pygame.mixer.get_init():
            return
        try:
            if home_music_paused:
                pygame.mixer.music.unpause()
                pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
                home_music_paused = False
            elif not pygame.mixer.music.get_busy():
                start_home_music()
        except pygame.error:
            start_home_music()

    def toggle_home_music_pause():
        nonlocal home_music_paused
        if not pygame.mixer.get_init():
            return
        try:
            if home_music_paused:
                pygame.mixer.music.unpause()
                pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
                home_music_paused = False
            elif pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                home_music_paused = True
            else:
                start_home_music()
        except pygame.error:
            start_home_music()

    def rebalance_voice_channels():
        active_channels = [ch for ch in voice_channels if ch.get_busy()]
        active_count = len(active_channels)
        if active_count <= 0:
            return
        if active_count == 1:
            volume = 1.0
        elif active_count == 2:
            volume = 0.9
        elif active_count == 3:
            volume = 0.82
        else:
            volume = 0.76
        for channel in voice_channels:
            channel.set_volume(volume if channel in active_channels else 1.0)

    def play_voice_sound(sound, *, preferred="secondary", priority=False, block_if_primary=False):
        if sound is None:
            return
        if not voice_channels:
            sound.play()
            return
        if block_if_primary and voice_primary_channel.get_busy():
            return

        if preferred == "primary":
            preferred_order = [voice_primary_channel, voice_secondary_channel] + voice_extra_channels
        else:
            preferred_order = [voice_secondary_channel] + voice_extra_channels + [voice_primary_channel]

        if priority:
            channel = voice_primary_channel
            channel.stop()
            channel.play(sound)
            rebalance_voice_channels()
            channel.set_volume(1.0)
            return

        channel = next((ch for ch in preferred_order if ch is not None and not ch.get_busy()), None)
        if channel is None:
            channel = next((ch for ch in preferred_order if ch is not None and ch is not voice_primary_channel), voice_primary_channel)
        channel.play(sound)
        rebalance_voice_channels()
    play_background_music(maid_arisu_theme_file)
    menu_state = "mode"
    game_mode = "sim"
    bot_difficulty = "medium"
    epstein_jumpscare_active = False
    epstein_jumpscare_timer = 0.0
    trump_jumpscare_active = False
    trump_jumpscare_timer = 0.0
    hp_multiplier = 1.0
    custom_count_input = ""
    zombie_count_input = ""
    zombie_stage_page = 0
    selected_zombie_stage_wave = 1
    mambo_count_input = ""
    current_wave = 1
    current_wave_elapsed_time = 0.0
    last_cleared_wave_time = None
    mambos_spawned_in_wave = 0
    mambos_to_spawn = 0
    wave_in_progress = False
    wave_complete = False
    has_finished_battle = False

    def is_boss_wave(wave_number):
        return wave_number % 20 == 10

    def is_zomboss_wave(wave_number):
        return wave_number > 0 and wave_number % 20 == 0

    def is_golden_wave(wave_number):
        return wave_number % 10 == 5

    def get_zombie_wave_music_mode(wave_number):
        if is_zomboss_wave(wave_number):
            return "zomboss"
        if is_boss_wave(wave_number):
            return "boss"
        if is_golden_wave(wave_number):
            return "golden"
        return "normal"
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
    zomboss_gadgets = []
    zomboss_warning_zones = []
    zomboss_beams = []
    zomboss_shockwaves = []
    epstein_decoys = []
    epstein_curses = []
    epstein_warning_zones = []
    epstein_beams = []
    epstein_shockwaves = []
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
    mambo_mario_fire_colors = {
        "particle": [
            (255, 150, 70),
            (255, 105, 55),
            (255, 188, 120),
            (255, 226, 170),
        ],
        "ring": (255, 110, 70),
        "core": (255, 168, 90),
        "core_highlight": (255, 238, 190),
    }
    elon_rocket_colors = {
        "particle": [
            (255, 185, 70),
            (255, 135, 55),
            (255, 225, 130),
            (255, 245, 210),
        ],
        "ring": (255, 168, 90),
        "core": (255, 118, 58),
        "core_highlight": (255, 245, 205),
    }
    epstein_shadow_colors = {
        "particle": [
            (40, 40, 48),
            (60, 60, 72),
            (85, 85, 110),
            (140, 110, 170),
        ],
        "ring": (70, 70, 100),
        "core": (30, 30, 44),
        "core_highlight": (180, 125, 220),
    }
    titan_gold_colors = {
        "particle": [
            (255, 195, 70),
            (255, 165, 48),
            (255, 220, 140),
            (255, 245, 205),
        ],
        "ring": (255, 180, 68),
        "core": (230, 130, 40),
        "core_highlight": (255, 245, 210),
    }
    colliding_pairs = set()
    running = True
    elapsed_time = 0.0
    battle_time = 0.0
    result_winner_name = ""
    result_show_options = False
    result_special_click_needed = False
    zombie_save_path = os.path.join(_game_dir, "mambo_apocalypse_save.json")
    zombie_stage_progress_path = os.path.join(_game_dir, "mambo_apocalypse_progress.json")
    pending_zombie_resume_data = None

    # Mode selection layout (match reference image)
    mode_button_names = [
        "character_info",
        "2p_simulation",
        "vs_bot",
        "vs_player",
        "custom_simulation",
        "mambo_apocalypse",
        "dummy_testing",
    ]
    mode_reference_width = 1778
    mode_reference_height = 1006
    mode_margin_left = max(24, int(screen_width * (28 / mode_reference_width)))
    mode_box_shift_x = -48
    mode_title_reference_rect = pygame.Rect(28, 0, 936, 300)
    mode_title_rect = pygame.Rect(
        int(round(mode_title_reference_rect.x / mode_reference_width * screen_width)),
        int(round(mode_title_reference_rect.y / mode_reference_height * screen_height)),
        int(round(mode_title_reference_rect.width / mode_reference_width * screen_width)),
        int(round(mode_title_reference_rect.height / mode_reference_height * screen_height)),
    )
    mode_2p_width = int(round(441 * 1.090909))
    mode_2p_height = int(round(223 * 1.090909))
    mode_reference_rects = {
        "character_info": pygame.Rect(1195 + mode_box_shift_x, 38, 458, 202),
        "2p_simulation": pygame.Rect(875, 260, mode_2p_width, mode_2p_height),
        "vs_bot": pygame.Rect(1371 + mode_box_shift_x, 273, 402, 216),
        "vs_player": pygame.Rect(900 + mode_box_shift_x, 518, 426, 227),
        "custom_simulation": pygame.Rect(1318 + mode_box_shift_x, 516, 444, 236),
        "mambo_apocalypse": pygame.Rect(851 + mode_box_shift_x, 755, 443, 219),
        "dummy_testing": pygame.Rect(1284 + mode_box_shift_x, 753, 428, 223),
    }
    mode_rects = []
    mode_tile_surfaces = {}
    mode_tile_draw_rects = {}
    for idx, mode_name in enumerate(mode_button_names):
        ref_rect = mode_reference_rects[mode_name]
        scaled_rect = pygame.Rect(
            int(round(ref_rect.x / mode_reference_width * screen_width)),
            int(round(ref_rect.y / mode_reference_height * screen_height)),
            int(round(ref_rect.width / mode_reference_width * screen_width)),
            int(round(ref_rect.height / mode_reference_height * screen_height)),
        )
        mode_rects.append(scaled_rect)
        image = mode_images.get(mode_name)
        if image is not None:
            tile_result = render_mode_tile_to_visible_box(image, scaled_rect.width, scaled_rect.height)
            if tile_result is not None:
                tile_surface, tile_offset_rect = tile_result
                mode_tile_surfaces[mode_name] = tile_surface
                mode_tile_draw_rects[mode_name] = tile_offset_rect.move(scaled_rect.topleft)

    mode_title_surface = None
    if mode_images.get("title") is not None:
        mode_title_surface = render_mode_tile(mode_images["title"], mode_title_rect.width, mode_title_rect.height)
    character_info_rect = mode_rects[0] if mode_rects else pygame.Rect(mode_title_rect.right + 40, mode_title_rect.y + 60, 260, 120)
    mode_title_visual_right = mode_title_rect.right + (50 if mode_title_surface is not None else 0)
    music_gap_left = mode_title_visual_right + 18
    music_gap_right = character_info_rect.x - 18
    music_toggle_size = max(68, min(116, character_info_rect.height - 40, max(68, music_gap_right - music_gap_left)))
    music_toggle_rect = pygame.Rect(
        music_gap_left + max(0, (music_gap_right - music_gap_left - music_toggle_size) // 2),
        character_info_rect.y + max(0, (character_info_rect.height - music_toggle_size) // 2),
        music_toggle_size,
        music_toggle_size,
    )
    zombie_count_rect = pygame.Rect(padding + original_window_width // 2 - 180, screen_height // 2 - 30, 360, 70)
    zombie_stage_back_rect = pygame.Rect(padding + original_window_width - 206, 38, 130, 54)
    zombie_stage_right_rect = pygame.Rect(padding + original_window_width - 126, screen_height - 96, 72, 56)
    zombie_stage_left_rect = pygame.Rect(padding + original_window_width - 216, screen_height - 96, 72, 56)
    zombie_stage_resume_rect = pygame.Rect(padding + original_window_width - 470, 38, 240, 54)
    option_rects = [
        pygame.Rect(20, 140, 168, 285),
        pygame.Rect(196, 140, 168, 285),
        pygame.Rect(372, 140, 168, 285),
        pygame.Rect(548, 140, 168, 285),
        pygame.Rect(724, 140, 168, 285),
        pygame.Rect(900, 140, 168, 285),  # Elon Musk
    ]
    hp_minus_rect = pygame.Rect(20, 440, 50, 50)
    hp_plus_rect = pygame.Rect(80, 440, 50, 50)
    difficulty_rects = [
        pygame.Rect(padding + original_window_width // 2 - 380, screen_height // 2 - 75, 170, 150),
        pygame.Rect(padding + original_window_width // 2 - 190, screen_height // 2 - 75, 170, 150),
        pygame.Rect(padding + original_window_width // 2, screen_height // 2 - 75, 170, 150),
        pygame.Rect(padding + original_window_width // 2 + 190, screen_height // 2 - 75, 170, 150),
    ]
    info_card_rects = [
        pygame.Rect(padding + 20, 138, 168, 150),
        pygame.Rect(padding + 196, 138, 168, 150),
        pygame.Rect(padding + 372, 138, 168, 150),
        pygame.Rect(padding + 548, 138, 168, 150),
        pygame.Rect(padding + 724, 138, 168, 150),
    ]
    info_detail_rect = pygame.Rect(padding + 30, 310, original_window_width - 60, screen_height - 340)
    custom_input_rect = pygame.Rect(padding + original_window_width // 2 - 180, screen_height // 2 - 30, 360, 70)
    select_back_rect = pygame.Rect(padding + original_window_width - 220, 30, 180, 54)
    result_button_rects = [
        pygame.Rect(arena_left + arena_width // 2 - 220, arena_top + arena_height // 2 + 120, 200, 72),
        pygame.Rect(arena_left + arena_width // 2 + 20, arena_top + arena_height // 2 + 120, 200, 72),
    ]
    win_button_rect = pygame.Rect(arena_left + arena_width + 20, arena_top + arena_height // 2 - 50, 120, 100)

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
        match_mambo_mario_image = scale_to_fit(mambo_mario_original, int(match_radius * 2 * 3.6), int(match_radius * 2 * 2.5))
        match_mambo_zomboss_image = scale_to_fit(mambo_zomboss_original, int(match_radius * 2 * 4.5), int(match_radius * 2 * 4.5))
        match_lucky_box_mambo_mario_image = scale_to_fit(lucky_box_mambo_mario_original, int(match_radius * 2.1), int(match_radius * 2.1))
        match_fire_flower_mambo_mario_image = scale_to_fit(fire_flower_mambo_mario_original, int(match_radius * 1.8), int(match_radius * 1.8))
        match_fireball_mambo_mario_image = scale_to_fit(fireball_mambo_mario_original, int(match_radius * 1.2), int(match_radius * 1.2))
        match_green_shell_mambo_mario_image = scale_to_fit(green_shell_mambo_mario_original, int(match_radius * 1.2), int(match_radius * 1.2))
        match_mika_gun_image = scale_to_fit(mika_ue_original, int(match_radius * 2.2), match_radius * 2)
        match_mika_meteor_image = scale_to_fit(mika_meteor_original, match_radius, match_radius)
        match_mika_finish_meteor_image = scale_to_fit(mika_meteor_original, match_radius * 4, match_radius * 4)
        match_mika_bullet_image = scale_to_fit(mika_bullet_original, max(20, int(56 * (match_radius / radius))), max(20, int(56 * (match_radius / radius))))
        match_mika_bullet_ultimate_image = scale_to_fit(mika_bullet_original, max(20, int(56 * (match_radius / radius))), max(20, int(56 * (match_radius / radius))))
        match_vu_projectile_image = scale_to_fit(vu_projectile_original, max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))), max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))))
        match_vu_ultimate_projectile_image = scale_to_fit(vu_ultimate_projectile_original, max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))), max(16, int(46 * 1.5 * 1.5 * (match_radius / radius))))
        match_faker_image = scale_to_fit(faker_original, max(1, int(radius * 2.2 * 1.3 * (match_radius / radius))), max(1, int(radius * 2.2 * 1.3 * (match_radius / radius))))
        match_epstein_height = match_faker_image.get_height() if match_faker_image else max(1, int(radius * 2.2 * 1.3 * (match_radius / radius)))
        match_epstein_image = scale_to_height(epstein_original, match_epstein_height)
        match_titan_trump_image = scale_to_height(titan_trump_original, match_epstein_height * 2)
        match_dummy_diddy_image = scale_to_height(dummy_diddy_original, max(1, int(match_epstein_height * 1.05)))
        match_elon_height = max(1, int(match_epstein_height * 1.2))
        match_elon_image = scale_to_height(elon_musk_original, match_elon_height)
        match_elon_display_height = match_elon_image.get_height() if match_elon_image else match_elon_height
        match_dogecoin_size = max(1, int(match_elon_display_height * 0.5))
        match_dogecoin_image = scale_to_fit(dogecoin_original, match_dogecoin_size, match_dogecoin_size)
        match_falcon_9_image = scale_to_height(falcon_9_original, max(1, int(match_elon_display_height * 3.0)))
        match_cybertruck_image = scale_to_height(cybertruck_original, max(1, int(match_elon_display_height)))
        match_space_x_rocket_image = scale_to_height(space_x_rocket_original, max(1, int(match_elon_display_height * 8.0)))
        match_faker_normal_attack_image = scale_to_fit(faker_normal_attack_original, max(18, int(radius * 1.2 * (match_radius / radius))), max(18, int(radius * 1.2 * (match_radius / radius))))
        match_faker_call_image = scale_to_fit(faker_call_original, max(18, int(radius * 1.15 * (match_radius / radius))), max(18, int(radius * 1.15 * (match_radius / radius))))
        match_epstein_normal_attack_image = scale_to_fit(epstein_normal_attack_blue_original, max(20, int(radius * 1.35 * (match_radius / radius))), max(20, int(radius * 1.35 * (match_radius / radius))))
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
            "epstein_image": match_epstein_image,
            "titan_trump_image": match_titan_trump_image,
            "faker_image": match_faker_image,
            "dummy_diddy_image": match_dummy_diddy_image,
            "elon_image": match_elon_image,
            "dogecoin_image": match_dogecoin_image,
            "falcon_9_image": match_falcon_9_image,
            "cybertruck_image": match_cybertruck_image,
            "space_x_rocket_image": match_space_x_rocket_image,
            "gojo_red_projectile_image": match_gojo_red_projectile_image,
            "gojo_blue_projectile_image": match_gojo_blue_projectile_image,
            "gojo_blue_merge_image": match_gojo_blue_merge_image,
            "gojo_hollow_purple_image": scale_to_fit(gojo_purple_original, max(16, int((radius * 1.1 * (match_radius / radius)) / 1.3)), max(16, int((radius * 1.1 * (match_radius / radius)) / 1.3))),
            "do_mixi_win_loser_image": match_do_mixi_win_loser_image,
            "mambo_image": match_mambo_image,
            "giorno_mambo_image": match_giorno_mambo_image,
            "mambo_mario_image": match_mambo_mario_image,
            "mambo_zomboss_image": match_mambo_zomboss_image,
            "lucky_box_mambo_mario_image": match_lucky_box_mambo_mario_image,
            "fire_flower_mambo_mario_image": match_fire_flower_mambo_mario_image,
            "fireball_mambo_mario_image": match_fireball_mambo_mario_image,
            "green_shell_mambo_mario_image": match_green_shell_mambo_mario_image,
            "mika_gun_image": match_mika_gun_image,
            "mika_meteor_image": match_mika_meteor_image,
            "mika_finish_meteor_image": match_mika_finish_meteor_image,
            "mika_bullet_image": match_mika_bullet_image,
            "mika_bullet_ultimate_image": match_mika_bullet_ultimate_image,
            "vu_projectile_image": match_vu_projectile_image,
            "vu_ultimate_projectile_image": match_vu_ultimate_projectile_image,
            "faker_normal_attack_image": match_faker_normal_attack_image,
            "faker_call_image": match_faker_call_image,
            "epstein_normal_attack_image": match_epstein_normal_attack_image,
            "mika_body_image": match_mika_body_image,
            "mika_halo_image": match_mika_halo_image,
        }

    match_assets = build_match_assets(radius)

    def get_character_label(character_id):
        if character_id == "Mika":
            return "Misono Mika"
        if character_id == "Gojo":
            return "Gojo Satoru"
        if character_id == "Epstein":
            return "Epstein"
        if character_id == "Faker":
            return "T1 Faker"
        if character_id == "Elon":
            return "Elon Musk"
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
    character_info_page = 0
    character_info_lines_per_page = 8
    character_info_card_page = 0
    character_info_entries = {
        "Mika": {
            "title": "Misono Mika",
            "subtitle": "Crit-heavy burst carry",
            "overview": [
                "Normal Attack: Fires a 5-shot burst every 1.5s.",
                "Each bullet deals 8 damage, always crits, and heals Mika for 1%",
                "of max HP whenever a crit lands.",
                "Meteor Volley: Every burst also calls 4 meteors for 30 damage each.",
                "Meteors always crit, so each one lands for 60 damage.",
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
                "Gojo can still move while charging Hollow Purple.",
                "Purple deals 300 on contact, 200 on wall explosion, and heals Gojo",
                "for 10% max HP when it connects.",
                "Ultimate - Domain Expansion: 15s cooldown and only unlocks after",
                "10s of battle time. Infinite Void opens a 4s domain state.",
            ],
        },
        "Epstein": {
            "title": "Epstein",
            "subtitle": "Slippery controller and summoner",
            "overview": [
                "Passive - Web of Influence corrupts a random network ally every 4s.",
                "Corrupted units gain either speed, damage, or shielding.",
                "Normal Attack: Shadow Contracts are slow homing dark orbs.",
                "They apply Marked, darkening pressure and empowering the next hit.",
                "Skill 1: Shadowstep teleports to a random edge and leaves a decoy.",
                "The decoy detonates after 1.5s, punishing tunnel vision.",
                "Skill 2: Blackmail Trigger curses a target for 2s, then either",
                "explodes beneath them or spawns a thrall beside them.",
                "Skill 3: Network Surge buffs the whole network and summons thralls.",
                "Below 60% HP he enters phase two and casts much faster.",
                "Ultimate: Summon Mahora J Trump. Epstein becomes untargetable while",
                "Mahora J Trump adapts, slams, beams, and buffs the network.",
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
        "Elon": {
            "title": "Elon Musk",
            "subtitle": "Technoking of Tesla and SpaceX",
            "overview": [
                "Normal Attack: Dogecoin Toss - Hurls glowing Dogecoins in rapid succession.",
                "Each coin deals moderate damage and has a chance to trigger 'To the Moon!'",
                "effect, making enemies bounce uncontrollably. Critical hits occur if the",
                "Doge face lands upright.",
                "Skill 1: Rocket Punch - Summons a mini Falcon 9 rocket that launches",
                "forward and explodes. Deals splash damage, but has a 30% chance to 'fail",
                "landing,' causing random chaos on the battlefield. Cooldown: 6 seconds.",
                "Skill 2: Cybertruck Shield - Deploys a polygonal Cybertruck barrier.",
                "Reflects projectiles but has a 50% chance to shatter dramatically.",
                "The shield is scaled to Elon and his own attacks pass straight through it.",
                "Passive: Neuralink Overclock - Grants increased attack speed and movement",
                "speed. Occasional random self-stun when 'software update' hits mid-battle.",
                "A slight yellow aura appears around Elon during the stun.",
                "Ultimate: Mars Colonization - Summons a giant SpaceX rocket 8x the size",
                "of Elon. Abducts enemies and launches them to Mars, dealing massive AoE",
                "damage. After a delay, drops enemies back to the battlefield, dealing",
                "additional damage and stunning them for 2 seconds. Allies gain 'Martian",
                "Citizenship' buff. Cooldown: Very long (like waiting for actual colonization).",
            ],
        },
        "Mambo": {
            "title": "Mambo Types",
            "subtitle": "Apocalypse enemy guide",
            "overview": [
                "Normal Mambo: Appears on non-special waves and caps at 10 per wave.",
                "Base HP starts at 1000 and gains +1200 every normal wave appearance.",
                "Touch damage starts at 20 and gains +1 every normal wave appearance.",
                "Golden Wind Mambo: Appears on waves ending in 5, always 5 enemies.",
                "Base HP starts at 5000 and gains +10000 every later golden wave.",
                "Touch damage starts at 5 and gains +1 every later golden wave.",
                "Mambo Mario: Boss appears on waves 10, 30, 50, 70, 90, etc.",
                "Boss HP starts at 60000 and gains +120000 every later boss wave.",
                "Touch damage starts at 10 and gains +1 every boss appearance.",
                "Mario normal attack throws a green shell every 0.6s for 100 damage.",
                "The shell moves at fireball speed and bounces 4 times off walls.",
                "Mario ultimate unlocks after 10s, lasts 8s, then goes on 10s cooldown.",
                "During ultimate, fireballs launch every 0.2s for 150 base damage.",
                "Mario fireball skill damage gains +100 every later boss appearance.",
                "In 2-player apocalypse, all mambo enemies spawn with 1.8x HP.",
            ],
        },
    }
    character_info_left_arrow_rect = pygame.Rect(padding + original_window_width - 178, screen_height - 80, 56, 44)
    character_info_right_arrow_rect = pygame.Rect(padding + original_window_width - 108, screen_height - 80, 56, 44)
    character_info_card_next_rect = pygame.Rect(padding + original_window_width - 108, screen_height - 120, 56, 44)

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

    def load_zombie_stage_progress():
        if not os.path.exists(zombie_stage_progress_path):
            return {"highest_cleared_wave": 0, "best_times": {}}
        try:
            with open(zombie_stage_progress_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            highest_cleared_wave = max(0, int(data.get("highest_cleared_wave", 0)))
            raw_best_times = data.get("best_times", {})
            best_times = {}
            if isinstance(raw_best_times, dict):
                for key, value in raw_best_times.items():
                    try:
                        best_times[str(int(key))] = float(value)
                    except (TypeError, ValueError):
                        continue
            return {"highest_cleared_wave": highest_cleared_wave, "best_times": best_times}
        except (OSError, ValueError, TypeError):
            return {"highest_cleared_wave": 0, "best_times": {}}

    def save_zombie_stage_progress(highest_cleared_wave, best_times=None):
        data = {
            "highest_cleared_wave": max(0, int(highest_cleared_wave)),
            "best_times": best_times or load_zombie_stage_progress().get("best_times", {}),
        }
        try:
            with open(zombie_stage_progress_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return True
        except OSError:
            return False

    def get_highest_cleared_zombie_wave():
        return load_zombie_stage_progress().get("highest_cleared_wave", 0)

    def get_highest_unlocked_zombie_wave():
        return max(1, get_highest_cleared_zombie_wave() + 1)

    def get_zombie_best_time(wave_number):
        return load_zombie_stage_progress().get("best_times", {}).get(str(int(wave_number)))

    def get_zombie_stage_page_for_wave(wave_number):
        return max(0, (max(1, wave_number) - 1) // 5)

    def get_zombie_stage_bonus_state(wave_number):
        completed_waves = max(0, wave_number - 1)
        return {
            "max_health": 1000 + completed_waves * 500,
            "skill_damage_bonus": completed_waves * 50,
            "normal_attack_damage_bonus": completed_waves * 5,
        }

    def format_stage_time(seconds):
        if seconds is None:
            return "--"
        total_centiseconds = max(0, int(round(seconds * 100)))
        minutes = total_centiseconds // 6000
        secs = (total_centiseconds % 6000) // 100
        centis = total_centiseconds % 100
        return f"{minutes:02d}:{secs:02d}.{centis:02d}"

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
        nonlocal menu_state, circles, bullets, meteors, damage_texts, red_explosions, purple_trails, faker_waves, faker_dust_trails, faker_magic_flames, zomboss_gadgets, zomboss_warning_zones, zomboss_beams, zomboss_shockwaves, epstein_decoys, epstein_curses, epstein_warning_zones, epstein_beams, epstein_shockwaves, screen_shake_timer, screen_shake_strength, faker_ultimate_hitstop_timer, elapsed_time, battle_time, current_wave_elapsed_time, last_cleared_wave_time, result_winner_name, result_show_options, result_special_click_needed, square_size, arena_left, arena_top, arena_width, arena_height, result_button_rects, match_assets, tube_top_height, zombie_spawn_timer, zomboss_wave_summons_spawned, current_wave, mambos_spawned_in_wave, mambos_to_spawn, wave_in_progress, wave_complete, zombie_music_mode, pending_zombie_resume_data, selected_zombie_stage_wave, home_music_paused
        menu_state = "play"
        pygame.mixer.music.stop()
        home_music_paused = False
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
                current_wave = max(1, selected_zombie_stage_wave)
                mambos_spawned_in_wave = 1
                mambos_to_spawn = 1
            wave_in_progress = True
            wave_complete = False

            ensure_zombie_wave_music(get_zombie_wave_music_mode(current_wave))
        else:
            tube_top_height = 0
            square_size = min(base_square_size * 1.2, screen_width - arena_margin * 2) if game_mode == "sim" else base_square_size
            square_size = int(square_size)
            arena_width = square_size
            arena_height = square_size
            arena_left = padding + (original_window_width - square_size) // 2
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
        zomboss_gadgets = []
        zomboss_warning_zones = []
        zomboss_beams = []
        zomboss_shockwaves = []
        epstein_decoys = []
        epstein_curses = []
        epstein_warning_zones = []
        epstein_beams = []
        epstein_shockwaves = []
        screen_shake_timer = 0.0
        screen_shake_strength = 0.0
        faker_ultimate_hitstop_timer = 0.0
        colliding_pairs.clear()
        elapsed_time = 0.0
        battle_time = 0.0
        current_wave_elapsed_time = 0.0
        last_cleared_wave_time = None
        result_winner_name = ""
        result_show_options = False
        result_special_click_needed = False

    def reset_to_home():
        nonlocal menu_state, game_mode, bot_difficulty, hp_multiplier, custom_count_input, zombie_count_input, zombie_stage_page, selected_zombie_stage_wave, player_count, selected_players, circles, bullets, meteors, damage_texts, red_explosions, purple_trails, faker_waves, faker_dust_trails, faker_magic_flames, zomboss_gadgets, zomboss_warning_zones, zomboss_beams, zomboss_shockwaves, epstein_decoys, epstein_curses, epstein_warning_zones, epstein_beams, epstein_shockwaves, screen_shake_timer, screen_shake_strength, faker_ultimate_hitstop_timer, elapsed_time, battle_time, result_winner_name, result_show_options, result_special_click_needed, square_size, arena_left, arena_top, arena_width, arena_height, result_button_rects, match_assets, tube_top_height, zombie_spawn_timer, zomboss_wave_summons_spawned, zombie_music_mode
        stop_all_audio()
        pygame.mixer.music.stop()
        menu_state = "mode"
        start_home_music()
        game_mode = "sim"
        bot_difficulty = "medium"
        hp_multiplier = 1.0
        custom_count_input = ""
        zombie_count_input = ""
        zombie_stage_page = 0
        selected_zombie_stage_wave = 1
        square_size = base_square_size
        arena_width = base_square_size
        arena_height = base_square_size
        arena_left = padding + (original_window_width - square_size) // 2
        arena_top = arena_margin
        tube_top_height = 0
        zombie_spawn_timer = 0.0
        zomboss_wave_summons_spawned = 0
        zombie_music_mode = None
        match_assets = build_match_assets(radius)
        result_button_rects = [
            pygame.Rect(arena_left + arena_width // 2 - 220, arena_top + arena_height // 2 + 120, 200, 72),
            pygame.Rect(arena_left + arena_width // 2 + 20, arena_top + arena_height // 2 + 120, 200, 72),
        ]

    def go_to_mode_screen():
        nonlocal menu_state
        menu_state = "mode"
        ensure_home_music_running()
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
        zomboss_gadgets = []
        zomboss_warning_zones = []
        zomboss_beams = []
        zomboss_shockwaves = []
        epstein_decoys = []
        epstein_curses = []
        epstein_warning_zones = []
        epstein_beams = []
        epstein_shockwaves = []
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
        nonlocal menu_state, result_winner_name, result_show_options, result_special_click_needed, has_finished_battle
        stop_all_audio()
        has_finished_battle = True
        alive = [c for c in circles if c.health > 0 and c.character_type != "Zombie" and not is_mambo_enemy(c) and not is_epstein_summon(c)]
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
        elif winner_circle and winner_circle.character_type == "Elon Musk" and elon_win_sound:
            amplified_elon_win = amplify_sound(elon_win_sound, 3.0)
            play_voice_sound(amplified_elon_win, preferred="secondary")
        elif winner_circle and winner_circle.character_type == "Epstein" and epstein_win_sound:
            play_voice_sound(epstein_win_sound, preferred="secondary")

    def activate_ultimate(circle):
        if circle.character_type == "Gojo Satoru":
            activate_gojo_domain(circle)
            return
        if circle.character_type == "Epstein":
            activate_epstein_ultimate(circle)
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

    def get_offscreen_launch_position(origin_x, origin_y, dir_x, dir_y, padding):
        back_x = -dir_x
        back_y = -dir_y
        distances = []
        if back_x > 0:
            distances.append((arena_width - origin_x) / back_x)
        elif back_x < 0:
            distances.append((0 - origin_x) / back_x)
        if back_y > 0:
            distances.append((arena_height - origin_y) / back_y)
        elif back_y < 0:
            distances.append((0 - origin_y) / back_y)
        travel = max((dist for dist in distances if dist >= 0), default=0.0) + padding
        return origin_x + back_x * travel, origin_y + back_y * travel

    def get_elon_attack_speed_multiplier(circle):
        morale_bonus = 1.08 if getattr(circle, "martian_citizenship_timer", 0.0) > 0 else 1.0
        return max(0.1, getattr(circle, "attack_speed_multiplier", 1.0) * morale_bonus)

    def get_elon_rocket_aoe_radius(projectile=None, image=None, fallback_size=None):
        rocket_image = image if image is not None else getattr(projectile, "image", None)
        rocket_size = fallback_size if fallback_size is not None else getattr(projectile, "size", radius * 3)
        rocket_length = rocket_image.get_height() if rocket_image is not None else rocket_size * 2.0
        return max(1.0, rocket_length / 3.0)

    def apply_elon_global_rocket_damage(owner_circle, damage_value):
        if owner_circle is None or owner_circle.health <= 0:
            return
        owner_index = circles.index(owner_circle) if owner_circle in circles else -1
        for idx, target_circle in enumerate(circles):
            if idx == owner_index or target_circle.health <= 0:
                continue
            if not circles_are_hostile(owner_circle, target_circle):
                continue
            damage_amount = damage_value(target_circle) if callable(damage_value) else damage_value
            apply_damage_to_circle(damage_texts, target_circle, damage_amount, True)

    def add_elon_thruster_trail(projectile, intensity=1.0):
        speed = math.hypot(projectile.vx, projectile.vy)
        if speed <= 0:
            return
        ux = -projectile.vx / speed
        uy = -projectile.vy / speed
        for plume_index in range(3):
            spread = (plume_index - 1) * projectile.size * 0.28 + random.uniform(-projectile.size * 0.12, projectile.size * 0.12)
            flame_x = projectile.x + ux * projectile.size * (0.6 + plume_index * 0.18) - uy * spread
            flame_y = projectile.y + uy * projectile.size * (0.6 + plume_index * 0.18) + ux * spread
            flame_radius = max(10.0, projectile.size * (0.26 + plume_index * 0.07) * intensity)
            flame_color = random.choice([(255, 125, 70), (255, 180, 90), (255, 230, 165)])
            add_faker_magic_flame(faker_magic_flames, flame_x, flame_y, flame_radius, flame_color)
        if (
            intensity > 1.6
            and random.random() < 0.35
            and 0 <= projectile.x <= arena_width
            and 0 <= projectile.y <= arena_height
        ):
            add_gojo_technique_explosion(
                red_explosions,
                projectile.x + ux * projectile.size * 0.25,
                projectile.y + uy * projectile.size * 0.25,
                projectile.size * 0.3,
                elon_rocket_colors,
            )

    def explode_elon_rocket(owner_circle, impact_x, impact_y, failed_landing=False):
        owner_index = circles.index(owner_circle) if owner_circle in circles else -1
        splash_radius = get_elon_rocket_aoe_radius(image=match_assets.get("falcon_9_image"), fallback_size=radius * 3)
        add_gojo_technique_explosion(red_explosions, impact_x, impact_y, splash_radius, elon_rocket_colors)
        apply_explosion_splash_damage(damage_texts, circles, owner_index, impact_x, impact_y, splash_radius, 100)
        if failed_landing:
            for _ in range(2):
                chaos_x = min(max(impact_x + random.uniform(-splash_radius * 0.8, splash_radius * 0.8), 0), arena_width)
                chaos_y = min(max(impact_y + random.uniform(-splash_radius * 0.8, splash_radius * 0.8), 0), arena_height)
                chaos_radius = splash_radius * 0.72
                add_gojo_technique_explosion(red_explosions, chaos_x, chaos_y, chaos_radius, elon_rocket_colors)
                apply_explosion_splash_damage(damage_texts, circles, owner_index, chaos_x, chaos_y, chaos_radius, 100)
                for splash_target in circles:
                    if splash_target.health <= 0 or not circles_are_hostile(owner_circle, splash_target):
                        continue
                    if math.hypot(splash_target.x - chaos_x, splash_target.y - chaos_y) <= chaos_radius + splash_target.radius:
                        splash_target.impulse_vx += random.uniform(-260.0, 260.0)
                        splash_target.impulse_vy += random.uniform(-180.0, 220.0)
                        splash_target.impulse_wall_bounces_remaining = max(splash_target.impulse_wall_bounces_remaining, 2)

    def grant_martian_citizenship(owner_circle):
        for ally in circles:
            if ally.health <= 0 or ally.character_type == "Cybertruck":
                continue
            if circles_are_hostile(owner_circle, ally):
                continue
            ally.martian_citizenship_timer = max(getattr(ally, "martian_citizenship_timer", 0.0), 8.0)
            add_status_text(damage_texts, ally, "+Martian Citizenship", color=(255, 190, 90))

    def release_mars_passengers(rocket, owner_circle):
        passenger_indices = list(getattr(rocket, "elon_passenger_indices", []))
        if not passenger_indices:
            if owner_circle is not None:
                grant_martian_citizenship(owner_circle)
            return
        for passenger_index in passenger_indices:
            if not (0 <= passenger_index < len(circles)):
                continue
            passenger = circles[passenger_index]
            if passenger.health <= 0:
                continue
            if getattr(passenger, "elon_abducted_by", None) is rocket:
                passenger.elon_abducted_by = None
            scatter_x = owner_circle.x + random.uniform(-arena_width * 0.18, arena_width * 0.18)
            scatter_y = owner_circle.y + random.uniform(-arena_height * 0.18, arena_height * 0.18)
            passenger.x = max(passenger.radius, min(arena_width - passenger.radius, scatter_x))
            passenger.y = max(passenger.radius, min(arena_height - passenger.radius, scatter_y))
            passenger.vx = 0.0
            passenger.vy = 0.0
            passenger.impulse_vx = random.uniform(-220.0, 220.0)
            passenger.impulse_vy = random.uniform(180.0, 280.0)
            passenger.impulse_wall_bounces_remaining = max(passenger.impulse_wall_bounces_remaining, 2)
            passenger.stun_timer = max(getattr(passenger, "stun_timer", 0.0), 2.0)
            add_status_text(damage_texts, passenger, "+Martian Citizenship", color=(255, 190, 90))
            apply_damage_to_circle(damage_texts, passenger, max(500.0, passenger.max_health * 0.05), True)
        rocket.elon_passenger_indices = []
        grant_martian_citizenship(owner_circle)

    def activate_elon_rocket_punch(circle):
        nonlocal bullets, screen_shake_timer, screen_shake_strength, faker_magic_flames
        if circle.health <= 0 or circle.elon_rocket_punch_cooldown > 0 or circle.elon_skill_state is not None:
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
        dist = math.hypot(dx, dy)
        if dist <= 0:
            return
        dir_x = dx / dist
        dir_y = dy / dist
        launch_x, launch_y = get_offscreen_launch_position(circle.x, circle.y, dir_x, dir_y, max(240.0, circle.radius * 7.5))
        flight_speed = ((300.0 * 3.0) / 1.3) * 0.7
        rocket_image = match_assets["falcon_9_image"]
        rocket_size = max(circle.radius * 2, (rocket_image.get_height() // 2) if rocket_image else circle.radius * 3)
        rocket = Bullet(
            launch_x,
            launch_y,
            dir_x * flight_speed,
            dir_y * flight_speed,
            circles.index(circle),
            size=rocket_size,
            image=rocket_image,
            source="elon_rocket_punch",
            damage=200,
            attack_type="skill",
        )
        rocket.wall_bounces_remaining = 0
        rocket.target_index = circles.index(target)
        rocket.elon_failed_landing = random.random() < 0.3
        rocket.elon_has_entered_arena = False
        rocket.elon_border_passes_remaining = 1
        bullets.append(rocket)

        circle.elon_skill_state = {"type": "rocket_punch", "timer": 0.35}
        circle.elon_rocket_punch_cooldown = 6.0
        apply_elon_global_rocket_damage(circle, 100.0)
        if elon_skill_voice_sounds:
            play_voice_sound(random.choice(elon_skill_voice_sounds), preferred="secondary")
        screen_shake_timer = max(screen_shake_timer, 0.2)
        screen_shake_strength = max(screen_shake_strength, 4.0)

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

    def activate_elon_cybertruck_shield(circle):
        nonlocal screen_shake_timer, screen_shake_strength, faker_magic_flames
        if circle.health <= 0 or circle.elon_cybertruck_cooldown > 0 or circle.elon_cybertruck_active:
            return

        if circle.target and circle.target.health > 0:
            dx = circle.target.x - circle.x
            dy = circle.target.y - circle.y
        else:
            dx, dy = circle.vx, circle.vy
        dist = math.hypot(dx, dy)
        if dist <= 0:
            dir_x, dir_y = 1.0, 0.0
        else:
            dir_x, dir_y = dx / dist, dy / dist

        circle.elon_cybertruck_active = True
        circle.elon_cybertruck_timer = 3.5
        circle.elon_cybertruck_cooldown = 7.0
        barrier_image = match_assets["cybertruck_image"]
        barrier_radius = max(circle.radius, (barrier_image.get_height() // 2) if barrier_image else circle.radius)
        barrier_distance = circle.radius + barrier_radius * 0.65
        barrier = Circle(
            circle.x + dir_x * barrier_distance,
            circle.y + dir_y * barrier_distance,
            0,
            0,
            barrier_radius,
            9999,
            (145, 145, 145),
            "Cybertruck Barrier",
            image=barrier_image,
            gun_image=None,
            character_type="Cybertruck",
        )
        barrier.controller = "shield"
        barrier.team_id = circle.team_id
        barrier.barrier_owner_index = circles.index(circle)
        barrier.reflects_projectiles = True
        barrier.barrier_lifetime = circle.elon_cybertruck_timer
        barrier.shatter_on_hit = random.random() < 0.5
        barrier.vx = 0.0
        barrier.vy = 0.0
        circles.append(barrier)
        add_faker_magic_flame(faker_magic_flames, barrier.x, barrier.y, max(barrier.radius * 0.8, 22.0), (190, 190, 190))
        add_faker_magic_flame(faker_magic_flames, barrier.x, barrier.y, max(barrier.radius * 1.1, 28.0), (120, 120, 120))
        if elon_skill_voice_sounds:
            play_voice_sound(random.choice(elon_skill_voice_sounds), preferred="secondary")
        screen_shake_timer = max(screen_shake_timer, 0.12)
        screen_shake_strength = max(screen_shake_strength, 3.6)

    def activate_mambo_mario_ultimate(circle):
        nonlocal screen_shake_timer, screen_shake_strength
        if circle.health <= 0 or circle.ultimate_active or circle.ultimate_cooldown_timer > 0:
            return
        if battle_time < 10.0:
            return
        circle.ultimate_active = True
        circle.mario_ultimate_stage = "jump"
        circle.mario_ultimate_timer = 0.8
        circle.ultimate_duration_timer = 0.0
        circle.mario_visual_y_offset = 0.0
        circle.mario_flower_y_offset = 0.0
        circle.mario_fireball_timer = 0.0
        circle.vx = 0.0
        circle.vy = 0.0
        circle.impulse_vx = 0.0
        circle.impulse_vy = 0.0
        screen_shake_timer = max(screen_shake_timer, 0.1)
        screen_shake_strength = max(screen_shake_strength, 4.5)

    def activate_elon_mars_colonization(circle):
        nonlocal bullets, screen_shake_timer, screen_shake_strength, faker_magic_flames
        if circle.health <= 0 or circle.elon_ultimate_cooldown > 0 or circle.elon_ultimate_active:
            return
        opponents = get_hostile_opponents(circle, circles)
        if not opponents:
            return
        primary_target = min(opponents, key=lambda other: math.hypot(other.x - circle.x, other.y - circle.y))
        dx = primary_target.x - circle.x
        dy = primary_target.y - circle.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dx, dy = 1.0, 0.0
            dist = 1.0
        dir_x = dx / dist
        dir_y = dy / dist
        launch_x, launch_y = get_offscreen_launch_position(circle.x, circle.y, dir_x, dir_y, max(560.0, circle.radius * 12.0))
        flight_speed = ((300.0 * 3.0) / 1.3) * 0.7
        rocket_image = match_assets["space_x_rocket_image"]
        rocket_size = max(circle.radius * 6, (rocket_image.get_height() // 2) if rocket_image else circle.radius * 8)
        ultimate_rocket = Bullet(
            launch_x,
            launch_y,
            dir_x * flight_speed,
            dir_y * flight_speed,
            circles.index(circle),
            size=rocket_size,
            image=rocket_image,
            source="elon_mars_ultimate",
            damage=0,
            attack_type="ultimate",
            is_ultimate=True,
        )
        ultimate_rocket.wall_bounces_remaining = 0
        ultimate_rocket.target_index = circles.index(primary_target)
        ultimate_rocket.elon_returning = False
        ultimate_rocket.elon_passenger_indices = []
        ultimate_rocket.elon_has_entered_arena = False
        ultimate_rocket.elon_border_passes_remaining = 1
        bullets.append(ultimate_rocket)
        circle.elon_ultimate_active = True
        circle.elon_ultimate_timer = 12.0
        circle.elon_ultimate_cooldown = 7.0
        circle.elon_skill_state = {"type": "mars_colonization", "timer": 1.1}
        apply_elon_global_rocket_damage(circle, lambda target_circle: max(500.0, target_circle.max_health * 0.05))
        if elon_skill_voice_sounds:
            play_voice_sound(random.choice(elon_skill_voice_sounds), preferred="secondary")
        screen_shake_timer = max(screen_shake_timer, 0.3)
        screen_shake_strength = max(screen_shake_strength, 8.0)

    def get_epstein_owner_index(circle):
        if circle is None:
            return -1
        if circle.character_type == "Epstein" and circle in circles:
            return circles.index(circle)
        return getattr(circle, "epstein_titan_owner_index", -1)

    def get_epstein_owner_circle(circle):
        owner_index = get_epstein_owner_index(circle)
        if 0 <= owner_index < len(circles):
            return circles[owner_index]
        return circle if circle is not None and circle.character_type == "Epstein" else None

    def epstein_owner_has_live_titan(owner_index):
        return any(
            other.health > 0
            and other.character_type == "Golden Titan"
            and other.epstein_titan_owner_index == owner_index
            for other in circles
        )

    def clear_epstein_titan_effects(owner_index):
        nonlocal epstein_beams, epstein_shockwaves
        epstein_beams = [beam for beam in epstein_beams if beam.get("owner_index") != owner_index]
        epstein_shockwaves = [wave for wave in epstein_shockwaves if wave.get("owner_index") != owner_index]

    def get_epstein_network_units(owner_circle):
        if owner_circle is None:
            return []
        return [
            other
            for other in circles
            if other.health > 0
            and other.team_id == owner_circle.team_id
            and other is not owner_circle
            and other.character_type in ("Epstein Thrall", "Golden Titan")
        ]

    def get_epstein_speed_multiplier(circle):
        if circle is None:
            return 1.0
        multiplier = 1.0
        if getattr(circle, "epstein_corruption_timer", 0.0) > 0 and getattr(circle, "epstein_corruption_type", None) == "speed":
            multiplier *= 1.35
        if circle.character_type == "Epstein" and getattr(circle, "epstein_phase_two", False):
            multiplier *= 1.12
        if circle.character_type == "Golden Titan" and getattr(circle, "titan_evolved", False):
            multiplier *= 1.2
        return multiplier

    def get_epstein_damage_bonus(circle):
        if circle is None:
            return 0.0
        bonus = 0.0
        if getattr(circle, "epstein_corruption_timer", 0.0) > 0 and getattr(circle, "epstein_corruption_type", None) == "damage":
            bonus += 28.0
        if circle.character_type == "Epstein" and getattr(circle, "epstein_phase_two", False):
            bonus += 20.0
        if circle.character_type == "Golden Titan" and getattr(circle, "titan_evolved", False):
            bonus += 36.0
        if game_mode == "zombie" and current_wave > 1:
            bonus += (current_wave - 1) * 20
        return bonus

    def fire_epstein_shadow_contract(circle, source_x=None, source_y=None, from_background=False):
        if circle is None or circle.health <= 0:
            return
        target = circle.target if circle.target and circle.target.health > 0 and circles_are_hostile(circle, circle.target) else None
        if target is None:
            hostiles = get_hostile_opponents(circle, circles)
            if not hostiles:
                return
            target = min(hostiles, key=lambda other: math.hypot(other.x - circle.x, other.y - circle.y))
            circle.target = target
        start_x = circle.x if source_x is None else source_x
        start_y = circle.y if source_y is None else source_y
        cursed_red_speed = (300.0 * 3.0) / 1.3
        speed = cursed_red_speed * 0.5
        aim_unit = get_lead_unit_vector(circle, target, speed, max_prediction_time=1.2, samples=18)
        if aim_unit:
            ux, uy = aim_unit
        else:
            dx = target.x - start_x
            dy = target.y - start_y
            dist = math.hypot(dx, dy)
            if dist <= 0:
                return
            ux, uy = dx / dist, dy / dist
        orb = Bullet(
            start_x,
            start_y,
            ux * speed,
            uy * speed,
            circles.index(circle) if circle in circles else get_epstein_owner_index(circle),
            color=(80, 70, 65),
            size=max(10, int(13 * (match_assets["radius"] / radius))),
            image=match_assets.get("epstein_normal_attack_image"),
            source="epstein_contract",
            damage=15 + get_epstein_damage_bonus(circle),
            attack_type="normal",
            wall_bounces_remaining=2,
        )
        orb.target_index = circles.index(target)
        orb.turn_rate = 0.0 if not from_background else 1.6
        bullets.append(orb)

    def spawn_epstein_thrall(owner_circle, spawn_x=None, spawn_y=None, corrupted=True):
        if owner_circle is None or owner_circle.health <= 0:
            return None
        team_thralls = [
            other for other in circles
            if other.health > 0 and other.team_id == owner_circle.team_id and other.character_type == "Epstein Thrall"
        ]
        if len(team_thralls) >= 7:
            return None
        thrall_radius = max(18, int(match_assets["radius"] * 0.58))
        if spawn_x is None or spawn_y is None:
            edge = random.choice(("top", "bottom", "left", "right"))
            if edge == "top":
                spawn_x = random.uniform(thrall_radius + 10, arena_width - thrall_radius - 10)
                spawn_y = thrall_radius + 10
            elif edge == "bottom":
                spawn_x = random.uniform(thrall_radius + 10, arena_width - thrall_radius - 10)
                spawn_y = arena_height - thrall_radius - 10
            elif edge == "left":
                spawn_x = thrall_radius + 10
                spawn_y = random.uniform(thrall_radius + 10, arena_height - thrall_radius - 10)
            else:
                spawn_x = arena_width - thrall_radius - 10
                spawn_y = random.uniform(thrall_radius + 10, arena_height - thrall_radius - 10)
        thrall = Circle(
            spawn_x,
            spawn_y,
            random.uniform(-40.0, 40.0),
            random.uniform(-40.0, 40.0),
            thrall_radius,
            260 if not corrupted else 340,
            (70, 66, 86),
            "Epstein Thrall",
            None,
            None,
            character_type="Epstein Thrall",
        )
        thrall.controller = "ai"
        thrall.team_id = owner_circle.team_id
        thrall.base_speed = 150.0
        thrall.bullet_timer = random.uniform(0.65, 1.0)
        thrall.damage = 16
        thrall.epstein_titan_owner_index = get_epstein_owner_index(owner_circle)
        if corrupted:
            thrall.epstein_corruption_timer = 6.0
            thrall.epstein_corruption_type = random.choice(("speed", "damage", "shield"))
        circles.append(thrall)
        return thrall

    def corrupt_epstein_network(owner_circle):
        if owner_circle is None or owner_circle.health <= 0:
            return
        network_units = get_epstein_network_units(owner_circle)
        target = random.choice(network_units) if network_units else spawn_epstein_thrall(owner_circle)
        if target is None:
            return
        target.epstein_corruption_timer = 6.0
        target.epstein_corruption_type = random.choice(("speed", "damage", "shield"))

    def activate_epstein_shadowstep(circle):
        nonlocal screen_shake_timer, screen_shake_strength
        if circle.health <= 0 or circle.epstein_shadowstep_cooldown > 0:
            return
        origin_x, origin_y = circle.x, circle.y
        edge = random.choice(("top", "bottom", "left", "right"))
        padding = circle.radius + 12
        if edge == "top":
            circle.x = random.uniform(padding, arena_width - padding)
            circle.y = padding
        elif edge == "bottom":
            circle.x = random.uniform(padding, arena_width - padding)
            circle.y = arena_height - padding
        elif edge == "left":
            circle.x = padding
            circle.y = random.uniform(padding, arena_height - padding)
        else:
            circle.x = arena_width - padding
            circle.y = random.uniform(padding, arena_height - padding)
        circle.vx = 0.0
        circle.vy = 0.0
        circle.impulse_vx = 0.0
        circle.impulse_vy = 0.0
        circle.epstein_shadowstep_cooldown = 2.2 if not circle.epstein_phase_two else 1.5
        circle.epstein_shadowstep_invuln_timer = 0.35
        epstein_decoys.append(
            {
                "x": origin_x,
                "y": origin_y,
                "timer": 1.5,
                "duration": 1.5,
                "radius": circle.radius * 1.45,
                "owner_index": circles.index(circle),
                "team_id": circle.team_id,
            }
        )
        add_gojo_technique_explosion(red_explosions, origin_x, origin_y, circle.radius * 1.8, epstein_shadow_colors)
        add_gojo_technique_explosion(red_explosions, circle.x, circle.y, circle.radius * 1.6, epstein_shadow_colors)
        screen_shake_timer = max(screen_shake_timer, 0.14)
        screen_shake_strength = max(screen_shake_strength, 7.0)

    def activate_epstein_blackmail(circle):
        if circle.health <= 0 or circle.epstein_blackmail_cooldown > 0:
            return
        target = circle.target if circle.target and circle.target.health > 0 and circles_are_hostile(circle, circle.target) else None
        if target is None:
            hostiles = get_hostile_opponents(circle, circles)
            if not hostiles:
                return
            target = min(hostiles, key=lambda other: math.hypot(other.x - circle.x, other.y - circle.y))
            circle.target = target
        epstein_curses.append(
            {
                "target": target,
                "owner_index": circles.index(circle),
                "timer": 1.4,
                "duration": 1.4,
                "outcome": random.choice(("explode", "spawn")),
            }
        )
        add_gojo_technique_explosion(red_explosions, target.x, target.y, target.radius * 1.5, epstein_shadow_colors)
        circle.epstein_blackmail_cooldown = 4.2 if not circle.epstein_phase_two else 3.1

    def activate_epstein_network_surge(circle):
        nonlocal screen_shake_timer, screen_shake_strength
        if circle.health <= 0 or circle.epstein_network_cooldown > 0:
            return
        corrupt_epstein_network(circle)
        for unit in get_epstein_network_units(circle):
            unit.epstein_corruption_timer = max(unit.epstein_corruption_timer, 7.0)
            unit.epstein_corruption_type = random.choice(("speed", "damage", "shield"))
        for _ in range(random.randint(2, 4)):
            spawn_epstein_thrall(circle)
        add_gojo_technique_explosion(red_explosions, circle.x, circle.y, circle.radius * 2.4, epstein_shadow_colors)
        circle.epstein_network_cooldown = 7.5 if not circle.epstein_phase_two else 5.5
        screen_shake_timer = max(screen_shake_timer, 0.18)
        screen_shake_strength = max(screen_shake_strength, 8.0)

    def spawn_epstein_titan(owner_circle):
        if owner_circle is None or owner_circle.health <= 0:
            return None
        if any(other.health > 0 and other.team_id == owner_circle.team_id and other.character_type == "Golden Titan" for other in circles):
            return None
        titan = Circle(
            arena_width * 0.72,
            arena_height * 0.46,
            0.0,
            0.0,
            max(50, int(match_assets["radius"] * 1.25)),
            3200,
            (220, 170, 65),
            "Mahora J Trump",
            match_assets.get("titan_trump_image"),
            None,
            character_type="Golden Titan",
        )
        titan.controller = "ai"
        titan.team_id = owner_circle.team_id
        titan.base_speed = 120.0
        titan.damage = 85 + current_wave * 0.5
        titan.epstein_titan_owner_index = circles.index(owner_circle)
        titan.titan_evolution_timer = 10.0
        titan.titan_evolved = False
        titan.titan_resistances = {"normal": 1.0, "skill": 1.0}
        titan.titan_slam_timer = 1.3
        titan.titan_aura_timer = 2.0
        titan.titan_beam_timer = 3.0
        titan.ultimate_duration_timer = 30.0
        titan.bullet_timer = 999.0
        circles.append(titan)
        add_gojo_technique_explosion(red_explosions, titan.x, titan.y, titan.radius * 2.8, titan_gold_colors)
        return titan

    def activate_epstein_ultimate(circle):
        nonlocal screen_shake_timer, screen_shake_strength
        if circle.health <= 0 or circle.ultimate_active or circle.ultimate_cooldown_timer > 0:
            return
        if any(other.health > 0 and other.team_id == circle.team_id and other.character_type == "Golden Titan" for other in circles):
            return
        circle.ultimate_active = True
        circle.epstein_ultimate_stage = "summon_intro"
        circle.epstein_voice_intro_timer = 7.0
        circle.epstein_banner_timer = 7.0
        circle.ultimate_duration_timer = 0.0
        circle.ultimate_cooldown_timer = 0.0
        circle.epstein_untargetable = True
        circle.epstein_minor_attack_timer = 0.0
        add_gojo_technique_explosion(red_explosions, circle.x, circle.y, 60, epstein_shadow_colors)
        screen_shake_timer = max(screen_shake_timer, 0.3)
        screen_shake_strength = max(screen_shake_strength, 11.0)
        if epstein_summon_sound:
            play_voice_sound(epstein_summon_sound, preferred="primary", priority=True)

    def trigger_titan_slam(titan):
        epstein_shockwaves.append(
            {
                "x": titan.x,
                "y": titan.y + titan.radius * 0.35,
                "radius": 18.0,
                "speed": 760.0 if not titan.titan_evolved else 980.0,
                "width": 38.0 if not titan.titan_evolved else 48.0,
                "damage": 55 + get_epstein_damage_bonus(titan),
                "owner_index": get_epstein_owner_index(titan),
                "hit_targets": set(),
            }
        )
        add_gojo_technique_explosion(red_explosions, titan.x, titan.y + titan.radius * 0.4, titan.radius * 1.8, titan_gold_colors)

    def trigger_titan_aura(titan):
        owner_circle = get_epstein_owner_circle(titan)
        if owner_circle is not None:
            for unit in get_epstein_network_units(owner_circle):
                unit.epstein_corruption_timer = max(unit.epstein_corruption_timer, 5.5)
                unit.epstein_corruption_type = random.choice(("speed", "damage", "shield"))
        for other in circles:
            if other.health <= 0 or not circles_are_hostile(titan, other):
                continue
            dx = other.x - titan.x
            dy = other.y - titan.y
            dist = math.hypot(dx, dy)
            if dist <= 0 or dist > titan.radius * 4.0:
                continue
            push = apply_radial_push(titan.x, titan.y, other.x, other.y, titan.radius * 4.0, 260.0)
            if push is not None:
                other.impulse_vx += push[0] * 4.2
                other.impulse_vy += push[1] * 4.2
                apply_damage_to_circle(damage_texts, other, 22 + get_epstein_damage_bonus(titan), False)
        add_gojo_technique_explosion(red_explosions, titan.x, titan.y, titan.radius * 2.0, titan_gold_colors)

    def trigger_titan_beam(titan):
        target = titan.target if titan.target and titan.target.health > 0 and circles_are_hostile(titan, titan.target) else None
        if target is None:
            hostiles = get_hostile_opponents(titan, circles)
            if not hostiles:
                return
            target = min(hostiles, key=lambda other: math.hypot(other.x - titan.x, other.y - titan.y))
            titan.target = target
        base_angle = math.atan2(target.y - titan.y, target.x - titan.x)
        epstein_beams.append(
            {
                "origin_x": titan.x,
                "origin_y": titan.y - titan.radius * 0.2,
                "base_angle": base_angle,
                "angle": base_angle - 0.6,
                "duration": 2.0 if not titan.titan_evolved else 1.6,
                "timer": 2.0 if not titan.titan_evolved else 1.6,
                "width": 42.0 if not titan.titan_evolved else 56.0,
                "length": arena_width * 1.3,
                "damage_per_second": 0.05,
                "percent_damage": True,
                "min_flat_damage": 80.0 if not titan.titan_evolved else 125.0,
                "sweep_range": 1.6 if not titan.titan_evolved else 2.2,
                "owner_index": get_epstein_owner_index(titan),
            }
        )
        add_gojo_technique_explosion(red_explosions, titan.x, titan.y - titan.radius * 0.15, titan.radius * 2.1, titan_gold_colors)

    def update_epstein_support_systems(dt):
        nonlocal epstein_decoys, epstein_curses, epstein_warning_zones, epstein_beams, epstein_shockwaves, screen_shake_timer, screen_shake_strength
        for circle in circles:
            if getattr(circle, "epstein_mark_timer", 0.0) > 0:
                circle.epstein_mark_timer = max(0.0, circle.epstein_mark_timer - dt)
                if circle.epstein_mark_timer <= 0:
                    circle.epstein_mark_owner_index = -1
            if getattr(circle, "epstein_corruption_timer", 0.0) > 0:
                circle.epstein_corruption_timer = max(0.0, circle.epstein_corruption_timer - dt)
            if getattr(circle, "epstein_corruption_timer", 0.0) > 0 and getattr(circle, "epstein_corruption_type", None) == "shield":
                circle.damage_taken_multiplier = min(circle.damage_taken_multiplier, 0.68)
            elif circle.character_type not in ("Mambo Zomboss",):
                circle.damage_taken_multiplier = 1.0

            if circle.character_type == "Epstein":
                circle.epstein_phase_two = circle.health > 0 and circle.max_health > 0 and circle.health <= circle.max_health * 0.6
                circle.epstein_shadowstep_cooldown = max(0.0, circle.epstein_shadowstep_cooldown - dt)
                circle.epstein_blackmail_cooldown = max(0.0, circle.epstein_blackmail_cooldown - dt)
                circle.epstein_network_cooldown = max(0.0, circle.epstein_network_cooldown - dt)
                circle.epstein_passive_timer = max(0.0, circle.epstein_passive_timer - dt)
                circle.epstein_minor_attack_timer = max(0.0, circle.epstein_minor_attack_timer - dt)
                circle.epstein_shadowstep_invuln_timer = max(0.0, getattr(circle, "epstein_shadowstep_invuln_timer", 0.0) - dt)
                circle.epstein_banner_timer = max(0.0, getattr(circle, "epstein_banner_timer", 0.0) - dt)

                titan_alive = any(other.health > 0 and other.team_id == circle.team_id and other.character_type == "Golden Titan" for other in circles)
                if circle.ultimate_active and circle.epstein_ultimate_stage == "summon_intro":
                    circle.epstein_untargetable = True
                else:
                    circle.epstein_untargetable = titan_alive or getattr(circle, "epstein_shadowstep_invuln_timer", 0.0) > 0

                if circle.epstein_passive_timer <= 0 and circle.health > 0:
                    corrupt_epstein_network(circle)
                    add_gojo_technique_explosion(red_explosions, circle.x, circle.y, circle.radius * 1.4, epstein_shadow_colors)
                    circle.epstein_passive_timer = 2.0 if not circle.epstein_phase_two else 1.4

                if circle.controller == "ai" and circle.health > 0 and circle.epstein_ultimate_stage != "summon_intro":
                    if circle.epstein_shadowstep_cooldown <= 0 and random.random() < (0.0035 if circle.epstein_phase_two else 0.002):
                        activate_epstein_shadowstep(circle)
                    if circle.epstein_blackmail_cooldown <= 0 and random.random() < (0.0032 if circle.epstein_phase_two else 0.002):
                        activate_epstein_blackmail(circle)
                    if circle.epstein_network_cooldown <= 0 and random.random() < 0.0016:
                        activate_epstein_network_surge(circle)
                    if not circle.ultimate_active and circle.ultimate_cooldown_timer <= 0 and random.random() < 0.0012:
                        activate_epstein_ultimate(circle)

            elif circle.character_type == "Golden Titan":
                circle.ultimate_duration_timer = max(0.0, circle.ultimate_duration_timer - dt)
                if circle.ultimate_duration_timer <= 0:
                    clear_epstein_titan_effects(circle.epstein_titan_owner_index)
                    circle.health = 0
                    continue
                circle.titan_evolution_timer = max(0.0, circle.titan_evolution_timer - dt)
                if circle.titan_evolution_timer <= 0 and not circle.titan_evolved:
                    circle.titan_evolved = True
                    screen_shake_timer = max(screen_shake_timer, 0.18)
                    screen_shake_strength = max(screen_shake_strength, 7.0)
                circle.titan_slam_timer = max(0.0, circle.titan_slam_timer - dt)
                circle.titan_aura_timer = max(0.0, circle.titan_aura_timer - dt)
                circle.titan_beam_timer = max(0.0, circle.titan_beam_timer - dt)
                if circle.titan_slam_timer <= 0:
                    trigger_titan_slam(circle)
                    circle.titan_slam_timer = 1.8 if not circle.titan_evolved else 1.1
                if circle.titan_aura_timer <= 0:
                    trigger_titan_aura(circle)
                    circle.titan_aura_timer = 2.6 if not circle.titan_evolved else 1.9
                if circle.titan_beam_timer <= 0:
                    trigger_titan_beam(circle)
                    circle.titan_beam_timer = 3.5 if not circle.titan_evolved else 2.25

        active_titan_owner_indices = {
            other.epstein_titan_owner_index
            for other in circles
            if other.health > 0 and other.character_type == "Golden Titan"
        }
        epstein_beams = [beam for beam in epstein_beams if beam.get("owner_index") in active_titan_owner_indices]
        epstein_shockwaves = [wave for wave in epstein_shockwaves if wave.get("owner_index") in active_titan_owner_indices]

        alive_decoys = []
        for decoy in epstein_decoys:
            decoy["timer"] -= dt
            if decoy["timer"] <= 0:
                owner_circle = circles[decoy["owner_index"]] if 0 <= decoy["owner_index"] < len(circles) else None
                add_gojo_technique_explosion(red_explosions, decoy["x"], decoy["y"], decoy["radius"] * 1.6, epstein_shadow_colors)
                for target in circles:
                    if target.health <= 0 or owner_circle is None or not circles_are_hostile(owner_circle, target):
                        continue
                    if math.hypot(target.x - decoy["x"], target.y - decoy["y"]) <= decoy["radius"] * 2.2 + target.radius:
                        apply_damage_to_circle(damage_texts, target, 140, False)
                continue
            alive_decoys.append(decoy)
        epstein_decoys = alive_decoys

        active_curses = []
        for curse in epstein_curses:
            curse["timer"] -= dt
            target = curse.get("target")
            if target is None or target.health <= 0:
                continue
            if curse["timer"] <= 0:
                owner_circle = circles[curse["owner_index"]] if 0 <= curse["owner_index"] < len(circles) else None
                if curse["outcome"] == "explode":
                    add_gojo_technique_explosion(red_explosions, target.x, target.y, target.radius * 2.2, epstein_shadow_colors)
                    for other in circles:
                        if other.health <= 0 or owner_circle is None or not circles_are_hostile(owner_circle, other):
                            continue
                        if math.hypot(other.x - target.x, other.y - target.y) <= target.radius * 2.4 + other.radius:
                            apply_damage_to_circle(damage_texts, other, 75 + get_epstein_damage_bonus(owner_circle), False)
                else:
                    spawn_epstein_thrall(owner_circle, target.x + random.uniform(-30, 30), target.y + random.uniform(-30, 30), corrupted=True)
                continue
            active_curses.append(curse)
        epstein_curses = active_curses

        live_beams = []
        for beam in epstein_beams:
            beam["timer"] -= dt
            if beam["timer"] <= 0:
                continue
            if not epstein_owner_has_live_titan(beam.get("owner_index", -1)):
                continue
            progress = 1.0 - (beam["timer"] / beam["duration"]) if beam["duration"] > 0 else 1.0
            beam["angle"] = beam["base_angle"] - beam["sweep_range"] * 0.5 + beam["sweep_range"] * progress
            dir_x = math.cos(beam["angle"])
            dir_y = math.sin(beam["angle"])
            owner_circle = circles[beam["owner_index"]] if 0 <= beam["owner_index"] < len(circles) else None
            for other in circles:
                if other.health <= 0 or owner_circle is None or not circles_are_hostile(owner_circle, other):
                    continue
                rel_x = other.x - beam["origin_x"]
                rel_y = other.y - beam["origin_y"]
                along = rel_x * dir_x + rel_y * dir_y
                side = abs(rel_x * -dir_y + rel_y * dir_x)
                if along < 0 or along > beam["length"] or side > beam["width"] + other.radius:
                    continue
                if beam.get("percent_damage", False):
                    base_damage = max(other.max_health * beam["damage_per_second"] * dt, beam.get("min_flat_damage", 0.0) * dt)
                else:
                    base_damage = (beam["damage_per_second"] + get_epstein_damage_bonus(owner_circle)) * dt
                damage = consume_epstein_mark_bonus(owner_circle, other, base_damage + get_epstein_damage_bonus(owner_circle) * dt, bonus_damage=20.0)
                apply_damage_to_circle(damage_texts, other, damage, False)
            live_beams.append(beam)
        epstein_beams = live_beams

        live_shockwaves = []
        for wave in epstein_shockwaves:
            if not epstein_owner_has_live_titan(wave.get("owner_index", -1)):
                continue
            wave["radius"] += wave["speed"] * dt
            if wave["radius"] > arena_width * 1.4:
                continue
            owner_circle = circles[wave["owner_index"]] if 0 <= wave["owner_index"] < len(circles) else None
            for other in circles:
                if other.health <= 0 or owner_circle is None or not circles_are_hostile(owner_circle, other):
                    continue
                if id(other) in wave["hit_targets"]:
                    continue
                dist = math.hypot(other.x - wave["x"], other.y - wave["y"])
                if abs(dist - wave["radius"]) <= wave["width"] + other.radius:
                    wave["hit_targets"].add(id(other))
                    damage = consume_epstein_mark_bonus(owner_circle, other, wave["damage"], bonus_damage=26.0)
                    apply_damage_to_circle(damage_texts, other, damage, False)
                    other.impulse_vx += (other.x - wave["x"]) * 0.8
                    other.impulse_vy += (other.y - wave["y"]) * 0.8
            live_shockwaves.append(wave)
        epstein_shockwaves = live_shockwaves

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
                if (
                    c.character_type == "Epstein"
                    and c.ultimate_active
                    and c.epstein_ultimate_stage == "summon_intro"
                ):
                    c.epstein_voice_intro_timer = max(0.0, c.epstein_voice_intro_timer - real_dt)
                    if c.epstein_voice_intro_timer <= 0:
                        c.ultimate_active = False
                        c.epstein_ultimate_stage = None
                        c.ultimate_cooldown_timer = 40.0
                        spawn_epstein_titan(c)
            gojo_voice_intro_active = any(
                c.character_type == "Gojo Satoru"
                and c.ultimate_active
                and c.gojo_ultimate_stage == "infinite_void_intro"
                for c in circles
            )
            epstein_voice_intro_active = any(
                c.character_type == "Epstein"
                and c.ultimate_active
                and c.epstein_ultimate_stage == "summon_intro"
                for c in circles
            )
            if gojo_voice_intro_active or epstein_voice_intro_active:
                sim_dt = 0.0
        else:
            gojo_voice_intro_active = False
            epstein_voice_intro_active = False
        elapsed_time += sim_dt if menu_state == "play" else real_dt
        if epstein_jumpscare_active:
            epstein_jumpscare_timer += real_dt
            if epstein_jumpscare_timer > 1.5:
                epstein_jumpscare_active = False
        if trump_jumpscare_active:
            trump_jumpscare_timer += real_dt
            if trump_jumpscare_timer > 1.4:
                trump_jumpscare_active = False
        cooldown_multiplier = 2 if game_mode == "dummy" else 1
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                play_next_home_music()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and menu_state == "mode":
                trump_jumpscare_active = True
                trump_jumpscare_timer = 0.0
                if epstein_jumpscare_sound:
                    epstein_jumpscare_sound.play()
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu_state == "play" and game_mode != "zombie":
                        menu_state = "pause"
                    elif menu_state == "pause":
                        if game_mode != "zombie":
                            menu_state = "play"
                        else:
                            menu_state = "play"
                    elif menu_state == "play" and game_mode == "zombie":
                        menu_state = "pause"
                    elif menu_state == "select":
                        go_to_mode_screen()
                    elif menu_state == "bot_difficulty":
                        menu_state = "select"
                    elif menu_state == "custom_count":
                        menu_state = "select"
                    elif menu_state == "zombie_count":
                        menu_state = "zombie_stage_select"
                    elif menu_state == "zombie_stage_select":
                        menu_state = "zombie_count"
                    elif menu_state == "character_info":
                        go_to_mode_screen()
                    elif menu_state == "result":
                        go_to_mode_screen()
                    # for "mode", do nothing
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((desktop_width, desktop_height), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((window_width, window_height))
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
                            selected_zombie_stage_wave = min(get_highest_unlocked_zombie_wave(), max(1, selected_zombie_stage_wave))
                            zombie_stage_page = get_zombie_stage_page_for_wave(selected_zombie_stage_wave)
                            menu_state = "zombie_stage_select"
                    elif event.key == pygame.K_BACKSPACE:
                        zombie_count_input = ""
                    elif event.unicode in ("1", "2"):
                        zombie_count_input = event.unicode
                elif menu_state == "play":
                    if not gojo_voice_intro_active and not epstein_voice_intro_active:
                        for circle in circles:
                            if circle.controller == "player1" and event.key == pygame.K_e and circle.character_type == "T1 Faker":
                                activate_faker_second_skill(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_q and circle.character_type == "Epstein":
                                activate_epstein_shadowstep(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_q and circle.character_type == "Elon Musk":
                                activate_elon_rocket_punch(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_e and circle.character_type == "Elon Musk":
                                activate_elon_cybertruck_shield(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_r and circle.character_type == "T1 Faker":
                                activate_ultimate(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_r and circle.character_type == "Elon Musk":
                                activate_elon_mars_colonization(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_e:
                                activate_ultimate(circle)
                            elif circle.controller == "player1" and event.key == pygame.K_q and circle.character_type == "T1 Faker":
                                activate_faker_first_skill(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_o and circle.character_type == "T1 Faker":
                                activate_faker_second_skill(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_u and circle.character_type == "Epstein":
                                activate_epstein_shadowstep(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_u and circle.character_type == "Elon Musk":
                                activate_elon_rocket_punch(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_o and circle.character_type == "Elon Musk":
                                activate_elon_cybertruck_shield(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_p and circle.character_type == "T1 Faker":
                                activate_ultimate(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_p and circle.character_type == "Elon Musk":
                                activate_elon_mars_colonization(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_o:
                                activate_ultimate(circle)
                            elif circle.controller == "player2" and event.key == pygame.K_u and circle.character_type == "T1 Faker":
                                activate_faker_first_skill(circle)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Convert to window coordinates for collision detection
                if fullscreen:
                    scale_x = window_width / desktop_width
                    scale_y = window_height / desktop_height
                    mx = int(mx * scale_x)
                    my = int(my * scale_y)
                if menu_state == "mode":
                    if music_toggle_rect.collidepoint(mx, my):
                        toggle_home_music_pause()
                    else:
                        clicked_mode = None
                        for idx, rect in enumerate(mode_rects):
                            if rect.collidepoint(mx, my) and idx < len(mode_button_names):
                                clicked_mode = mode_button_names[idx]
                                break
                        if clicked_mode == "character_info":
                            character_info_selected = "Mika"
                            menu_state = "character_info"
                        elif clicked_mode == "2p_simulation":
                            game_mode = "sim"
                            player_count = 2
                            selected_players = []
                            menu_state = "select"
                        elif clicked_mode == "vs_bot":
                            game_mode = "bot"
                            player_count = 2
                            selected_players = []
                            menu_state = "bot_difficulty"
                        elif clicked_mode == "vs_player":
                            game_mode = "pvp"
                            player_count = 2
                            selected_players = []
                            menu_state = "select"
                        elif clicked_mode == "custom_simulation":
                            game_mode = "custom"
                            player_count = 0
                            custom_count_input = ""
                            selected_players = []
                            menu_state = "custom_count"
                        elif clicked_mode == "mambo_apocalypse":
                            game_mode = "zombie"
                            pending_zombie_resume_data = None
                            player_count = 0
                            zombie_count_input = ""
                            selected_players = []
                            selected_zombie_stage_wave = min(get_highest_unlocked_zombie_wave(), max(1, selected_zombie_stage_wave))
                            zombie_stage_page = get_zombie_stage_page_for_wave(selected_zombie_stage_wave)
                            menu_state = "zombie_count"
                        elif clicked_mode == "dummy_testing":
                            game_mode = "dummy"
                            player_count = 1
                            selected_players = []
                            menu_state = "select"
                    if epstein_classroom_original and not epstein_jumpscare_active:
                        scaled_h = epstein_classroom_original.get_height() // 3
                        scaled_w = epstein_classroom_original.get_width() // 3
                        epstein_rect = pygame.Rect(0, screen_height - scaled_h, scaled_w, scaled_h)
                        if epstein_rect.collidepoint(mx, my):
                            epstein_jumpscare_active = True
                            epstein_jumpscare_timer = 0.0
                            if epstein_jumpscare_sound:
                                epstein_jumpscare_sound.play()
                elif menu_state == "bot_difficulty":
                    difficulty_names = ["easy", "medium", "hard", "impossible"]
                    for idx, rect in enumerate(difficulty_rects):
                        if rect.collidepoint(mx, my):
                            bot_difficulty = difficulty_names[idx]
                            selected_players = []
                            menu_state = "select"
                            break
                elif menu_state == "character_info":
                    selected_entry = character_info_entries.get(character_info_selected, character_info_entries["Mika"])
                    info_pages = max(1, math.ceil(len(selected_entry["overview"]) / character_info_lines_per_page))
                    if select_back_rect.collidepoint(mx, my):
                        go_to_mode_screen()
                    elif info_card_rects[0].collidepoint(mx, my):
                        char_idx = character_info_card_page * 5 + 0
                        if char_idx < len(info_order):
                            character_info_selected = info_order[char_idx]
                            character_info_page = 0
                    elif info_card_rects[1].collidepoint(mx, my):
                        char_idx = character_info_card_page * 5 + 1
                        if char_idx < len(info_order):
                            character_info_selected = info_order[char_idx]
                            character_info_page = 0
                    elif info_card_rects[2].collidepoint(mx, my):
                        char_idx = character_info_card_page * 5 + 2
                        if char_idx < len(info_order):
                            character_info_selected = info_order[char_idx]
                            character_info_page = 0
                    elif info_card_rects[3].collidepoint(mx, my):
                        char_idx = character_info_card_page * 5 + 3
                        if char_idx < len(info_order):
                            character_info_selected = info_order[char_idx]
                            character_info_page = 0
                    elif info_card_rects[4].collidepoint(mx, my):
                        char_idx = character_info_card_page * 5 + 4
                        if char_idx < len(info_order):
                            character_info_selected = info_order[char_idx]
                            character_info_page = 0
                    elif character_info_card_next_rect.collidepoint(mx, my):
                        max_page = (len(info_order) - 1) // 5
                        if character_info_card_page < max_page:
                            character_info_card_page += 1
                        character_info_page = 0
                    elif info_pages > 1 and character_info_left_arrow_rect.collidepoint(mx, my):
                        character_info_page = (character_info_page - 1) % info_pages
                    elif info_pages > 1 and character_info_right_arrow_rect.collidepoint(mx, my):
                        character_info_page = (character_info_page + 1) % info_pages
                elif menu_state == "zombie_stage_select":
                    highest_cleared_wave = get_highest_cleared_zombie_wave()
                    highest_unlocked_wave = max(1, highest_cleared_wave + 1)
                    page_start_wave = zombie_stage_page * 5 + 1
                    stage_centers = [
                        (160, 295),
                        (320, 230),
                        (500, 295),
                        (680, 230),
                        (840, 295),
                    ]
                    if zombie_stage_back_rect.collidepoint(mx, my):
                        menu_state = "zombie_count"
                    elif zombie_stage_left_rect.collidepoint(mx, my) and zombie_stage_page > 0:
                        zombie_stage_page -= 1
                    elif zombie_stage_right_rect.collidepoint(mx, my):
                        zombie_stage_page += 1
                    elif load_zombie_progress() is not None and zombie_stage_resume_rect.collidepoint(mx, my):
                        saved_run = load_zombie_progress()
                        if saved_run is not None:
                            game_mode = "zombie"
                            player_count = int(saved_run.get("player_count", len(saved_run.get("selected_players", [])) or 1))
                            selected_players = list(saved_run.get("selected_players", []))
                            pending_zombie_resume_data = saved_run
                            start_match()
                    else:
                        for idx, center in enumerate(stage_centers):
                            wave_number = page_start_wave + idx
                            if wave_number > highest_unlocked_wave:
                                continue
                            stage_rect = pygame.Rect(0, 0, 96, 96)
                            stage_rect.center = center
                            if stage_rect.collidepoint(mx, my):
                                selected_zombie_stage_wave = wave_number
                                selected_players = []
                                menu_state = "select"
                                break
                elif menu_state == "select":
                    shifted_select_back_rect_click = pygame.Rect(select_back_rect.x + 30, select_back_rect.y, select_back_rect.width, select_back_rect.height)
                    shifted_option_rects_click = [pygame.Rect(rect.x + 30, rect.y, rect.width, rect.height) for rect in option_rects]
                    shifted_hp_minus_rect_click = pygame.Rect(hp_minus_rect.x + 30, hp_minus_rect.y, hp_minus_rect.width, hp_minus_rect.height)
                    shifted_hp_plus_rect_click = pygame.Rect(hp_plus_rect.x + 30, hp_plus_rect.y, hp_plus_rect.width, hp_plus_rect.height)
                    if shifted_select_back_rect_click.collidepoint(mx, my):
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
                                go_to_mode_screen()
                        elif game_mode == "zombie":
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                menu_state = "zombie_stage_select"
                        else:
                            if len(selected_players) > 0:
                                selected_players.pop()
                            else:
                                go_to_mode_screen()
                    elif shifted_option_rects_click[0].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Mika")
                    elif shifted_option_rects_click[1].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Gojo")
                    elif shifted_option_rects_click[2].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Vu")
                    elif shifted_option_rects_click[3].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Faker")
                    elif shifted_option_rects_click[4].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Epstein")
                    elif shifted_option_rects_click[5].collidepoint(mx, my) and len(selected_players) < player_count:
                        selected_players.append("Elon")
                    elif shifted_hp_minus_rect_click.collidepoint(mx, my):
                        hp_multiplier = max(0.1, hp_multiplier - 0.1)
                    elif shifted_hp_plus_rect_click.collidepoint(mx, my):
                        hp_multiplier = min(10.0, hp_multiplier + 0.1)

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
                    if game_mode == "zombie":
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
                    else:
                        pause_buttons = [
                            pygame.Rect(pause_rect.x + 40, pause_rect.y + 60, pause_rect.width - 80, 42),
                            pygame.Rect(pause_rect.x + 40, pause_rect.y + 112, pause_rect.width - 80, 42),
                        ]
                        if pause_buttons[0].collidepoint(mx, my):
                            menu_state = "play"
                        elif pause_buttons[1].collidepoint(mx, my):
                            reset_to_home()
                elif menu_state == "play" and game_mode == "dummy" and win_button_rect.collidepoint(mx, my):
                    for circle in circles:
                        if circle.character_type == "Dummy Diddy":
                            circle.health = 0
                            break
                    show_result_screen()



        if menu_state == "mode":
            draw_surface.fill((0, 0, 0))
            if arona_and_plana_original:
                scaled = scale_to_fit(arona_and_plana_original, screen_width, screen_height)
                if scaled:
                    draw_surface.blit(scaled, (0, 0))
            # Title/banner on the left
            if mode_title_surface is not None:
                shrink_factor = 1.1
                new_width = int(mode_title_rect.width / shrink_factor)
                new_height = int(mode_title_rect.height / shrink_factor)
                scaled_title = pygame.transform.smoothscale(mode_title_surface, (new_width, new_height))
                # Create mask with rounded corners
                mask = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
                border_radius = min(20, new_width // 10, new_height // 10)
                pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=border_radius)
                # Apply mask to scaled_title
                final_title = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
                final_title.blit(scaled_title, (0, 0))
                final_title.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                # Position: move right a little, top y=0
                title_x = mode_title_rect.x + 50  # move right a little
                title_y = 0
                draw_surface.blit(final_title, (title_x, title_y))
            else:
                pygame.draw.rect(draw_surface, (40, 45, 70), mode_title_rect, border_radius=16)
                pygame.draw.rect(draw_surface, (120, 160, 230), mode_title_rect, 3, border_radius=16)
                draw_text(draw_surface, "Game Modes", mode_title_rect.x + 22, mode_title_rect.y + 20, size=44)

            draw_media_toggle_button(draw_surface, music_toggle_rect, home_music_paused)

            # Right-side grid buttons
            for idx, mode_name in enumerate(mode_button_names):
                tile = mode_tile_surfaces.get(mode_name)
                if tile is not None:
                    draw_surface.blit(tile, mode_tile_draw_rects[mode_name])
                else:
                    rect = mode_rects[idx]
                    pygame.draw.rect(draw_surface, (50, 55, 80), rect, border_radius=18)
                    pygame.draw.rect(draw_surface, (120, 160, 230), rect, 3, border_radius=18)
                    draw_text(draw_surface, mode_name.replace("_", " ").title(), rect.x + 18, rect.y + 18, size=22)

            # Trump jumpscare
            if trump_jumpscare_active and trump_jumpscare_original:
                progress = min(1.0, trump_jumpscare_timer / 0.2)
                current_y = screen_height - (screen_height * progress)
                scale_factor = screen_height / trump_jumpscare_original.get_height()
                scaled_w = int(trump_jumpscare_original.get_width() * scale_factor)
                scaled_trump = pygame.transform.smoothscale(trump_jumpscare_original, (scaled_w, screen_height))
                x_pos = (screen_width - scaled_w) // 2
                draw_surface.blit(scaled_trump, (x_pos, int(current_y)))

            # Bottom left image
            if epstein_classroom_original:
                if epstein_jumpscare_active:
                    progress = min(1.0, epstein_jumpscare_timer / 0.2)
                    target_scale = (screen_height * 2) / epstein_classroom_original.get_height()
                    scale_factor = 1/3 + (target_scale - 1/3) * progress
                    scaled_w = int(epstein_classroom_original.get_width() * scale_factor)
                    scaled_h = int(epstein_classroom_original.get_height() * scale_factor)
                    scaled_epstein = pygame.transform.smoothscale(epstein_classroom_original, (scaled_w, scaled_h))
                    original_scaled_h = epstein_classroom_original.get_height() // 3
                    original_scaled_w = epstein_classroom_original.get_width() // 3
                    original_x = 0
                    original_y = screen_height - original_scaled_h
                    target_x = screen_width // 2 - scaled_w // 2
                    target_y = 0
                    current_x = original_x + (target_x - original_x) * progress
                    current_y = original_y + (target_y - original_y) * progress
                    draw_surface.blit(scaled_epstein, (int(current_x), int(current_y)))
                else:
                    scaled_epstein = pygame.transform.smoothscale(epstein_classroom_original, (epstein_classroom_original.get_width() // 3, epstein_classroom_original.get_height() // 3))
                    draw_surface.blit(scaled_epstein, (0, screen_height - scaled_epstein.get_height()))
        elif menu_state == "character_info":
            draw_surface.fill((0, 0, 0))
            header_rect = pygame.Rect(20, 20, screen_width - 40, 90)
            pygame.draw.rect(draw_surface, (40, 45, 70), header_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), header_rect, 3, border_radius=16)
            draw_button(draw_surface, select_back_rect, "Back", fill_color=(160, 110, 70))
            draw_text(draw_surface, "Characters Info", header_rect.x + 20, header_rect.y + 18, size=36)
            draw_text(draw_surface, "Click a character card to read the full kit.", header_rect.x + 20, header_rect.y + 58, (220, 220, 255), size=22)

            info_order = ["Mika", "Gojo", "Vu", "Faker", "Epstein", "Elon"]
            info_titles = ["Mika", "Gojo", "Do Mixi", "Faker", "Epstein", "Elon Musk"]
            info_subtitles = ["Misono Mika", "Gojo Satoru", "Vu A Vu", "T1 Faker", "Network Master", "Technoking"]
            info_previews = [mika_original, gojo_original, vu_original, faker_original, epstein_original, elon_musk_original]
            info_sizes = [(92, 92), (92, 92), (126, 92), (112, 112), (92, 92)]
            info_centers = [246, 246, 246, 248, 246]
            cards_per_page = 5
            for idx in range(cards_per_page):
                char_idx = character_info_card_page * cards_per_page + idx
                if char_idx >= len(info_order):
                    continue
                rect = info_card_rects[idx]
                is_selected = character_info_selected == info_order[char_idx]
                border_color = (255, 230, 150) if is_selected else (120, 160, 230)
                fill_color = (66, 72, 104) if is_selected else (50, 55, 80)
                pygame.draw.rect(draw_surface, fill_color, rect, border_radius=18)
                pygame.draw.rect(draw_surface, border_color, rect, 3, border_radius=18)
                draw_text(draw_surface, info_titles[char_idx], rect.x + 14, rect.y + 18, size=24)
                draw_text(draw_surface, info_subtitles[char_idx], rect.x + 14, rect.y + 52, (220, 220, 255), size=16)
                preview_source = info_previews[char_idx]
                if preview_source:
                    preview = pygame.transform.smoothscale(preview_source, info_sizes[idx])
                    draw_surface.blit(preview, preview.get_rect(center=(rect.centerx, rect.y + info_centers[idx] - rect.y)))

            max_card_page = (len(info_order) - 1) // cards_per_page
            if character_info_card_page < max_card_page:
                draw_button(draw_surface, character_info_card_next_rect, ">", fill_color=(74, 120, 86))

            pygame.draw.rect(draw_surface, (40, 45, 70), info_detail_rect, border_radius=20)
            pygame.draw.rect(draw_surface, (120, 160, 230), info_detail_rect, 3, border_radius=20)
            entry = character_info_entries.get(character_info_selected, character_info_entries["Mika"])
            total_info_pages = max(1, math.ceil(len(entry["overview"]) / character_info_lines_per_page))
            character_info_page = min(character_info_page, total_info_pages - 1)
            page_start = character_info_page * character_info_lines_per_page
            page_end = page_start + character_info_lines_per_page
            page_lines = entry["overview"][page_start:page_end]
            draw_text(draw_surface, entry["title"], info_detail_rect.x + 24, info_detail_rect.y + 20, size=36)
            draw_text(draw_surface, entry["subtitle"], info_detail_rect.x + 24, info_detail_rect.y + 62, (220, 220, 255), size=22)
            draw_text_lines(draw_surface, page_lines, info_detail_rect.x + 24, info_detail_rect.y + 110, size=20, line_gap=7)
            if total_info_pages > 1:
                pygame.draw.rect(draw_surface, (58, 64, 96), character_info_left_arrow_rect, border_radius=12)
                pygame.draw.rect(draw_surface, (58, 64, 96), character_info_right_arrow_rect, border_radius=12)
                pygame.draw.rect(draw_surface, (120, 160, 230), character_info_left_arrow_rect, 2, border_radius=12)
                pygame.draw.rect(draw_surface, (120, 160, 230), character_info_right_arrow_rect, 2, border_radius=12)
                draw_text(draw_surface, "<", character_info_left_arrow_rect.x + 18, character_info_left_arrow_rect.y + 5, size=28)
                draw_text(draw_surface, ">", character_info_right_arrow_rect.x + 18, character_info_right_arrow_rect.y + 5, size=28)
                page_label = f"Page {character_info_page + 1}/{total_info_pages}"
                page_size = get_font(20).size(page_label)
                draw_text(
                    draw_surface,
                    page_label,
                    character_info_left_arrow_rect.x - page_size[0] - 18,
                    character_info_left_arrow_rect.y + 11,
                    (220, 220, 255),
                    size=20,
                )
        elif menu_state == "zombie_count":
            draw_surface.fill((0, 0, 0))
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(draw_surface, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(draw_surface, "Mambo Apocalypse", title_rect.x + 20, title_rect.y + 20, size=40)
            draw_text(draw_surface, "Choose players, then pick a wave stage.", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            pygame.draw.rect(draw_surface, (50, 55, 80), zombie_count_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), zombie_count_rect, 3, border_radius=16)
            zc_text = zombie_count_input if zombie_count_input else "Type 1 or 2 and press Enter"
            zc_color = (255, 255, 255) if zombie_count_input else (180, 180, 200)
            draw_text(draw_surface, zc_text, zombie_count_rect.x + 18, zombie_count_rect.y + 20, color=zc_color, size=28)
        elif menu_state == "zombie_stage_select":
            draw_surface.fill((0, 0, 0))
            highest_cleared_wave = get_highest_cleared_zombie_wave()
            highest_unlocked_wave = max(1, highest_cleared_wave + 1)
            page_start_wave = zombie_stage_page * 5 + 1
            page_end_wave = page_start_wave + 4
            header_rect = pygame.Rect(24, 24, screen_width - 48, 108)
            panel_rect = pygame.Rect(44, 164, screen_width - 88, 360)
            stage_centers = [
                (160, 295),
                (320, 230),
                (500, 295),
                (680, 230),
                (840, 295),
            ]

            pygame.draw.rect(draw_surface, (40, 45, 70), header_rect, border_radius=18)
            pygame.draw.rect(draw_surface, (120, 160, 230), header_rect, 3, border_radius=18)
            pygame.draw.rect(draw_surface, (32, 54, 36), panel_rect, border_radius=26)
            pygame.draw.rect(draw_surface, (102, 180, 110), panel_rect, 3, border_radius=26)
            draw_button(draw_surface, zombie_stage_back_rect, "Back", fill_color=(160, 110, 70))
            draw_text(draw_surface, "Mambo Apocalypse Waves", header_rect.x + 20, header_rect.y + 18, size=38)
            draw_text(draw_surface, f"Page {zombie_stage_page + 1}: waves {page_start_wave}-{page_end_wave}", header_rect.x + 20, header_rect.y + 66, (220, 235, 220), size=22)
            draw_text(draw_surface, f"Cleared through wave {highest_cleared_wave}", panel_rect.x + 22, panel_rect.y + 18, (214, 240, 214), size=22)

            for idx in range(4):
                start = stage_centers[idx]
                end = stage_centers[idx + 1]
                pygame.draw.line(draw_surface, (148, 208, 148), start, end, 6)

            for idx, center in enumerate(stage_centers):
                wave_number = page_start_wave + idx
                if wave_number <= highest_cleared_wave:
                    fill_color = (60, 205, 90)
                    border_color = (210, 255, 220)
                    text_color = (255, 255, 255)
                    label = str(wave_number)
                elif wave_number == highest_unlocked_wave:
                    fill_color = (34, 104, 42)
                    border_color = (150, 220, 160)
                    text_color = (232, 255, 232)
                    label = str(wave_number)
                else:
                    fill_color = (20, 68, 28)
                    border_color = (76, 118, 82)
                    text_color = (215, 235, 215)
                    label = None

                pygame.draw.circle(draw_surface, fill_color, center, 46)
                pygame.draw.circle(draw_surface, border_color, center, 46, 4)

                if label is not None:
                    wave_surface = get_font(28).render(label, True, text_color)
                    wave_rect = wave_surface.get_rect(center=center)
                    draw_surface.blit(wave_surface, wave_rect)
                else:
                    draw_lock_icon(draw_surface, center[0], center[1], color=text_color)

                caption = "Cleared" if wave_number <= highest_cleared_wave else ("Unlocked" if wave_number == highest_unlocked_wave else "Locked")
                caption_surface = get_font(18).render(caption, True, (230, 245, 230))
                caption_rect = caption_surface.get_rect(center=(center[0], center[1] + 68))
                draw_surface.blit(caption_surface, caption_rect)

            if zombie_stage_page > 0:
                draw_button(draw_surface, zombie_stage_left_rect, "<", fill_color=(74, 120, 86))
            draw_button(draw_surface, zombie_stage_right_rect, ">", fill_color=(74, 120, 86))

            saved_run = load_zombie_progress()
            if saved_run is not None:
                draw_button(draw_surface, zombie_stage_resume_rect, "Resume Saved Run", fill_color=(80, 136, 190))
                resume_wave = int(saved_run.get("current_wave", 1))
                draw_text(draw_surface, f"Resume from wave {resume_wave}", zombie_stage_resume_rect.x + 16, zombie_stage_resume_rect.y + 60, (220, 235, 255), size=18)
        elif menu_state == "bot_difficulty":
            draw_surface.fill((0, 0, 0))
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(draw_surface, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(draw_surface, "Bot Difficulty", title_rect.x + 20, title_rect.y + 20, size=44)
            draw_text(draw_surface, "Choose the bot HP strength.", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            difficulty_labels = ["Easy", "Medium", "Hard", "Impossible"]
            difficulty_hps = ["0.8x HP", "1.0x HP", "2.0x HP", "4.0x HP"]
            for idx, rect in enumerate(difficulty_rects):
                pygame.draw.rect(draw_surface, (50, 55, 80), rect, border_radius=18)
                pygame.draw.rect(draw_surface, (120, 160, 230), rect, 3, border_radius=18)
                draw_text(draw_surface, difficulty_labels[idx], rect.x + 22, rect.y + 28, size=30)
                draw_text(draw_surface, difficulty_hps[idx], rect.x + 32, rect.y + 82, (220, 220, 255), size=22)
        elif menu_state == "custom_count":
            draw_surface.fill((0, 0, 0))
            title_rect = pygame.Rect(40, 40, screen_width - 80, 100)
            pygame.draw.rect(draw_surface, (40, 45, 70), title_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), title_rect, 3, border_radius=16)
            draw_text(draw_surface, "Custom Character Simulation", title_rect.x + 20, title_rect.y + 20, size=40)
            draw_text(draw_surface, "How many characters?", title_rect.x + 20, title_rect.y + 70, (200, 200, 220), size=22)

            pygame.draw.rect(draw_surface, (50, 55, 80), custom_input_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), custom_input_rect, 3, border_radius=16)
            input_text = custom_count_input if custom_count_input else "Type a number and press Enter"
            input_color = (255, 255, 255) if custom_count_input else (180, 180, 200)
            draw_text(draw_surface, input_text, custom_input_rect.x + 18, custom_input_rect.y + 20, color=input_color, size=28)
            draw_text(draw_surface, "Every 10 extra characters shrinks the ball size by 1.5x.", custom_input_rect.x - 10, custom_input_rect.bottom + 24, (220, 220, 255), size=20)
        elif menu_state == "select":
            draw_surface.fill((0, 0, 0))
            display_names = build_display_names(selected_players)
            header_rect = pygame.Rect(50, 20, screen_width - 40, 90)
            shifted_select_back_rect = pygame.Rect(select_back_rect.x + 30, select_back_rect.y, select_back_rect.width, select_back_rect.height)
            shifted_option_rects = [pygame.Rect(rect.x + 30, rect.y, rect.width, rect.height) for rect in option_rects]
            shifted_hp_minus_rect = pygame.Rect(hp_minus_rect.x + 30, hp_minus_rect.y, hp_minus_rect.width, hp_minus_rect.height)
            shifted_hp_plus_rect = pygame.Rect(hp_plus_rect.x + 30, hp_plus_rect.y, hp_plus_rect.width, hp_plus_rect.height)
            pygame.draw.rect(draw_surface, (40, 45, 70), header_rect, border_radius=16)
            pygame.draw.rect(draw_surface, (120, 160, 230), header_rect, 3, border_radius=16)
            draw_button(draw_surface, shifted_select_back_rect, "Back", fill_color=(160, 110, 70))
            draw_text(draw_surface, "Choose Your Fighters", header_rect.x + 20, header_rect.y + 18, size=36)
            if game_mode == "bot" and len(selected_players) == 0:
                choose_prompt = "Choose Player"
            elif game_mode == "bot":
                choose_prompt = "Choose Bot"
            elif game_mode == "custom":
                choose_prompt = f"Choose character {len(selected_players) + 1} of {player_count}"
            elif game_mode == "dummy":
                choose_prompt = "Choose 1 character for Dummy tester."
            elif game_mode == "zombie":
                choose_prompt = f"Wave {selected_zombie_stage_wave}: choose character {len(selected_players) + 1} of {player_count}"
            else:
                choose_prompt = f"Player {len(selected_players) + 1}: choose your character."
            draw_text(draw_surface, choose_prompt, header_rect.x + 20, header_rect.y + 52, (200, 200, 220), size=22)

            for idx, player_name in enumerate(display_names):
                draw_text(
                    draw_surface,
                    f"{idx + 1}. {player_name}",
                    50,
                    header_rect.bottom + 12 + idx * 24,
                    (220, 220, 220),
                    size=20,
                )

            pygame.draw.rect(draw_surface, (50, 55, 80), shifted_option_rects[0], border_radius=18)
            for rect in shifted_option_rects:
                pygame.draw.rect(draw_surface, (50, 55, 80), rect, border_radius=18)
                pygame.draw.rect(draw_surface, (120, 160, 230), rect, 3, border_radius=18)

            draw_text(draw_surface, "Mika", shifted_option_rects[0].x + 14, shifted_option_rects[0].y + 18, size=24)
            draw_text(draw_surface, "Gojo", shifted_option_rects[1].x + 14, shifted_option_rects[1].y + 18, size=24)
            draw_text(draw_surface, "Do Mixi", shifted_option_rects[2].x + 14, shifted_option_rects[2].y + 18, size=24)
            draw_text(draw_surface, "Faker", shifted_option_rects[3].x + 14, shifted_option_rects[3].y + 18, size=24)
            draw_text(draw_surface, "Epstein", shifted_option_rects[4].x + 14, shifted_option_rects[4].y + 18, size=24)
            draw_text(draw_surface, "Elon Musk", shifted_option_rects[5].x + 14, shifted_option_rects[5].y + 18, size=24)
            draw_text(draw_surface, "Misono Mika", shifted_option_rects[0].x + 14, shifted_option_rects[0].y + 52, (220, 220, 255), size=16)
            draw_text(draw_surface, "Gojo Satoru", shifted_option_rects[1].x + 14, shifted_option_rects[1].y + 52, (220, 220, 255), size=16)
            draw_text(draw_surface, "Vu A Vu", shifted_option_rects[2].x + 14, shifted_option_rects[2].y + 52, (220, 220, 255), size=16)
            draw_text(draw_surface, "T1 Faker", shifted_option_rects[3].x + 14, shifted_option_rects[3].y + 52, (220, 220, 255), size=16)
            draw_text(draw_surface, "Control Boss", shifted_option_rects[4].x + 14, shifted_option_rects[4].y + 52, (220, 220, 255), size=16)
            draw_text(draw_surface, "Technoking", shifted_option_rects[5].x + 14, shifted_option_rects[5].y + 52, (220, 220, 255), size=16)

            if mika_original:
                scale_factor = shifted_option_rects[0].width / mika_original.get_width()
                scaled_w = int(shifted_option_rects[0].width * (1 / 1.2))
                scaled_h = int(mika_original.get_height() * scale_factor * (1 / 1.2))
                preview = pygame.transform.smoothscale(mika_original, (scaled_w, scaled_h))
                rect = preview.get_rect(midbottom=(shifted_option_rects[0].centerx, shifted_option_rects[0].bottom - 10))
                draw_surface.blit(preview, rect)
            if gojo_original:
                scale_factor = shifted_option_rects[1].width / gojo_original.get_width()
                scaled_w = int(shifted_option_rects[1].width * (1 / 1.2))
                scaled_h = int(gojo_original.get_height() * scale_factor * (1 / 1.2))
                preview = pygame.transform.smoothscale(gojo_original, (scaled_w, scaled_h))
                rect = preview.get_rect(midbottom=(shifted_option_rects[1].centerx, shifted_option_rects[1].bottom - 10))
                draw_surface.blit(preview, rect)
            if vu_original:
                scale_factor = shifted_option_rects[2].width / vu_original.get_width()
                scaled_w = int(shifted_option_rects[2].width * 1.7)
                scaled_h = int(vu_original.get_height() * scale_factor * 1.7)
                preview = pygame.transform.smoothscale(vu_original, (scaled_w, scaled_h))
                rect = preview.get_rect(midbottom=(shifted_option_rects[2].centerx + 10, shifted_option_rects[2].bottom - 10))
                draw_surface.blit(preview, rect)
            if faker_original:
                scale_factor = shifted_option_rects[3].width / faker_original.get_width()
                scaled_w = int(shifted_option_rects[3].width * 1.2)
                scaled_h = int(faker_original.get_height() * scale_factor * 1.2)
                preview = pygame.transform.smoothscale(faker_original, (scaled_w, scaled_h))
                rect = preview.get_rect(midbottom=(shifted_option_rects[3].centerx, shifted_option_rects[3].bottom - 10))
                draw_surface.blit(preview, rect)
            if epstein_original:
                scale_factor = shifted_option_rects[4].width / epstein_original.get_width()
                scaled_w = int(shifted_option_rects[4].width * 1.6)
                scaled_h = int(epstein_original.get_height() * scale_factor * 1.6)
                preview = pygame.transform.smoothscale(epstein_original, (scaled_w, scaled_h))
                rect = preview.get_rect(midbottom=(shifted_option_rects[4].centerx - 10, shifted_option_rects[4].bottom - 10))
                draw_surface.blit(preview, rect)
            if elon_musk_original:
                scale_factor = shifted_option_rects[5].width / elon_musk_original.get_width()
                scaled_w = int(shifted_option_rects[5].width * 1.5)
                scaled_h = int(elon_musk_original.get_height() * scale_factor * 1.5)
                preview = pygame.transform.smoothscale(elon_musk_original, (scaled_w, scaled_h))
                rect = preview.get_rect(midbottom=(shifted_option_rects[5].centerx + 10, shifted_option_rects[5].bottom - 10))
                draw_surface.blit(preview, rect)

            draw_text(draw_surface, f"HP Multiplier: {hp_multiplier:.1f}", 50, 400, size=20)
            draw_button(draw_surface, shifted_hp_minus_rect, "-", fill_color=(160, 110, 70))
            draw_button(draw_surface, shifted_hp_plus_rect, "+", fill_color=(70, 130, 220))
        elif menu_state == "play":
            battle_time += sim_dt
            if game_mode == "zombie" and wave_in_progress and not wave_complete:
                current_wave_elapsed_time += sim_dt
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
                if game_mode == "zombie" and not is_mambo_enemy(circle):
                    wave_damage_bonus += getattr(circle, 'damage_bonus', 0)
                    break
            
            def spawn_mambo():
                rz = max(25, int(match_assets["radius"] * 0.7))
                sx = random.uniform(0.2, 0.8) * arena_width
                sy = rz + 10
                sp = 100.0 * 1.5
                regular_wave_index = max(0, current_wave - 1)
                enemy_health_multiplier = 1.8 if player_count >= 2 else 1.0
                
                z = Circle(
                    sx,
                    sy,
                    random.uniform(-30, 30),
                    120,
                    rz,
                    (1000 + regular_wave_index * 1200) * enemy_health_multiplier,
                    (255, 255, 255),
                    "Green Mob",
                    match_assets.get("mambo_image"),
                    None,
                    character_type="Green Mob",
                )
                z.controller = "zombie"
                z.team_id = "mambo_enemy"
                z.base_speed = sp
                z.bullet_timer = 9999.0
                z.damage = 20 + regular_wave_index
                circles.append(z)

            def spawn_giorno_mambo():
                rz = max(35, int(match_assets["radius"] * 0.9))
                sx = random.uniform(0.3, 0.7) * arena_width
                sy = rz + 10
                sp = 80.0 * 1.5
                golden_wave_index = max(0, (current_wave - 5) // 10)
                stage_wave_damage_bonus = max(0, current_wave - 1)
                enemy_health_multiplier = 1.8 if player_count >= 2 else 1.0
                
                z = Circle(
                    sx,
                    sy,
                    random.uniform(-20, 20),
                    100,
                    rz,
                    (5000 + golden_wave_index * 10000) * enemy_health_multiplier,
                    (255, 255, 255),
                    "Giorno Mambo",
                    match_assets.get("giorno_mambo_image"),
                    None,
                    character_type="Giorno Mambo",
                )
                z.controller = "zombie"
                z.team_id = "mambo_enemy"
                z.base_speed = sp
                z.bullet_timer = 9999.0
                z.damage = 5 + stage_wave_damage_bonus
                circles.append(z)

            def spawn_mambo_mario():
                rz = max(96, int(match_assets["radius"] * 2.3))
                sx = arena_width * 0.5
                sy = rz + 10
                sp = 85.0 * 1.5
                boss_wave_index = max(1, (current_wave + 10) // 20)
                stage_wave_damage_bonus = max(0, current_wave - 1)
                enemy_health_multiplier = 1.8 if player_count >= 2 else 1.0
                boss_total_health = (60000 + (boss_wave_index - 1) * 120000) * enemy_health_multiplier

                z = Circle(
                    sx,
                    sy,
                    random.uniform(-15, 15),
                    95,
                    rz,
                    boss_total_health,
                    (255, 255, 255),
                    "Mambo Mario",
                    match_assets.get("mambo_mario_image"),
                    None,
                    character_type="Mambo Mario",
                )
                z.controller = "zombie"
                z.team_id = "mambo_enemy"
                z.base_speed = sp
                z.bullet_timer = 9999.0
                z.damage = 10 + stage_wave_damage_bonus
                z.boss_health_segment = 10000
                z.boss_health_bars_total = boss_wave_index * 3
                z.boss_total_health = boss_total_health
                z.mario_skill_damage_bonus = (boss_wave_index - 1) * 100
                z.base_radius = rz
                z.phase_two_radius = max(1, int(rz * 0.7))
                z.phase_three_radius = max(1, int(rz * 0.4))
                boss_image = match_assets.get("mambo_mario_image")
                z.base_image = boss_image
                z.phase_two_image = scale_to_fit(boss_image, max(1, int(boss_image.get_width() * 0.7)), max(1, int(boss_image.get_height() * 0.7))) if boss_image else None
                z.phase_three_image = scale_to_fit(boss_image, max(1, int(boss_image.get_width() * 0.4)), max(1, int(boss_image.get_height() * 0.4))) if boss_image else None
                z.lucky_box_image = match_assets.get("lucky_box_mambo_mario_image")
                z.fire_flower_image = match_assets.get("fire_flower_mambo_mario_image")
                z.fireball_image = match_assets.get("fireball_mambo_mario_image")
                z.green_shell_image = match_assets.get("green_shell_mambo_mario_image")
                z.mario_ultimate_stage = None
                z.mario_ultimate_timer = 0.0
                z.ultimate_cooldown_timer = 10.0
                z.mario_boss_wave_index = boss_wave_index
                z.mario_visual_y_offset = 0.0
                z.mario_flower_y_offset = 0.0
                z.mario_fireball_timer = 0.0
                z.mario_shell_timer = 0.0
                circles.append(z)

            def spawn_mambo_zomboss():
                rz = max(225, int(match_assets["radius"] * 4.5))
                sx = arena_width - rz + int(rz * 0.22)
                sy = arena_height * 0.5
                sp = 0.0
                zomboss_wave_index = max(1, current_wave // 20)
                stage_wave_damage_bonus = max(0, current_wave - 1)
                enemy_health_multiplier = 1.8 if player_count >= 2 else 1.0
                boss_total_health = (200000 + (zomboss_wave_index - 1) * 400000) * enemy_health_multiplier

                z = Circle(
                    sx,
                    sy,
                    0.0,
                    0.0,
                    rz,
                    boss_total_health,
                    (255, 255, 255),
                    "Mambo Zomboss",
                    match_assets.get("mambo_zomboss_image"),
                    None,
                    character_type="Mambo Zomboss",
                )
                z.controller = "zombie"
                z.team_id = "mambo_enemy"
                z.base_speed = sp
                z.bullet_timer = 9999.0
                z.damage = 10 + stage_wave_damage_bonus
                z.boss_health_segment = 10000
                z.boss_health_bars_total = zomboss_wave_index * 3
                z.boss_total_health = boss_total_health
                z.base_radius = rz
                z.phase_two_radius = rz
                z.phase_three_radius = rz
                z.base_image = match_assets.get("mambo_zomboss_image")
                z.phase_two_image = z.base_image
                z.phase_three_image = z.base_image
                z.anchor_x = sx
                z.anchor_y = sy
                z.zomboss_attack_cycle = 0
                z.zomboss_normal_attack_timer = 1.3
                z.zomboss_gadget_timer = 4.0
                z.zomboss_deploy_timer = 6.5
                z.zomboss_rocket_timer = 8.0
                z.zomboss_freeze_timer = 11.5
                z.zomboss_stomp_timer = 5.0
                z.zomboss_missile_hell_timer = 7.5
                z.zomboss_laser_timer = 9.0
                z.zomboss_rampage = False
                z.zomboss_banner_timer = 0.0
                z.damage_taken_multiplier = 1.0
                circles.append(z)

            def get_wave_spawn_target(wave_number):
                if is_zomboss_wave(wave_number):
                    return 1
                if is_boss_wave(wave_number):
                    return 1
                if is_golden_wave(wave_number):
                    return 5
                if wave_number > 10 and wave_number % 5 != 0:
                    return 10
                return min(wave_number, 10)

            def spawn_wave_enemies(initial=False):
                nonlocal mambos_spawned_in_wave, mambos_to_spawn, zombie_spawn_timer, zomboss_wave_summons_spawned
                mambos_to_spawn = get_wave_spawn_target(current_wave)
                mambos_spawned_in_wave = 0
                zomboss_wave_summons_spawned = 0
                if is_zomboss_wave(current_wave):
                    spawn_mambo_zomboss()
                    mambos_spawned_in_wave = 1
                    zombie_spawn_timer = 9999.0
                elif is_boss_wave(current_wave):
                    spawn_mambo_mario()
                    mambos_spawned_in_wave = 1
                    zombie_spawn_timer = 9999.0
                elif is_golden_wave(current_wave):
                    for _ in range(mambos_to_spawn):
                        spawn_giorno_mambo()
                    mambos_spawned_in_wave = mambos_to_spawn
                    zombie_spawn_timer = 9999.0
                elif initial:
                    spawn_mambo()
                    mambos_spawned_in_wave = 1
                    zombie_spawn_timer = 9999.0
                else:
                    zombie_spawn_timer = 0.0

            def update_mambo_mario_phase(circle):
                if circle.character_type != "Mambo Mario" or circle.max_health <= 0:
                    return
                health_ratio = max(0.0, circle.health / circle.max_health)
                if health_ratio <= (1.0 / 3.0):
                    circle.radius = getattr(circle, "phase_three_radius", circle.radius)
                    circle.image = getattr(circle, "phase_three_image", circle.image)
                elif health_ratio <= (2.0 / 3.0):
                    circle.radius = getattr(circle, "phase_two_radius", circle.radius)
                    circle.image = getattr(circle, "phase_two_image", circle.image)
                else:
                    circle.radius = getattr(circle, "base_radius", circle.radius)
                    circle.image = getattr(circle, "base_image", circle.image)

            def update_mambo_mario_ultimate(circle, dt):
                nonlocal screen_shake_timer, screen_shake_strength
                if circle.character_type != "Mambo Mario" or circle.health <= 0:
                    return
                circle.ultimate_cooldown_timer = max(0.0, circle.ultimate_cooldown_timer - dt)
                if battle_time >= 10.0 and not circle.ultimate_active and circle.ultimate_cooldown_timer <= 0:
                    activate_mambo_mario_ultimate(circle)

                stage = getattr(circle, "mario_ultimate_stage", None)
                circle.mario_visual_y_offset = 0.0
                if stage is None:
                    return

                circle.vx = 0.0
                circle.vy = 0.0
                circle.impulse_vx = 0.0
                circle.impulse_vy = 0.0
                circle.mario_ultimate_timer = max(0.0, circle.mario_ultimate_timer - dt)

                if stage == "jump":
                    duration = 0.8
                    progress = 1.0 - (circle.mario_ultimate_timer / duration if duration > 0 else 1.0)
                    jump_height = circle.base_radius * 1.8
                    circle.mario_visual_y_offset = -math.sin(progress * math.pi) * jump_height
                    if circle.mario_ultimate_timer <= 0:
                        circle.mario_ultimate_stage = "flower_rise"
                        circle.mario_ultimate_timer = 0.35
                        circle.mario_flower_y_offset = 0.0
                elif stage == "flower_rise":
                    duration = 0.35
                    progress = 1.0 - (circle.mario_ultimate_timer / duration if duration > 0 else 1.0)
                    circle.mario_flower_y_offset = -circle.base_radius * 0.55 * progress
                    if circle.mario_ultimate_timer <= 0:
                        circle.mario_ultimate_stage = "flower_fall"
                        circle.mario_ultimate_timer = 0.28
                elif stage == "flower_fall":
                    duration = 0.28
                    progress = 1.0 - (circle.mario_ultimate_timer / duration if duration > 0 else 1.0)
                    circle.mario_flower_y_offset = -circle.base_radius * 0.55 * (1.0 - progress)
                    if circle.mario_ultimate_timer <= 0:
                        circle.mario_ultimate_stage = "empowered"
                        circle.ultimate_duration_timer = 8.0
                        circle.mario_fireball_timer = 0.0
                        circle.mario_shell_timer = 0.0
                        circle.mario_flower_y_offset = 0.0
                        screen_shake_timer = max(screen_shake_timer, 0.12)
                        screen_shake_strength = max(screen_shake_strength, 5.0)
                elif stage == "empowered":
                    circle.ultimate_active = True
                    circle.ultimate_duration_timer = max(0.0, circle.ultimate_duration_timer - dt)
                    if circle.ultimate_duration_timer <= 0:
                        circle.ultimate_active = False
                        circle.mario_ultimate_stage = None
                        circle.ultimate_cooldown_timer = 10.0
                        circle.mario_shell_timer = 0.0

            def get_zombie_survivor_players(include_dead=False):
                players = [
                    circle
                    for circle in circles
                    if circle.controller in ("player1", "player2")
                    and not is_mambo_enemy(circle)
                    and (include_dead or circle.health > 0)
                ]
                players.sort(key=lambda c: 0 if c.controller == "player1" else 1)
                return players

            def revive_dead_zombie_players():
                survivor_players = get_zombie_survivor_players(include_dead=True)
                positions = initial_positions_zombie(player_count, match_assets["radius"], arena_width, arena_height)
                for idx, circle in enumerate(survivor_players):
                    if idx < len(positions):
                        circle.x, circle.y = positions[idx]
                    circle.target = None
                    circle.vx = 0.0
                    circle.vy = 0.0
                    circle.impulse_vx = 0.0
                    circle.impulse_vy = 0.0
                    circle.impulse_wall_bounces_remaining = 0
                    if circle.health <= 0:
                        circle.health = circle.max_health

            def spawn_zomboss_minion(origin_x, origin_y, hp_source):
                nonlocal zomboss_wave_summons_spawned
                if zomboss_wave_summons_spawned >= 10:
                    return False
                rz = max(24, int(match_assets["radius"] * 0.62))
                spawn_x = min(max(rz + 4, origin_x), arena_width - rz - 4)
                spawn_y = min(max(rz + 4, origin_y), arena_height - rz - 4)
                z = Circle(
                    spawn_x,
                    spawn_y,
                    random.uniform(-16, 16),
                    120,
                    rz,
                    max(1500, hp_source * 0.05),
                    (255, 255, 255),
                    "Green Mob",
                    match_assets.get("mambo_image"),
                    None,
                    character_type="Green Mob",
                )
                z.controller = "zombie"
                z.team_id = "mambo_enemy"
                z.base_speed = 135.0
                z.bullet_timer = 9999.0
                z.damage = 20 + max(0, current_wave - 1)
                circles.append(z)
                zomboss_wave_summons_spawned += 1
                return True

            def spawn_zomboss_gadget(boss, gadget_type=None):
                if boss is None or boss.health <= 0:
                    return
                if len(zomboss_gadgets) >= 4:
                    zomboss_gadgets.pop(0)
                gadget_type = gadget_type or random.choice(("turret", "spawner", "shield"))
                spawn_x = random.uniform(max(140.0, arena_width * 0.52), max(180.0, arena_width - boss.radius * 1.1))
                spawn_y = random.uniform(110.0, arena_height - 110.0)
                zomboss_gadgets.append(
                    {
                        "type": gadget_type,
                        "x": spawn_x,
                        "y": spawn_y,
                        "radius": 20.0 if gadget_type == "turret" else (24.0 if gadget_type == "spawner" else 28.0),
                        "ttl": 14.0 if gadget_type != "shield" else 10.0,
                        "build_timer": 0.55,
                        "attack_timer": 0.9,
                        "pulse": random.uniform(0.0, math.tau),
                    }
                )

            def fire_zomboss_pea_spread(boss, charged=False, from_turret=None):
                source_x = from_turret["x"] if from_turret is not None else boss.x - boss.radius * 0.55
                source_y = from_turret["y"] if from_turret is not None else boss.y - boss.radius * 0.18
                target = boss.target if boss.target and boss.target.health > 0 else None
                if target is None:
                    hostiles = get_hostile_opponents(boss, circles)
                    if not hostiles:
                        return
                    target = min(hostiles, key=lambda other: math.hypot(other.x - source_x, other.y - source_y))
                    boss.target = target
                speed = 520.0 if from_turret is not None else 600.0
                aim_dx = target.x - source_x
                aim_dy = target.y - source_y
                base_angle = math.atan2(aim_dy, aim_dx)
                spread_angles = [0.0] if charged or from_turret is not None else (-0.14, 0.0, 0.14)
                for offset in spread_angles:
                    angle = base_angle + offset
                    bullet = Bullet(
                        source_x,
                        source_y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        circles.index(boss),
                        color=(135, 255, 150) if not charged else (255, 170, 110),
                        size=max(8, int((16 if charged else 10) * (match_assets["radius"] / radius))),
                        source="zomboss_charged_pea" if charged else ("zomboss_turret_pea" if from_turret is not None else "zomboss_pea"),
                        damage=0,
                        attack_type="skill" if charged else "normal",
                    )
                    bullet.zomboss_damage_fraction = 0.05 if charged else 0.01
                    bullet.target_index = circles.index(target)
                    bullets.append(bullet)

            def trigger_zomboss_deployment(boss, summon_count=None):
                summon_count = summon_count if summon_count is not None else random.randint(2, 3)
                for summon_index in range(summon_count):
                    spawn_x = boss.x - boss.radius * 0.75 - summon_index * 32
                    spawn_y = boss.y + random.uniform(-boss.radius * 0.4, boss.radius * 0.4)
                    spawn_zomboss_minion(spawn_x, spawn_y, boss.max_health)

            def get_zomboss_percent_damage(target, damage_fraction):
                if target is None or target.max_health <= 0:
                    return 0.0
                return max(1.0, target.max_health * damage_fraction)

            def trigger_zomboss_rocket_barrage(boss, missile_hell=False):
                zone_count = random.randint(8, 12) if missile_hell else random.randint(3, 5)
                for _ in range(zone_count):
                    zomboss_warning_zones.append(
                        {
                            "x": random.uniform(100.0, arena_width - 100.0),
                            "y": random.uniform(110.0, arena_height - 80.0),
                            "radius": random.uniform(34.0, 52.0) if not missile_hell else random.uniform(28.0, 44.0),
                            "timer": 1.0 if not missile_hell else 0.75,
                            "damage_fraction": 0.05,
                            "kind": "rocket",
                        }
                    )

            def trigger_zomboss_beam(boss, laser_sweep=False):
                target = boss.target if boss.target and boss.target.health > 0 else None
                if target is None:
                    hostiles = get_hostile_opponents(boss, circles)
                    if not hostiles:
                        return
                    target = min(hostiles, key=lambda other: math.hypot(other.x - boss.x, other.y - boss.y))
                    boss.target = target
                base_angle = math.atan2(target.y - boss.y, target.x - boss.x)
                if laser_sweep:
                    zomboss_beams.append(
                        {
                            "mode": "laser_sweep",
                            "origin_x": boss.x - boss.radius * 0.45,
                            "origin_y": boss.y - boss.radius * 0.18,
                            "base_angle": base_angle,
                            "angle": base_angle - 0.75,
                            "duration": 2.8,
                            "timer": 2.8,
                            "width": 90.0,
                            "length": arena_width * 1.25,
                            "damage_fraction_per_second": 0.05,
                            "sweep_range": 1.5,
                            "hit_targets": set(),
                        }
                    )
                else:
                    zomboss_beams.append(
                        {
                            "mode": "freeze",
                            "origin_x": boss.x - boss.radius * 0.45,
                            "origin_y": boss.y - boss.radius * 0.18,
                            "base_angle": base_angle,
                            "angle": base_angle,
                            "duration": 2.2,
                            "timer": 2.2,
                            "width": 70.0,
                            "length": arena_width * 1.1,
                            "damage_fraction_per_second": 0.10,
                            "sweep_range": 0.55,
                            "hit_targets": set(),
                        }
                    )

            def trigger_zomboss_shockwave(boss):
                zomboss_shockwaves.append(
                    {
                        "x": boss.x - boss.radius * 0.25,
                        "y": arena_height - 18.0,
                        "radius": 12.0,
                        "speed": 760.0,
                        "width": 28.0,
                        "damage_fraction": 0.05,
                        "hit_targets": set(),
                    }
                )

            def update_zomboss_support_systems(dt):
                nonlocal screen_shake_timer, screen_shake_strength, zomboss_gadgets, zomboss_warning_zones, zomboss_beams, zomboss_shockwaves
                zomboss_boss = next((c for c in circles if c.character_type == "Mambo Zomboss" and c.health > 0), None)

                for survivor in get_zombie_survivor_players(include_dead=True):
                    survivor.zomboss_slow_timer = max(0.0, getattr(survivor, "zomboss_slow_timer", 0.0) - dt)
                    survivor.zomboss_freeze_timer = max(0.0, getattr(survivor, "zomboss_freeze_timer", 0.0) - dt)
                    survivor.zomboss_freeze_build = max(0.0, getattr(survivor, "zomboss_freeze_build", 0.0) - dt * 0.55)

                shield_active = False
                alive_gadgets = []
                for gadget in zomboss_gadgets:
                    gadget["ttl"] -= dt
                    if gadget["ttl"] <= 0:
                        continue
                    gadget["build_timer"] = max(0.0, gadget["build_timer"] - dt)
                    gadget["pulse"] += dt * 3.0
                    if gadget["build_timer"] > 0:
                        alive_gadgets.append(gadget)
                        continue
                    gadget["attack_timer"] -= dt
                    if gadget["type"] == "shield":
                        shield_active = True
                    elif gadget["type"] == "turret" and gadget["attack_timer"] <= 0 and zomboss_boss is not None:
                        fire_zomboss_pea_spread(zomboss_boss, from_turret=gadget)
                        gadget["attack_timer"] = 1.05
                    elif gadget["type"] == "spawner" and gadget["attack_timer"] <= 0 and zomboss_boss is not None:
                        spawn_zomboss_minion(gadget["x"] - 24, gadget["y"] + random.uniform(-28, 28), zomboss_boss.max_health)
                        gadget["attack_timer"] = 3.8
                    alive_gadgets.append(gadget)
                zomboss_gadgets = alive_gadgets

                if zomboss_boss is not None:
                    rampage_multiplier = 0.7 if getattr(zomboss_boss, "zomboss_rampage", False) else 1.0
                    shield_multiplier = 0.68 if shield_active else 1.0
                    zomboss_boss.damage_taken_multiplier = rampage_multiplier * shield_multiplier

                alive_warning_zones = []
                for zone in zomboss_warning_zones:
                    zone["timer"] -= dt
                    if zone["timer"] <= 0:
                        add_gojo_technique_explosion(red_explosions, zone["x"], zone["y"], zone["radius"] * 0.7, gojo_red_colors)
                        for human in get_zombie_survivor_players():
                            if math.hypot(human.x - zone["x"], human.y - zone["y"]) <= zone["radius"] + human.radius:
                                apply_damage_to_circle(damage_texts, human, get_zomboss_percent_damage(human, zone.get("damage_fraction", 0.05)), False)
                        screen_shake_timer = max(screen_shake_timer, 0.1)
                        screen_shake_strength = max(screen_shake_strength, 5.0)
                        continue
                    alive_warning_zones.append(zone)
                zomboss_warning_zones = alive_warning_zones

                alive_beams = []
                for beam in zomboss_beams:
                    beam["timer"] -= dt
                    if beam["timer"] <= 0:
                        continue
                    progress = 1.0 - (beam["timer"] / beam["duration"]) if beam["duration"] > 0 else 1.0
                    if beam["mode"] == "laser_sweep":
                        beam["angle"] = beam["base_angle"] - beam["sweep_range"] * 0.5 + beam["sweep_range"] * progress
                    else:
                        beam["angle"] = beam["base_angle"] - beam["sweep_range"] * 0.5 + beam["sweep_range"] * math.sin(progress * math.pi)
                    dir_x = math.cos(beam["angle"])
                    dir_y = math.sin(beam["angle"])
                    hit_targets = beam.get("hit_targets", set())
                    for human in get_zombie_survivor_players():
                        human_id = id(human)
                        if human_id in hit_targets:
                            continue
                        rel_x = human.x - beam["origin_x"]
                        rel_y = human.y - beam["origin_y"]
                        along = rel_x * dir_x + rel_y * dir_y
                        side = abs(rel_x * -dir_y + rel_y * dir_x)
                        if along < 0 or along > beam["length"] or side > beam["width"] + human.radius:
                            continue
                        hit_targets.add(human_id)
                        apply_damage_to_circle(
                            damage_texts,
                            human,
                            get_zomboss_percent_damage(human, beam.get("damage_fraction_per_second", 0.05) * dt),
                            False,
                        )
                        human.zomboss_slow_timer = max(getattr(human, "zomboss_slow_timer", 0.0), 1.0)
                        human.zomboss_freeze_build = getattr(human, "zomboss_freeze_build", 0.0) + dt
                        if human.zomboss_freeze_build >= 0.65:
                            human.zomboss_freeze_timer = max(getattr(human, "zomboss_freeze_timer", 0.0), 0.45)
                            human.zomboss_freeze_build = 0.25
                    alive_beams.append(beam)
                zomboss_beams = alive_beams

                alive_shockwaves = []
                for wave in zomboss_shockwaves:
                    wave["radius"] += wave["speed"] * dt
                    if wave["radius"] > arena_width * 1.4:
                        continue
                    for human in get_zombie_survivor_players():
                        dist = math.hypot(human.x - wave["x"], human.y - wave["y"])
                        if abs(dist - wave["radius"]) <= wave["width"] + human.radius and id(human) not in wave["hit_targets"]:
                            wave["hit_targets"].add(id(human))
                            apply_damage_to_circle(damage_texts, human, get_zomboss_percent_damage(human, wave.get("damage_fraction", 0.05)), False)
                            human.impulse_vx -= 240.0
                            human.impulse_vy -= 120.0
                    alive_shockwaves.append(wave)
                zomboss_shockwaves = alive_shockwaves

            update_zomboss_support_systems(sim_dt)
            update_epstein_support_systems(sim_dt)
            
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
                elif game_mode == "dummy":
                    positions = [(arena_width * 0.24, arena_height * 0.5)]
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
                    elif character == "Epstein":
                        image = match_assets.get("epstein_image")
                        gun_image = None
                        name = display_names[idx]
                        character_type = "Epstein"
                    elif character == "Faker":
                        image = match_assets["faker_image"]
                        gun_image = None
                        name = display_names[idx]
                        character_type = "T1 Faker"
                    elif character == "Elon":
                        image = match_assets["elon_image"]
                        gun_image = None
                        name = display_names[idx]
                        character_type = "Elon Musk"
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
                        circle.team_id = "survivor"
                        starting_bonus_state = get_zombie_stage_bonus_state(current_wave)
                        circle.max_health = starting_bonus_state["max_health"]
                        circle.health = circle.max_health
                        circle.damage_bonus = 0  # Damage bonus from killing mambos
                        circle.skill_damage_bonus = starting_bonus_state["skill_damage_bonus"]
                        circle.normal_attack_damage_bonus = starting_bonus_state["normal_attack_damage_bonus"]
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
                        circle.team_id = "player" if idx == 0 else "bot"
                    elif game_mode == "pvp":
                        circle.controller = "player1" if idx == 0 else "player2"
                        circle.team_id = "player1" if idx == 0 else "player2"
                    elif game_mode == "dummy":
                        circle.controller = "player1"
                        circle.team_id = "tester_player"
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
                    elif character_type == "Epstein":
                        circle.bullet_timer = 1.6
                        circle.base_speed = 220.0
                        circle.ultimate_cooldown_timer = 8.0
                        circle.epstein_shadowstep_cooldown = 2.2
                        circle.epstein_blackmail_cooldown = 3.5
                        circle.epstein_network_cooldown = 7.0
                        circle.epstein_passive_timer = 1.5
                    elif character_type == "T1 Faker":
                        circle.bullet_timer = 1.0
                        circle.ultimate_cooldown_timer = 8.0
                        circle.faker_ultimate_cooldown_timer = 12.0
                    elif character_type == "Elon Musk":
                        circle.bullet_timer = 0.55
                        circle.base_speed *= 1.18
                        circle.attack_speed_multiplier = 1.18
                        circle.elon_rocket_punch_cooldown = 0.0
                        circle.elon_cybertruck_cooldown = 0.0
                        circle.elon_ultimate_cooldown = 7.0
                        circle.elon_passive_stun_timer = 0.0
                        circle.elon_cybertruck_active = False
                        circle.elon_cybertruck_timer = 0.0
                    if circle.controller != "ai":
                        circle.max_health = int(circle.max_health * hp_multiplier)
                        circle.health = int(circle.health * hp_multiplier)
                        circle.elon_ultimate_active = False
                        circle.elon_ultimate_timer = 0.0
                        circle.elon_skill_state = None
                    circles.append(circle)
                if game_mode == "dummy":
                    dummy_radius = max(match_assets["radius"], int(match_assets["radius"] * 1.05))
                    dummy = Circle(
                        arena_width * 0.76,
                        arena_height * 0.5,
                        0.0,
                        0.0,
                        dummy_radius,
                        1,
                        (235, 235, 235),
                        "Dummy Diddy",
                        match_assets.get("dummy_diddy_image"),
                        None,
                        character_type="Dummy Diddy",
                    )
                    dummy.controller = "dummy"
                    dummy.team_id = "dummy_target"
                    dummy.base_speed = 0.0
                    dummy.max_health = 1
                    dummy.health = 1
                    dummy.dummy_damage_taken_total = 0.0
                    circles.append(dummy)
                if game_mode == "zombie":
                    if pending_zombie_resume_data is not None:
                        spawn_wave_enemies()
                        pending_zombie_resume_data = None
                    else:
                        spawn_wave_enemies(initial=True)
            if game_mode == "zombie" and len(circles) > 0:
                humans = [c for c in circles if c.health > 0 and not is_mambo_enemy(c)]
                all_survivor_players = get_zombie_survivor_players(include_dead=True)
                
                # Check if wave is complete (all mambos dead)
                mambos = [c for c in circles if is_mambo_enemy(c) and c.health > 0]
                
                if not mambos and wave_in_progress and not wave_complete:
                    # Wave complete, start next wave after delay
                    wave_in_progress = False
                    wave_complete = True
                    zombie_spawn_timer = 3.0  # Delay before next wave
                    last_cleared_wave_time = current_wave_elapsed_time
                    stage_progress = load_zombie_stage_progress()
                    best_times = dict(stage_progress.get("best_times", {}))
                    best_time_key = str(int(current_wave))
                    previous_best = best_times.get(best_time_key)
                    if previous_best is None or last_cleared_wave_time < previous_best:
                        best_times[best_time_key] = last_cleared_wave_time
                    save_zombie_stage_progress(max(stage_progress.get("highest_cleared_wave", 0), current_wave), best_times)
                    for human in all_survivor_players:
                        human.max_health += 500
                        human.skill_damage_bonus = getattr(human, "skill_damage_bonus", 0) + 50
                        human.normal_attack_damage_bonus = getattr(human, "normal_attack_damage_bonus", 0) + 5
                        if human.health > 0:
                            human.health = human.max_health
                elif not wave_in_progress and wave_complete:
                    # Start next wave
                    zombie_spawn_timer -= sim_dt
                    if zombie_spawn_timer <= 0:
                        current_wave += 1
                        wave_complete = False
                        wave_in_progress = True
                        current_wave_elapsed_time = 0.0
                        if humans:
                            revive_dead_zombie_players()

                        ensure_zombie_wave_music(get_zombie_wave_music_mode(current_wave))
                        spawn_wave_enemies()
                
                if wave_in_progress:
                    zombie_spawn_timer -= sim_dt
                    if zombie_spawn_timer <= 0 and mambos_spawned_in_wave < mambos_to_spawn:
                        remaining = mambos_to_spawn - mambos_spawned_in_wave
                        spawn_count = random.randint(2, 3)
                        actual_spawn = min(spawn_count, remaining)
                        for _ in range(actual_spawn):
                            spawn_mambo()
                        mambos_spawned_in_wave += actual_spawn
                        
                        # Random spawn delay between groups
                        zombie_spawn_timer = 1.0 + random.uniform(0, 1.0)

            for circle in circles:
                if game_mode == "zombie":
                    update_mambo_mario_phase(circle)
                    update_mambo_mario_ultimate(circle, sim_dt)
                circle.stun_timer = max(0.0, getattr(circle, "stun_timer", 0.0) - sim_dt)
                circle.martian_citizenship_timer = max(0.0, getattr(circle, "martian_citizenship_timer", 0.0) - sim_dt)
                if circle.character_type == "Cybertruck":
                    circle.barrier_lifetime = max(0.0, getattr(circle, "barrier_lifetime", 0.0) - sim_dt)
                    owner_index = getattr(circle, "barrier_owner_index", -1)
                    owner_alive = 0 <= owner_index < len(circles) and circles[owner_index].health > 0 and getattr(circles[owner_index], "elon_cybertruck_active", False)
                    if not owner_alive or circle.barrier_lifetime <= 0:
                        circle.health = 0
                if circle.character_type == "Elon Musk":
                    circle.elon_rocket_punch_cooldown = max(0.0, getattr(circle, "elon_rocket_punch_cooldown", 0.0) - sim_dt * cooldown_multiplier)
                    circle.elon_cybertruck_cooldown = max(0.0, getattr(circle, "elon_cybertruck_cooldown", 0.0) - sim_dt * cooldown_multiplier)
                    circle.elon_ultimate_cooldown = max(0.0, getattr(circle, "elon_ultimate_cooldown", 0.0) - sim_dt * cooldown_multiplier)
                    circle.elon_cybertruck_timer = max(0.0, getattr(circle, "elon_cybertruck_timer", 0.0) - sim_dt)
                    circle.elon_ultimate_timer = max(0.0, getattr(circle, "elon_ultimate_timer", 0.0) - sim_dt)
                    if circle.elon_skill_state is not None:
                        circle.elon_skill_state["timer"] = max(0.0, circle.elon_skill_state.get("timer", 0.0) - sim_dt)
                        if circle.elon_skill_state["timer"] <= 0:
                            circle.elon_skill_state = None
                    owner_index = circles.index(circle)
                    if circle.elon_cybertruck_active:
                        has_live_barrier = any(
                            other.health > 0
                            and other.character_type == "Cybertruck"
                            and getattr(other, "barrier_owner_index", -1) == owner_index
                            for other in circles
                        )
                        if not has_live_barrier or circle.elon_cybertruck_timer <= 0:
                            circle.elon_cybertruck_active = False
                            for other in circles:
                                if other.character_type == "Cybertruck" and getattr(other, "barrier_owner_index", -1) == owner_index:
                                    other.health = 0
                    if circle.elon_ultimate_active:
                        has_live_rocket = any(
                            bullet.source == "elon_mars_ultimate" and bullet.owner_index == owner_index
                            for bullet in bullets
                        )
                        if not has_live_rocket or circle.elon_ultimate_timer <= 0:
                            circle.elon_ultimate_active = False
                abducting_rocket = getattr(circle, "elon_abducted_by", None)
                if abducting_rocket is not None:
                    if abducting_rocket in bullets:
                        passenger_indices = getattr(abducting_rocket, "elon_passenger_indices", [])
                        circle_index = circles.index(circle)
                        slot = passenger_indices.index(circle_index) if circle_index in passenger_indices else 0
                        passenger_count = max(1, len(passenger_indices))
                        rocket_speed = math.hypot(abducting_rocket.vx, abducting_rocket.vy)
                        if rocket_speed > 0:
                            dir_x = abducting_rocket.vx / rocket_speed
                            dir_y = abducting_rocket.vy / rocket_speed
                        else:
                            dir_x, dir_y = 1.0, 0.0
                        side_x = -dir_y
                        side_y = dir_x
                        slot_offset = (slot - (passenger_count - 1) / 2.0) * circle.radius * 1.35
                        circle.x = abducting_rocket.x - dir_x * abducting_rocket.size * 0.18 + side_x * slot_offset
                        circle.y = abducting_rocket.y - dir_y * abducting_rocket.size * 0.18 + side_y * slot_offset
                        circle.vx = 0.0
                        circle.vy = 0.0
                        circle.impulse_vx = 0.0
                        circle.impulse_vy = 0.0
                        circle.impulse_wall_bounces_remaining = 0
                        continue
                    circle.elon_abducted_by = None
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
                        circle.ultimate_cooldown_timer -= sim_dt * cooldown_multiplier
                        if circle.controller == "ai" and circle.ultimate_cooldown_timer <= 0:
                            activate_ultimate(circle)
                elif circle.character_type == "Do Mixi":
                    if circle.ultimate_active:
                        circle.ultimate_duration_timer -= sim_dt
                        if circle.ultimate_duration_timer <= 0:
                            circle.ultimate_active = False
                            circle.ultimate_cooldown_timer = 7.0
                    else:
                        circle.ultimate_cooldown_timer -= sim_dt * cooldown_multiplier
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
                elif circle.character_type == "Epstein":
                    circle.ultimate_cooldown_timer = max(0.0, circle.ultimate_cooldown_timer - sim_dt * cooldown_multiplier)
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
                    circle.faker_skill_cooldown_timer = max(0.0, circle.faker_skill_cooldown_timer - sim_dt * cooldown_rate * cooldown_multiplier)
                    circle.faker_ultimate_cooldown_timer = max(0.0, circle.faker_ultimate_cooldown_timer - sim_dt * cooldown_multiplier)
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
                elif circle.character_type == "Elon Musk":
                    pass
                elif circle.character_type == "Mambo Mario":
                    pass
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
                            circle.bullet_timer -= sim_dt * cooldown_multiplier
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
                                                    damage=30,
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
                            circle.bullet_timer -= sim_dt * cooldown_multiplier
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
                            circle.bullet_timer -= sim_dt * cooldown_multiplier
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
                        elif circle.character_type == "Epstein":
                            circle.bullet_timer -= sim_dt * cooldown_multiplier
                            if circle.bullet_timer <= 0 and circle.target and circle.target.health > 0 and circle.epstein_ultimate_stage != "summon_intro":
                                fire_epstein_shadow_contract(circle)
                                add_gojo_technique_explosion(red_explosions, circle.x, circle.y, circle.radius * 1.2, epstein_shadow_colors)
                                circle.bullet_timer = 0.5
                                if circle.epstein_blackmail_cooldown <= 0 and random.random() < 0.45:
                                    activate_epstein_blackmail(circle)
                                elif circle.epstein_network_cooldown <= 0 and random.random() < 0.25:
                                    activate_epstein_network_surge(circle)
                                elif circle.epstein_shadowstep_cooldown <= 0 and random.random() < 0.35:
                                    activate_epstein_shadowstep(circle)
                        elif circle.character_type == "Epstein Thrall":
                            circle.bullet_timer -= sim_dt * cooldown_multiplier
                            if circle.bullet_timer <= 0 and circle.target and circle.target.health > 0:
                                fire_epstein_shadow_contract(circle)
                                add_gojo_technique_explosion(red_explosions, circle.x, circle.y, circle.radius * 0.9, epstein_shadow_colors)
                                circle.bullet_timer = 0.5 if getattr(circle, "epstein_corruption_type", None) == "speed" else 0.68
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
                                circle.bullet_timer -= sim_dt * cooldown_multiplier
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
                        elif circle.character_type == "Mambo Mario":
                            red_speed = (300.0 * 3.0) / 1.3
                            projectile_speed = red_speed * 0.5
                            if getattr(circle, "mario_ultimate_stage", None) == "empowered":
                                circle.mario_fireball_timer -= sim_dt
                                if circle.mario_fireball_timer <= 0 and circle.target and circle.target.health > 0:
                                    aim_unit = get_lead_unit_vector(circle, circle.target, projectile_speed)
                                    if aim_unit:
                                        ux, uy = aim_unit
                                        fireball = Bullet(
                                            circle.x,
                                            circle.y - circle.radius * 0.15,
                                            ux * projectile_speed,
                                            uy * projectile_speed,
                                            circles.index(circle),
                                            color=(255, 120, 50),
                                            size=max(10, int(18 * (match_assets["radius"] / radius))),
                                            image=getattr(circle, "fireball_image", None),
                                            source="mambo_mario_fireball",
                                            damage=150 + getattr(circle, "mario_skill_damage_bonus", 0),
                                            attack_type="skill",
                                        )
                                        bullets.append(fireball)
                                    circle.mario_fireball_timer = 0.2
                            elif getattr(circle, "mario_ultimate_stage", None) is None:
                                circle.mario_shell_timer -= sim_dt
                                if circle.mario_shell_timer <= 0 and circle.target and circle.target.health > 0:
                                    aim_unit = get_lead_unit_vector(circle, circle.target, projectile_speed)
                                    if aim_unit:
                                        ux, uy = aim_unit
                                        shell = Bullet(
                                            circle.x,
                                            circle.y - circle.radius * 0.15,
                                            ux * projectile_speed,
                                            uy * projectile_speed,
                                            circles.index(circle),
                                            color=(110, 255, 120),
                                            size=max(10, int(18 * (match_assets["radius"] / radius))),
                                            image=getattr(circle, "green_shell_image", None),
                                            source="mambo_mario_shell",
                                            damage=100,
                                            attack_type="normal",
                                            wall_bounces_remaining=4,
                                        )
                                        bullets.append(shell)
                                    circle.mario_shell_timer = 0.6
                        elif circle.character_type == "Elon Musk":
                            if circle.elon_passive_stun_timer <= 0 and random.random() < 0.025 * sim_dt:
                                circle.elon_passive_stun_timer = 0.45
                                add_status_text(damage_texts, circle, "Software Update", color=(255, 225, 110), ttl=0.8)
                            if circle.controller == "ai" and circle.target and circle.elon_passive_stun_timer <= 0:
                                if circle.elon_ultimate_cooldown <= 0 and not circle.elon_ultimate_active and random.random() < 0.0025:
                                    activate_elon_mars_colonization(circle)
                                elif circle.elon_cybertruck_cooldown <= 0 and not circle.elon_cybertruck_active and random.random() < 0.007:
                                    activate_elon_cybertruck_shield(circle)
                                elif circle.elon_rocket_punch_cooldown <= 0 and circle.elon_skill_state is None and random.random() < 0.012:
                                    activate_elon_rocket_punch(circle)
                            if circle.elon_passive_stun_timer > 0:
                                circle.elon_passive_stun_timer = max(0.0, circle.elon_passive_stun_timer - sim_dt)
                            elif circle.elon_skill_state is None and not circle.elon_ultimate_active:
                                circle.bullet_timer -= sim_dt * cooldown_multiplier
                                if circle.bullet_timer <= 0 and circle.target and circle.target.health > 0:
                                    dogecoin_speed = ((300.0 * 3.0) / 1.3) * 0.5
                                    aim_unit = get_lead_unit_vector(circle, circle.target, dogecoin_speed)
                                    if aim_unit:
                                        ux, uy = aim_unit
                                        bullets.append(
                                            Bullet(
                                                circle.x,
                                                circle.y - circle.radius * 0.1,
                                                ux * dogecoin_speed,
                                                uy * dogecoin_speed,
                                                circles.index(circle),
                                                color=(255, 220, 50),
                                                size=max(8, (match_assets["dogecoin_image"].get_width() // 2) if match_assets.get("dogecoin_image") else int(circle.radius * 0.8)),
                                                image=match_assets.get("dogecoin_image"),
                                                source="elon_dogecoin",
                                                damage=28,
                                                attack_type="normal",
                                                crit_chance=0.18,
                                                crit_damage=56,
                                                bounce_forever=random.random() < 0.3,
                                            )
                                        )
                                        add_faker_magic_flame(faker_magic_flames, circle.x, circle.y, max(circle.radius * 0.45, 10.0), (255, 220, 80))
                                    circle.bullet_timer = max(0.16, 0.62 / get_elon_attack_speed_multiplier(circle))
                        elif circle.character_type == "Mambo Zomboss":
                            if circle.health <= circle.max_health * 0.5 and not getattr(circle, "zomboss_rampage", False):
                                circle.zomboss_rampage = True
                                circle.zomboss_banner_timer = 2.2
                                circle.zomboss_stomp_timer = 1.6
                                circle.zomboss_missile_hell_timer = 3.0
                                circle.zomboss_laser_timer = 5.0
                                circle.zomboss_gadget_timer = min(circle.zomboss_gadget_timer, 4.0)
                                circle.zomboss_deploy_timer = min(circle.zomboss_deploy_timer, 3.4)
                                circle.zomboss_rocket_timer = min(circle.zomboss_rocket_timer, 4.8)
                                circle.zomboss_freeze_timer = min(circle.zomboss_freeze_timer, 6.6)
                                screen_shake_timer = max(screen_shake_timer, 0.18)
                                screen_shake_strength = max(screen_shake_strength, 8.0)
                            circle.zomboss_banner_timer = max(0.0, getattr(circle, "zomboss_banner_timer", 0.0) - sim_dt)
                            circle.zomboss_normal_attack_timer -= sim_dt
                            if circle.zomboss_normal_attack_timer <= 0 and circle.target and circle.target.health > 0:
                                circle.zomboss_attack_cycle += 1
                                is_charged = circle.zomboss_attack_cycle % 5 == 0
                                fire_zomboss_pea_spread(circle, charged=is_charged)
                                circle.zomboss_normal_attack_timer = 0.58 if getattr(circle, "zomboss_rampage", False) else 0.85

                            circle.zomboss_gadget_timer -= sim_dt
                            if circle.zomboss_gadget_timer <= 0:
                                spawn_zomboss_gadget(circle)
                                circle.zomboss_gadget_timer = random.uniform(5.5, 8.0) if getattr(circle, "zomboss_rampage", False) else random.uniform(8.0, 12.0)

                            circle.zomboss_deploy_timer -= sim_dt
                            if circle.zomboss_deploy_timer <= 0:
                                trigger_zomboss_deployment(circle, summon_count=random.randint(2, 3) if random.random() < 0.75 else 1)
                                circle.zomboss_deploy_timer = random.uniform(4.2, 5.8) if getattr(circle, "zomboss_rampage", False) else random.uniform(6.5, 8.2)

                            circle.zomboss_rocket_timer -= sim_dt
                            if circle.zomboss_rocket_timer <= 0:
                                trigger_zomboss_rocket_barrage(circle, missile_hell=getattr(circle, "zomboss_rampage", False) and random.random() < 0.55)
                                circle.zomboss_rocket_timer = random.uniform(4.8, 6.8) if getattr(circle, "zomboss_rampage", False) else random.uniform(7.5, 9.8)

                            circle.zomboss_freeze_timer -= sim_dt
                            if circle.zomboss_freeze_timer <= 0:
                                trigger_zomboss_beam(circle, laser_sweep=getattr(circle, "zomboss_rampage", False) and random.random() < 0.5)
                                circle.zomboss_freeze_timer = random.uniform(5.5, 7.5) if getattr(circle, "zomboss_rampage", False) else random.uniform(10.0, 12.5)

                            if getattr(circle, "zomboss_rampage", False):
                                circle.zomboss_stomp_timer -= sim_dt
                                if circle.zomboss_stomp_timer <= 0:
                                    trigger_zomboss_shockwave(circle)
                                    circle.zomboss_stomp_timer = random.uniform(4.5, 6.0)
                                circle.zomboss_missile_hell_timer -= sim_dt
                                if circle.zomboss_missile_hell_timer <= 0:
                                    trigger_zomboss_rocket_barrage(circle, missile_hell=True)
                                    circle.zomboss_missile_hell_timer = random.uniform(7.5, 9.2)
                                circle.zomboss_laser_timer -= sim_dt
                                if circle.zomboss_laser_timer <= 0:
                                    trigger_zomboss_beam(circle, laser_sweep=True)
                                    circle.zomboss_laser_timer = random.uniform(8.0, 10.5)
                        if not gojo_voice_intro_active and not epstein_voice_intro_active:
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
                            elif circle.character_type == "Cybertruck":
                                circle.vx = 0.0
                                circle.vy = 0.0
                                circle.impulse_vx = 0.0
                                circle.impulse_vy = 0.0
                            elif circle.character_type == "Dummy Diddy":
                                circle.vx = 0.0
                                circle.vy = 0.0
                            elif getattr(circle, "stun_timer", 0.0) > 0 or getattr(circle, "elon_passive_stun_timer", 0.0) > 0:
                                circle.vx = 0.0
                                circle.vy = 0.0
                                circle.impulse_vx *= max(0.0, 1.0 - 8.0 * sim_dt)
                                circle.impulse_vy *= max(0.0, 1.0 - 8.0 * sim_dt)
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
                            elif circle.character_type == "Epstein" and circle.controller == "ai":
                                if circle.ultimate_active or circle.epstein_untargetable:
                                    circle.vx = 0.0
                                    circle.vy = 0.0
                                elif circle.target and circle.target.health > 0:
                                    dx = circle.target.x - circle.x
                                    dy = circle.target.y - circle.y
                                    dist = math.hypot(dx, dy)
                                    move_speed = circle.base_speed * get_epstein_speed_multiplier(circle) * (1.15 if circle.epstein_phase_two else 0.85)
                                    if dist > 0:
                                        if dist < arena_width * 0.34:
                                            circle.vx = (-dx / dist) * move_speed
                                            circle.vy = (-dy / dist) * move_speed
                                        else:
                                            side_x = -dy / dist
                                            side_y = dx / dist
                                            circle.vx = (side_x * 0.72 + dx / dist * 0.28) * move_speed
                                            circle.vy = (side_y * 0.72 + dy / dist * 0.28) * move_speed
                            elif circle.character_type == "Epstein Thrall" and circle.target and circle.target.health > 0:
                                dx = circle.target.x - circle.x
                                dy = circle.target.y - circle.y
                                dist = math.hypot(dx, dy)
                                if dist > 0:
                                    move_speed = circle.base_speed * get_epstein_speed_multiplier(circle)
                                    circle.vx = (dx / dist) * move_speed
                                    circle.vy = (dy / dist) * move_speed
                            elif circle.character_type == "Golden Titan" and circle.target and circle.target.health > 0:
                                dx = circle.target.x - circle.x
                                dy = circle.target.y - circle.y
                                dist = math.hypot(dx, dy)
                                if dist > 0:
                                    move_speed = circle.base_speed * get_epstein_speed_multiplier(circle)
                                    circle.vx = (dx / dist) * move_speed
                                    circle.vy = (dy / dist) * move_speed
                            elif circle.controller == "player1":
                                keys = pygame.key.get_pressed()
                                if getattr(circle, "zomboss_freeze_timer", 0.0) > 0:
                                    circle.vx, circle.vy = 0.0, 0.0
                                else:
                                    move_speed = 280.0 * (0.35 if getattr(circle, "zomboss_slow_timer", 0.0) > 0 else 1.0)
                                    if circle.character_type == "Epstein":
                                        move_speed = 300.0 * get_epstein_speed_multiplier(circle) * (0.35 if getattr(circle, "zomboss_slow_timer", 0.0) > 0 else 1.0)
                                    circle.vx, circle.vy = get_controlled_velocity(keys, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, speed=move_speed)
                            elif circle.controller == "player2":
                                keys = pygame.key.get_pressed()
                                if getattr(circle, "zomboss_freeze_timer", 0.0) > 0:
                                    circle.vx, circle.vy = 0.0, 0.0
                                else:
                                    move_speed = 280.0 * (0.35 if getattr(circle, "zomboss_slow_timer", 0.0) > 0 else 1.0)
                                    if circle.character_type == "Epstein":
                                        move_speed = 300.0 * get_epstein_speed_multiplier(circle) * (0.35 if getattr(circle, "zomboss_slow_timer", 0.0) > 0 else 1.0)
                                    circle.vx, circle.vy = get_controlled_velocity(keys, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, speed=move_speed)
                            elif circle.controller == "zombie" and is_mambo_enemy(circle):
                                if circle.character_type == "Mambo Zomboss":
                                    circle.x = getattr(circle, "anchor_x", circle.x)
                                    circle.y = getattr(circle, "anchor_y", circle.y)
                                    circle.vx = 0.0
                                    circle.vy = 0.0
                                    circle.impulse_vx = 0.0
                                    circle.impulse_vy = 0.0
                                    continue
                                if circle.character_type == "Mambo Mario" and getattr(circle, "mario_ultimate_stage", None) in ("jump", "flower_rise", "flower_fall"):
                                    circle.vx = 0.0
                                    circle.vy = 0.0
                                    continue
                                humans = [c for c in circles if c.health > 0 and not is_mambo_enemy(c)]
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
                        if getattr(circle, "martian_citizenship_timer", 0.0) > 0 and circle.character_type != "Cybertruck":
                            current_speed = math.hypot(circle.vx, circle.vy)
                            if current_speed > 0:
                                boost_speed = current_speed * 1.12
                                circle.vx = (circle.vx / current_speed) * boost_speed
                                circle.vy = (circle.vy / current_speed) * boost_speed
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
                if circles[i].health <= 0:
                    continue
                for j in range(i + 1, len(circles)):
                    if circles[j].health <= 0:
                        continue
                    if game_mode == "zombie" and (
                        is_player_controlled_human(circles[i]) or is_player_controlled_human(circles[j])
                    ):
                        continue
                    resolve_circle_collision(circles[i], circles[j])
                    if game_mode == "zombie":
                        circles[i].clamp_to_trapezoid(0, 0, arena_width, arena_height)
                        circles[j].clamp_to_trapezoid(0, 0, arena_width, arena_height)
                        for fixed_circle in (circles[i], circles[j]):
                            if fixed_circle.character_type == "Mambo Zomboss":
                                fixed_circle.x = getattr(fixed_circle, "anchor_x", fixed_circle.x)
                                fixed_circle.y = getattr(fixed_circle, "anchor_y", fixed_circle.y)
                                fixed_circle.vx = 0.0
                                fixed_circle.vy = 0.0
                                fixed_circle.impulse_vx = 0.0
                                fixed_circle.impulse_vy = 0.0
                    else:
                        circles[i].bounce_impulse_off_wall(arena_width, arena_height)
                        circles[j].bounce_impulse_off_wall(arena_width, arena_height)
                        circles[i].clamp_to_arena(arena_width, arena_height)
                        circles[j].clamp_to_arena(arena_width, arena_height)
            if game_mode == "zombie":
                # Track mambos that die this frame
                mambos_before = [c for c in circles if is_mambo_enemy(c) and c.health > 0]
                
                for z in circles:
                    if not is_mambo_enemy(z) or z.health <= 0:
                        continue
                    for h in circles:
                        if is_mambo_enemy(h) or h.health <= 0:
                            continue
                        if z.hit(h):
                            base_damage = getattr(z, 'damage', 20)
                            wave_bonus = current_wave * 0.5
                            z_damage = (base_damage + wave_bonus) * sim_dt
                            apply_damage_to_circle(damage_texts, h, z_damage, False)
                
                # Check for dead mambos and reward players
                mambos_after = [c for c in circles if is_mambo_enemy(c) and c.health > 0]
                mambos_before_ids = set(id(c) for c in mambos_before)
                mambos_after_ids = set(id(c) for c in mambos_after)
                dead_mambos = mambos_before_ids - mambos_after_ids
                
                if dead_mambos:
                    dead_count = len(dead_mambos)
                    # Reward all alive human players
                    for h in circles:
                        if h.health > 0 and not is_mambo_enemy(h):
                            # Heal 100 HP per mambo killed
                            h.health = min(h.health + 100 * dead_count, h.max_health)
                            # Increase damage by 30 per mambo killed
                            if hasattr(h, 'damage'):
                                h.damage = getattr(h, 'damage', 20) + 30 * dead_count

            for circle in circles:
                if circle.health > 0 and circle.controller == "ai" and circle.base_speed > 0:
                    if gojo_voice_intro_active or epstein_voice_intro_active:
                        continue
                    if (
                        active_gojo_domain is not None
                        and circle is not active_gojo_domain
                        and active_gojo_domain.gojo_domain_freeze_timer > 0
                    ):
                        continue
                    normalize_velocity(circle, circle.base_speed)

            active_gojo_infinity_users = []
            gojo_infinity_radius = max(76.0, radius * 1.52)
            for idx, circle in enumerate(circles):
                if circle.health <= 0 or circle.character_type != "Gojo Satoru":
                    continue
                if gojo_voice_intro_active or epstein_voice_intro_active:
                    continue
                active_gojo_infinity_users.append((idx, circle))

            for circle_index, circle in enumerate(circles):
                if circle.health <= 0:
                    continue
                for gojo_index, gojo_circle in active_gojo_infinity_users:
                    if circle_index == gojo_index:
                        continue
                    if not circles_are_hostile(gojo_circle, circle):
                        continue
                    apply_gojo_infinity_slow(gojo_circle, circle, ("vx", "vy"), gojo_infinity_radius)
                    apply_gojo_infinity_slow(gojo_circle, circle, ("impulse_vx", "impulse_vy"), gojo_infinity_radius)

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
                for gojo_index, gojo_circle in active_gojo_infinity_users:
                    if bullet.owner_index == gojo_index or bullet_ignores_gojo_infinity(bullet, gojo_index):
                        continue
                    apply_gojo_infinity_slow(gojo_circle, bullet, ("vx", "vy"), gojo_infinity_radius)
                bullet.move(sim_dt)
                if bullet.source == "gojo_purple":
                    add_gojo_purple_trail(purple_trails, bullet.x, bullet.y, bullet.size)
                elif bullet.source == "faker_charm":
                    add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(bullet.size * 0.8, 8.0), random.choice([(255, 120, 220), (120, 220, 255), (255, 190, 240)]))
                elif bullet.source == "faker_orb":
                    add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(bullet.size * 0.8, 8.0), random.choice([(110, 210, 255), (150, 230, 255), (210, 245, 255)]))
                elif bullet.source == "elon_rocket_punch":
                    add_elon_thruster_trail(bullet, 1.0)
                elif bullet.source == "elon_mars_ultimate":
                    add_elon_thruster_trail(bullet, 2.3)
                if bullet.source in ("elon_rocket_punch", "elon_mars_ultimate"):
                    if 0 <= bullet.x <= arena_width and 0 <= bullet.y <= arena_height:
                        if not getattr(bullet, "elon_has_entered_arena", False):
                            bullet.elon_has_entered_arena = True
                    elif not getattr(bullet, "elon_has_entered_arena", False):
                        new_bullets.append(bullet)
                        continue
                if bullet.pushes_projectiles or bullet.pushes_characters:
                    if bullet.pushes_projectiles:
                        for other_bullet in bullets:
                            if other_bullet is bullet:
                                continue
                            if (
                                bullet.source == "gojo_blue"
                                and bullet.hold_timer <= 0
                                and bullet.field_activation_delay <= 0
                            ):
                                touch_distance = bullet.size + other_bullet.size
                                if math.hypot(other_bullet.x - bullet.x, other_bullet.y - bullet.y) <= touch_distance:
                                    convert_bullet_to_gojo_owner(other_bullet, bullet.owner_index)
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
                elif bullet.source == "mambo_mario_shell":
                    bounced = bullet.bounce_off_wall(arena_width, arena_height)
                    if bounced and bullet.wall_bounces_remaining <= 0:
                        add_gojo_technique_explosion(red_explosions, bullet.x, bullet.y, bullet.size * 2.1, mambo_mario_fire_colors)
                        continue
                elif bullet.source == "epstein_contract":
                    bounced = bullet.bounce_off_wall(arena_width, arena_height)
                    if bounced:
                        add_gojo_technique_explosion(red_explosions, bullet.x, bullet.y, bullet.size * 2.0, epstein_shadow_colors)
                        if bullet.wall_bounces_remaining <= 0:
                            continue

                touched_wall = (
                    bullet.x - bullet.size <= 0
                    or bullet.x + bullet.size >= arena_width
                    or bullet.y - bullet.size <= 0
                    or bullet.y + bullet.size >= arena_height
                )
                if bullet.source in ("elon_rocket_punch", "elon_mars_ultimate") and getattr(bullet, "elon_has_entered_arena", False):
                    if getattr(bullet, "elon_border_passes_remaining", 0) > 0:
                        if touched_wall:
                            new_bullets.append(bullet)
                            continue
                        bullet.elon_border_passes_remaining = 0
                if bullet.source == "mambo_mario_shell" and bounced:
                    new_bullets.append(bullet)
                    continue
                if bullet.source == "epstein_contract" and bounced:
                    new_bullets.append(bullet)
                    continue
                if bullet.source == "gojo_red" and touched_wall:
                    impact_x = min(max(bullet.x, 0), arena_width)
                    impact_y = min(max(bullet.y, 0), arena_height)
                    add_gojo_technique_explosion(red_explosions, impact_x, impact_y, bullet.size * 2.2, gojo_red_colors)
                    continue
                if bullet.source == "mambo_mario_fireball" and touched_wall:
                    impact_x = min(max(bullet.x, 0), arena_width)
                    impact_y = min(max(bullet.y, 0), arena_height)
                    add_gojo_technique_explosion(red_explosions, impact_x, impact_y, bullet.size * 2.4, mambo_mario_fire_colors)
                    continue
                if bullet.source in ("zomboss_pea", "zomboss_turret_pea") and touched_wall:
                    add_gojo_technique_explosion(red_explosions, bullet.x, bullet.y, bullet.size * 1.7, [(120, 255, 120), (210, 255, 120), (255, 255, 255)])
                    continue
                if bullet.source == "zomboss_charged_pea" and touched_wall:
                    impact_x = min(max(bullet.x, 0), arena_width)
                    impact_y = min(max(bullet.y, 0), arena_height)
                    splash_radius = max(48.0, bullet.size * 3.8)
                    add_gojo_technique_explosion(red_explosions, impact_x, impact_y, splash_radius, [(110, 255, 120), (255, 205, 90), (255, 255, 255)])
                    owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                    for idx, circle in enumerate(circles):
                        if idx == bullet.owner_index or circle.health <= 0:
                            continue
                        if not circles_are_hostile(owner_circle, circle):
                            continue
                        if math.hypot(circle.x - impact_x, circle.y - impact_y) <= splash_radius:
                            apply_damage_to_circle(damage_texts, circle, max(1.0, circle.max_health * 0.05), False)
                    continue
                if bullet.source == "gojo_blue" and touched_wall:
                    continue
                if bullet.source == "elon_rocket_punch" and touched_wall:
                    owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                    explode_elon_rocket(
                        owner_circle,
                        min(max(bullet.x, 0), arena_width),
                        min(max(bullet.y, 0), arena_height),
                        failed_landing=getattr(bullet, "elon_failed_landing", False),
                    )
                    if owner_circle is not None:
                        owner_circle.elon_skill_state = None
                    continue
                if bullet.source == "elon_mars_ultimate" and touched_wall:
                    owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                    impact_x = min(max(bullet.x, 0), arena_width)
                    impact_y = min(max(bullet.y, 0), arena_height)
                    splash_radius = get_elon_rocket_aoe_radius(projectile=bullet)
                    add_gojo_technique_explosion(red_explosions, impact_x, impact_y, splash_radius, elon_rocket_colors)
                    if owner_circle is not None:
                        for idx, circle in enumerate(circles):
                            if idx == bullet.owner_index or circle.health <= 0:
                                continue
                            if not circles_are_hostile(owner_circle, circle):
                                continue
                            if math.hypot(circle.x - impact_x, circle.y - impact_y) <= splash_radius + circle.radius:
                                apply_damage_to_circle(damage_texts, circle, max(500.0, circle.max_health * 0.05), True)
                        release_mars_passengers(bullet, owner_circle)
                        owner_circle.elon_ultimate_active = False
                        owner_circle.elon_skill_state = None
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
                        if bullet.source == "epstein_contract" and not circles_are_hostile(owner_circle, circle):
                            continue
                        if bullet.source == "mambo_mario_fireball" and not circles_are_hostile(owner_circle, circle):
                            continue
                        if bullet.source == "mambo_mario_shell" and not circles_are_hostile(owner_circle, circle):
                            continue
                        if bullet.source in ("zomboss_pea", "zomboss_turret_pea", "zomboss_charged_pea") and not circles_are_hostile(owner_circle, circle):
                            continue
                        if bullet.source in ("elon_dogecoin", "elon_rocket_punch", "elon_mars_ultimate") and not circles_are_hostile(owner_circle, circle):
                            continue
                        hit_radius = circle.radius + (bullet.size * 0.55 if bullet.source == "gojo_purple" else 0.0)
                        # Check for Cybertruck barrier reflection
                        if circle.character_type == "Cybertruck" and getattr(circle, "reflects_projectiles", False):
                            if owner_circle is not None and not circles_are_hostile(owner_circle, circle):
                                continue
                            if bullet.source.startswith("elon_"):
                                continue
                            # Reflect the bullet
                            dx = bullet.x - circle.x
                            dy = bullet.y - circle.y
                            dist = math.hypot(dx, dy)
                            if dist > 0:
                                # Reflect velocity vector
                                nx = dx / dist
                                ny = dy / dist
                                # Calculate reflection: v' = v - 2(v·n)n
                                dot_product = bullet.vx * nx + bullet.vy * ny
                                bullet.vx = bullet.vx - 2 * dot_product * nx
                                bullet.vy = bullet.vy - 2 * dot_product * ny
                                # Add visual effect
                                add_faker_magic_flame(faker_magic_flames, bullet.x, bullet.y, max(bullet.size * 0.8, 8.0), (200, 200, 200))
                                if getattr(circle, "shatter_on_hit", False):
                                    circle.health = 0
                                    barrier_owner_index = getattr(circle, "barrier_owner_index", -1)
                                    if 0 <= barrier_owner_index < len(circles):
                                        circles[barrier_owner_index].elon_cybertruck_active = False
                                        circles[barrier_owner_index].elon_cybertruck_timer = 0.0
                                    add_gojo_technique_explosion(red_explosions, circle.x, circle.y, circle.radius * 1.4, elon_rocket_colors)
                                continue  # Skip further processing for this bullet-circle pair

                        if math.hypot(circle.x - bullet.x, circle.y - bullet.y) <= hit_radius:
                            if bullet.source == "elon_mars_ultimate":
                                if idx in bullet.hit_targets or getattr(circle, "elon_abducted_by", None) is bullet:
                                    continue
                                bullet.hit_targets.add(idx)
                                bullet.elon_passenger_indices.append(idx)
                                circle.elon_abducted_by = bullet
                                circle.stun_timer = max(getattr(circle, "stun_timer", 0.0), 2.0)
                                add_status_text(damage_texts, circle, "+Martian Citizenship", color=(255, 190, 90))
                                continue
                            if bullet.source == "faker_charm":
                                if not circles_are_hostile(owner_circle, circle):
                                    continue
                                if circle.character_type == "Dummy Diddy":
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
                            if bullet.source == "zomboss_charged_pea":
                                splash_radius = max(circle.radius * 1.25, bullet.size * 3.8)
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    splash_radius,
                                    [(110, 255, 120), (255, 205, 90), (255, 255, 255)],
                                )
                                for splash_idx, splash_target in enumerate(circles):
                                    if splash_idx == bullet.owner_index or splash_target.health <= 0:
                                        continue
                                    if not circles_are_hostile(owner_circle, splash_target):
                                        continue
                                    if math.hypot(splash_target.x - bullet.x, splash_target.y - bullet.y) <= splash_radius:
                                        apply_damage_to_circle(damage_texts, splash_target, max(1.0, splash_target.max_health * 0.05), False)
                                hit_any = True
                                break
                            if bullet.source in ("gojo_blue", "gojo_purple") and idx in bullet.hit_targets:
                                continue
                            if circle.character_type == "Dummy Diddy":
                                hit_any = True
                                break
                            if bullet.damage is not None:
                                if hasattr(bullet, "zomboss_damage_fraction"):
                                    is_crit = False
                                    damage = max(1.0, circle.max_health * bullet.zomboss_damage_fraction)
                                    owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                    attack_type = getattr(bullet, "attack_type", "skill")
                                else:
                                    is_crit = random.random() < bullet.crit_chance
                                    owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                    base_damage = bullet.crit_damage if is_crit else bullet.damage
                                    attack_type = bullet.attack_type or "skill"
                                    damage = scale_apocalypse_damage(owner, base_damage, attack_type)
                            elif bullet.source == "mika":
                                is_crit = True
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = 8
                                attack_type = "normal"
                                damage = scale_apocalypse_damage(owner, base_damage, attack_type)
                            elif bullet.source == "vu_bamia":
                                is_crit = False
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                attack_type = "skill"
                                damage = scale_apocalypse_damage(owner, 36, attack_type)
                            elif bullet.size == 5 and bullet.color == (255, 220, 50):  # normal yellow bullets
                                is_crit = random.random() < 0.1
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = 2 if is_crit else 1
                                attack_type = "normal"
                                damage = scale_apocalypse_damage(owner, base_damage, attack_type)
                            else:
                                is_crit = random.random() < 0.1
                                owner = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                                base_damage = 30 if is_crit else 15
                                attack_type = "normal"
                                damage = scale_apocalypse_damage(owner, base_damage, attack_type)
                            damage = consume_epstein_mark_bonus(owner, circle, damage)
                            damage = apply_titan_adaptive_resistance(circle, damage, attack_type)
                            apply_damage_to_circle(damage_texts, circle, damage, is_crit)
                            if bullet.source == "elon_dogecoin":
                                bounce_scale = 0.65 if getattr(bullet, "bounce_forever", False) else 0.35
                                circle.impulse_vx += bullet.vx * bounce_scale
                                circle.impulse_vy += bullet.vy * bounce_scale
                                if getattr(bullet, "bounce_forever", False):
                                    circle.impulse_wall_bounces_remaining = max(circle.impulse_wall_bounces_remaining, 5)
                            if bullet.source == "elon_rocket_punch":
                                explode_elon_rocket(owner, bullet.x, bullet.y, failed_landing=getattr(bullet, "elon_failed_landing", False))
                                if owner is not None:
                                    owner.elon_skill_state = None
                            if bullet.source == "epstein_contract":
                                add_gojo_technique_explosion(red_explosions, bullet.x, bullet.y, bullet.size * 2.1, epstein_shadow_colors)
                                apply_epstein_mark(bullet.owner_index, circle)
                            if bullet.source == "vu_bamia_ultimate" and owner is not None and owner.health > 0:
                                owner.health = min(owner.max_health, owner.health + 12)
                            if is_crit and 0 <= bullet.owner_index < len(circles):
                                owner = circles[bullet.owner_index]
                                if owner.character_type == "Misono Mika" and owner.health > 0:
                                    owner.health = min(owner.max_health, owner.health + owner.max_health * 0.01)
                            if bullet.source == "gojo_red":
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    max(circle.radius * 0.9, bullet.size * 2.8),
                                    gojo_red_colors,
                                )
                            elif bullet.source == "mambo_mario_fireball":
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    max(circle.radius * 0.85, bullet.size * 2.6),
                                    mambo_mario_fire_colors,
                                )
                            elif bullet.source == "mambo_mario_shell":
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    max(circle.radius * 0.8, bullet.size * 2.3),
                                    mambo_mario_fire_colors,
                                )
                            elif bullet.source in ("zomboss_pea", "zomboss_turret_pea"):
                                add_gojo_technique_explosion(
                                    red_explosions,
                                    bullet.x,
                                    bullet.y,
                                    max(circle.radius * 0.7, bullet.size * 1.8),
                                    [(110, 255, 120), (230, 255, 150), (255, 255, 255)],
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
                        if bullet.source == "elon_mars_ultimate":
                            owner_circle = circles[bullet.owner_index] if 0 <= bullet.owner_index < len(circles) else None
                            if not getattr(bullet, "elon_returning", False):
                                target_circle = circles[bullet.target_index] if 0 <= bullet.target_index < len(circles) else None
                                if target_circle is not None and target_circle.health > 0:
                                    turn_distance = max(target_circle.radius + bullet.size * 0.15, bullet.size * 0.3)
                                    if math.hypot(target_circle.x - bullet.x, target_circle.y - bullet.y) <= turn_distance:
                                        bullet.elon_returning = True
                                        bullet.vx = -bullet.vx
                                        bullet.vy = -bullet.vy
                            elif owner_circle is not None:
                                release_distance = max(owner_circle.radius + bullet.size * 0.15, bullet.size * 0.3)
                                if math.hypot(owner_circle.x - bullet.x, owner_circle.y - bullet.y) <= release_distance:
                                    release_mars_passengers(bullet, owner_circle)
                                    owner_circle.elon_ultimate_active = False
                                    owner_circle.elon_skill_state = None
                                    continue
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
                                damage = consume_epstein_mark_bonus(owner, circle, damage)
                                damage = apply_titan_adaptive_resistance(circle, damage, attack_type)
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
            draw_surface.fill((20, 20, 30))
            faker_ultimate_visual = any(circle.character_type == "T1 Faker" and circle.ultimate_active for circle in circles)
            if faker_ultimate_visual:
                dark_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                dark_surface.fill((26, 10, 32, 56 if faker_ultimate_hitstop_timer <= 0 else 96))
                draw_surface.blit(dark_surface, (0, 0))
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
                    draw_surface.blit(video_surface, (padding, 0))
                else:
                    draw_infinite_void_background(draw_surface, pygame.Rect(padding, 0, original_window_width, window_height), elapsed_time)
            
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
                pygame.draw.circle(draw_surface, (255, 255, 255), (tube_left, 0), dot_radius)
                pygame.draw.circle(draw_surface, (255, 255, 255), (tube_right, 0), dot_radius)
                
                # Draw diagonal lines from dots to rectangle corners (funnel shape)
                pygame.draw.line(draw_surface, (255, 255, 255), (tube_left, 0), (render_arena_left, render_arena_top), 3)
                pygame.draw.line(draw_surface, (255, 255, 255), (tube_right, 0), (render_arena_left + arena_width, render_arena_top), 3)
                
                # Draw white lines to enclose the playable region (left, right, bottom)
                pygame.draw.line(draw_surface, (255, 255, 255), (render_arena_left, render_arena_top), (render_arena_left, render_arena_top + arena_height), 3)
                pygame.draw.line(draw_surface, (255, 255, 255), (render_arena_left + arena_width, render_arena_top), (render_arena_left + arena_width, render_arena_top + arena_height), 3)
                pygame.draw.line(draw_surface, (255, 255, 255), (render_arena_left, render_arena_top + arena_height), (render_arena_left + arena_width, render_arena_top + arena_height), 3)
            else:
                pygame.draw.rect(draw_surface, (200, 200, 200), border_rect, 3)

            draw_gojo_technique_explosions(draw_surface, red_explosions, render_arena_left, render_arena_top)
            draw_gojo_purple_trails(draw_surface, purple_trails, render_arena_left, render_arena_top)
            draw_faker_dust_trails(draw_surface, faker_dust_trails, render_arena_left, render_arena_top)
            draw_faker_magic_flames(draw_surface, faker_magic_flames, render_arena_left, render_arena_top)
            draw_faker_charm_status(draw_surface, circles, elapsed_time, render_arena_left, render_arena_top)
            draw_faker_soldier_waves(draw_surface, faker_waves, elapsed_time, render_arena_left, render_arena_top)
            faker_banner_owner = next((circle for circle in circles if circle.character_type == "T1 Faker" and circle.faker_ultimate_banner_timer > 0), None)
            if faker_banner_owner is not None:
                banner_rect = pygame.Rect(screen_width // 2 - 310, 32, 620, 76)
                pygame.draw.rect(draw_surface, (45, 12, 38), banner_rect, border_radius=18)
                pygame.draw.rect(draw_surface, (255, 105, 190), banner_rect, 3, border_radius=18)
                draw_text(draw_surface, "UNKILLABLE DEMON KING", banner_rect.x + 40, banner_rect.y + 18, color=(255, 245, 255), size=34)
            if gojo_domain_banner_owner is not None:
                banner_rect = pygame.Rect(screen_width // 2 - 340, 118, 680, 72)
                pygame.draw.rect(draw_surface, (34, 18, 54), banner_rect, border_radius=18)
                pygame.draw.rect(draw_surface, (205, 125, 255), banner_rect, 3, border_radius=18)
                draw_text(draw_surface, "Domain Expansion: Infinite Void", banner_rect.x + 34, banner_rect.y + 18, color=(248, 238, 255), size=32)
            zomboss_banner_owner = next((circle for circle in circles if circle.character_type == "Mambo Zomboss" and getattr(circle, "zomboss_banner_timer", 0.0) > 0), None)
            if zomboss_banner_owner is not None:
                banner_rect = pygame.Rect(screen_width // 2 - 300, 198, 600, 78)
                pygame.draw.rect(draw_surface, (42, 20, 14), banner_rect, border_radius=18)
                pygame.draw.rect(draw_surface, (255, 96, 72), banner_rect, 3, border_radius=18)
                draw_text(draw_surface, "ZOMBOT RAMPAGE MODE", banner_rect.x + 42, banner_rect.y + 20, color=(255, 240, 232), size=34)

            for gadget in zomboss_gadgets:
                gx = int(gadget["x"] + render_arena_left)
                gy = int(gadget["y"] + render_arena_top)
                build_ratio = 1.0 - min(1.0, gadget["build_timer"] / 1.0) if gadget["build_timer"] > 0 else 1.0
                pulse = 0.88 + 0.12 * math.sin(elapsed_time * 5.0 + gadget["pulse"])
                gadget_radius = gadget.get("radius", 20.0 if gadget.get("type") == "turret" else (24.0 if gadget.get("type") == "spawner" else 28.0))
                body_r = max(12, int(gadget_radius * (0.55 + 0.45 * build_ratio) * pulse))
                if gadget["type"] == "turret":
                    colors = [(80, 220, 120, 28), (135, 255, 160, 130), (240, 255, 240, 140)]
                elif gadget["type"] == "spawner":
                    colors = [(130, 170, 80, 28), (175, 215, 96, 130), (250, 255, 210, 120)]
                else:
                    colors = [(120, 220, 255, 24), (130, 235, 255, 110), (225, 255, 255, 100)]
                draw_soft_glow(
                    draw_surface,
                    gx,
                    gy,
                    body_r,
                    [
                        (body_r + 18, colors[0], 0),
                        (body_r + 6, colors[1], 3),
                        (max(8, body_r * 0.72), colors[2], 2),
                    ],
                )
                if gadget["type"] == "turret":
                    pygame.draw.circle(draw_surface, (56, 120, 62), (gx, gy), max(10, body_r))
                    pygame.draw.rect(draw_surface, (192, 255, 180), pygame.Rect(gx + body_r - 4, gy - 4, body_r + 8, 8), border_radius=4)
                elif gadget["type"] == "spawner":
                    pygame.draw.circle(draw_surface, (90, 108, 38), (gx, gy), max(10, body_r))
                    pygame.draw.circle(draw_surface, (215, 255, 150), (gx, gy), max(3, body_r // 3), 2)
                else:
                    pygame.draw.circle(draw_surface, (58, 104, 126), (gx, gy), max(10, body_r), 3)
                    pygame.draw.circle(draw_surface, (128, 238, 255), (gx, gy), max(8, body_r + 10), 2)

            for zone in zomboss_warning_zones:
                zx = int(zone["x"] + render_arena_left)
                zy = int(zone["y"] + render_arena_top)
                telegraph_ratio = max(0.0, min(1.0, zone["timer"] / zone.get("duration", 1.0)))
                ring_r = int(zone["radius"] * (0.82 + 0.18 * math.sin(elapsed_time * 12.0)))
                alpha = int(60 + (1.0 - telegraph_ratio) * 110)
                warning_surface = pygame.Surface((ring_r * 2 + 18, ring_r * 2 + 18), pygame.SRCALPHA)
                center = warning_surface.get_width() // 2
                pygame.draw.circle(warning_surface, (255, 36, 36, max(28, alpha // 3)), (center, center), max(8, ring_r - 8))
                pygame.draw.circle(warning_surface, (255, 78, 62, alpha), (center, center), ring_r, 4)
                pygame.draw.circle(warning_surface, (255, 220, 220, min(255, alpha + 40)), (center, center), max(10, ring_r - 16), 2)
                draw_surface.blit(warning_surface, warning_surface.get_rect(center=(zx, zy)))

            for beam in zomboss_beams:
                start = (int(beam["origin_x"] + render_arena_left), int(beam["origin_y"] + render_arena_top))
                end = (
                    int(start[0] + math.cos(beam["angle"]) * beam["length"]),
                    int(start[1] + math.sin(beam["angle"]) * beam["length"]),
                )
                if beam["mode"] == "laser_sweep":
                    beam_colors = [(255, 75, 48, 34), (255, 112, 70, 72), (255, 220, 190, 140)]
                else:
                    beam_colors = [(120, 225, 255, 24), (150, 240, 255, 62), (235, 255, 255, 120)]
                for width_mul, color in ((1.9, beam_colors[0]), (1.25, beam_colors[1]), (0.7, beam_colors[2])):
                    temp = pygame.Surface(draw_surface.get_size(), pygame.SRCALPHA)
                    pygame.draw.line(temp, color, start, end, max(2, int(beam["width"] * width_mul)))
                    draw_surface.blit(temp, (0, 0))

            for wave in zomboss_shockwaves:
                wave_surface = pygame.Surface(draw_surface.get_size(), pygame.SRCALPHA)
                pygame.draw.circle(
                    wave_surface,
                    (255, 126, 72, 116),
                    (int(wave["x"] + render_arena_left), int(wave["y"] + render_arena_top)),
                    int(wave["radius"]),
                    max(3, int(wave["width"])),
                )
                draw_surface.blit(wave_surface, (0, 0))

            epstein_dark_pressure = any(getattr(circle, "epstein_mark_timer", 0.0) > 0 for circle in circles)
            epstein_titan_banner = any(circle.character_type == "Golden Titan" and circle.health > 0 for circle in circles)
            if epstein_dark_pressure or epstein_titan_banner:
                overlay = pygame.Surface(draw_surface.get_size(), pygame.SRCALPHA)
                overlay_alpha = 22 if epstein_dark_pressure else 12
                if epstein_titan_banner:
                    overlay_alpha += 24
                overlay.fill((12, 10, 18, min(90, overlay_alpha)))
                draw_surface.blit(overlay, (0, 0))
            if epstein_titan_banner:
                banner_rect = pygame.Rect(screen_width // 2 - 240, 198, 480, 72)
                pygame.draw.rect(draw_surface, (28, 18, 12), banner_rect, border_radius=18)
                pygame.draw.rect(draw_surface, (245, 180, 84), banner_rect, 3, border_radius=18)
                draw_text(draw_surface, "SUMMON MAHORA J TRUMP", banner_rect.x + 22, banner_rect.y + 20, color=(255, 242, 210), size=30)

            for decoy in epstein_decoys:
                ratio = max(0.0, decoy["timer"] / decoy["duration"]) if decoy["duration"] > 0 else 0.0
                draw_soft_glow(
                    draw_surface,
                    decoy["x"] + render_arena_left,
                    decoy["y"] + render_arena_top,
                    decoy["radius"] * (1.35 + (1.0 - ratio) * 0.85),
                    [
                        (decoy["radius"] * 2.5, (45, 35, 58, 42), 0),
                        (decoy["radius"] * 1.75, (120, 90, 150, 95), 3),
                        (decoy["radius"] * 1.05, (220, 180, 255, 90), 2),
                    ],
                )

            for curse in epstein_curses:
                target = curse.get("target")
                if target is None or target.health <= 0:
                    continue
                pulse = 0.82 + 0.18 * math.sin(elapsed_time * 12.0)
                cx = int(target.x + render_arena_left)
                cy = int(target.y - target.radius - 18 + render_arena_top)
                draw_soft_glow(draw_surface, cx, cy, 22 * pulse, [(28, (80, 40, 120, 34), 0), (18, (190, 120, 255, 110), 2)])
                pygame.draw.circle(draw_surface, (105, 70, 135), (cx, cy), max(10, int(13 * pulse)), 2)
                pygame.draw.line(draw_surface, (185, 145, 220), (cx - 10, cy - 10), (cx + 10, cy + 10), 2)
                pygame.draw.line(draw_surface, (185, 145, 220), (cx + 10, cy - 10), (cx - 10, cy + 10), 2)

            for beam in epstein_beams:
                start = (int(beam["origin_x"] + render_arena_left), int(beam["origin_y"] + render_arena_top))
                end = (
                    int(start[0] + math.cos(beam["angle"]) * beam["length"]),
                    int(start[1] + math.sin(beam["angle"]) * beam["length"]),
                )
                for width_mul, color in ((2.4, (255, 160, 70, 38)), (1.55, (255, 205, 120, 92)), (0.8, (255, 242, 190, 165))):
                    temp = pygame.Surface(draw_surface.get_size(), pygame.SRCALPHA)
                    pygame.draw.line(temp, color, start, end, max(2, int(beam["width"] * width_mul)))
                    draw_surface.blit(temp, (0, 0))

            for wave in epstein_shockwaves:
                temp = pygame.Surface(draw_surface.get_size(), pygame.SRCALPHA)
                pygame.draw.circle(
                    temp,
                    (255, 190, 100, 148),
                    (int(wave["x"] + render_arena_left), int(wave["y"] + render_arena_top)),
                    int(wave["radius"]),
                    max(4, int(wave["width"])),
                )
                draw_surface.blit(temp, (0, 0))

            for meteor in meteors:
                meteor.draw(draw_surface, render_arena_left, render_arena_top)

            for idx, circle in enumerate(circles):
                if circle.health <= 0:
                    continue
                draw_x = circle.x + render_arena_left
                draw_y = circle.y + render_arena_top + getattr(circle, "mario_visual_y_offset", 0.0)
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
                    draw_surface.blit(aura_surface, aura_surface.get_rect(center=(int(draw_x), int(draw_y))))
                if circle.character_type == "Gojo Satoru":
                    infinity_radius = max(76.0, radius * 1.52)
                    pulse = 0.92 + 0.08 * math.sin(elapsed_time * 6.5 + idx * 0.7)
                    draw_soft_glow(
                        draw_surface,
                        draw_x,
                        draw_y,
                        infinity_radius * pulse,
                        [
                            (infinity_radius + 16, (140, 220, 255, 12), 0),
                            (infinity_radius, (170, 235, 255, 58), 2),
                            (max(circle.radius * 1.1, infinity_radius * 0.42), (245, 250, 255, 44), 1),
                        ],
                    )
                if circle.character_type == "Epstein":
                    pulse = 0.9 + 0.1 * math.sin(elapsed_time * 7.0 + idx)
                    draw_soft_glow(
                        draw_surface,
                        draw_x,
                        draw_y,
                        circle.radius * 1.7 * pulse,
                        [
                            (circle.radius * 2.0, (24, 24, 34, 26), 0),
                            (circle.radius * 1.55, (100, 78, 126, 64), 2),
                        ],
                    )
                if circle.character_type == "Golden Titan":
                    pulse = 0.9 + 0.1 * math.sin(elapsed_time * (6.5 if circle.titan_evolved else 3.8))
                    draw_soft_glow(
                        draw_surface,
                        draw_x,
                        draw_y,
                        circle.radius * 2.1 * pulse,
                        [
                            (circle.radius * 2.5, (255, 180, 80, 24), 0),
                            (circle.radius * 1.9, (255, 205, 110, 68), 4),
                            (circle.radius * 1.3, (255, 240, 200, 70), 2),
                        ],
                    )
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
                    draw_surface.blit(aura_surface, aura_surface.get_rect(center=(int(draw_x), int(draw_y))))
                if circle.character_type == "Elon Musk":
                    pulse = 0.84 + 0.16 * math.sin(elapsed_time * 8.0 + idx * 0.4)
                    yellow_alpha = 86 if getattr(circle, "elon_passive_stun_timer", 0.0) <= 0 else 136
                    draw_soft_glow(
                        draw_surface,
                        draw_x,
                        draw_y,
                        circle.radius * 1.85 * pulse,
                        [
                            (circle.radius * 2.35, (255, 235, 120, 18), 0),
                            (circle.radius * 1.8, (255, 220, 110, 42), 2),
                            (circle.radius * 1.25, (255, 240, 170, yellow_alpha), 2),
                        ],
                    )
                if getattr(circle, "martian_citizenship_timer", 0.0) > 0:
                    pulse = 0.88 + 0.12 * math.sin(elapsed_time * 10.5 + idx * 0.3)
                    draw_soft_glow(
                        draw_surface,
                        draw_x,
                        draw_y,
                        circle.radius * 1.6 * pulse,
                        [
                            (circle.radius * 2.05, (255, 120, 70, 14), 0),
                            (circle.radius * 1.7, (255, 175, 95, 40), 2),
                            (circle.radius * 1.2, (255, 225, 130, 96), 2),
                        ],
                    )
                if circle.character_type == "Misono Mika" and circle.ultimate_active:
                    pulse = 0.84 + 0.16 * math.sin(elapsed_time * 8.2)
                    outer_r = max(18, circle.radius * 2.15 * pulse)
                    draw_soft_glow(
                        draw_surface,
                        draw_x,
                        draw_y,
                        outer_r,
                        [
                            (outer_r + 20, (255, 165, 225, 24), 0),
                            (outer_r + 10, (255, 125, 210, 42), 0),
                            (outer_r, (255, 190, 235, 138), 4),
                            (max(10, outer_r * 0.63), (255, 240, 250, 96), 2),
                        ],
                    )
                if circle.character_type == "Mambo Mario" and getattr(circle, "mario_ultimate_stage", None) == "empowered":
                    aura_surface = pygame.Surface((int(circle.radius * 6), int(circle.radius * 6)), pygame.SRCALPHA)
                    aura_center = aura_surface.get_width() // 2
                    pulse = 0.9 + 0.1 * math.sin(elapsed_time * 7.2)
                    outer_r = max(16, int(circle.radius * 1.65 * pulse))
                    inner_r = max(8, int(circle.radius * 1.08))
                    pygame.draw.circle(aura_surface, (255, 96, 42, 26), (aura_center, aura_center), outer_r + 12)
                    pygame.draw.circle(aura_surface, (255, 132, 62, 48), (aura_center, aura_center), outer_r + 4)
                    pygame.draw.circle(aura_surface, (255, 178, 92, 110), (aura_center, aura_center), outer_r, 3)
                    pygame.draw.circle(aura_surface, (255, 220, 164, 82), (aura_center, aura_center), inner_r, 2)
                    draw_surface.blit(aura_surface, aura_surface.get_rect(center=(int(draw_x), int(draw_y))))
                if circle.character_type == "Mambo Zomboss":
                    pulse = 0.88 + 0.12 * math.sin(elapsed_time * (6.0 if getattr(circle, "zomboss_rampage", False) else 3.0))
                    outer_r = max(30, circle.radius * (1.08 if getattr(circle, "zomboss_rampage", False) else 0.96) * pulse)
                    if getattr(circle, "zomboss_rampage", False):
                        glow_colors = [
                            (outer_r + 30, (255, 84, 64, 20), 0),
                            (outer_r + 14, (255, 116, 72, 42), 0),
                            (outer_r, (255, 210, 160, 92), 4),
                        ]
                    else:
                        glow_colors = [
                            (outer_r + 24, (128, 220, 120, 16), 0),
                            (outer_r + 10, (152, 255, 136, 28), 0),
                            (outer_r, (236, 255, 220, 64), 3),
                        ]
                    draw_soft_glow(draw_surface, draw_x, draw_y, outer_r, glow_colors)
                current_image = circle.image
                if circle.character_type == "Misono Mika" and circle.ultimate_active and match_assets["mika_body_image"]:
                    current_image = match_assets["mika_body_image"]
                elif circle.character_type == "Do Mixi" and circle.ultimate_active and circle.ultimate_image:
                    current_image = circle.ultimate_image

                # Draw health bar for mambo enemies.
                if circle.character_type in ("Zombie", "Green Mob", "Giorno Mambo"):
                    bar_width = 40
                    bar_height = 4
                    bar_x = int(draw_x - bar_width // 2)
                    bar_y = int(draw_y - circle.radius - 15)
                    
                    # Calculate health ratio
                    health_ratio = max(0.0, min(1.0, circle.health / circle.max_health))
                    
                    # Draw red background (damage taken)
                    pygame.draw.rect(draw_surface, (200, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                    # Draw green foreground (remaining health)
                    pygame.draw.rect(draw_surface, (50, 200, 50), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
                    
                    # Draw HP text above health bar
                    hp_text = f"{int(circle.health)}/{circle.max_health}"
                    font = get_font(12)
                    rendered = font.render(hp_text, True, (255, 255, 255))
                    text_rect = rendered.get_rect()
                    text_rect.centerx = bar_x + bar_width // 2
                    text_rect.y = bar_y - 12
                    draw_surface.blit(rendered, text_rect)

                if current_image:
                    image_rect = current_image.get_rect()
                    image_rect.center = (int(draw_x), int(draw_y))
                    draw_surface.blit(current_image, image_rect)
                else:
                    pygame.draw.circle(
                        draw_surface,
                        circle.color,
                        (int(draw_x), int(draw_y)),
                        circle.radius,
                    )
                if circle.character_type == "Dummy Diddy":
                    draw_text(
                        draw_surface,
                        "dummy diddy",
                        int(draw_x - circle.radius * 0.9),
                        int(draw_y - circle.radius - 38),
                        color=(255, 245, 180),
                        size=18,
                    )
                if circle.character_type == "Epstein" and circle.epstein_untargetable:
                    pygame.draw.circle(draw_surface, (165, 135, 210), (int(draw_x), int(draw_y)), int(circle.radius * 1.15), 2)
                elif circle.character_type == "Epstein Thrall":
                    pygame.draw.circle(draw_surface, (22, 22, 28), (int(draw_x), int(draw_y)), max(6, int(circle.radius * 0.72)))
                    pygame.draw.circle(draw_surface, (175, 130, 220), (int(draw_x), int(draw_y)), max(3, int(circle.radius * 0.16)))
                elif circle.character_type == "Golden Titan" and circle.titan_evolved:
                    pygame.draw.circle(draw_surface, (255, 235, 180), (int(draw_x), int(draw_y)), int(circle.radius * 1.1), 2)
                if getattr(circle, "epstein_mark_timer", 0.0) > 0:
                    pulse = 0.9 + 0.1 * math.sin(elapsed_time * 10.0)
                    pygame.draw.circle(draw_surface, (165, 120, 210), (int(draw_x), int(draw_y)), max(circle.radius + 6, int((circle.radius + 8) * pulse)), 2)
                if circle.character_type == "Mambo Mario":
                    mario_stage = getattr(circle, "mario_ultimate_stage", None)
                    box_image = getattr(circle, "lucky_box_image", None)
                    flower_image = getattr(circle, "fire_flower_image", None)
                    head_y = draw_y - circle.radius * 0.95
                    if mario_stage == "jump" and box_image:
                        box_rect = box_image.get_rect(center=(int(draw_x), int(head_y - box_image.get_height() * 0.5)))
                        draw_surface.blit(box_image, box_rect)
                    elif mario_stage in ("flower_rise", "flower_fall") and flower_image:
                        flower_rect = flower_image.get_rect(
                            center=(int(draw_x), int(head_y - circle.radius * 0.9 + getattr(circle, "mario_flower_y_offset", 0.0)))
                        )
                        draw_surface.blit(flower_image, flower_rect)
                if circle.character_type == "T1 Faker" and circle.ultimate_active:
                    eye_y = int(draw_y - circle.radius * 0.18)
                    eye_dx = max(4, int(circle.radius * 0.22))
                    pygame.draw.circle(draw_surface, (255, 95, 125), (int(draw_x - eye_dx), eye_y), max(2, int(circle.radius * 0.11)))
                    pygame.draw.circle(draw_surface, (255, 95, 125), (int(draw_x + eye_dx), eye_y), max(2, int(circle.radius * 0.11)))
                if (
                    circle.character_type == "Gojo Satoru"
                    and circle.ultimate_active
                    and circle.gojo_ultimate_stage in ("infinite_void_intro", "domain")
                ):
                    eye_y = int(draw_y - circle.radius * 0.16)
                    eye_dx = max(4, int(circle.radius * 0.22))
                    pygame.draw.circle(draw_surface, (220, 170, 255), (int(draw_x - eye_dx), eye_y), max(2, int(circle.radius * 0.1)))
                    pygame.draw.circle(draw_surface, (220, 170, 255), (int(draw_x + eye_dx), eye_y), max(2, int(circle.radius * 0.1)))

                if circle.character_type == "Misono Mika" and circle.ultimate_active and match_assets["mika_halo_image"]:
                    halo_float = math.sin(elapsed_time * 8.0) * 6.0
                    halo_rect = match_assets["mika_halo_image"].get_rect(
                        center=(int(draw_x), int(draw_y - circle.radius - 10 + halo_float))
                    )
                    draw_surface.blit(match_assets["mika_halo_image"], halo_rect)

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
                        gun_rect.center = (int(draw_x + x_offset), int(draw_y + y_offset))
                        draw_surface.blit(gun_rotated, gun_rect)

                if circle.character_type == "Gojo Satoru":
                    draw_gojo_hollow_purple_charge(draw_surface, circle, circle.target, elapsed_time, match_assets, render_arena_left, render_arena_top)

            for bullet in bullets:
                draw_gojo_blue_black_hole(draw_surface, bullet, elapsed_time, render_arena_left, render_arena_top)

            for bullet in bullets:
                bullet.draw(draw_surface, render_arena_left, render_arena_top)

            for meteor in meteors:
                meteor.draw(draw_surface, render_arena_left, render_arena_top)

            new_damage_texts = []
            for dmg in damage_texts:
                dmg["y"] += dmg["vy"] * sim_dt
                dmg["ttl"] -= sim_dt
                if dmg["ttl"] > 0:
                    draw_text(draw_surface, dmg["text"], int(dmg["x"] + render_arena_left), int(dmg["y"] + render_arena_top), color=dmg["color"], size=22)
                    new_damage_texts.append(dmg)
            damage_texts = new_damage_texts

            if game_mode == "dummy":
                draw_button(draw_surface, win_button_rect, "WIN", fill_color=(0, 150, 0))

            human_circles = [c for c in circles if not is_mambo_enemy(c) and not is_epstein_summon(c)]
            
            if game_mode == "zombie":
                # Zombie mode UI in white bottom area
                panel_top = arena_top + arena_height + 20
                
                # Draw wave indicator at top of arena
                if wave_complete:
                    best_time_text = format_stage_time(get_zombie_best_time(current_wave))
                    clear_time_text = format_stage_time(last_cleared_wave_time)
                    draw_text(draw_surface, f"WAVE {current_wave} COMPLETED!", arena_left + arena_width // 2 - 140, arena_top + 40, (255, 255, 255), size=36)
                    draw_text(draw_surface, f"Clear Time: {clear_time_text}", arena_left + arena_width // 2 - 112, arena_top + 80, (255, 255, 255), size=24)
                    draw_text(draw_surface, f"Best: {best_time_text}", arena_left + arena_width // 2 - 82, arena_top + 110, (180, 255, 190), size=22)
                    countdown = max(0, zombie_spawn_timer)
                    draw_text(draw_surface, f"Next wave in {int(countdown) + 1}s...", arena_left + arena_width // 2 - 100, arena_top + 142, (255, 255, 255), size=28)
                else:
                    draw_text(draw_surface, f"WAVE {current_wave}", arena_left + arena_width // 2 - 60, arena_top + 20, (255, 255, 255), size=32)
                
                bar_x = arena_left + 50
                bar_width = max(300, screen_width - bar_x - 50)
                bar_height = 25
                bar_gap = 72
                
                for idx, circle in enumerate(human_circles):
                    y = panel_top + idx * bar_gap
                    health_ratio = 0.0 if circle.max_health <= 0 else max(0.0, min(1.0, circle.health / circle.max_health))
                    
                    # Draw health bar background (dark for contrast on white)
                    pygame.draw.rect(draw_surface, (40, 40, 40), (bar_x, y, bar_width, bar_height), border_radius=6)
                    # Draw health bar fill
                    pygame.draw.rect(draw_surface, circle.color, (bar_x, y, int(bar_width * health_ratio), bar_height), border_radius=6)
                    # Draw health bar border
                    pygame.draw.rect(draw_surface, (0, 0, 0), (bar_x, y, bar_width, bar_height), 2, border_radius=6)
                    
                    # Player name and health text
                    draw_text(draw_surface, circle.name, bar_x - 10, y - 25, color=(255, 255, 255), size=22)
                    draw_text(draw_surface, f"HP: {circle.health}/{circle.max_health}", bar_x, y + 3, color=(255, 255, 255), size=16)
                    
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
                    elif circle.character_type == "Epstein":
                        if circle.ultimate_active and circle.epstein_ultimate_stage == "summon_intro":
                            ult_text = "ULT: SUMMONING TITAN"
                            ult_color = (230, 185, 90)
                        elif circle.ultimate_cooldown_timer <= 0:
                            ult_text = "ULTIMATE READY"
                            ult_color = (0, 150, 0)
                        else:
                            ult_text = f"ULT {circle.ultimate_cooldown_timer:.1f}s"
                            ult_color = (130, 100, 185)
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
                    elif circle.character_type == "Elon Musk":
                        if circle.elon_ultimate_active:
                            ult_text = "R: MARS COLONIZATION"
                            ult_color = (255, 200, 110)
                        elif circle.elon_ultimate_cooldown <= 0:
                            ult_text = "R READY"
                            ult_color = (255, 200, 90)
                        else:
                            ult_text = f"R {circle.elon_ultimate_cooldown:.1f}s"
                            ult_color = (205, 150, 85)
                    elif circle.ultimate_cooldown_timer <= 0:
                        ult_text = "ULTIMATE READY"
                        ult_color = (0, 150, 0)
                    else:
                        ult_text = f"ULTIMATE COOLDOWN: {circle.ultimate_cooldown_timer:.1f}s"
                        ult_color = (100, 0, 0)
                    
                    draw_text(draw_surface, ult_text, bar_x, y + 30, color=ult_color, size=16)
                    if circle.character_type == "T1 Faker":
                        q_text = "Q READY" if circle.faker_skill_cooldown_timer <= 0 else f"Q {circle.faker_skill_cooldown_timer:.1f}s"
                        e_text = "E READY" if circle.ultimate_cooldown_timer <= 0 else f"E {circle.ultimate_cooldown_timer:.1f}s"
                        r_text = "R READY" if circle.faker_ultimate_cooldown_timer <= 0 else f"R {circle.faker_ultimate_cooldown_timer:.1f}s"
                        e_color = (120, 220, 255) if circle.ultimate_cooldown_timer <= 0 else (140, 160, 190)
                        r_color = (255, 120, 200) if circle.faker_ultimate_cooldown_timer <= 0 else (185, 120, 175)
                        q_color = (255, 225, 120) if circle.faker_skill_cooldown_timer <= 0 else (180, 165, 120)
                        draw_text(draw_surface, q_text, bar_x, y + 50, color=q_color, size=15)
                        draw_text(draw_surface, e_text, bar_x + 100, y + 50, color=e_color, size=15)
                        draw_text(draw_surface, r_text, bar_x + 220, y + 50, color=r_color, size=15)
                    elif circle.character_type == "Epstein":
                        q_text = "Q READY" if circle.epstein_shadowstep_cooldown <= 0 else f"Q {circle.epstein_shadowstep_cooldown:.1f}s"
                        draw_text(draw_surface, q_text, bar_x, y + 50, color=(180, 150, 220), size=15)
                    elif circle.character_type == "Elon Musk":
                        q_text = "Q READY" if circle.elon_rocket_punch_cooldown <= 0 else f"Q {circle.elon_rocket_punch_cooldown:.1f}s"
                        e_text = "E READY" if circle.elon_cybertruck_cooldown <= 0 else f"E {circle.elon_cybertruck_cooldown:.1f}s"
                        r_text = "R READY" if circle.elon_ultimate_cooldown <= 0 else f"R {circle.elon_ultimate_cooldown:.1f}s"
                        draw_text(draw_surface, q_text, bar_x, y + 50, color=(255, 220, 120), size=15)
                        draw_text(draw_surface, e_text, bar_x + 100, y + 50, color=(195, 205, 215), size=15)
                        draw_text(draw_surface, r_text, bar_x + 220, y + 50, color=(255, 190, 110), size=15)
                    
                    # Ultimate ready indicator
                    if circle.character_type == "T1 Faker":
                        ult_ready = circle.faker_ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    elif circle.character_type == "Elon Musk":
                        ult_ready = circle.elon_ultimate_cooldown <= 0 and not circle.elon_ultimate_active
                    else:
                        ult_ready = circle.ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    if circle.character_type == "Gojo Satoru":
                        ult_ready = ult_ready and battle_time >= 10.0
                    if circle.character_type == "Epstein":
                        ult_ready = ult_ready and battle_time >= 8.0
                    ready_color = (0, 200, 0) if ult_ready else (150, 150, 150)
                    pygame.draw.circle(draw_surface, ready_color, (bar_x - 30, y + bar_height // 2), 10)
                pygame.draw.circle(draw_surface, (255, 255, 255), (bar_x - 30, y + bar_height // 2), 10, 2)

                boss_circle = next((c for c in circles if c.character_type in ("Mambo Mario", "Mambo Zomboss") and c.health > 0), None)
                if boss_circle is not None:
                    boss_y = panel_top + len(human_circles) * bar_gap + 10
                    boss_bar_height = 34
                    boss_health_ratio = 0.0 if boss_circle.max_health <= 0 else max(0.0, min(1.0, boss_circle.health / boss_circle.max_health))
                    boss_bar_rect = pygame.Rect(bar_x, boss_y, bar_width, boss_bar_height)
                    pygame.draw.rect(draw_surface, (65, 10, 10), boss_bar_rect, border_radius=8)
                    pygame.draw.rect(draw_surface, (210, 30, 30), (bar_x, boss_y, int(bar_width * boss_health_ratio), boss_bar_height), border_radius=8)
                    pygame.draw.rect(draw_surface, (255, 220, 220), boss_bar_rect, 2, border_radius=8)

                    bars_remaining = max(0, int(math.ceil(boss_circle.health / max(1, getattr(boss_circle, "boss_health_segment", 10000)))))
                    draw_text(draw_surface, boss_circle.name, bar_x, boss_y - 28, color=(255, 245, 245), size=26)
                    draw_text(draw_surface, f"{bars_remaining} health bars remaining", bar_x, boss_y + 6, color=(255, 240, 240), size=18)

                    boss_hp_text = f"{int(max(0, boss_circle.health)):,} HP"
                    boss_hp_surface = get_font(18).render(boss_hp_text, True, (255, 245, 245))
                    boss_hp_rect = boss_hp_surface.get_rect()
                    boss_hp_rect.midright = (bar_x + bar_width - 12, boss_y + boss_bar_height // 2)
                    draw_surface.blit(boss_hp_surface, boss_hp_rect)

                # Players alive counter (only human players, not zombies)
                alive_count = sum(1 for c in circles if c.health > 0 and c.character_type != "Zombie" and not is_mambo_enemy(c) and not is_epstein_summon(c))
                counter_y = panel_top + len(human_circles) * bar_gap + (60 if boss_circle is not None else 20)
                draw_text(draw_surface, f"Survivors: {alive_count}", arena_left + 24, counter_y, (255, 255, 255), size=24)

            if game_mode == "zombie":
                # Check win condition: game ends when all human players are dead
                human_alive_count = sum(1 for c in circles if c.health > 0 and c.character_type != "Zombie" and not is_mambo_enemy(c) and not is_epstein_summon(c))
                if battle_time > 3.0 and human_alive_count <= 0:
                    show_result_screen()
            else:
                # Regular mode UI
                panel_top = arena_top + arena_height + 12
                bar_x = arena_left + 170
                bar_width = max(220, screen_width - bar_x - 30)
                bar_height = 20
                bar_gap = 68
                bar_targets = [c for c in circles if not is_epstein_summon(c)]
                for idx, circle in enumerate(bar_targets):
                    y = panel_top + idx * bar_gap
                    if circle.character_type == "Dummy Diddy":
                        health_ratio = 1.0
                    else:
                        health_ratio = 0.0 if circle.max_health <= 0 else max(0.0, min(1.0, circle.health / circle.max_health))
                    pygame.draw.rect(draw_surface, (55, 55, 65), (bar_x, y, bar_width, bar_height), border_radius=8)
                    pygame.draw.rect(draw_surface, circle.color, (bar_x, y, int(bar_width * health_ratio), bar_height), border_radius=8)
                    pygame.draw.rect(draw_surface, (220, 220, 230), (bar_x, y, bar_width, bar_height), 2, border_radius=8)
                    draw_text(draw_surface, circle.name, arena_left + 24, y - 1, color=(230, 230, 235), size=20)
                    if circle.character_type == "Dummy Diddy":
                        draw_text(draw_surface, "INF HP", bar_x + bar_width - 86, y - 1, color=(245, 245, 250), size=18)
                    else:
                        draw_text(draw_surface, f"{circle.health}/{circle.max_health}", bar_x + bar_width - 92, y - 1, color=(245, 245, 250), size=18)
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
                    elif circle.character_type == "Epstein":
                        if circle.ultimate_active and circle.epstein_ultimate_stage == "summon_intro":
                            ult_text = "ULT: SUMMONING TITAN"
                            ult_color = (255, 215, 110)
                        elif circle.ultimate_cooldown_timer <= 0:
                            ult_text = "ULT READY"
                            ult_color = (255, 220, 70)
                        else:
                            ult_text = f"ULT {circle.ultimate_cooldown_timer:.1f}s"
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
                    elif circle.character_type == "Elon Musk":
                        if circle.elon_ultimate_active:
                            ult_text = "R: MARS COLONIZATION"
                            ult_color = (255, 210, 120)
                        elif circle.elon_ultimate_cooldown <= 0:
                            ult_text = "R READY"
                            ult_color = (255, 210, 95)
                        else:
                            ult_text = f"R {circle.elon_ultimate_cooldown:.1f}s"
                            ult_color = (225, 185, 120)
                    elif circle.character_type == "Dummy Diddy":
                        ult_text = "TEST TARGET"
                        ult_color = (255, 220, 140)
                    elif circle.ultimate_cooldown_timer <= 0:
                        ult_text = "ULT READY"
                        ult_color = (255, 220, 70)
                    else:
                        ult_text = f"ULT {circle.ultimate_cooldown_timer:.1f}s"
                        ult_color = (200, 220, 255)
                    draw_text(draw_surface, ult_text, arena_left + 24, y + 20, color=ult_color, size=18)
                    if circle.character_type == "T1 Faker":
                        q_text = "Q READY" if circle.faker_skill_cooldown_timer <= 0 else f"Q {circle.faker_skill_cooldown_timer:.1f}s"
                        e_text = "E READY" if circle.ultimate_cooldown_timer <= 0 else f"E {circle.ultimate_cooldown_timer:.1f}s"
                        r_text = "R READY" if circle.faker_ultimate_cooldown_timer <= 0 else f"R {circle.faker_ultimate_cooldown_timer:.1f}s"
                        e_color = (120, 220, 255) if circle.ultimate_cooldown_timer <= 0 else (160, 180, 210)
                        r_color = (255, 140, 210) if circle.faker_ultimate_cooldown_timer <= 0 else (215, 160, 205)
                        q_color = (255, 220, 90) if circle.faker_skill_cooldown_timer <= 0 else (190, 175, 130)
                        draw_text(draw_surface, q_text, arena_left + 24, y + 42, color=q_color, size=16)
                        draw_text(draw_surface, e_text, arena_left + 122, y + 42, color=e_color, size=16)
                        draw_text(draw_surface, r_text, arena_left + 220, y + 42, color=r_color, size=16)
                    elif circle.character_type == "Epstein":
                        q_text = "Q READY" if circle.epstein_shadowstep_cooldown <= 0 else f"Q {circle.epstein_shadowstep_cooldown:.1f}s"
                        draw_text(draw_surface, q_text, arena_left + 24, y + 42, color=(215, 185, 255), size=16)
                    elif circle.character_type == "Elon Musk":
                        q_text = "Q READY" if circle.elon_rocket_punch_cooldown <= 0 else f"Q {circle.elon_rocket_punch_cooldown:.1f}s"
                        e_text = "E READY" if circle.elon_cybertruck_cooldown <= 0 else f"E {circle.elon_cybertruck_cooldown:.1f}s"
                        r_text = "R READY" if circle.elon_ultimate_cooldown <= 0 else f"R {circle.elon_ultimate_cooldown:.1f}s"
                        draw_text(draw_surface, q_text, arena_left + 24, y + 42, color=(255, 220, 100), size=16)
                        draw_text(draw_surface, e_text, arena_left + 122, y + 42, color=(210, 220, 230), size=16)
                        draw_text(draw_surface, r_text, arena_left + 220, y + 42, color=(255, 195, 110), size=16)
                    elif circle.character_type == "Dummy Diddy":
                        total_damage = int(round(getattr(circle, "dummy_damage_taken_total", 0.0)))
                        draw_text(draw_surface, f"Damage recorded: {total_damage:,}", arena_left + 24, y + 42, color=(255, 215, 140), size=16)
                    if circle.character_type == "T1 Faker":
                        ult_ready = circle.faker_ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    elif circle.character_type == "Elon Musk":
                        ult_ready = circle.elon_ultimate_cooldown <= 0 and not circle.elon_ultimate_active
                    elif circle.character_type == "Dummy Diddy":
                        ult_ready = False
                    else:
                        ult_ready = circle.ultimate_cooldown_timer <= 0 and not circle.ultimate_active
                    if circle.character_type == "Gojo Satoru":
                        ult_ready = ult_ready and battle_time >= 10.0
                    if circle.character_type == "Epstein":
                        ult_ready = ult_ready and battle_time >= 8.0
                    ready_sign_color = (255, 220, 70) if ult_ready else (110, 110, 120)
                    pygame.draw.circle(draw_surface, ready_sign_color, (arena_left + 148, y + 9), 8)

                alive_count = sum(1 for c in circles if c.health > 0 and not is_epstein_summon(c))
                draw_text(draw_surface, f"Players alive: {alive_count}", arena_left + 24, panel_top + len(bar_targets) * bar_gap + 8, (220, 220, 220), size=20)

                # Regular mode win condition
                alive_count = sum(1 for c in circles if c.health > 0 and not is_epstein_summon(c))
                if battle_time > 3.0 and alive_count <= 1:
                    show_result_screen()
        elif menu_state == "pause":
            draw_surface.fill((20, 20, 30))
            border_rect = pygame.Rect(arena_left, arena_top, arena_width, arena_height)
            pygame.draw.rect(draw_surface, (200, 200, 200), border_rect, 3)

            pause_rect = pygame.Rect(arena_left + arena_width // 2 - 180, arena_top + arena_height // 2 - 120, 360, 240)
            pygame.draw.rect(draw_surface, (40, 45, 70), pause_rect, border_radius=18)
            pygame.draw.rect(draw_surface, (120, 160, 230), pause_rect, 3, border_radius=18)
            draw_text(draw_surface, "RUN MENU", pause_rect.x + 102, pause_rect.y + 18, (255, 255, 255), size=34)

            if game_mode == "zombie":
                pause_buttons = [
                    (pygame.Rect(pause_rect.x + 40, pause_rect.y + 60, pause_rect.width - 80, 42), "Continue", (70, 130, 220)),
                    (pygame.Rect(pause_rect.x + 40, pause_rect.y + 112, pause_rect.width - 80, 42), "Save Progress", (90, 170, 110)),
                    (pygame.Rect(pause_rect.x + 40, pause_rect.y + 164, pause_rect.width - 80, 42), "Delete Run", (190, 90, 90)),
                ]
            else:
                pause_buttons = [
                    (pygame.Rect(pause_rect.x + 40, pause_rect.y + 60, pause_rect.width - 80, 42), "Continue", (70, 130, 220)),
                    (pygame.Rect(pause_rect.x + 40, pause_rect.y + 112, pause_rect.width - 80, 42), "Back to Home Screen", (190, 150, 60)),
                ]
            for rect, label, fill in pause_buttons:
                draw_button(draw_surface, rect, label, fill_color=fill)
        elif menu_state == "result":
            draw_surface.fill((20, 20, 30))
            border_rect = pygame.Rect(arena_left, arena_top, arena_width, arena_height)
            pygame.draw.rect(draw_surface, (200, 200, 200), border_rect, 3)

            result_title = result_winner_name if result_winner_name == "GAME OVER" else f"{result_winner_name} wins"
            win_surface = get_font(38).render(result_title, True, (255, 220, 70))
            win_rect = win_surface.get_rect(center=(arena_left + arena_width // 2, arena_top + 36))
            draw_surface.blit(win_surface, win_rect)

            for circle in circles:
                current_image = circle.image
                if circle.character_type == "Misono Mika" and circle.ultimate_active and match_assets["mika_body_image"]:
                    current_image = match_assets["mika_body_image"]
                elif circle.character_type == "Do Mixi" and circle.ultimate_active and circle.ultimate_image:
                    current_image = circle.ultimate_image

                if current_image:
                    image_rect = current_image.get_rect(center=(int(circle.x + arena_left), int(circle.y + arena_top)))
                    draw_surface.blit(current_image, image_rect)
                else:
                    pygame.draw.circle(draw_surface, circle.color, (int(circle.x + arena_left), int(circle.y + arena_top)), circle.radius)

            if result_special_click_needed:
                prompt_surface = get_font(24).render("Click once to continue", True, (255, 245, 180))
                prompt_rect = prompt_surface.get_rect(center=(arena_left + arena_width // 2, arena_top + arena_height - 20))
                draw_surface.blit(prompt_surface, prompt_rect)
            elif result_show_options:
                draw_button(draw_surface, result_button_rects[0], "Home", fill_color=(190, 150, 60))
                draw_button(draw_surface, result_button_rects[1], "Rematch", fill_color=(70, 130, 220))
                draw_text(draw_surface, "Return to Home Screen", result_button_rects[0].x - 8, result_button_rects[0].bottom + 12, (230, 230, 235), size=20)
                draw_text(draw_surface, "Rematch", result_button_rects[1].x + 48, result_button_rects[1].bottom + 12, (230, 230, 235), size=20)

        if fullscreen:
            scaled_surface = pygame.transform.scale(game_surface, (desktop_width, desktop_height))
            screen.blit(scaled_surface, (0, 0))
        else:
            screen.blit(game_surface, (0, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    simulate()
