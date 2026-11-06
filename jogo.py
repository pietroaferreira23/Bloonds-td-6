"""
DEFENSORES DO VALE
Jogo tower defense original feito em Python + Pygame.
"""

import json
import math
import os
import random
import sys
from dataclasses import dataclass

import pygame

# CONFIGURACAO

WIDTH, HEIGHT = 1100, 700
FPS = 60
TITLE = "Defensores do Vale"
SAVE_FILE = "perfil_defensores.json"

BG = (21, 31, 43)
PANEL = (31, 45, 60)
PANEL_LIGHT = (43, 61, 78)
WHITE = (242, 246, 250)
MUTED = (173, 190, 204)
GREEN = (77, 181, 111)
RED = (222, 83, 83)
GOLD = (245, 194, 76)
BLUE = (82, 164, 224)

MAPS = [
    {
        "name": "Pradaria Serena",
        "color": (103, 157, 91),
        "path": [
            (0, 390), (170, 390), (170, 180),
            (420, 180), (420, 510), (700, 510),
            (700, 300), (930, 300), (1100, 300)
        ]
    },
    {
        "name": "Desfiladeiro Azul",
        "color": (83, 137, 151),
        "path": [
            (0, 160), (260, 160), (260, 470),
            (500, 470), (500, 240), (790, 240),
            (790, 530), (1100, 530)
        ]
    },
    {
        "name": "Bosque Dourado",
        "color": (151, 142, 76),
        "path": [
            (0, 530), (190, 530), (190, 300),
            (390, 300), (390, 120), (700, 120),
            (700, 390), (930, 390), (930, 210),
            (1100, 210)
        ]
    },
]

TOWERS = {
    "arqueiro": {
        "name": "Arqueiro",
        "price": 100,
        "range": 145,
        "damage": 17,
        "cooldown": .62,
        "color": (70, 160, 225),
        "radius": 17,
        "desc": "Rapido e equilibrado"
    },
    "mago": {
        "name": "Mago",
        "price": 160,
        "range": 125,
        "damage": 34,
        "cooldown": 1.05,
        "color": (177, 105, 224),
        "radius": 17,
        "desc": "Dano magico forte"
    },
    "canhao": {
        "name": "Canhao",
        "price": 210,
        "range": 112,
        "damage": 48,
        "cooldown": 1.45,
        "color": (218, 137, 67),
        "radius": 19,
        "desc": "Explosao em area"
    },
}

ENEMY_COLORS = [
    (226, 91, 91),
    (235, 145, 66),
    (193, 102, 194),
    (80, 180, 170)
]


def load_profile():
    default = {
        "coins": 0,
        "unlocked_maps": [0],
        "wins": 0,
        "best_wave": 0
    }

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for key, value in default.items():
            data.setdefault(key, value)

        return data

    except (OSError, json.JSONDecodeError):
        return default


def save_profile(profile):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                profile,
                f,
                ensure_ascii=False,
                indent=2
            )
    except OSError:
        pass


def draw_text(
    surface, text, size, color, pos,
    center=False, bold=False
):
    font = pygame.font.SysFont(
        "arial", size, bold=bold
    )

    image = font.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    surface.blit(image, rect)
    return rect


def distance(a, b):
    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )


@dataclass
class Enemy:
    x: float
    y: float
    hp: float
    max_hp: float
    speed: float
    reward: int
    path_index: int = 1
    progress: float = 0.0
    alive: bool = True
    color: tuple = (226, 91, 91)

    def update(self, dt, path):
        if not self.alive:
            return

        remaining = self.speed * dt

        while remaining > 0 and self.path_index < len(path):
            target = path[self.path_index]

            dx = target[0] - self.x
            dy = target[1] - self.y
            length = math.hypot(dx, dy)

            if length < 0.001:
                self.path_index += 1
                continue

            step = min(remaining, length)

            self.x += dx / length * step
            self.y += dy / length * step

            self.progress += step
            remaining -= step

            if step >= length:
                self.path_index += 1

        if self.path_index >= len(path):
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            (50, 45, 48),
            (int(self.x + 2), int(self.y + 3)),
            15
        )

        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            14
        )

        pygame.draw.circle(
            surface,
            (255, 225, 210),
            (int(self.x - 4), int(self.y - 4)),
            4
        )

        pygame.draw.rect(
            surface,
            (65, 35, 40),
            (self.x - 17, self.y - 23, 34, 5),
            border_radius=3
        )

        pygame.draw.rect(
            surface,
            GREEN,
            (
                self.x - 17,
                self.y - 23,
                34 * max(0, self.hp / self.max_hp),
                5
            ),
            border_radius=3
        )


@dataclass
class Projectile:
    x: float
    y: float
    target: Enemy
    damage: float
    speed: float
    color: tuple
    splash: float = 0

    def update(self, dt, enemies):
        if not self.target.alive:
            return True

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        length = math.hypot(dx, dy)

        if length <= self.speed * dt + 5:
            if self.splash:
                for enemy in enemies:
                    if (
                        enemy.alive
                        and distance(
                            (enemy.x, enemy.y),
                            (self.target.x, self.target.y)
                        ) <= self.splash
                    ):
                        enemy.hp -= self.damage

                        if enemy.hp <= 0:
                            enemy.alive = False
            else:
                self.target.hp -= self.damage

                if self.target.hp <= 0:
                    self.target.alive = False

            return True

        self.x += dx / length * self.speed * dt
        self.y += dy / length * self.speed * dt

        return False

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            5
        )


class Tower:
    def __init__(self, kind, pos):
        self.kind = kind
        self.x, self.y = pos
        self.level = 1
        self.cooldown = random.random() * .3
        self.target_mode = "Mais avancado"
        self.total_spent = TOWERS[kind]["price"]

    @property
    def stats(self):
        base = TOWERS[self.kind]

        return {
            "range": base["range"] + (self.level - 1) * 13,
            "damage": base["damage"] * (
                1 + .48 * (self.level - 1)
            ),
            "cooldown": max(
                .22,
                base["cooldown"] * (
                    1 - .10 * (self.level - 1)
                )
            ),
        }

    def update(self, dt, enemies, projectiles):
        self.cooldown -= dt

        if self.cooldown > 0:
            return

        stats = self.stats

        targets = [
            e for e in enemies
            if e.alive
            and distance(
                (self.x, self.y),
                (e.x, e.y)
            ) <= stats["range"]
        ]

        if not targets:
            return

        if self.target_mode == "Mais forte":
            target = max(targets, key=lambda e: e.hp)

        elif self.target_mode == "Mais proximo":
            target = min(
                targets,
                key=lambda e: distance(
                    (self.x, self.y),
                    (e.x, e.y)
                )
            )

        else:
            target = max(
                targets,
                key=lambda e: e.progress
            )

        splash = 48 if self.kind == "canhao" else 0

        projectiles.append(
            Projectile(
                self.x,
                self.y,
                target,
                stats["damage"],
                390,
                TOWERS[self.kind]["color"],
                splash
            )
        )

        self.cooldown = stats["cooldown"]

    def draw(self, surface, selected=False, show_range=False):
        info = TOWERS[self.kind]

        if selected and show_range:
            pygame.draw.circle(
                surface,
                (230, 235, 245),
                (int(self.x), int(self.y)),
                int(self.stats["range"]),
                1
            )

        pygame.draw.circle(
            surface,
            (39, 48, 58),
            (int(self.x + 3), int(self.y + 5)),
            info["radius"] + 2
        )

        pygame.draw.circle(
            surface,
            info["color"],
            (int(self.x), int(self.y)),
            info["radius"]
        )

        pygame.draw.circle(
            surface,
            (245, 245, 240),
            (int(self.x - 5), int(self.y - 5)),
            5
        )

        draw_text(
            surface,
            str(self.level),
            13,
            WHITE,
            (self.x, self.y + 25),
            center=True,
            bold=True
        )
