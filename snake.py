import pygame
import random
import sys
from collections import deque

pygame.init()

# 화면 설정
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
INFO_HEIGHT = 40

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GRAY = (40, 40, 40)

HUMAN_HEAD = (0, 220, 0)
HUMAN_BODY = (0, 140, 0)
AI_HEAD = (60, 140, 255)
AI_BODY = (30, 80, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT + INFO_HEIGHT))
pygame.display.set_caption("Snake: Human vs AI")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 44)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def opposite(d):
    return (-d[0], -d[1])


def in_bounds(pos):
    return 0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT


def random_food_position(occupied):
    free_cells = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in occupied
    ]
    if not free_cells:
        return None
    return random.choice(free_cells)


def draw_cell(pos, color):
    rect = pygame.Rect(
        pos[0] * CELL_SIZE, pos[1] * CELL_SIZE + INFO_HEIGHT, CELL_SIZE, CELL_SIZE
    )
    pygame.draw.rect(screen, color, rect)


def show_message(text, y_offset=0, font_obj=None):
    font_obj = font_obj or big_font
    surface = font_obj.render(text, True, WHITE)
    rect = surface.get_rect(
        center=(WIDTH // 2, (HEIGHT + INFO_HEIGHT) // 2 + y_offset)
    )
    screen.blit(surface, rect)


def bfs_path_direction(start, goal, obstacles):
    """start에서 goal까지 최단 경로의 첫 방향을 반환. 못 찾으면 None."""
    if start == goal:
        return None
    queue = deque([start])
    came_from = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for d in (UP, DOWN, LEFT, RIGHT):
            nxt = (current[0] + d[0], current[1] + d[1])
            if not in_bounds(nxt) or nxt in obstacles or nxt in came_from:
                continue
            came_from[nxt] = current
            queue.append(nxt)

    if goal not in came_from:
        return None

    # goal에서부터 역추적하여 start 바로 다음 칸을 찾는다
    step = goal
    while came_from[step] != start:
        step = came_from[step]
        if step is None:
            return None
    return (step[0] - start[0], step[1] - start[1])


def flood_fill_count(start, obstacles, limit=None):
    """start에서 도달 가능한 빈 칸 개수를 센다."""
    if start in obstacles or not in_bounds(start):
        return 0
    visited = {start}
    queue = deque([start])
    count = 0
    while queue:
        current = queue.popleft()
        count += 1
        if limit is not None and count >= limit:
            return count
        for d in (UP, DOWN, LEFT, RIGHT):
            nxt = (current[0] + d[0], current[1] + d[1])
            if in_bounds(nxt) and nxt not in obstacles and nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return count


def choose_ai_direction(ai_head, ai_dir, food, obstacles):
    """AI 뱀의 다음 방향을 결정한다."""
    valid_dirs = [d for d in (UP, DOWN, LEFT, RIGHT) if d != opposite(ai_dir)]

    # 1) 사과까지 최단 경로 시도
    path_dir = bfs_path_direction(ai_head, food, obstacles)
    if path_dir is not None and path_dir in valid_dirs:
        nxt = (ai_head[0] + path_dir[0], ai_head[1] + path_dir[1])
        if in_bounds(nxt) and nxt not in obstacles:
            return path_dir

    # 2) 경로가 없으면 가장 넓은 공간으로 이동 (생존 우선)
    best_dir = None
    best_space = -1
    for d in valid_dirs:
        nxt = (ai_head[0] + d[0], ai_head[1] + d[1])
        if not in_bounds(nxt) or nxt in obstacles:
            continue
        space = flood_fill_count(nxt, obstacles)
        if space > best_space:
            best_space = space
            best_dir = d

    if best_dir is not None:
        return best_dir

    # 3) 안전한 곳이 없으면 아무 방향이나 (곧 게임 오버)
    return ai_dir


def main():
    human = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
    human_dir = RIGHT
    human_next_dir = RIGHT

    ai = [(GRID_WIDTH * 3 // 4, GRID_HEIGHT // 2)]
    ai_dir = LEFT

    occupied = set(human) | set(ai)
    food = random_food_position(occupied)

    human_score = 0
    ai_score = 0
    speed = 10

    game_over = False
    result_text = ""
    human_alive = True
    ai_alive = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_RETURN:
                        return main()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                else:
                    if event.key in (pygame.K_UP, pygame.K_w) and human_dir != DOWN:
                        human_next_dir = UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and human_dir != UP:
                        human_next_dir = DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and human_dir != RIGHT:
                        human_next_dir = LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and human_dir != LEFT:
                        human_next_dir = RIGHT

        if not game_over:
            human_dir = human_next_dir

            obstacles_for_ai = set(human) | set(ai)
            ai_dir = choose_ai_direction(ai[0], ai_dir, food, obstacles_for_ai)

            new_human_head = (human[0][0] + human_dir[0], human[0][1] + human_dir[1])
            new_ai_head = (ai[0][0] + ai_dir[0], ai[0][1] + ai_dir[1])

            human_body_set = set(human)
            ai_body_set = set(ai)

            # 벽 충돌
            if not in_bounds(new_human_head):
                human_alive = False
            if not in_bounds(new_ai_head):
                ai_alive = False

            # 자기 몸 충돌
            if human_alive and new_human_head in human_body_set:
                human_alive = False
            if ai_alive and new_ai_head in ai_body_set:
                ai_alive = False

            # 서로의 몸 충돌 (상대의 현재 몸 전체와 비교)
            if human_alive and new_human_head in ai_body_set:
                human_alive = False
            if ai_alive and new_ai_head in human_body_set:
                ai_alive = False

            # 정면 충돌 (같은 칸으로 진입)
            if human_alive and ai_alive and new_human_head == new_ai_head:
                human_alive = False
                ai_alive = False

            if not human_alive or not ai_alive:
                game_over = True
                if not human_alive and not ai_alive:
                    result_text = "Draw!"
                elif not human_alive:
                    result_text = "AI Wins!"
                else:
                    result_text = "You Win!"
            else:
                human.insert(0, new_human_head)
                if new_human_head == food:
                    human_score += 1
                    food = random_food_position(set(human) | set(ai))
                else:
                    human.pop()

                ai.insert(0, new_ai_head)
                if new_ai_head == food:
                    ai_score += 1
                    food = random_food_position(set(human) | set(ai))
                else:
                    ai.pop()

                speed = min(20, 10 + max(human_score, ai_score) // 5)

                if food is None:
                    game_over = True
                    result_text = "Board Full!"

        screen.fill(BLACK)

        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRAY, (x, INFO_HEIGHT), (x, HEIGHT + INFO_HEIGHT))
        for y in range(INFO_HEIGHT, HEIGHT + INFO_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        for i, segment in enumerate(human):
            draw_cell(segment, HUMAN_HEAD if i == 0 else HUMAN_BODY)
        for i, segment in enumerate(ai):
            draw_cell(segment, AI_HEAD if i == 0 else AI_BODY)
        if food is not None:
            draw_cell(food, RED)

        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, INFO_HEIGHT))
        score_text = f"You: {human_score}   AI: {ai_score}"
        score_surface = font.render(score_text, True, WHITE)
        screen.blit(score_surface, (10, 8))

        if game_over:
            show_message(result_text, -20)
            show_message(
                "Press ENTER to restart, ESC to quit", 20, font_obj=font
            )

        pygame.display.flip()
        clock.tick(speed)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
