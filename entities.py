import random
import pyxel
from constants import GRAVITY
from constants import SPRITE_SPEED_X
from constants import SPRITE_JUMP_INITIAL_SPEED
from constants import HEIGHT
from constants import FPS


class Entities:
    def __init__(self, x: int, y: int, w: int, h: int):
        """:param x: int,
        :param y: int
        :param w: int
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x_vel = 0
        self.y_vel = 0
        self.sprite = [0, 0, 0, 0, 0]
        self.lives = 0
        self.upside_down_delay = 5  # seconds
        self.upside_down_delay_frames = self.__upside_down_delay * FPS
        # all these values that are 0 will be defined when the child classes are initialized

        self.gravity = GRAVITY
        self.direc = None  # will be defined when we generate the element
        self.generated = False  # this tells us if the sprite has been fully generated and created on the screen
        self.degenerate = False  # for when it un-generates upon reaching a tube
        self.ups_down = False  # upside down state (not upside_down since there's already a method)
        self.normal = True  # if they are normal state or the color changes
        self.angry = False  # only for sidesteppers, but if not defined here, animation function will have problems
        self.width = 0  # will be defined for each entity in their own separate class
        self.height = 0

        self.animation_dictionary = {}
        # In the dictionary above (according to the numbering below), the sprites (u) values for each animation
        # 1: normal
        # 2: normal, upside-down
        # 3: after color change
        # 4: after color change, upside-down
        # 5: normal, angry (crabs)
        # 6: after color change, angry (crabs)

        self.in_side()

    @property
    def upside_down_delay(self):
        return self.__upside_down_delay

    @upside_down_delay.setter
    def upside_down_delay(self, value):
        self.__upside_down_delay = value
        self.upside_down_delay_frames = self.__upside_down_delay * FPS

    @property
    def upside_down_delay_frames(self):
        return self.__upside_down_delay_frames

    @upside_down_delay_frames.setter
    def upside_down_delay_frames(self, value):
        self.__upside_down_delay_frames = value

    @property
    def is_upside_down(self):
        return self.ups_down

    def move(self, x_vel, y_vel):
        self.x += x_vel
        self.y -= y_vel
        if self.x >= (self.w + 1):  # again, how to make the sprites move to the other edge once out of range
            self.x = 0
        elif self.x <= (-1):
            self.x = self.w

    # change dir would be used when there's a collision, and they change direction: changes the velocity and image
    def change_direction(self):
        if self.direc:  # when direction is true, it's going right
            self.direc = False  # so now they go left
            self.x_vel = -self.x_vel  # the speed is inverted
            self.sprite[3] = -self.sprite[3]  # and so is the image
        elif not self.direc:  # same when they're going left, everything is inverted
            self.direc = True
            self.x_vel = -self.x_vel
            self.sprite[3] = -self.sprite[3]

    def loop(self):
        self.y_vel -= self.gravity
        self.move(self.x_vel, self.y_vel)

    def in_side(self):  # a form to randomly generate the side where they will appear
        side = random.randint(0, 1)
        if side == 0:  # appears on the left, moves to right
            self.direc, self.x, self.x_vel, self.y = True, 48, self.x_vel, 56
        else:
            self.direc, self.x, self.x_vel, self.y = False, self.w - 32 - 16, -self.x_vel, 56

    def generate_loop(self):
        if self.direc:  # to slowly generate the image:
            if self.sprite[3] < self.width:
                # we will slowly add pixels to the width of the image until it reaches the correct width,
                # particular to each entity
                self.sprite[3] += 1  # so we add one pyxel each time to the width
                self.sprite[1] -= 1  # but since we want to see the sprite generate slowly,
                # starting with the front of it, we slowly decrease the u position of the image.
                # That is, the u position was initially set on the edge of the image, where the front would be.
                # But as the width starts increasing, we must show more of the image,
                # and we move the u starting point to the left.
            else:  # and once the image has been generated, this stops, and we give the moving values
                self.generated = True
                self.gravity, self.x_vel = GRAVITY, SPRITE_SPEED_X
        else:  # this process would be inverted when the sprite is on the right
            if -self.sprite[3] < self.width:
                self.sprite[3] -= 1  # instead of adding, we take one less, since the image is, after all, inverted
                self.sprite[1] -= 1
                self.x -= SPRITE_SPEED_X // 2  # this is just to compensate, otherwise the image would go backwards
            else:
                self.generated = True
                self.gravity, self.x_vel = GRAVITY, -SPRITE_SPEED_X

    def de_generate(self):
        self.x_vel = self.y_vel = self.gravity = 0      # the sprite will no longer move nor be affected by gravity
        self.y = self.h - 40    # to set the height of the lower tube
        if self.direc:  # to specify if it's on the left or right tube
            if self.sprite[3] > 0:  # we will do the opposite thing as we did on the generate loop
                self.sprite[3] -= 1     # we remove one from its width, making it seem that it's walking inside
                self.x += 1
                # and to make it seem that it's actually walking it, and not that there's a black screen hiding the image
                # it must move one step forward
            else:
                self.change_direction()
                # once this is done, we must make it seem it comes up the upper tube, so we change its direction
                self.sprite[1] = self.width     # we reset the width so the generate loop can work
                self.y, self.x = 56, self.w - 32 - 16   # and move the sprite to the correct coordinates
                self.generated = False      # and establish that the entity is no longer generated, so it can generate again
        else:   # similarly, when it's going left
            if self.sprite[3] < 0:
                self.sprite[3] += 1     # since the image is inverted by making the width-sprite value negative,
                # instead of subtracting, we add.
            else:
                self.change_direction()
                self.sprite[1] = self.width
                self.y, self.x = 56, 48
                self.generated = False

    def reach_tube(self):
        """Coordinates of the tube so the ge-generate loop can start working"""
        return (((self.direc and self.w - 32 - self.width <= self.x) or (not self.direc and 32 >= self.x))
                and (self.y == 224 or self.y == 216))

    def upside_down(self):
        # if the object was already upside down, they would stand up again:
        if self.ups_down:
            self.ups_down = False
            if self.direc:
                self.x_vel = SPRITE_SPEED_X
            else:
                self.x_vel = -SPRITE_SPEED_X
            if self.normal:
                self.sprite[1] = self.animation_dictionary[1][0]
            if not self.normal:
                self.sprite[1] = self.animation_dictionary[3][0]
                self.x_vel *= 2
        # if the object wasn't upside down, now it is
        else:
            self.ups_down = True
            if self.normal:
                self.sprite[1] = self.animation_dictionary[2][0]
            if not self.normal:
                self.sprite[1] = self.animation_dictionary[4][0]
            self.x_vel = 0

    def angry_sprite(self):
        """This method is optional. Should be implemented only if the
        creature can be angry: sidestepper"""

    def color_change(self):
        """If too much time passes, they change color and increase speed"""
        self.normal = False
        self.x_vel = SPRITE_SPEED_X * 2

    def animation(self):
        # so we have to put all the combinations for the animation (sidestepper will have extra)
        # 1. Not upsidedown, normal state
        # 2. Upsidedown, normal state
        # 3. Not upsidedown, color changed state
        # 4. Upsidedown, color changed state
        if self.generated:  # only if the entity is fully generated
            if not self.ups_down and self.normal and not self.angry:
                # angry is added here so when we use inheritance, the sidesteppers will work
                if pyxel.frame_count % 12 < 6:
                    self.sprite[1] = self.animation_dictionary[1][0]
                elif pyxel.frame_count % 12 < 12:
                    self.sprite[1] = self.animation_dictionary[1][1]
                """Explanation of how this works. As seen in the code above, we control the time time that passes
                via de pyxel.frame_count, modules and comparisons we know how much time has passed.
                Modules give us the remainder of a division. In this case I chose module 12 so as to not make the 
                animation too quick. When a certain amount of time has passed (ie frame_count % 12 < 6: every six
                frame updates, the sprite changes. These sprites have been previously organized and stored in the 
                animation dictionary. Now say we had three sprites in for a certain entity state and we wanted the
                the sequence to last six frame updates as above. Instead of taking module 12, we'd take module 18
                (3*6), and we'd have if the module was smaller than 6, than 12 or than 18.
                If instead we wanted it to last just three frame counts, and we have two images, we take module 6
                (2*3)."""
            elif self.ups_down and self.normal:
                if pyxel.frame_count % 12 < 6:
                    self.sprite[1] = self.animation_dictionary[2][0]
                elif pyxel.frame_count % 12 < 12:
                    self.sprite[1] = self.animation_dictionary[2][1]
            elif not self.ups_down and not self.normal and not self.angry:
                if pyxel.frame_count % 12 < 6:
                    self.sprite[1] = self.animation_dictionary[3][0]
                elif pyxel.frame_count % 12 < 12:
                    self.sprite[1] = self.animation_dictionary[3][1]
            elif self.ups_down and not self.normal:
                if pyxel.frame_count % 12 < 6:
                    self.sprite[1] = self.animation_dictionary[4][0]
                elif pyxel.frame_count % 12 < 12:
                    self.sprite[1] = self.animation_dictionary[4][1]

#Code waste
    """def update(self):
        if not self.generated and not self.degenerate:  # if it hasn't been generated, the speed will be 0
            self.gravity = self.y_vel = self.x_vel = 0
            self.generate_loop()
        elif self.generated and not self.degenerate:  # else, we have that it all works normally
            if self.y_vel - self.gravity < -8:
                self.y_vel = -8 + self.gravity
            self.loop()
        elif self.degenerate:
            self.gravity = self.y_vel = self.x_vel = 0
            self.de_generate()"""

    def draw(self):
        """Draws the entity on the screen"""
        pyxel.blt(self.x, self.y, *self.sprite, colkey=0)


class Coin(Entities):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.sprite = [0, 8, 24, 0, 8]
        self.width = 8
        self.height = 8
        self.animation_dictionary = {1: (0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88)}

    # particular animation for coin cause it moves a bit faster than the others
    def animation(self):
        """And so in the case of the coin, we have 12 different images, and we want them to change every 4 frames
        4*12 = 48. We will use module 48"""
        if not self.ups_down and self.normal:
            if pyxel.frame_count % 48 < 4:
                self.sprite[1] = self.animation_dictionary[1][0]
            elif pyxel.frame_count % 48 < 8:
                self.sprite[1] = self.animation_dictionary[1][1]
            elif pyxel.frame_count % 48 < 12:
                self.sprite[1] = self.animation_dictionary[1][2]
            elif pyxel.frame_count % 48 < 16:
                self.sprite[1] = self.animation_dictionary[1][3]
            elif pyxel.frame_count % 48 < 20:
                self.sprite[1] = self.animation_dictionary[1][4]
            elif pyxel.frame_count % 48 < 24:
                self.sprite[1] = self.animation_dictionary[1][5]
            elif pyxel.frame_count % 48 < 28:
                self.sprite[1] = self.animation_dictionary[1][6]
            elif pyxel.frame_count % 48 < 32:
                self.sprite[1] = self.animation_dictionary[1][7]
            elif pyxel.frame_count % 48 < 36:
                self.sprite[1] = self.animation_dictionary[1][8]
            elif pyxel.frame_count % 48 < 40:
                self.sprite[1] = self.animation_dictionary[1][9]
            elif pyxel.frame_count % 48 < 44:
                self.sprite[1] = self.animation_dictionary[1][10]
            elif pyxel.frame_count % 48 < 48:
                self.sprite[1] = self.animation_dictionary[1][11]


class Shellcreeper(Entities):
    def __init__(self, x, y, w: int, h: int):
        super().__init__(x, y, w, h)
        self.x, self.y = x, y
        self.sprite = [0, 16, 32, 0, 16]
        self.width = 16
        self.height = 16
        self.lives = 1
        self.animation_dictionary = {1: (0, 16), 2: (32, 48), 3: (80, 96), 4: (112, 128)}
        self.upside_down_delay = 2  # seconds
        self.in_side()


class Sidestepper(Entities):
    def __init__(self, x, y, w, h: int):
        super().__init__(x, y, w, h)
        self.x, self.y = x, y
        self.sprite = [0, 16, 64, 0, 16]
        self.width = 16
        self.height = 16
        self.lives = 2
        self.x_vel = 0
        self.angry = False  # to add an extra to the animation
        self.animation_dictionary = {1: (0, 16), 2: (64, 80), 3: (96, 112), 4: (160, 176), 5: (32, 48), 6: (128, 144)}
        # 5. Angry, but normal
        # 6. Angry after color change
        self.in_side()

    def angry_sprite(self):
        self.angry = True
        if self.normal:
            self.sprite[1] = self.animation_dictionary[5][0]
            self.x_vel = SPRITE_SPEED_X * 2
        if not self.normal:
            self.sprite[1] = self.animation_dictionary[6][0]
            self.x_vel = SPRITE_SPEED_X * 4

    def animation(self):
        """Extra animations for the sidestepper, since it has one extra state"""
        if not self.ups_down and self.angry and self.normal:
            if pyxel.frame_count % 12 < 6:
                self.sprite[1] = self.animation_dictionary[5][0]
            elif pyxel.frame_count % 12 < 12:
                self.sprite[1] = self.animation_dictionary[5][1]
        if not self.ups_down and not self.normal and self.angry:
            if pyxel.frame_count % 12 < 6:
                self.sprite[1] = self.animation_dictionary[6][0]
            elif pyxel.frame_count % 12 < 12:
                self.sprite[1] = self.animation_dictionary[6][1]
        super().animation()


class Fly(Entities):
    def __init__(self, x, y, w, h: int):
        super().__init__(x, y, w, h)
        self.x, self.y = x, y
        self.sprite = [0, 16, 48, 0, 16]
        self.width = 16
        self.height = 16
        self.lives = 1
        self.jumping = False
        self.animation_dictionary = {1: (0, 16, 32), 2: (48, 64)}
        self.in_side()

    def animation(self):
        if not self.ups_down:
            if pyxel.frame_count % 18 < 6:
                self.sprite[1] = self.animation_dictionary[1][0]
            elif pyxel.frame_count % 18 < 12:
                self.sprite[1] = self.animation_dictionary[1][1]
            elif pyxel.frame_count % 18 < 18:
                self.sprite[1] = self.animation_dictionary[1][2]
        elif self.ups_down:
            if pyxel.frame_count % 12 < 6:
                self.sprite[1] = self.animation_dictionary[2][0]
            elif pyxel.frame_count % 12 < 12:
                self.sprite[1] = self.animation_dictionary[2][1]

    def loop(self):     # similar to how mario jumps
        if not self.jumping:
            self.jumping = True
            self.y_vel = SPRITE_JUMP_INITIAL_SPEED // 2
        super().loop()