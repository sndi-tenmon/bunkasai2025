import pyxel, math

# リソースファイル（画像などの入っているファイル）
RESOURCE_FILE = "my_resource.pyxres"

# 無敵モードにしたいときはTrueにする
IS_MUTEKI_MODE = False
#IS_MUTEKI_MODE = True

# ゲーム時間
GAME_TIME = 120

# +++ 敵クラス +++
class Enemy:
    def __init__(self, x, y, takoyaki=False):
        self.enemy_x = x
        self.enemy_y = y
        self.enemy_width = 15  # 幅
        self.enemy_height = 13  # 高さ
        self.is_takoyaki = takoyaki  # たこやきフラグ
        
    # 敵を動かす
    def update(self, speed):
        self.enemy_x -= speed

    # 敵を描画する
    def draw(self):
        pyxel.blt(self.enemy_x, self.enemy_y, 0, 16, 0, self.enemy_width, self.enemy_height, 0)

# +++ 敵列クラス +++
class Enemy_colmun:
    def __init__(self, x, size):
        self.enemies = []  # 列に詰める敵を入れておくためのリスト
        self.score_line_x = x + 10  # 通過判定用の線
        self.is_scored = False      # スコア加算済フラグ
        self.column_size = size     # 列の幅（敵の幅）
    
    # ** 列に敵を詰める **
    def add_enemy(self):
        # プレイヤーが通り抜けるための穴をつくる
        hole_size = 3  # 空ける穴の数

        # 穴の開始位置を決める。rndiはランダムな数を生成する。
        hole_index = pyxel.rndi(1, self.column_size - hole_size) 

        # たこやきを配置する位置
        # 穴をあけた上下の2箇所に設定
        takoyaki_index_top = hole_index -1
        takoyaki_index_low = hole_index + hole_size

        # 次に入れる敵と重ならないように距離をつくる
        enemy_distance = 0

        # 敵をリストに詰める
        for i in range(self.column_size):
            if  i == takoyaki_index_top or i == takoyaki_index_low:  # たこ焼き
                self.enemies.append(Enemy(pyxel.width, enemy_distance, takoyaki=True))
            elif i not in range(hole_index,hole_index + hole_size):  # 通常の敵
                self.enemies.append(Enemy(pyxel.width, enemy_distance))                
            enemy_distance += 14

    # ** 敵列を移動させる **
    def update(self, speed):
        # 通過判定用の線の移動
        self.score_line_x -= speed

        # リスト内の敵の移動（Enemyクラスのupdateメソッドを実行する）
        for enemy in self.enemies:
            enemy.update(speed)

    # ** 敵列を描画する **
    def draw(self):
        for enemy in self.enemies:
            if enemy.is_takoyaki:
                pyxel.blt(enemy.enemy_x, enemy.enemy_y, 0, 48, 16, enemy.enemy_width, enemy.enemy_height, 0)                        
            else:
                pyxel.blt(enemy.enemy_x, enemy.enemy_y, 0, 16, 0, enemy.enemy_width, enemy.enemy_height, 0)

# +++ ミサイルクラス +++
class Missile:
    def __init__(self, x, y,):
        self.x = x
        self.y = y
        self.width = 14
        self.height = 5
        self.speed = 4
    
    def update(self):
        self.x += self.speed

    def draw(self):
        pyxel.blt(self.x +5, self.y +2, 1, 0, 0, self.width, self.height, 0)

# +++ 飛行物クラス +++
class Flying_thing:
    def __init__(self, x, y, bank_x, bank_y, width, height, c_width, c_height, mode,  bank_no=0, 
                 speed=1, amplitude=30, period=30, frame=0):
        self.fl_x = x
        self.fl_y = y
        self.bank_x = bank_x
        self.bank_y = bank_y
        self.bank_w = width
        self.bank_h = height
        self.mode = mode  # 動き方  
        self.bank_no = bank_no
        self.speed = speed
        self.amplitude = amplitude  # 振幅
        self.period = period  # 周期
        self.frame = frame  # 波の進み具合
        self.base_y = y
        self.width = c_width
        self.width = c_height


    # ** 前に進める **
    def update(self):
        self.fl_x -= self.speed
        if self.mode == "s":  # 真っ直ぐ
            pass
        elif self.mode == "w":  # 波状
            self.frame += 0.5
            self.fl_y = self.base_y + math.sin(self.frame / self.period * 2 * math.pi) * self.amplitude

    # ** 描画 **
    def draw(self):
        pyxel.blt(self.fl_x, self.fl_y, self.bank_no, self.bank_x, self.bank_y, self.bank_w, self.bank_h, 0, scale=1.5)

# +++ メインのクラス +++
class Game:
    def __init__(self):
        pyxel.init(160, 120, title="F星より愛をこめて")
        # pyxel.load("umplus_j10r.bdf")
        # self.jp_font = pyxel.Font("umplus_j10r.bdf")
        self.jp_font = pyxel.Font("misaki_gothic.bdf")
        
        # 初期値を設定
        self.reset()  

        # リソースファイルの読み込み
        pyxel.load(RESOURCE_FILE)
        pyxel.run(self.update, self.draw)

    # ** リセット **
    def reset(self):
        # * ゲーム画面：初期値はタイトル画面 *
        self.game_mode = "title"

        # * 時間 *
        self.timer = GAME_TIME
        self.timer_counter = 0
        self.timeover = False
        self.game_finish = False
        self.game_finish_display = 45
        self.is_kekkahappyo = False
        self.result_comment = ""
        self.comment_font_color = None
        #ready go の表示の時間
        self.ready_count = 90
        self.is_ready = True
        self.ready_mongon = ""
        # ** レベル・点数 **
        self.level = 1
        self.level_counter = 0
        self.score = 0
        self.level_up = 0
        self.fusei_score = 0
        self.fusei_gekihascore = 0

        # 敵列・飛行物のスピード
        self.enemy_speed = 1

        # * プレイヤーのパラメータ *
        self.player_x = 10
        self.player_y = 55
        self.player_width = 16 
        self.player_height = 9
        self.player_speed = 2
        self.player_vy = 0       # Y方向の速度
        self.gravity = 0.15 + self.level * 0.015       # 重力
        self.jump_power = -1.8   # ジャンプの強さ（マイナスで上昇）

        # * 敵列（障害物）*
        self.enemy_columns = []

        # 新しい敵列を出現させるまでのフレーム数（時間）
        # 初期値はプレイ開始直後に現れているように短めに設定
        self.spawn_interval = 15

        # * 飛行物 * 
        # 飛行物リストの設定
        self.flying_list = [
            Flying_thing(pyxel.width, 60, 16, 16, 17, 6,24,6, "w"),  # 彗星
            Flying_thing(pyxel.width, 60, 32, 16, 16, 16,18,18, "w"),  # 人工衛星
            Flying_thing(pyxel.width, 60, 16, 32, 16, 16,18,18, "w"),  # 地球
            Flying_thing(pyxel.width, 60, 34, 37, 13, 5,13,5, "w"),  # 黒板消し
            Flying_thing(pyxel.width, 60, 0, 16, 16, 7,17,6, "w"), # UFO
            Flying_thing(pyxel.width, 60, 48, 0, 16, 13,18,14, "w")  # ウシ
        ]

        # 飛行物リストのINDEX
        self.fl_index = 0
        # self.fl_fusei = Flying_thing(pyxel.width, 60, 35, 65, 41, 31, "w")  # 布星

        # 敵のHP
        self.destroyed_point = 3  # HP3として設定


        # 飛行物のインスタンスを代入
        self.flying_thing = self.flying_list[self.fl_index]
        self.flying_thing_fusei = Flying_thing(pyxel.width, 60, 35, 65, 41, 31,41,33, "w")
        self.is_destroyed = False
        self.is_fusei = False
        # リストを変数に入れて可読性をあげる
        # self.fl_thing = self.flying_list[self.fl_index]

        # リストを変数に入れて可読性をあげる
        # self.fl_thing = self.flying_list[self.fl_index]

        # 飛行物がとんでくるまでの時間 (最初は長めにとる）
        self.fl_time_counter = 600         
        self.is_flying = False  # 飛行物出現フラグ

        # * ミサイル *
        self.missiles = []  # ミサイルを格納するリスト
        self.missile_count = 200  # ミサイル数

        # * 衝突 *
        self.is_collision = False # 衝突フラグ
        self.collision_time = 60 # 衝突停止時間
        self.saituyo_time = 0  # 無敵時間
        self.itai = 0  #あたった回数
    # ** 四角形の衝突判定 **
    # 引数：プレイヤーのX座標, プレイヤーのY座標, プレイヤーの幅, プレイヤーの高さ
    # 　　　　敵のX座標, 敵のY座標, 敵の幅, 敵の高さ
    def is_collision_rect(self, x_1, y_1, width_1,  height_1, x_2, width_2, y_2, height_2):
        if (x_1 + width_1 > x_2 and x_1 < x_2 + width_2 and
            y_1 + height_1 > y_2 and y_1 < y_2 + height_2):
            return True
        else:
            return False

    # ** 円の衝突判定 **
    # 半径を考慮して、中心間距離で衝突判定を行う。引数は四角形と同じ
    def is_collision_circle(self, x_1, y_1, width_1, height_1, x_2, y_2, width_2, height_2):
        # 半径は長辺の半分。幅と髙さ、大きい方の値を半分にする。
        r_1 = max(width_1, height_1) / 2 * 0.85
        r_2 = max(width_2, height_2) / 2 * 0.85

        # 中心の座標を計算
        cx_1 = x_1 + width_1 / 2
        cy_1 = y_1 + height_1 / 2
        cx_2 = x_2 + width_2 / 2
        cy_2 = y_2 + height_2 / 2

        # 中心間の距離を計算
        dx = cx_1 - cx_2
        dy = cy_1 - cy_2

        # sqrtは平方根を出す関数
        distance = math.sqrt(dx**2 + dy**2) 

        # 衝突判定
        return distance < (r_1 + r_2)

    # **********
    # 更新処理
    # **********
    def update(self):
        # タイトル画面
        if self.game_mode == "title":
            self.update_title()

        # ゲームプレイ画面
        elif self.game_mode == "play":
            # ゲームオーバーフラグが立っていない時にゲームを実行する
            self.update_play()

        # 結果発表！
        elif self.game_mode == "finish":
            self.update_finish()
  
    # === タイトル画面時_更新 ===
    def update_title(self):
        if (pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)):
            self.game_mode = "play"  # プレイ画面へ移行

    # === プレイ画面_更新 ===
    def update_play(self):
        if pyxel.btnp(pyxel.KEY_E):
            self.reset()
            self.game_mode = "title"  # プレイ画面へ移行

        # 衝突時はプレイヤーを動かさずに止める
        if self.is_collision:
            self.update_play_itai()  # 当たった時の処理。痛い。
            # self.update_play_time()  # 時間の更新・処理
            return

        # 無敵状態の時は、無敵時間数を減らす
        if self.saituyo_time > 0:
            self.saituyo_time -= 1

        # ゲーム開始直後は動きを止める
        if self.is_ready:
            self.update_play_ready()
        else:
            self.update_play_player_control() # プレイヤーの操作
            self.update_play_missile()  # ミサイルの更新
            self.update_play_time()  # 時間の更新・処理

        self.update_play_shogai_butu()  # 障害物の生成・更新
        self.update_play_missile_collision()  # ミサイルとの衝突判定
        self.update_play_flying_thing()  # 飛行物の生成・更新
        self.update_play_level()  # レベルの更新

        if not IS_MUTEKI_MODE:  # テスト用に無敵モードじゃないとき
            self.update_play_enemy_collision()  # 敵との衝突判定

        if self.timer <= 30:
            self.update_play_fusei_fight()  # 布星との戯れ

    def update_play_ready(self):
        # 準備時間のタイマーストップ
        self.ready_count -= 1 
        if self.ready_count >= 30:
            self.ready_mongon = "Ready"
        elif self.ready_count >= 0:
            self.ready_mongon = "GO!!"
        else:
            self.is_ready = False
            self.ready_mongon = ""

    # ** プレイヤー操作 **
    def update_play_player_control(self):
            # ENTERキーを押した時、大きく上昇する
            if (pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)) and self.player_y:
                self.player_vy = self.jump_power - 0.3
                self.player_y -= self.player_speed
            # ENTERキーを押した時、小さく上昇する
            if (pyxel.btnp(pyxel.KEY_0)or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) and self.player_y:
                self.player_vy = self.jump_power + 0.5
                self.player_y -= self.player_speed
            # 重力をかける
            self.player_vy += self.gravity
            self.player_y += self.player_vy

            if self.player_y > pyxel.height - self.player_height:
                self.player_y = pyxel.height - self.player_height
                self.player_vy = 0

            # 天井にぶつかったら止める
            if self.player_y < 0:
                self.player_y = 0
                self.player_vy = 0

    # ** ミサイル処理 **
    def update_play_missile(self):
        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)) and self.missile_count > 0:
            # プレイヤーの中央からミサイルを発射する
            missile_x = self.player_x + self.player_width // 2  
            missile_y = self.player_y

            # ミサイルをリストに追加
            self.missiles.append(Missile(missile_x, missile_y))  
        
            # ミサイルを発射したとき、ミサイルの数を減らす
            self.missile_count -= 1  

        # それぞれのミサイルを取り出して、missile.y -= missile.speedをする。
        for missile in self.missiles:
            missile.update()
        
        alive_missiles = []
        for missile in self.missiles:
            if missile.y > 0:
                alive_missiles.append(missile)
        self.missiles = alive_missiles      

   # ** 障害物（敵列）の処理 **
    def update_play_shogai_butu(self):
        # 障害物の列をつくる
        if self.spawn_interval <= 0:
            column = Enemy_colmun(pyxel.width, 9)  # 敵列を生成
            column.add_enemy()  # 敵列に敵＆たこやきを充填
            self.enemy_columns.append(column)
            self.spawn_interval = 100 - self.level * 12
        else:
            # 規定時間になっていなければ、カウンターを減らす
            self.spawn_interval -= 1

        # 画面内に残っている敵を格納する「生存リスト」を定義
        alive_enemy_columns = []  

        # 敵をリストから1つずつ取り出して処理を行う
        for enemy_column in self.enemy_columns:
            enemy_column.update(self.enemy_speed)  # 敵を動かす

            # プレイヤーを通過したかチェックしてスコア加算
            if enemy_column.score_line_x < self.player_x and not enemy_column.is_scored:
                enemy_column.is_scored = True

                # 衝突時と無敵状態の時以外でスコアを加算する
                if not self.is_collision and self.saituyo_time == 0:
                    self.score += 15
                    self.level_counter += 1
                    # self.level_up += 1
            # 画面内に敵が残っている列だけ保持
            if enemy_column.score_line_x >= 0:
                alive_enemy_columns.append(enemy_column)
            
        # 画面内の敵列リストを更新
        self.enemy_columns = alive_enemy_columns

    # ** 飛行物の設定 **
    def update_play_flying_thing(self):
        # まだ出現待ちならカウンターを減らす
        if not self.is_flying:
            if self.fl_time_counter > 0:
                self.fl_time_counter -= 1
                return
            else:
                # 出現させる
                self.is_flying = True
                self.flying_thing = self.flying_list[self.fl_index]
                self.flying_thing.fl_x = pyxel.width
                self.destroyed_point = 3
            return  # 出現待ち中はこれ以降処理しない

        # 出現中の飛行物を更新
        self.flying_thing.update()

        # 撃破された場合
        if self.is_destroyed:
            self.is_destroyed = False
            self.is_flying = False
            self.fl_time_counter = 240  # 10秒待つ
            # 次の飛行物インデックスを進める（ループ）
            self.fl_index = (self.fl_index + 1) % len(self.flying_list)

        # 画面外に出た場合も同じ処理
        if self.flying_thing.fl_x <= 0 - self.flying_thing.bank_w:
            self.is_flying = False
            self.fl_time_counter = 240  # 10秒待つ
            self.fl_index = (self.fl_index + 1) % len(self.flying_list)

      # ** 敵との衝突判定 **
    def update_play_enemy_collision(self):
        # ① プレイヤーの衝突判定
        if self.saituyo_time <= 0:  # 無敵時間以外の時に判定する
            # 上下にぶつかったら死亡
            if self.saituyo_time <= 0:
                if self.player_y <= 0 or self.player_y >= pyxel.height - self.player_height:
                    self.is_collision = True

            # 敵列との衝突
            for enemy_column in self.enemy_columns:
                for enemy in enemy_column.enemies:
                    if self.is_collision_circle(self.player_x, self.player_y, self.player_width - 5, self.player_height,
                                enemy.enemy_x, enemy.enemy_y, enemy.enemy_width, enemy.enemy_height):
                        self.is_collision = True

            # ② 飛行物との衝突
            if self.flying_thing is not None:
                if self.is_collision_circle(self.player_x, self.player_y, self.player_width - 5, self.player_height,
                                                self.flying_thing.fl_x - 10, self.flying_thing.fl_y, self.flying_thing.bank_w, self.flying_thing.bank_h):
                    self.is_collision = True
     
            # あたった回数
            if self.is_collision == True:
                self.itai += 1
                # 布星タイム以外は時間を5秒減らす
                if not self.is_fusei:
                    self.timer -= 2
   
    # 布星との戯れ
    def update_play_fusei_fight(self):
        self.is_fusei = True
        self.flying_thing_fusei.update()
        if self.flying_thing_fusei.fl_x <= 150:
            self.flying_thing_fusei.speed = 0.1
        #布星の撃破スコア
        if self.fusei_score >= 50:
            self.fusei_gekihascore = 100
   
   # ** ミサイルとの衝突判定 ** 
    def update_play_missile_collision(self):
        # 削除リストを定義
        missiles_to_remove = []
        enemies_to_remove= []

        # 敵とミサイルの衝突
        for missile in self.missiles: # ミサイルのループ
            for enemy_column in self.enemy_columns:  # 敵列
                for enemy in enemy_column.enemies :
                    if self.is_collision_circle(missile.x, missile.y, missile.width, missile.height,
                        enemy.enemy_x, enemy.enemy_y, enemy.enemy_width, enemy.enemy_height):
                            # コピーしたmissileとenemyの要素を削除リストへ追加
                            if missile not in missiles_to_remove:
                                missiles_to_remove.append(missile)
                            if not enemy.is_takoyaki and enemy not in enemies_to_remove:
                                enemies_to_remove.append((enemy_column, enemy))
                            break
            # 飛行物
            if self.is_flying:
                if self.is_collision_circle(missile.x, missile.y, missile.width, missile.height,
                        self.flying_thing.fl_x, self.flying_thing.fl_y-10, self.flying_thing.bank_w*1.5, self.flying_thing.bank_h*2):
                    self.destroyed_point -= 1  
                    missiles_to_remove.append(missile)                 
                    if self.destroyed_point <= 0:
                        self.is_flying = False
                        self.is_destroyed = True
                        self.score += 25

            # 布星
            if self.is_fusei:
                if self.is_collision_circle(missile.x, missile.y, missile.width, missile.height,
                        self.flying_thing_fusei.fl_x, self.flying_thing_fusei.fl_y-10, self.flying_thing_fusei.bank_w, self.flying_thing_fusei.bank_h*2):
                    self.fusei_score += 1


                    missiles_to_remove.append(missile)

        # まとめて削除
        for missile in missiles_to_remove:
            if missile in self.missiles:
                self.missiles.remove(missile)

        for enemy_column, enemy in enemies_to_remove:
            if enemy in enemy_column.enemies:
                enemy_column.enemies.remove(enemy)
   
    # *** レベルアップ処理 ***
    def update_play_level(self):
        if self.level_counter >= 10:
            self.level_counter = 0
            self.level += 1
            self.enemy_speed += 0.8
            self.collision_time -= 5

            print()

    # *** 衝突時の処理、痛い ***
    def update_play_itai(self):
        # 衝突時、数秒間の無敵処理を行う
        self.saituyo_time = 45  # 無敵時間

        self.collision_time -= 1 
        if self.collision_time <= 0:
            self.collision_time = 45  # 衝突停止時間
            self.is_collision = False

    # *** 時間の更新・処理 ***
    def update_play_time(self):
        # 制限時間の更新
        if self.timer_counter >= 30:  # 30フレームで1秒を減らす
            self.timer -= 1
            self.timer_counter = 0
        else:
            self.timer_counter += 1

        # タイムオーバー時の処理
        if self.timer < 0:
            self.timeover = True  # タイムオーバーフラグを立てる
        if self.timeover:
            self.game_mode = "finish"  # 結果発表に変更
            return        

    # === 結果発表画面 ===
    def update_finish(self):
        self.timeover = True  # タイムオーバーフラグを立てる
        self.game_finish_display -= 1
        if self.game_finish_display == 0:
                self.game_finish = True
        if (pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
            self.reset()

    # **********
    # 描画処理
    # **********
    def draw(self):
        if self.game_mode == "title":
            self.draw_title()
        elif self.game_mode == "play":
            self.draw_play()
        elif self.game_mode == "finish":
            self.draw_finish()

    # === タイトル画面_描画 ===
    def draw_title(self):
        # 画面を黒く塗りつぶす
        pyxel.cls(0) 
        # 太陽系
        pyxel.blt(-5, -8, 2, 0, 0, 85, 160, 0,scale=0.9) 
        # タイトル
        pyxel.text(80, 10, "Ｆ星より愛をこめて", 7, self.jp_font) 
        # 天文台
        pyxel.blt(100, 75, 1, 1, 16, 48, 39, 0,scale=1.5)                         
        # pyxel.text(60, 10, "月がキレイなお前のゲーム", 7, self.jp_font) 
        # pyxel.text(35, 60, "Press Big Jump button", 7)
        pyxel.text(5, 110, "Presented by 天文部Ｐ班", 7, self.jp_font) 

    # === プレイ画面_描画 ===
    def draw_play(self):

         # 画面を黒く塗りつぶす
        pyxel.cls(0) 

        # レディーゴーの表示
        pyxel.text(63,50,self.ready_mongon,10)              

        # 画面の縁を紫にする
        pyxel.line(0,0,160,0,2)
        pyxel.line(0,1,160,1,2)
        pyxel.line(0,119,160,119,2)

        # プレイヤーの描画
        if self.saituyo_time == 0 or self.saituyo_time % 5 == 0 :
            pyxel.blt(self.player_x, self.player_y, 0, 0, 0, self.player_width, self.player_height, 0)

        # 敵列の描画。敵列リストから1つずつ取り出して描画する。
        for enemy_column in self.enemy_columns:
            enemy_column.draw()

        #ミサイルの描写
        for missile in self.missiles: 
            missile.draw()

        # ミサイル数
        now_missile = f"MISSILE:{self.missile_count:02}"
        pyxel.text(40, 2, now_missile, 7)

        # 飛行物の描画
        if self.is_flying:
            self.flying_thing.draw()

        # 爆発の描画
        if self.is_collision:
            pyxel.blt(self.player_x +1 , self.player_y -2, 0, 32, 0, 16, 15, 0)

        # タイムオーバーの文字描画
        if self.timeover:
            pyxel.text(63, 70, "Time Over", 14) 

        # 時間
        now_timer = f"TIME:{round(self.timer):03}"
        pyxel.text(1, 2, now_timer, 7)

        # レベル
        now_level=f"LEVEL:{round(self.level):02}"
        pyxel.text(120, 8, now_level, 7)

        # スコアの描画
        now_score = f"SCORE:{round(self.score):04}"
        pyxel.text(120, 2, now_score, 7)        

        # 布星の描画
        if self.is_fusei:
            self.flying_thing_fusei.draw()
        #布星コンボの描写
        if self.fusei_score >=1:
            fusei_combo = f"{self.fusei_score}"
            pyxel.text(self.flying_thing_fusei.fl_x +17,self.flying_thing_fusei.fl_y -15,fusei_combo,7)

    # === 成績発表！画面_描画 ===
    def draw_finish(self):
        # comment_font_color = None

        if self.timeover:
            pyxel.text(63, 50, "TIME UP", 14) 
        if self.game_finish : 
            score_result = f"SCORE       {self.score:04}"
            zandan_result = f"ZANDANSU     {self.missile_count:03}"
            itai_result = f"ITAI!!       {self.itai:03} "       
            fusei_result = f"FUSEI SCORE {self.fusei_score*10 +self.fusei_gekihascore :04}"
            self.total_score = self.score + self.missile_count + self.fusei_score *10 + self.fusei_gekihascore - self.itai *5
            total_result = f"TOTAL       {self.total_score :04}"

                # 布星コメント
            if not self.is_kekkahappyo :
                comment_great = ["うん、すばらしい", "よくやりましたね", "それはいいですね"]
                comment_good = ["いいと思います", "満点が10点なら7点です", "ざんねん！惜しい！"]
                comment_normal = ["おや、めずらしい", "それも正解になりうるが...", "それはちがくないか？"]
                comment_bad = ["      「 ... 」","     I'm camel", "      「 ラクダ...い？ 」"]

                comment_index = pyxel.rndi(0,2)
                if self.total_score >= 1500:
                    self.result_comment = comment_great[comment_index]
                    self.comment_font_color = 10

                elif self.total_score >= 750 : 
                    self.result_comment = comment_good[comment_index]
                    self.comment_font_color = 7
                elif self.total_score >= 500 :
                    self.result_comment = comment_normal[comment_index]
                    self.comment_font_color  = 8
                else :
                    self.result_comment = comment_bad[comment_index]
                    self.comment_font_color  = 13
   
                self.is_kekkahappyo = True
            
            pyxel.cls(0)
            # 太陽系
            #pyxel.blt(0, 0, 2, 0, 0, 85, 160, 0,scale=1) 
            reseult_defx = 90
            resurlt_y = 10
            pyxel.text(reseult_defx, resurlt_y, score_result,7)
            pyxel.text(reseult_defx, resurlt_y + 10, zandan_result, 7)
            pyxel.text(reseult_defx, resurlt_y + 20,fusei_result,7)
            pyxel.text(reseult_defx, resurlt_y + 30, itai_result, 8)
            pyxel.line(reseult_defx - 5, resurlt_y + 38,160,48,7)
            pyxel.text(reseult_defx, 52, total_result, 7)

            # 布星
            if self.total_score >= 500 :
                pyxel.blt(10,55,0,35,56,76,96,scale=0.9)
            # あまりにも点が低いとラクダが現れる
            else :
                pyxel.blt(25,75,0,0,113,16,16,scale=2)
                
            # 布星コメント
            pyxel.text(5, 100, self.result_comment, self.comment_font_color, self.jp_font) 
            # pyxel.text(70, 100, "それも正解となりうるが", 7, self.jp_font) 

# ゲームを実行する！
Game() 