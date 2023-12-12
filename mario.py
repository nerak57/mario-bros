import pyxel
from constants import SPRITE_SPEED_X
from constants import GRAVITY
from constants import SPRITE_JUMP_INITIAL_SPEED


class Mario:
    def __init__(self, x: int, y: int, size: int):
        """
        :param x: int,
        :param y: int,
        :param size: int
        """
        # position in the sprite image bank: image, u (x posit in bank),
        # v (y image posit in bank), w, h
        self.sprite = [0, 0, 0, 16, 24]
        self.mario_w = self.sprite[3]  # height
        self.__dying = False
        self.jumping = False
        self.gravity = GRAVITY
        self.__x = x
        self.__y = y
        self.x_vel = SPRITE_SPEED_X
        self.y_vel = 0
        self.size = size
        self.__lives = 3

    def move_y(self, dy):
        self.y -= dy

    def move_x(self, direc: bool):
        if direc:  # if mario is moving right
            self.sprite[3] = 16
            self.x += self.x_vel
        elif not direc:
            self.sprite[3] = -16  # invert the image sprite
            self.x -= self.x_vel
        if self.x >= (self.size + 1):  # once mario is out of the screen, here on the right side
            self.x = 0 - self.mario_w  # his x position moves to the other side
        elif self.x <= (-1 - self.mario_w):  # while here, he moves out of the left size.
            # I put -1 instead of 0 to give a little margin, and he doesn't disappear right when he reached the edge
            self.x = self.size

    def animation(self):
        if self.jumping:
            self.sprite[1] = 48     # if mario is jumping, there is a fixed sprite
        elif ((pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D) or
                pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A))):
            if pyxel.frame_count % 12 < 4:
                self.sprite[1] = 0
            elif pyxel.frame_count % 12 < 8:
                self.sprite[1] = 16
            elif pyxel.frame_count % 12 < 12:
                self.sprite[1] = 32

    def loop(self):
        self.y_vel -= self.gravity
        self.move_y(self.y_vel)
        self.animation()

    def jump(self):
        self.y_vel = SPRITE_JUMP_INITIAL_SPEED

    @property
    def x(self) -> int:
        return self.__x

    @x.setter
    def x(self, x: int):
        if type(x) is not int:
            raise TypeError("x must be an integer")
        else:
            self.__x = x

    @property
    def y(self) -> int:
        return int(self.__y)

    @y.setter
    def y(self, y: float):
        self.__y = y

    @property
    def lives(self) -> int:
        return self.__lives

    @lives.setter
    def lives(self, lives: int):
        if type(lives) is not int:
            raise TypeError("lives value must be an integer")
        elif lives > 3:
            raise ValueError("Mario can't have more than 3 lives")
        else:
            self.__lives = lives

    @property
    def dying(self) -> bool:
        return self.__dying

    @dying.setter
    def dying(self, new_dying):
        self.__dying = new_dying

    def draw(self):
        if not self.__dying:
            self.animation()
            pyxel.blt(self.__x, self.__y, *self.sprite, colkey=0)
