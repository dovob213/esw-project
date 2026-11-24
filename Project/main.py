
from PIL import Image, ImageDraw, ImageFont
import time
import random

from Joystick import Joystick


# ==============================
# 게임 설정
# ==============================

WIDTH = 240
HEIGHT = 240

GAME_TIME = 60
FPS_DELAY = 0.04

# 물고기 종류 및 점수
FISH_LIST = [
    {"name": "SMALL FISH", "score": 10, "weight": 50},
    {"name": "CARP", "score": 20, "weight": 30},
    {"name": "GOLD FISH", "score": 50, "weight": 15},
    {"name": "RARE FISH", "score": 100, "weight": 5}
]


# 게임 초기화

def main():

    joystick = Joystick()

    screen = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(screen)

    font = ImageFont.load_default()

    # 게임 상태
    state = "TITLE"

    score = 0
    remaining_time = GAME_TIME

    # 낚시 위치
    fishing_x = WIDTH // 2

    # 낚시 관련 시간
    game_start_time = 0
    bite_time = 0
    result_time = 0

    # 현재 낚인 물고기
    current_fish = None

    result_message = ""

    # 버튼 입력 이전 상태
    previous_buttons = {
        "A": False,
        "B": False,
        "C": False,
        "L": False,
        "R": False,
        "U": False,
        "D": False
    }

    # ==============================
    # 버튼 입력 처리
    # ==============================

    def get_inputs():

        buttons = {
            "A": not joystick.button_A.value,
            "B": not joystick.button_B.value,
            "C": not joystick.button_C.value,
            "L": not joystick.button_L.value,
            "R": not joystick.button_R.value,
            "U": not joystick.button_U.value,
            "D": not joystick.button_D.value
        }

        just_pressed = {}

        for key in buttons:
            just_pressed[key] = (
                buttons[key] and not previous_buttons[key]
            )

        previous_buttons.update(buttons)

        return just_pressed

    # ==============================
    # 물고기 선택
    # ==============================

    def select_fish():

        weights = [fish["weight"] for fish in FISH_LIST]

        return random.choices(
            FISH_LIST,
            weights=weights,
            k=1
        )[0]

    # ==============================
    # 텍스트 출력
    # ==============================

    def draw_center_text(text, y, color="black"):

        bbox = draw.textbbox((0, 0), text, font=font)

        text_width = bbox[2] - bbox[0]

        x = (WIDTH - text_width) // 2

        draw.text((x, y), text, fill=color, font=font)

    # ==============================
    # 배경 그리기
    # ==============================

    def draw_background():

        # 하늘
        draw.rectangle(
            (0, 0, WIDTH, 100),
            fill=(135, 206, 235)
        )

        # 땅
        draw.rectangle(
            (0, 100, WIDTH, HEIGHT),
            fill=(80, 170, 120)
        )

        # 연못
        draw.ellipse(
            (5, 105, 235, 230),
            fill=(40, 120, 190)
        )

        # 물결
        for x in range(20, 230, 40):

            draw.arc(
                (x, 145, x + 25, 155),
                0,
                180,
                fill=(180, 220, 255)
            )

            draw.arc(
                (x + 10, 185, x + 35, 195),
                0,
                180,
                fill=(180, 220, 255)
            )

    # ==============================
    # 플레이어 그리기
    # ==============================

    def draw_player():

        # 머리
        draw.ellipse(
            (fishing_x - 10, 75, fishing_x + 10, 95),
            fill=(255, 210, 160)
        )

        # 몸
        draw.rectangle(
            (fishing_x - 10, 95, fishing_x + 10, 125),
            fill=(50, 50, 180)
        )

        # 낚싯대
        draw.line(
            (fishing_x + 8, 100, fishing_x + 35, 65),
            fill=(90, 60, 30),
            width=2
        )

    # ==============================
    # ==============================
    # ==============================
    
    # 게임 화면 출력   (함수들 호출하기)
    # ==============================

    def render():

        draw_background()

        # 플레이어
        draw_player()

        # 낚시 위치 표시
        draw.line(
            (fishing_x + 30, 65, fishing_x + 30, 135),
            fill=(255, 255, 255),
            width=1
        )

        # 물고기 입질 표시
        if state == "BITING":

            draw.ellipse(
                (fishing_x + 20, 150, fishing_x + 40, 165),
                fill=(255, 220, 50)
            )

            draw_center_text("BITE!", 30, "red")

        # 상단 정보
        draw.rectangle(
            (0, 0, WIDTH, 20),
            fill=(20, 50, 80)
        )

        draw.text(
            (5, 5),
            f"SCORE: {score}",
            fill="white",
            font=font
        )

        draw.text(
            (170, 5),
            f"{int(remaining_time)}s",
            fill="white",
            font=font
        )

        # 상태별 안내
        if state == "IDLE":

            draw_center_text("PRESS A TO CAST", 210)

        elif state == "WAITING":

            draw_center_text("WAITING...", 210, "white")

        elif state == "BITING":

            draw_center_text("PRESS B NOW!", 210, "yellow")

        elif state == "RESULT":

            draw.rectangle(
                (25, 75, 215, 170),
                fill=(255, 255, 255)
            )

            draw_center_text(result_message, 95, "black")

            if current_fish:
                draw_center_text(
                    current_fish["name"],
                    120,
                    "blue"
                )

        joystick.disp.image(screen)

    # ==============================
    # 메인 게임 루프
    # ==============================

    try:

        while True:

            now = time.monotonic()

            command = get_inputs()

            # ----------------------
            # 시작 화면
            # ----------------------

            if state == "TITLE":

                screen = Image.new(
                    "RGB",
                    (WIDTH, HEIGHT),
                    (30, 100, 150)
                )

                draw = ImageDraw.Draw(screen)

                draw_center_text("PIXEL FISHING", 75, "white")
                draw_center_text("FISHING GAME", 110, "yellow")
                draw_center_text("PRESS ANY BUTTON", 180, "white")

                joystick.disp.image(screen)

                if any(command.values()):

                    state = "IDLE"
                    game_start_time = now

            # ----------------------
            # 게임 진행 시간 관리
            # ----------------------

            else:

                remaining_time = max(
                    0,
                    GAME_TIME - (now - game_start_time)
                )

                if remaining_time <= 0:

                    state = "GAMEOVER"

            # ----------------------
            # 낚시 대기 상태
            # ----------------------

            if state == "IDLE":

                if command["L"]:
                    fishing_x = max(20, fishing_x - 10)

                if command["R"]:
                    fishing_x = min(190, fishing_x + 10)

                if command["A"]:

                    state = "WAITING"

                    # 입질까지 랜덤 대기 시간
                    bite_time = now + random.uniform(2, 5)

            # ----------------------
            # 물고기 입질 대기
            # ----------------------

            elif state == "WAITING":

                if now >= bite_time:

                    state = "BITING"

                    # 입질 후 제한 시간
                    bite_time = now + 1.5

            # ----------------------
            # 물고기 낚기
            # ----------------------

            elif state == "BITING":

                if command["B"]:

                    current_fish = select_fish()

                    score += current_fish["score"]

                    result_message = "SUCCESS!"

                    state = "RESULT"

                    result_time = now

                elif now >= bite_time:

                    current_fish = None

                    result_message = "ESCAPED!"

                    state = "RESULT"

                    result_time = now

            # ----------------------
            # 결과 화면
            # ----------------------

            elif state == "RESULT":

                if now - result_time >= 1.5:

                    state = "IDLE"

            # ----------------------
            # 게임 종료
            # ----------------------

            elif state == "GAMEOVER":

                screen = Image.new(
                    "RGB",
                    (WIDTH, HEIGHT),
                    (20, 50, 80)
                )

                draw = ImageDraw.Draw(screen)

                draw_center_text("GAME OVER", 65, "white")

                draw_center_text(
                    f"FINAL SCORE: {score}",
                    110,
                    "yellow"
                )

                draw_center_text(
                    "PRESS C TO RESTART",
                    180,
                    "white"
                )

                joystick.disp.image(screen)

                if command["C"]:

                    score = 0
                    remaining_time = GAME_TIME
                    fishing_x = WIDTH // 2

                    game_start_time = now

                    state = "IDLE"

            # ----------------------
            # 일반 게임 화면 출력
            # ----------------------

            if state not in ("TITLE", "GAMEOVER"):

                render()

            time.sleep(FPS_DELAY)

    except KeyboardInterrupt:

        print("Game terminated.")


if __name__ == "__main__":
    main()
