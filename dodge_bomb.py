import os
import sys
import pygame as pg
import random
import time


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5), 
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


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
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

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
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        if kk_rct.colliderect(bb_rct): # こうかとんRectと爆弾Rectが重なったら
            # print("ゲームオーバー")
            gameover(screen)
            return
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] # 横方向の移動量
                sum_mv[1] += mv[1] # 縦方向の移動量
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
