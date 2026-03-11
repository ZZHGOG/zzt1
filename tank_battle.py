import math
import random
import tkinter as tk
from dataclasses import dataclass
from typing import List

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS_MS = 16  # about 60fps

PLAYER_SPEED = 3.2
ENEMY_SPEED = 2.0
BULLET_SPEED = 7.5
BULLET_RADIUS = 4

PLAYER_COLOR = "#2ecc71"
ENEMY_COLOR = "#e74c3c"
BULLET_COLOR = "#f1c40f"
BG_COLOR = "#1f2937"
TEXT_COLOR = "#e5e7eb"


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    owner: str
    alive: bool = True

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.y < 0 or self.x > WINDOW_WIDTH or self.y > WINDOW_HEIGHT:
            self.alive = False


@dataclass
class Tank:
    x: float
    y: float
    angle: float
    speed: float
    color: str
    is_player: bool
    hp: int = 3
    cooldown: int = 0

    @property
    def body_radius(self) -> float:
        return 20

    def update_cooldown(self) -> None:
        if self.cooldown > 0:
            self.cooldown -= 1

    def move_forward(self, amount: float) -> None:
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * amount
        self.y += math.sin(rad) * amount
        self._clamp_inside()

    def move_backward(self, amount: float) -> None:
        self.move_forward(-amount)

    def rotate_left(self, amount: float) -> None:
        self.angle = (self.angle - amount) % 360

    def rotate_right(self, amount: float) -> None:
        self.angle = (self.angle + amount) % 360

    def shoot(self) -> Bullet | None:
        if self.cooldown > 0:
            return None
        rad = math.radians(self.angle)
        muzzle = self.body_radius + 8
        bullet = Bullet(
            x=self.x + math.cos(rad) * muzzle,
            y=self.y + math.sin(rad) * muzzle,
            vx=math.cos(rad) * BULLET_SPEED,
            vy=math.sin(rad) * BULLET_SPEED,
            owner="player" if self.is_player else "enemy",
        )
        self.cooldown = 20
        return bullet

    def draw(self, canvas: tk.Canvas) -> None:
        r = self.body_radius
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill=self.color, outline="")

        rad = math.radians(self.angle)
        gun_len = r + 10
        x2 = self.x + math.cos(rad) * gun_len
        y2 = self.y + math.sin(rad) * gun_len
        canvas.create_line(self.x, self.y, x2, y2, fill="#111827", width=6, capstyle=tk.ROUND)

        hp_text = f"{self.hp}"
        canvas.create_text(self.x, self.y - r - 12, text=hp_text, fill=TEXT_COLOR, font=("Segoe UI", 9, "bold"))

    def _clamp_inside(self) -> None:
        r = self.body_radius
        self.x = max(r, min(WINDOW_WIDTH - r, self.x))
        self.y = max(r, min(WINDOW_HEIGHT - r, self.y))


class TankBattleGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("坦克大战（Windows 可运行版）")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self.player = Tank(100, WINDOW_HEIGHT / 2, 0, PLAYER_SPEED, PLAYER_COLOR, True)
        self.enemies: List[Tank] = self._spawn_enemies(5)
        self.bullets: List[Bullet] = []

        self.keys: set[str] = set()
        self.frame = 0
        self.score = 0
        self.game_over = False

        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)

    def _spawn_enemies(self, count: int) -> List[Tank]:
        enemies = []
        for _ in range(count):
            x = random.randint(WINDOW_WIDTH // 2, WINDOW_WIDTH - 60)
            y = random.randint(60, WINDOW_HEIGHT - 60)
            angle = random.randint(0, 359)
            enemies.append(Tank(x, y, angle, ENEMY_SPEED, ENEMY_COLOR, False, hp=2))
        return enemies

    def _on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "j" and not self.game_over:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)
        if key == "r" and self.game_over:
            self._restart()

    def _on_key_release(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        self.keys.discard(key)

    def run(self) -> None:
        self._tick()
        self.root.mainloop()

    def _tick(self) -> None:
        self.frame += 1
        if not self.game_over:
            self._update()
        self._draw()
        self.root.after(FPS_MS, self._tick)

    def _update(self) -> None:
        self._handle_player_input()
        self.player.update_cooldown()

        for enemy in self.enemies:
            self._update_enemy(enemy)
            enemy.update_cooldown()

        for bullet in self.bullets:
            bullet.update()

        self._process_collisions()
        self.bullets = [b for b in self.bullets if b.alive]
        self.enemies = [e for e in self.enemies if e.hp > 0]

        if not self.enemies:
            self.enemies.extend(self._spawn_enemies(4))

        if self.player.hp <= 0:
            self.game_over = True

    def _handle_player_input(self) -> None:
        if "a" in self.keys:
            self.player.rotate_left(3)
        if "d" in self.keys:
            self.player.rotate_right(3)
        if "w" in self.keys:
            self.player.move_forward(self.player.speed)
        if "s" in self.keys:
            self.player.move_backward(self.player.speed)

    def _update_enemy(self, enemy: Tank) -> None:
        if self.frame % 40 == 0:
            enemy.rotate_right(random.choice([-20, -10, 0, 10, 20, 30]))

        enemy.move_forward(enemy.speed)
        if random.random() < 0.03:
            enemy.rotate_right(random.randint(90, 180))

        if random.random() < 0.02:
            enemy.angle = math.degrees(math.atan2(self.player.y - enemy.y, self.player.x - enemy.x))

        if random.random() < 0.015:
            bullet = enemy.shoot()
            if bullet:
                self.bullets.append(bullet)

    def _process_collisions(self) -> None:
        for bullet in self.bullets:
            if not bullet.alive:
                continue

            if bullet.owner == "player":
                for enemy in self.enemies:
                    if self._hit(bullet.x, bullet.y, enemy.x, enemy.y, enemy.body_radius):
                        enemy.hp -= 1
                        bullet.alive = False
                        if enemy.hp <= 0:
                            self.score += 100
                        break
            else:
                if self._hit(bullet.x, bullet.y, self.player.x, self.player.y, self.player.body_radius):
                    self.player.hp -= 1
                    bullet.alive = False

    def _draw(self) -> None:
        self.canvas.delete("all")

        for bullet in self.bullets:
            self.canvas.create_oval(
                bullet.x - BULLET_RADIUS,
                bullet.y - BULLET_RADIUS,
                bullet.x + BULLET_RADIUS,
                bullet.y + BULLET_RADIUS,
                fill=BULLET_COLOR,
                outline="",
            )

        self.player.draw(self.canvas)
        for enemy in self.enemies:
            enemy.draw(self.canvas)

        tips = "操作: W/S 前后移动, A/D 旋转, J 开火"
        self.canvas.create_text(12, 12, anchor="nw", text=tips, fill=TEXT_COLOR, font=("Segoe UI", 11))
        self.canvas.create_text(12, 36, anchor="nw", text=f"分数: {self.score}", fill=TEXT_COLOR, font=("Segoe UI", 12, "bold"))

        if self.game_over:
            self.canvas.create_text(
                WINDOW_WIDTH / 2,
                WINDOW_HEIGHT / 2,
                text="游戏结束\n按 R 重新开始",
                fill="#fca5a5",
                font=("Segoe UI", 28, "bold"),
                justify="center",
            )

    def _restart(self) -> None:
        self.player = Tank(100, WINDOW_HEIGHT / 2, 0, PLAYER_SPEED, PLAYER_COLOR, True)
        self.enemies = self._spawn_enemies(5)
        self.bullets = []
        self.score = 0
        self.game_over = False

    @staticmethod
    def _hit(x1: float, y1: float, x2: float, y2: float, radius: float) -> bool:
        return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= radius ** 2


def main() -> None:
    root = tk.Tk()
    game = TankBattleGame(root)
    game.run()


if __name__ == "__main__":
    main()
