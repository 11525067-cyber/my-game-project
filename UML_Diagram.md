# UML Class Diagram - pythongame

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  Circle                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ - x: float                                                                   │
│ - y: float                                                                   │
│ - vx: float                                                                  │
│ - vy: float                                                                  │
│ - radius: float                                                              │
│ - health: float                                                             │
│ - max_health: float                                                          │
│ - color: tuple                                                              │
│ - name: str                                                                 │
│ - character_type: str                                                       │
│ - image: Surface                                                            │
│ - gun_image: Surface                                                         │
│ - bullet_timer: float                                                        │
│ - target: Circle                                                            │
│ - colliding: bool                                                          │
│ - bullet_count: int                                                          │
│ - ultimate_active: bool                                                     │
│ - burst_remaining: int                                                      │
│ - burst_timer: float                                                        │
│ - burst_is_ultimate: bool                                                   │
│ - attack_count: int                                                        │
│ - ultimate_duration_timer: float                                            │
│ - ultimate_cooldown_timer: float                                           │
│ - normal_image: Surface                                                    │
│ - ultimate_image: Surface                                                 │
│ - controller: str                                                          │
│ - impulse_vx: float                                                        │
│ - impulse_vy: float                                                        │
│ - impulse_wall_bounces_remaining: int                                      │
│ - damage: float                                                            │
│ - damage_bonus: float                                                       │
│ - team_id: int                                                              │
│ - damage_taken_multiplier: float                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ + move(dt)                                                                   │
│ + bounce_off_wall(width, height)                                            │
│ + clamp_to_arena(width, height)                                             │
│ + clamp_to_trapezoid(arena_left, arena_top, arena_width, arena_height)        │
│ + bounce_impulse_off_wall(width, height)                                   │
│ + hit(other): bool                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                                    │ has
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   Bullet                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ - x: float                                                                   │
│ - y: float                                                                   │
│ - vx: float                                                                  │
│ - vy: float                                                                  │
│ - owner_index: int                                                          │
│ - color: tuple                                                              │
│ - size: int                                                                 │
│ - image: Surface                                                            │
│ - is_ultimate: bool                                                        │
│ - source: str                                                               │
│ - damage: float                                                             │
│ - attack_type: str                                                          │
│ - crit_chance: float                                                        │
│ - crit_damage: float                                                       │
│ - bounce_forever: bool                                                     │
│ - expires_with_owner_ultimate: bool                                       │
│ - wall_bounces_remaining: int                                             │
│ - field_radius: float                                                     │
│ - field_strength: float                                                   │
│ - pushes_projectiles: bool                                                │
│ - pushes_characters: bool                                                  │
│ - hold_timer: float                                                       │
│ - hold_duration: float                                                   │
│ - blue_charging: bool                                                     │
│ - hold_offset: float                                                      │
│ - release_speed: float                                                    │
│ - pending_vx: float                                                       │
│ - pending_vy: float                                                       │
│ - target_index: int                                                       │
│ - turn_rate: float                                                         │
│ - field_damage_per_second: float                                          │
│ - hit_targets: set                                                         │
│ - pull_strength: float                                                     │
│ - push_strength: float                                                     │
│ - inner_push_radius: float                                                │
│ - field_activation_delay: float                                           │
│ - gojo_blue_converted: bool                                               │
│ - gojo_blue_border_color: tuple                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ + move(dt)                                                                   │
│ + bounce_off_wall(width, height): bool                                      │
│ + draw(surface, offset_x, offset_y)                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                                    │ has
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   Meteor                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ - x: float                                                                   │
│ - y: float                                                                   │
│ - vx: float                                                                  │
│ - vy: float                                                                  │
│ - size: int                                                                 │
│ - owner_index: int                                                          │
│ - target_index: int                                                        │
│ - damage: float                                                             │
│ - attack_type: str                                                          │
│ - is_crit: bool                                                            │
│ - max_bounces: int                                                          │
│ - turn_rate: float                                                         │
│ - color: tuple                                                             │
│ - image: Surface                                                            │
│ - bounce_count: int                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ + move(dt, circles)                                                          │
│ + bounce_off_wall(width, height)                                            │
│ + draw(surface, offset_x, offset_y)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Game Flow & Key Functions

### Initialization
```
simulate()  ─────┬────> load_image()
                 │      scale_to_fit()
                 │      scale_to_height()
                 │      load_optional_sound()
                 └────> build_match_assets()
```

### Game Loop
```
┌──────────────────────────────────────────────────────────────────────┐
│                      Main Game Loop                      │
├──────────────────────────────────────────────────────────────────────┤
│  1. Handle Input (pygame events)                          │
│  2. Update Game State                                  │
│     - Update circles (AI movement)                    │
│     - Update bullets (movement, collision)            │
│     - Update meteors (seek targets)                 │
│     - Handle collisions                            │
│     - Process damage                               │
│  3. Render Frame                                   │
│     - Draw background                            │
│     - Draw circles                               │
│     - Draw bullets                               │
│     - Draw UI elements                          │
└──────────────────────────────────────────────────────────────────────┘
```

### Character Types Supported
- **Mika** (Misono Mika) - Crit-heavy burst carry
- **Gojo** (Gojo Satoru) - Control mage with chained finishers  
- **Epstein** - Slippery controller and summoner
- **Vu** (Do Mixi) - Straight-line pressure and barrage zoning
- **Faker** (T1 Faker) - Mobile control fighter with clutch windows
- **Mambo** types - Apocalypse enemies:
  - Green Mob
  - Giorno Mambo
  - Mambo Mario
  - Mambo Zomboss
  - Golden Titan

### Key Helper Functions
```
Damage & Combat:
  - apply_damage_to_circle()
  - apply_explosion_splash_damage()
  - consume_epstein_mark_bonus()
  - apply_titan_adaptive_resistance()
  - scale_apocalypse_damage()

Collision Detection:
  - circles_are_hostile()
  - is_zombie_side()
  - is_player_controlled_human()
  - resolve_circle_collision()
  - apply_radial_push()

Movement & AI:
  - get_hostile_opponents()
  - get_lead_unit_vector()
  - normalize_velocity()

Special Effects:
  - add_gojo_technique_explosion()
  - draw_gojo_blue_black_hole()
  - add_faker_magic_flame()
  - update_video_background()
```

### Game Modes
- **sim** - Regular battle simulation
- **zombie** - Mambo Apocalypse wave mode
- **custom** - Custom character selection

### Audio System
- Voice channels (primary/secondary)
- Music channel
- Sound effects with amplification support