import pygame

# Initialize pygame
pygame.init()

# Get the number of available displays
num_displays = pygame.display.get_num_displays()
print("Number of screens:", num_displays)

# Quit pygame
pygame.quit()
