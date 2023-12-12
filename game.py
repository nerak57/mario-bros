import pyxel
import time
from constants import WIDTH
from constants import HEIGHT
from constants import CAPTION
from constants import FPS
from scoreboard import Map
from tilemap import Tilemap
from constants import GRAVITY
from constants import CANVAS_DISPLAY_SCALE
from constants import DEBUG
from constants import GAME_RESOURCES
from constants import MARIO_LIVES
from constants import GAME_OVER_DELAY
from constants import BIGENTITY_DEATH_SCORE
from constants import BIGENTITY_UPSIDE_SCORE
from constants import COIN_SCORE
from constants import MARIO_LIVES
from animations import Animations
from collisions import CollisionMario
from collisions import CollisionEnemy
from collisions import CollisionCoin
from levels import Level
from levels import Levels
from mario import Mario
from enemies import EntitiesManager


class Game:
    def __init__(self):
        """Everything almost with constants, having replaced the self.height
        and self.width because they are always the same. Also initialized
        the Collision class."""
        pyxel.init(WIDTH, HEIGHT, title=CAPTION, fps=FPS, display_scale=CANVAS_DISPLAY_SCALE)
        pyxel.load(GAME_RESOURCES)
        self.map = Map(WIDTH, HEIGHT)
        self.__game_status = 0
        self.__endgame_delay_fps = 0
        self.__playing_level: Level = None
        # Different values:
        # game_statues = 0 -> start new game
        # game statues = 1 -> start level
        # game_statues = 2 -> game loop
        # game_statues = 3 -> end game
        # game_statues = 4 -> end application

        level1 = Level(num_coins=6, num_shellcreepers=2, num_sidesteppers=0,
                       num_fliers=0, layout=Tilemap(0))
        level2 = Level(num_coins=6, num_shellcreepers=2, num_sidesteppers=0,
                       num_fliers=0, layout=Tilemap(1))
        self.__levels = Levels([level1, level2])

        pyxel.run(self.update, self.draw)

    @property
    def levels(self):
        return self.__levels

    @property
    def layout(self) -> Tilemap:
        """Property for layout"""
        return self.__levels.current_level_object.layout

    @property
    def current_level_object(self) -> Level:
        """Property for current level object"""
        return self.__levels.current_level_object

    @property
    def playing_level(self) -> Level:
        """Property for playing level"""
        return self.__playing_level

    @property
    def collision_mario(self) -> CollisionMario:
        """Property for Collision"""
        return self.__collision_mario

    @property
    def collision_shellcreeper(self) -> CollisionEnemy:
        """Property for Collision of entities other than Mario"""
        return self.__collision_shellcreeper

    @property
    def collision_coin(self) -> CollisionCoin:
        """Property for Collision of entities other than Mario"""
        return self.__collision_coin

    def __prepare_play(self):
        self.__animations = Animations()
        self.__animations.add("POW", 120, 188, True)
        self.map.mario = Mario(20, HEIGHT - 42, WIDTH)

    def __prepare_level(self):
        # Initialize the entities managers from the information of the level
        self.map.coins = EntitiesManager(2, 4, 0, 1, self.playing_level.num_coins)
        self.map.shellcreepers = EntitiesManager(2, 3, 1, 1, self.playing_level.num_shellcreepers)
        self.__collision_mario = CollisionMario(layout=self.layout)
        self.__collision_shellcreeper = CollisionEnemy(
            layout=self.layout)
        self.__collision_coin = CollisionCoin(layout=self.layout)
        self.__bump_big = None

    def __debug(self):
        if DEBUG:
            # This just lets me show the stats I need to see when coding
            pyxel.text(192, 8, f"X = {self.map.mario.x}", 7)
            pyxel.text(192, 16, f"Y = {self.map.mario.y}", 7)
            pyxel.text(
                192,
                24,
                f"Tile = {self.layout.get_tile(self.map.mario.x, self.map.mario.y + 32)}",
                7,
            )
            pyxel.text(
                192,
                32,
                f"on floor ={self.layout.is_floor(self.layout.get_tile(self.map.mario.x, self.map.mario.y + 32))}",
                7,
            )
            pyxel.text(192, 40, f"yval={self.map.mario.y_vel}", 7)
            pyxel.text(
                192,
                48,
                f"on ceiling ="
                f"{self.collision_mario.touches_ceiling(self.map.mario)}",
                7,
            )
            pyxel.rectb(self.map.mario.x, self.map.mario.y, 16, 24, 7)
            pyxel.rectb(
                (self.map.mario.x // 8) * 8,
                ((self.map.mario.y + 24) // 8) * 8,
                16,
                8,
                3,
            )

            pyxel.rectb(
                (self.map.mario.x // 8) * 8, ((self.map.mario.y - 8) // 8)
                * 8, 16, 8, 3
            )
            pyxel.text(192, 56, f"contact = {self.__contact_little}", 7)
            pyxel.text(192, 64, f"contact = {self.__contact_big}", 7)
            pyxel.text(192, 72, f"bump = {self.__bump_big}", 7)

    def __draw_lives(self):
        x = 56
        for n in range(self.map.mario.lives):
            x += 10
            pyxel.blt(x, *self.map.lives_sprite)

    def __draw_scores(self):
        pyxel.blt(*self.map.i_sprite)
        pyxel.blt(*self.map.top_sprite)
        x = 32
        for n in range(6):
            x += 8
            pyxel.blt(x, 14, *self.map.i_score_sprite[n])
            pyxel.blt(x + 96, 14, *self.map.top_score_sprite[n])
        self.map.score_update(self.__score)
        # img=self.map.i_score[n][0], u=self.map.i_score[n][1],
        # v=self.map.i_score[n][2], h=self.map.i_score[n][3],
        # w=self.map.i_score[n][4]

    # Notes from the game: 1. When Mario dies, everything keeps moving. 2.
    # When mario passes a level, everything stops (fire and coins). 3. Mario
    # finishes a level when all the enemies have died: there are a limited
    # number of enemies for each lever 4. Mario does not interact in any way
    # with the tubes 5. Despite their increased speed, angry enemies still
    # spawn at the same speed as normal enemies

    def update(self):
        if self.__game_status == 0:
            # Set start level to 0
            self.levels.current_level = 0
            # We will paint here a black screen with INSERT COIN and PRESS A
            self.__prepare_play()
            self.map.mario.lives = MARIO_LIVES
            self.__score = 0
            self.map.score_update(self.__score)
            # KEY TO START GAME
            if pyxel.btnp(pyxel.KEY_S):
                self.__game_status = 1

        if self.__game_status == 1:
            # Here we initialize the level
            self.__playing_level = self.levels.current_level_object
            self.__prepare_level()
            self.__game_status = 2
        if self.__game_status == 2:
            if not self.map.mario.dying:
                if pyxel.btnp(pyxel.KEY_ESCAPE):
                    pyxel.quit()  # exit pyxel

                # ----  IMPORTANT CHANGES FOR COLLISIONS TO WORK ----
                # Limit the falling speed to guarantee mario will. Important change
                if self.map.mario.y_vel - self.map.mario.gravity < -8:
                    self.map.mario.y_vel = -8 + self.map.mario.gravity

                if (self.map.mario.y_vel > 0 and
                        self.collision_mario.touches_ceiling(self.map.mario)):
                    # When Mario makes a big jump (not really necessary anymore but
                    # still useful) and by big jump I mean the frames change,
                    # we need to take care of his velocity and make it negative so
                    # it makes sense (to fall when hit in the head with the block)
                    self.map.mario.y_vel = self.map.mario.y_vel * -1

                # -------- MARIO --------
                # the loop in mario is the one in charge
                # of gravity and the complement of jumping
                self.map.mario.loop()


                # Here is the code for going to the floor and not sinking in.
                if self.map.mario.y_vel <= 0 and self.collision_mario.touches_floor(
                        self.map.mario):
                    # once it reaches that point, the speed at which mario falls is
                    # 0, as well as the gravity
                    self.map.mario.gravity = 0
                    self.map.mario.y_vel = 0
                    self.map.mario.sprite[1] = 0
                    self.map.mario.jumping = False
                    self.map.mario.y = (self.map.mario.y // 8) * 8
                else:
                    # Using the constant for gravity
                    self.map.mario.gravity = GRAVITY

                self.__contact_little = self.collision_mario.touch_little_entity(
                    self.map.mario, self.map.coins.entities)
                if self.__contact_little is not None:
                    self.__animations.add("BONUS_COIN",
                                          self.__contact_little.x + 16,
                                          self.__contact_little.y,
                                          False)
                    self.map.coins.remove(self.__contact_little)
                    self.__score += COIN_SCORE
                self.__contact_big = self.collision_mario.touch_big_entity(
                    self.map.mario, self.map.shellcreepers.entities)
                if self.__contact_big is not None:

                    if self.__contact_big.is_upside_down:
                        self.__animations.add("BIGENTITY_DYING", self.__contact_big.x, self.__contact_big.y, False)
                        self.map.shellcreepers.remove(self.__contact_big)
                        self.__score += BIGENTITY_DEATH_SCORE
                    else:
                        self.map.mario.dying = True
                        self.__animations.add("MARIO_DYING", self.map.mario.x,
                                              self.map.mario.y, False)

                if not self.map.mario.dying:
                    # mario goes right, activating the move_x function in Mario
                    if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
                        self.map.mario.move_x(True)
                    # mario goes left, activating the move_x function in Mario
                    elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                        self.map.mario.move_x(False)
                    # mario can only jump once before setting on the ground or a platform
                    if not self.map.mario.jumping:
                        # mario jumps, activating the jump function in mario
                        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                            self.map.mario.gravity = GRAVITY
                            self.map.mario.jumping = True
                            self.map.mario.sprite[1] = 48
                            self.map.mario.jump()

                # -------- Enemies -------- #
                for shellcreeper in self.map.shellcreepers.entities:
                    if not shellcreeper.generated:
                        shellcreeper.gravity = shellcreeper.y_vel = shellcreeper.x_vel = 0
                        shellcreeper.generate_loop()
                    else:
                        shellcreeper.loop()
                        if shellcreeper and self.collision_shellcreeper.touches_floor(shellcreeper):
                            # once it reaches that point, the speed at which mario falls is
                            # 0, as well as the gravity
                            shellcreeper.gravity = 0
                            shellcreeper.y_vel = 0
                            shellcreeper.y = (shellcreeper.y // 8) * 8
                        else:
                            # Using the constant for gravity
                            shellcreeper.gravity = GRAVITY
                    if shellcreeper.reach_tube():
                        shellcreeper.de_generate()

                for coin in self.map.coins.entities:
                    if not coin.generated:
                        coin.gravity = coin.y_vel = coin.x_vel = 0
                        coin.generate_loop()
                    else:
                        coin.loop()
                        if coin and self.collision_coin.touches_floor(coin):
                            # once it reaches that point, the speed at which mario falls is
                            # 0, as well as the gravity
                            coin.gravity = 0
                            coin.y_vel = 0
                            coin.y = (coin.y // 8) * 8
                        else:
                            # Using the constant for gravity
                            coin.gravity = GRAVITY

                if (self.map.mario.y_vel > 0 and
                        self.collision_mario.touches_ceiling(self.map.mario)):
                    ceiling_type = self.layout.get_tile_ceiling_index(self.map.mario.x, self.map.mario.y)
                    if ceiling_type > 0:
                        self.map.mario.y_vel = self.map.mario.y_vel * -1
                        self.__animations.add(f"CEILING_BUMP_{ceiling_type}",
                                              (self.map.mario.x // 8) * 8,
                                              ((self.map.mario.y - 16) // 8) * 8,
                                              False)
                        self.__bump_big = self.collision_mario.bump_entity(self.map.mario, self.map.shellcreepers.entities)
                    if self.__bump_big is not None:
                        if not self.__bump_big.is_upside_down:
                            self.__animations.add("SHELLCREEPER_UPSIDE", self.__bump_big.x, self.__bump_big.y, False)
                            self.__bump_big.upside_down()
                            self.__score += BIGENTITY_UPSIDE_SCORE

                # Check if the level is finished
                if self.playing_level.completed:
                    # We will have to do something here
                    self.__game_status = 1
                    self.levels.next_level()

                # Update level goals
                self.playing_level.update(num_coins=self.map.coins.pending_entities,
                                          num_shellcreepers=self.map.shellcreepers.pending_entities,
                                          num_sidesteppers=0,
                                          num_fliers=0)

                # Update animations
                self.map.coins.update()
                self.map.shellcreepers.update()

                # Update sprites enemies
                for shellcreeper in self.map.shellcreepers.entities:
                    shellcreeper.animation()

                # Update sprites coins
                for coin in self.map.coins.entities:
                    coin.animation()

            elif not self.__animations.exist_active("MARIO_DYING"):
                new_lives = self.map.mario.lives - 1
                self.map.mario.dying = False
                self.__prepare_play()
                self.__prepare_level()
                self.map.mario.lives = new_lives
                if self.map.mario.lives == 0:
                    self.__game_status = 3

        if self.__game_status == 3:
            if pyxel.btnp(pyxel.KEY_L):
                self.__game_status = 4
            # It is game over. We need a screen of everything stopped and a
        # text saying GAME OVER

        if self.__game_status == 4:
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        if self.__game_status == 0:  # It's a state machine!!!
            self.__endgame_delay_fps = GAME_OVER_DELAY * FPS
            # 1. Background layout
            self.layout.draw()

            # 2. draw icons:
            # 2.1. Score:
            self.__draw_scores()

            pyxel.text(80, 100, "PRESS S TO START NEW GAME", 7)
            pyxel.blt(118, 124, 0, 112, 0, 16, 24, 0)
        if self.__game_status == 2:
            # We are going to paint on the screen from less moving parts
            # to more moving parts

            # 1. Background layout
            self.layout.draw()

            # 2. draw icons:
            # 2.1. Lives
            self.__draw_lives()
            # 2.2. Score:
            self.__draw_scores()

            # 3. draw animations
            self.__animations.draw()

            # 4. draw enemies
            for shellcreeper in self.map.shellcreepers.entities:
                shellcreeper.draw()

            # 5. draw coins
            for coin in self.map.coins.entities:
                coin.draw()

            # 6. draw mario
            self.map.mario.draw()

            self.__debug()

        if self.__game_status == 3:
            # 1. Background layout
            self.layout.draw()

            # 2. draw icons:
            # 2.1. Lives
            self.__draw_lives()
            # 2.2. Score:
            self.__draw_scores()

            pyxel.text(100, 100, "GAME OVER", 7)

            self.__endgame_delay_fps -= 1
            if self.__endgame_delay_fps == 0:
                self.__game_status = 0
