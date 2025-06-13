import cv2
import mediapipe as mp
import math
import time
import random
import pygame

# Initialize pygame mixer for sound
pygame.mixer.init()
eat_sound = pygame.mixer.Sound('eat.mp3')  # You must have eat.wav
gameover_sound = pygame.mixer.Sound('end.mp3')

# Initialize camera and MediaPipe
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Game variables
snake_points = []
lengths = []
total_length = 0
max_length = 150
score = 0
food = [300, 300]
food_radius = 12
colors = [(255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 255, 255)]
game_over = False
prev = [0, 0]

def restart_game():
    global snake_points, lengths, total_length, max_length, score, food, game_over, prev
    snake_points = []
    lengths = []
    total_length = 0
    max_length = 150
    score = 0
    food = [random.randint(100, 500), random.randint(100, 400)]
    game_over = False
    prev = [0, 0]

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if not game_over:
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark
            index_finger = lm[8]
            cx, cy = int(index_finger.x * w), int(index_finger.y * h)

            if len(snake_points) == 0:
                snake_points.append([cx, cy])
                prev = [cx, cy]
            else:
                dist = math.hypot(cx - prev[0], cy - prev[1])
                if dist > 5:
                    snake_points.append([cx, cy])
                    lengths.append(dist)
                    total_length += dist
                    prev = [cx, cy]

                while total_length > max_length:
                    total_length -= lengths[0]
                    lengths.pop(0)
                    snake_points.pop(0)

            # Check for collision with food
            if math.hypot(cx - food[0], cy - food[1]) < food_radius + 10:
                score += 1
                max_length += 20
                food = [random.randint(50, w - 50), random.randint(50, h - 50)]
                eat_sound.play()

            # Self collision
            for pt in snake_points[:-20]:  # ignoring head area
                if math.hypot(cx - pt[0], cy - pt[1]) < 10:
                    gameover_sound.play()
                    game_over = True
                    break

        # Draw Snake
        for i in range(1, len(snake_points)):
            color = colors[i % len(colors)]
            cv2.line(img, tuple(snake_points[i - 1]), tuple(snake_points[i]), color, 15)

        # Draw Food
        cv2.circle(img, tuple(food), food_radius, (0, 0, 255), -1)

        # Score
        cv2.putText(img, f'Score: {score}', (10, 40), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)

    else:
        # Game Over UI
        cv2.putText(img, 'GAME OVER!', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
        cv2.putText(img, f'Your Score: {score}', (180, 260), cv2.FONT_HERSHEY_COMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(img, 'Press R to Restart', (180, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("Hand-Controlled Snake Game 🎮", img)

    key = cv2.waitKey(1)
    if key == 27:  # ESC to quit
        break
    if key == ord('r'):
        restart_game()

cap.release()
cv2.destroyAllWindows()
