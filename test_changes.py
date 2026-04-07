# Test script to verify zombie mode changes
import pygame

# Initialize pygame
pygame.init()

# Create screen
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Test Zombie Mode Changes")

# Colors
DARK_BLUE = (20, 20, 30)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Test variables
game_mode = "zombie"
arena_left = 100
arena_top = 80
arena_width = 600
arena_height = 400
tube_top_height = 80

# Main test loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill background
    screen.fill(DARK_BLUE)
    
    # Draw zombie mode elements
    if game_mode == "zombie":
        # Calculate tube opening
        tube_w = 120
        top_center_x = arena_left + arena_width // 2
        tube_left = top_center_x - tube_w // 2
        tube_right = top_center_x + tube_w // 2
        
        # Draw tube opening lines
        pygame.draw.line(screen, WHITE, (tube_left, 0), (tube_left, tube_top_height), 2)
        pygame.draw.line(screen, WHITE, (tube_right, 0), (tube_right, tube_top_height), 2)
        
        # Draw rectangle boundary (connected)
        pygame.draw.line(screen, WHITE, (arena_left, arena_top), (arena_left, arena_top + arena_height), 2)
        pygame.draw.line(screen, WHITE, (arena_left + arena_width, arena_top), (arena_left + arena_width, arena_top + arena_height), 2)
        pygame.draw.line(screen, WHITE, (arena_left, arena_top + arena_height), (arena_left + arena_width, arena_top + arena_height), 2)
        
        # Connect tube to rectangle
        pygame.draw.line(screen, WHITE, (tube_left, tube_top_height), (tube_left, arena_top), 2)
        pygame.draw.line(screen, WHITE, (tube_right, tube_top_height), (tube_right, arena_top), 2)
        
        # Draw test text
        font = pygame.font.Font(None, 24)
        text = font.render("ZOMBIE MODE TEST", True, YELLOW)
        screen.blit(text, (200, 200))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
