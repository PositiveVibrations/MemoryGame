import pygame
import sys
import random
import time
import os

# Default game settings - Users can modify these settings as needed
DEFAULT_SETTINGS = {
    'screen_size': (800, 600),  # Window size
    'ui_height': 100,           # Height of the UI area at the top of the screen
    'initial_grid_size': 3,     # Initial size of the grid (3x3)
    'initial_lives': 5,         # Initial number of lives
    'initial_level': 1,         # Starting level
    'initial_score': 0,         # Starting score
    'high_score_file': "high_score.txt",  # File to store the high score
    'num_revealed_squares': 3,  # Number of squares revealed at the start
}



# Updated color scheme
COLOR_SCHEME = {'background': '#121236',
 'grid_face_down': '#3a3a52',
 'grid_correct': '#008000',
 'grid_incorrect': '#f85757',
 'ui_area': '#3a3a52', #top bar with
 'text_color': '#ffffff',
 'button_color': '#121236',
 'highlight_color': '#a9b7c6',
}

# New Function to Load and Save High Score
def load_high_score(file_path):
    try:
        with open(file_path, "r") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(file_path, high_score):
    with open(file_path, "w") as file:
        file.write(str(high_score))

def create_board(grid_size, screen_size, ui_height):
    square_size = (screen_size[1] - ui_height - 10 * (grid_size + 1)) // grid_size
    return [[{'face_up': False, 'color': COLOR_SCHEME['grid_face_down'], 'width': square_size, 'guessed': False} for _ in range(grid_size)] for _ in range(grid_size)]


def draw_grid(screen, grid, screen_size, ui_height):
    screen_width, screen_height = screen_size
    total_gap_size = 10 * (len(grid) + 1)
    square_size = (screen_height - ui_height - total_gap_size) // len(grid)
    offset_x = (screen_width - (square_size * len(grid) + total_gap_size)) // 2
    offset_y = ui_height

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            square = grid[row][col]
            x = offset_x + col * (square_size + 10) + 10
            y = offset_y + row * (square_size + 10) + 10
            pygame.draw.rect(screen, square['color'], (x, y, square_size, square_size))

def randomly_reveal_squares(grid, num_revealed_squares):
    revealed_squares = set()
    for _ in range(num_revealed_squares):
        while True:
            row, col = random.randint(0, len(grid) - 1), random.randint(0, len(grid) - 1)
            if not grid[row][col]['face_up']:
                revealed_squares.add((row, col))
                grid[row][col]['face_up'] = True
                grid[row][col]['color'] = COLOR_SCHEME['grid_correct']  # Bright green for correct
                break

    return revealed_squares

def get_user_guess(grid, guess_row, guess_col, revealed_squares, lives, score, correct_sound, incorrect_sound):
    if (guess_row, guess_col) in revealed_squares and not grid[guess_row][guess_col]['guessed']:
        print("Correct guess!")
        grid[guess_row][guess_col]['color'] = COLOR_SCHEME['grid_correct']  # Bright green for correct
        grid[guess_row][guess_col]['face_up'] = True
        grid[guess_row][guess_col]['guessed'] = True  # Mark as correctly guessed
        
        correct_sound.play()  # Play the correct sound effect
        return True, lives, score + 1
    elif (guess_row, guess_col) in revealed_squares:
        print("Already guessed.")
        return False, lives, score  # No change in lives or score for already guessed squares
    else:
        #check if the incorrect square was already guessed
        if grid[guess_row][guess_col]['guessed']:
            print("Already guessed.")
            return False, lives, score
        elif lives == 1:  # Check if this is the last life
            print("Game over.")
            grid[guess_row][guess_col]['color'] = COLOR_SCHEME['grid_incorrect']  
            grid[guess_row][guess_col]['face_up'] = True
            incorrect_sound.play()
            return False, lives - 1, score
        else:
            print("Incorrect guess.")
            grid[guess_row][guess_col]['color'] = COLOR_SCHEME['grid_incorrect'] 
            grid[guess_row][guess_col]['face_up'] = True
            grid[guess_row][guess_col]['guessed'] = True  # Mark as guessed
            incorrect_sound.play()  # Play the incorrect sound effect
            return False, lives - 1, score

def get_grid_position(mouse_x, mouse_y, grid_size, square_size, offset_x, offset_y):
    col = (mouse_x - offset_x) // (square_size + 10)
    row = (mouse_y - offset_y) // (square_size + 10)
    if 0 <= row < grid_size and 0 <= col < grid_size:
        return row, col
    return None, None

def determine_next_round(grid_size, num_revealed_squares):
    next_num_revealed_squares = num_revealed_squares + 1  # Always increase by 1

    if next_num_revealed_squares > grid_size * grid_size // 2:
        grid_size += 1  # Increase the grid size if more than half are green
        

    return grid_size, next_num_revealed_squares

# New function to display game information along the top
def display_game_info(screen, level, score, high_score, lives, ui_height):
    font = pygame.font.SysFont(None, 45)
    # Clear the text area with the UI area color
    pygame.draw.rect(screen, COLOR_SCHEME['ui_area'], (0, 0, screen.get_size()[0], ui_height))
    texts = [
        font.render(f'Level: {level}', True, COLOR_SCHEME['text_color']),
        font.render(f'Score: {score}', True, COLOR_SCHEME['text_color']),
        font.render(f'High Score: {high_score}', True, COLOR_SCHEME['text_color']),
        font.render(f'Lives: {lives}', True, COLOR_SCHEME['text_color'])
    ]

    screen_width = screen.get_size()[0]
    total_text_width = sum(text.get_width() for text in texts)
    spacing = (screen_width - total_text_width) / (len(texts) + 1)

    x_position = spacing
    for text in texts:
        screen.blit(text, (x_position + 5 , ui_height - 70))  # Adjusted y position
        x_position += text.get_width() + spacing

# New function to display the end of round menu
def display_end_of_round_menu(screen, level, score, high_score, ui_height, screen_size):
    font = pygame.font.SysFont(None, 48)
    round_text = font.render(f'Level {level}', True, COLOR_SCHEME['text_color'])
    score_text = font.render(f'Your Score: {score}', True, COLOR_SCHEME['text_color'])
    high_score_text = font.render(f'High Score: {high_score}', True, COLOR_SCHEME['text_color'])

    # Calculate dimensions for the menu
    menu_width = max(round_text.get_width(), score_text.get_width(), high_score_text.get_width()) + 40
    menu_height = round_text.get_height() + score_text.get_height() + high_score_text.get_height() + 60
    menu_x = (screen_size[0] - menu_width) // 2
    menu_y = (screen_size[1] - menu_height) // 2

    # Border dimensions and color
    border_color = COLOR_SCHEME['highlight_color']
    border_width = 5  # Width of the border
    border_rect = (menu_x - border_width, menu_y - border_width, menu_width + 2 * border_width, menu_height + 2 * border_width)

    # Draw a rectangle for the border
    pygame.draw.rect(screen, border_color, border_rect)

    # Draw a rectangle for the menu background using the ui_area color
    pygame.draw.rect(screen, COLOR_SCHEME['ui_area'], (menu_x, menu_y, menu_width, menu_height))

    # Positioning the text within the menu
    x_position = (screen_size[0] - round_text.get_width()) // 2
    y_position = menu_y + 20

    screen.blit(round_text, (x_position, y_position))
    y_position += round_text.get_height() + 20
    screen.blit(score_text, ((screen_size[0] - score_text.get_width()) // 2, y_position))
    y_position += score_text.get_height() + 20
    screen.blit(high_score_text, ((screen_size[0] - high_score_text.get_width()) // 2, y_position))

    pygame.display.update()

# New function to wait for a duration and ignore input
def wait_and_ignore_input(duration):
    end_time = pygame.time.get_ticks() + duration
    while pygame.time.get_ticks() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    pygame.init()
    num_revealed_squares = DEFAULT_SETTINGS['num_revealed_squares']
    screen_size = DEFAULT_SETTINGS['screen_size']
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Memory Game')

    ui_height = DEFAULT_SETTINGS['ui_height']
    grid_size = DEFAULT_SETTINGS['initial_grid_size']
    lives = DEFAULT_SETTINGS['initial_lives']
    level = DEFAULT_SETTINGS['initial_level']
    score = DEFAULT_SETTINGS['initial_score']
    high_score_file = DEFAULT_SETTINGS['high_score_file']
    high_score = load_high_score(high_score_file)
    game_over = False
    allow_input = True  # Added to control user input during memorization period

    # Initialize Pygame mixer module
    pygame.mixer.init()

    # Load the audio files for correct and incorrect guesses
    correct_sound = pygame.mixer.Sound(os.path.join("media", "correct3.mp3"))
    incorrect_sound = pygame.mixer.Sound(os.path.join("media", "incorrect2.wav"))
    # Load the audio file for level up
    levelup_sound = pygame.mixer.Sound(os.path.join("media", "levelup.mp3"))

    while not game_over:
        grid = create_board(grid_size, screen_size, ui_height)
        revealed_squares = randomly_reveal_squares(grid, num_revealed_squares)

        screen.fill((18, 18, 54))  # A dark blue shade for the background
        draw_grid(screen, grid, screen_size, ui_height)

        # Redraw game information here
        display_game_info(screen, level, score, high_score, lives, ui_height)

        pygame.display.update()

        allow_input = False  # Disable input during the memorization period

        wait_and_ignore_input(3000)  # Wait for 3 seconds to memorize the squares

        allow_input = True  # Re-enable input after the memorization period

        # Hide the squares
        for row, col in revealed_squares:
            grid[row][col]['face_up'] = False
            grid[row][col]['color'] = COLOR_SCHEME['grid_face_down']

        screen.fill((18, 18, 54))  # A dark blue shade for the background
        draw_grid(screen, grid, screen_size, ui_height)

        # Redraw game information again here
        display_game_info(screen, level, score, high_score, lives, ui_height)

        pygame.display.update()

        guesses_made = 0
        misses = 0  # Initialize misses
        correct_guesses = 0  # Track correct guesses within the round

        while lives > 0 and guesses_made < (misses + num_revealed_squares):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if allow_input:  # Check if input is allowed
                        mouse_x, mouse_y = event.pos
                        guess_row, guess_col = get_grid_position(
                            mouse_x, mouse_y, grid_size,
                            (screen_size[1] - ui_height - 10 * (grid_size + 1)) // grid_size,
                            (screen_size[0] - ((screen_size[1] - ui_height - 10 * (grid_size + 1)) // grid_size * grid_size + 10 * (grid_size + 1))) // 2, ui_height
                        )
                        if guess_row is not None and guess_col is not None:
                            correct, lives, score = get_user_guess(grid, guess_row, guess_col, revealed_squares, lives, score, correct_sound, incorrect_sound)
                            guesses_made += 1
                            if correct:
                                correct_guesses += 1  # Increment correct_guesses for correct guesses
                                #update the game information
                                display_game_info(screen, level, score, high_score, lives, ui_height)
                            else:
                                misses += 1  # Increment misses for incorrect guesses
                                #update the game information
                                display_game_info(screen, level, score, high_score, lives, ui_height)
                            draw_grid(screen, grid, screen_size, ui_height)

                            pygame.display.update()

        # Check if all green squares were clicked to increase the level
        if correct_guesses == num_revealed_squares:
            level += 1
            correct_guesses = 0  # Reset correct_guesses for the next level
            levelup_sound.play()

        # Determine if we need to increase the grid size for the next round
        grid_size, num_revealed_squares = determine_next_round(grid_size, num_revealed_squares)

        # Ensure that the number of revealed squares does not exceed the grid capacity
        num_revealed_squares = min(num_revealed_squares, grid_size * grid_size)

        # Check for Game Over
        if lives <= 0:
           
            display_game_info(screen, level, score, high_score, lives, ui_height)

            if score > high_score:
                high_score = score
                save_high_score(high_score_file, high_score)
            display_end_of_round_menu(screen, level, score, high_score, ui_height, screen_size)

            pygame.display.update()

            # Reset the game settings
            score = 0
          
            lives = DEFAULT_SETTINGS['initial_lives']
            grid_size = DEFAULT_SETTINGS['initial_grid_size']
            num_revealed_squares = DEFAULT_SETTINGS['num_revealed_squares']
            correct_guesses = 0  # Reset correct_guesses
            level = DEFAULT_SETTINGS['initial_level']  # Reset the level to 1

            # Wait for player input to start the next round
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        waiting_for_input = False

        pygame.display.update()

if __name__ == '__main__':
    main()
