import pygame
import sys
import random
import time
import os

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
    return [[{'face_up': False, 'color': (58, 58, 82), 'width': square_size, 'guessed': False} for _ in range(grid_size)] for _ in range(grid_size)]

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
                grid[row][col]['color'] = (0, 128, 0)  # Dark green for correct
                break

    return revealed_squares

def get_user_guess(grid, guess_row, guess_col, revealed_squares, lives, score, correct_sound, incorrect_sound):
    if (guess_row, guess_col) in revealed_squares and not grid[guess_row][guess_col]['guessed']:
        print("Correct guess!")
        grid[guess_row][guess_col]['color'] = (0, 128, 0)  # Dark green for correct
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
            grid[guess_row][guess_col]['color'] = (128, 0, 0)
            grid[guess_row][guess_col]['face_up'] = True
            incorrect_sound.play()
            return False, lives - 1, score
        else:
            print("Incorrect guess.")
            grid[guess_row][guess_col]['color'] = (128, 0, 0)  # Dark red for incorrect
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
    font = pygame.font.SysFont(None, 36)
    texts = [
        font.render(f'Level: {level}', True, (169, 183, 198)),  # Light grey text
        font.render(f'Score: {score}', True, (169, 183, 198)),
        font.render(f'High Score: {high_score}', True, (169, 183, 198)),
        font.render(f'Lives: {lives}', True, (169, 183, 198))
    ]

    screen_width = screen.get_size()[0]
    total_text_width = sum(text.get_width() for text in texts)
    spacing = (screen_width - total_text_width) / (len(texts) + 1)

    x_position = spacing
    for text in texts:
        screen.blit(text, (x_position + 50, ui_height - 80))  # Adjusted y position
        x_position += text.get_width() + spacing

# New function to display the end of round menu
def display_end_of_round_menu(screen, level, score, high_score, ui_height, screen_size):
    font = pygame.font.SysFont(None, 48)
    round_text = font.render(f'Level {level}', True, (255, 255, 255))
    score_text = font.render(f'Your Score: {score}', True, (255, 255, 255))
    high_score_text = font.render(f'High Score: {high_score}', True, (255, 255, 255))

    # Create a dark blue rectangle behind the text
    menu_width = max(round_text.get_width(), score_text.get_width(), high_score_text.get_width()) + 40
    menu_height = round_text.get_height() + score_text.get_height() + high_score_text.get_height() + 60
    menu_x = (screen_size[0] - menu_width) // 2
    menu_y = (screen_size[1] - menu_height) // 2

    pygame.draw.rect(screen, (18, 18, 54), (menu_x, menu_y, menu_width, menu_height))

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

def main(num_revealed_squares):
    pygame.init()
    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Memory Game')

    ui_height = 100
    grid_size = 3  # Start with a 3x3 grid
    lives = 3  # Start with 3 lives
    level = 1  # Initialize level
    score = 0  # Initialize score
    high_score_file = "high_score.txt"
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
            grid[row][col]['color'] = (58, 58, 82)  # Dark grey for face down squares

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
                            else:
                                misses += 1  # Increment misses for incorrect guesses
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
            if score > high_score:
                high_score = score
                save_high_score(high_score_file, high_score)
            display_end_of_round_menu(screen, level, score, high_score, ui_height, screen_size)

            pygame.display.update()

            # Reset the game settings
            score = 0
            lives = 3
            grid_size = 3
            num_revealed_squares = 3
            correct_guesses = 0  # Reset correct_guesses
            level = 1  # Reset the level to 1

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
    main(3)
