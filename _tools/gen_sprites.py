"""Génère des sprites placeholder simples (formes plates + contour) pour pouvoir
tester le projet immédiatement, sans dépendre d'assets graphiques externes.
L'énoncé autorise à choisir son propre univers visuel : ces sprites sont à
remplacer par de vrais assets (voir GameArt2D - Freebies) une fois le
gameplay validé.
"""
from PIL import Image, ImageDraw
import os

OUT = "/home/claude/project/RunAndGun2D/Assets/Sprites"
UI_OUT = "/home/claude/project/RunAndGun2D/Assets/UI"
os.makedirs(OUT, exist_ok=True)
os.makedirs(UI_OUT, exist_ok=True)

OUTLINE = (20, 20, 24, 255)


def new_canvas(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def save(img, name, folder=OUT):
    path = os.path.join(folder, name)
    img.save(path)
    print("wrote", path)


def humanoid(body_color, w=48, h=64, weapon=False, weapon_color=(60, 60, 60, 255)):
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    cx = w // 2

    # tête
    head_r = w * 0.22
    d.ellipse([cx - head_r, h * 0.06, cx + head_r, h * 0.06 + head_r * 2], fill=body_color, outline=OUTLINE, width=2)

    # torse
    torso_top = h * 0.30
    torso_bottom = h * 0.66
    d.rounded_rectangle([w * 0.28, torso_top, w * 0.72, torso_bottom], radius=w * 0.12,
                         fill=body_color, outline=OUTLINE, width=2)

    # jambes
    leg_w = w * 0.16
    d.rounded_rectangle([w * 0.30, torso_bottom - 4, w * 0.30 + leg_w, h * 0.96], radius=4,
                         fill=body_color, outline=OUTLINE, width=2)
    d.rounded_rectangle([w * 0.70 - leg_w, torso_bottom - 4, w * 0.70, h * 0.96], radius=4,
                         fill=body_color, outline=OUTLINE, width=2)

    # bras
    d.rounded_rectangle([w * 0.12, torso_top + 2, w * 0.28, torso_top + h * 0.28], radius=4,
                         fill=body_color, outline=OUTLINE, width=2)
    d.rounded_rectangle([w * 0.72, torso_top + 2, w * 0.88, torso_top + h * 0.28], radius=4,
                         fill=body_color, outline=OUTLINE, width=2)

    if weapon:
        d.rounded_rectangle([w * 0.80, torso_top + h * 0.10, w * 1.02, torso_top + h * 0.20], radius=2,
                             fill=weapon_color, outline=OUTLINE, width=1)

    return img


def circle_projectile(color, d_px=16):
    img = new_canvas(d_px, d_px)
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, d_px - 2, d_px - 2], fill=color, outline=OUTLINE, width=1)
    # petite traînée
    d.ellipse([d_px * 0.35, d_px * 0.35, d_px * 0.65, d_px * 0.65], fill=(255, 255, 255, 160))
    return img


def platform_tile(w=64, h=64):
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=(91, 64, 43, 255), outline=OUTLINE, width=2)
    d.rectangle([0, 0, w - 1, h * 0.22], fill=(76, 153, 63, 255), outline=OUTLINE, width=2)
    for x in range(0, w, 16):
        d.line([(x, h * 0.22), (x, h)], fill=(70, 48, 32, 255), width=1)
    return img


def pickup_health(w=32, h=32):
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, w - 2, h - 2], fill=(255, 255, 255, 255), outline=OUTLINE, width=2)
    cw = w * 0.16
    d.rectangle([w / 2 - cw / 2, h * 0.2, w / 2 + cw / 2, h * 0.8], fill=(214, 40, 40, 255))
    d.rectangle([w * 0.2, h / 2 - cw / 2, w * 0.8, h / 2 + cw / 2], fill=(214, 40, 40, 255))
    return img


def pickup_ammo(w=32, h=32):
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([w * 0.30, h * 0.10, w * 0.70, h * 0.75], radius=4,
                         fill=(212, 175, 55, 255), outline=OUTLINE, width=2)
    d.polygon([(w * 0.30, h * 0.10), (w * 0.70, h * 0.10), (w * 0.5, h * -0.02)], fill=(212, 175, 55, 255))
    d.rectangle([w * 0.30, h * 0.75, w * 0.70, h * 0.90], fill=(120, 120, 120, 255), outline=OUTLINE, width=1)
    return img


def healthbar_bg(w=200, h=24):
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=(40, 40, 40, 220), outline=OUTLINE, width=2)
    return img


def healthbar_fill(w=200, h=24):
    img = new_canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=(214, 40, 40, 255))
    return img


# Joueur : bleu
save(humanoid((52, 108, 191, 255), weapon=True, weapon_color=(50, 50, 55, 255)), "player.png")

# Ennemi mêlée : rouge
save(humanoid((176, 46, 46, 255)), "enemy_melee.png")

# Ennemi à distance : orange, avec arme
save(humanoid((214, 130, 40, 255), weapon=True, weapon_color=(70, 40, 20, 255)), "enemy_ranged.png")

# Projectiles
save(circle_projectile((250, 220, 70, 255), 14), "projectile_player.png")
save(circle_projectile((170, 70, 220, 255), 14), "projectile_enemy.png")

# Plateforme
save(platform_tile(), "platform.png")

# Pickups
save(pickup_health(), "pickup_health.png")
save(pickup_ammo(), "pickup_ammo.png")

# UI
save(healthbar_bg(), "healthbar_bg.png", UI_OUT)
save(healthbar_fill(), "healthbar_fill.png", UI_OUT)

print("done")
