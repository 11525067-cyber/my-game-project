import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 1200, 800   # big map size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Player setup
player = pygame.Rect(100, 100, 40, 40)
player_speed = 5

# Enemy setup (placeholder rectangle, replace with PNG later)
enemy = pygame.Rect(900, 600, 40, 40)
enemy_speed = 2

# Exit setup
exit_rect = pygame.Rect(WIDTH-80, HEIGHT-80, 60, 60)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.y -= player_speed
    if keys[pygame.K_s]: player.y += player_speed
    if keys[pygame.K_a]: player.x -= player_speed
    if keys[pygame.K_d]: player.x += player_speed

    # Enemy chases player
    if enemy.x < player.x: enemy.x += enemy_speed
    if enemy.x > player.x: enemy.x -= enemy_speed
    if enemy.y < player.y: enemy.y += enemy_speed
    if enemy.y > player.y: enemy.y -= enemy_speed

    # Check win/lose
    if player.colliderect(exit_rect):
        print("You escaped!")
        pygame.quit()
        sys.exit()
    if player.colliderect(enemy):
        print("Caught by the entity!")
        pygame.quit()
        sys.exit()

    # Draw everything
    screen.fill((20,20,20))
    pygame.draw.rect(screen, (0,255,0), player)   # player
    pygame.draw.rect(screen, (255,0,0), enemy)    # enemy placeholder
    pygame.draw.rect(screen, (0,0,255), exit_rect) # exit
    pygame.display.flip()
    clock.tick(60)
