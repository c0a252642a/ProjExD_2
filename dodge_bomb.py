import os
import sys
import pygame as pg
import random
import time
import math


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5), 
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """方向ごとのこうかとん画像を生成して辞書を返す"""
    base_img = pg.image.load("fig/3.png")
    right_img = pg.transform.flip(base_img, True, False)

    kk_dict = {
        (0, 0): None,
        (-5,  0): pg.transform.rotozoom(base_img, 0, 0.9),
        (-5, -5): pg.transform.rotozoom(base_img, -45, 0.9),
        ( 0, -5): pg.transform.rotozoom(right_img, 90, 0.9),
        (+5, -5): pg.transform.rotozoom(right_img, 45, 0.9),
        (+5,  0): pg.transform.rotozoom(right_img, 0, 0.9),
        (+5, +5): pg.transform.rotozoom(right_img, -45, 0.9),
        ( 0, +5): pg.transform.rotozoom(right_img, -90, 0.9),
        (-5, +5): pg.transform.rotozoom(base_img, 45, 0.9),
    }
    return kk_dict

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    始点(org)から終点(dst)へ向かう、ノルムが√50の方向ベクトルを計算する。
    ただし、距離が300未満の場合は元の方向(current_xy)を維持する。
    
    引数:
        org: 始点（爆弾）のRect
        dst: 終点（こうかとん）のRect
        current_xy: 現在の方向ベクトル (vx, vy)
    戻り値:
        次に移動すべき方向ベクトル (vx, vy)
    """
    # 1. 爆弾(org)とこうかとん(dst)の「中心座標」の差ベクトルを求める
    x_diff = dst.centerx - org.centerx
    y_diff = dst.centery - org.centery
    
    # 2. 2点間の距離（差ベクトルのノルム）を計算する（三平方の定理： √(x^2 + y^2) ）
    distance = math.hypot(x_diff, y_diff) # math.sqrt(x_diff**2 + y_diff**2) と同じ
    
    # 3. 距離が300未満、または距離が0（重なっている）の場合は、慣性として現在の方向をそのまま返す
    if distance < 300 or distance == 0:
        return current_xy
        
    # 4. 差ベクトルのノルムが √50 (約7.07) になるように正規化する
    # 一度長さを 1 にして（distanceで割る）、そこに √50 を掛けます
    target_norm = math.sqrt(50)
    vx = (x_diff / distance) * target_norm
    vy = (y_diff / distance) * target_norm
    
    return vx, vy

def check_bound(rct:pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル（横方向判定結果, 縦方向判定結果）
    True：画面内／False：画面外
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の大きさを変えた爆弾Surfaceのリストと加速度のリストを準備する
    戻り値: (bb_imgs, bb_accs)のタプル
    """
    bb_imgs = []
    # 1~10段階の爆弾画像を作成
    for r in range(1,11):
        bb_img = pg.Surface((20 * r, 20 * r))
        # 背景を透明にするための設定
        bb_img.set_colorkey((0, 0, 0))
        # 円の描画
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    
    # 加速度
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

def gameover(screen: pg.Surface) -> None:
    bbg_img = pg.Surface(screen.get_size())
    bbg_img.fill((0, 0, 0))
    bbg_img.set_alpha(180)
    screen.blit(bbg_img, [0,0])

    font = pg.font.Font(None, 80)
    text_surf = font.render("Game Over", True, (255, 255, 255))
    text_rct = text_surf.get_rect()
    text_rct.center = (screen.get_width() // 2, screen.get_height() // 2 - 40)
    screen.blit(text_surf, text_rct)

    cry_kk_img1 = pg.image.load("fig/8.png")
    cry_kk_rct1 = cry_kk_img1.get_rect()
    cry_kk_rct1.center = (screen.get_width() // 2-200, screen.get_height() // 2-50)
    screen.blit(cry_kk_img1, cry_kk_rct1)

    cry_kk_img2 = pg.image.load("fig/8.png")
    cry_kk_rct2 = cry_kk_img2.get_rect()
    cry_kk_rct2.center = (screen.get_width() // 2+200, screen.get_height() // 2-50)
    screen.blit(cry_kk_img2, cry_kk_rct2)

    pg.display.update()
    time.sleep(5)

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(-5,  0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    flash_kk_img = kk_imgs[(-5,  0)]

    # 拡大、加速のリストを取得
    bb_imgs, bb_accs = init_bb_imgs()
    
    # 爆弾の作成
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0,WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx = 5
    vy = 5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        # ゲーム終了判定
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        if kk_rct.colliderect(bb_rct): # こうかとんRectと爆弾Rectが重なったら
            gameover(screen)
            return
        
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] # 横方向の移動量
                sum_mv[1] += mv[1] # 縦方向の移動量

        kk_img = kk_imgs[tuple(sum_mv)] if kk_imgs[tuple(sum_mv)] is not None else flash_kk_img
        flash_kk_img = kk_img

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 500フレームごとに難易度が上がっていく。難易度は10段階
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]

        orig_center = bb_rct.center
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        bb_rct.center = orig_center

        bb_rct.move_ip((avx, avy))
        tate, yoko = check_bound(bb_rct)
        if not tate:
            vx *= -1
        if not yoko:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
