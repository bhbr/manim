from big_ol_pile_of_manim_imports import *

class Pencil(ImageMobject):
    CONFIG = {
        'x': 0,
        'y': 0,
        'pointing_angle': 1/8 * TAU, # from the top
    }

    def __init__(self, **kwargs):
        ImageMobject.__init__(self, filename_or_array='pencil_white2', **kwargs)
        self.tip = self.x * RIGHT + self.y * UP
        self.scale(3.1)
        self.point_to(self.tip)
        self.rotate(self.pointing_angle, about_point = self.tip)

    def point_to(self, target):
        self.tip = target
        self.next_to(self.tip, DOWN)


class PencilScene(Scene):

    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle=TAU/4)
        self.add(self.frame, self.pencil)
        self.pencil.point_to(3*UP)
