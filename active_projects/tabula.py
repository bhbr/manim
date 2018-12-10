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


class DrawnLine(Line):
    CONFIG = {
        'fill_color': BLACK,
        'stroke_opacity': 0,
        'width': 0.02,
        'drop_density': 100, # per unit length
        'path_arc': 1/4*TAU # it's a circular arc
    }

    def __init__(self, start, end, **kwargs):
        Line.__init__(self, start, end, **kwargs)
        length = np.linalg.norm(start - end)
        self.n_arc_anchors = int(self.drop_density * length) + 1
        self.generate_points()
        self.set_fill(opacity=0)
        for point in self.get_anchors():
            circle = Dot(
                radius=0.5*self.width,
                fill_color=self.fill_color
            )
            circle.move_to(point + self.width/10 * np.random.randn(3))
            self.add(circle)





class PencilScene(Scene):

    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle=TAU/4)
        self.add_foreground_mobject(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(3*UP)

        line = DrawnLine(LEFT, self.pencil.tip)
        self.add(line)





