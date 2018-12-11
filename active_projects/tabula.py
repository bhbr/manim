from big_ol_pile_of_manim_imports import *

class Pencil(ImageMobject):
    CONFIG = {
        'tip': ORIGIN,
        'pointing_angle': 1/8 * TAU, # from the top
    }

    def __init__(self, **kwargs):
        ImageMobject.__init__(self, filename_or_array='pencil_white2', **kwargs)
        self.scale(3.1)
        self.next_to(self.tip, DOWN, buff = 0)
        self.rotate(self.pointing_angle, about_point = self.tip)
        print('initialized')

    def point_to(self, target):
        dv = target - self.tip
        self.shift(dv)
        self.tip = target


class DrawnLine(Line):
    CONFIG = {
        'fill_color': BLACK,
        'stroke_opacity': 0,
        'width': 0.02,
        'drop_density': 100, # per unit length
        'arc_angle': 1/4*TAU # if it's a circular arc
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


class Draw(Animation):
    CONFIG = {
        'color': BLACK,
        'arc_angle': 0,
        'canvas': None
    }

    def __init__(self, mobject, target, **kwargs):
        Animation.__init__(self, mobject, **kwargs)
        self.pencil = mobject
        self.start = self.pencil.tip
        self.end = target
        self.drawn_line = DrawnLine(self.start, self.end,
            fill_color=self.color, fill_opacity=0, path_arc=self.arc_angle)
        self.canvas.add(self.drawn_line)
        self.drops = self.drawn_line.submobjects
        for drop in self.drops:
            drop.set_fill(opacity = 0)
        self.n_drops = len(self.drops)
        self.n_visible_drops = 0

    def update_mobject(self, alpha):
        if alpha == 0:
            return
        if self.arc_angle == 0:
            tip_point = interpolate(self.start, self.end, alpha)
        else:
            s = np.sin(self.arc_angle * DEGREES)
            c = np.cos(self.arc_angle * DEGREES)
            R = np.array([[c, -s],[s, c]])
            b = self.end - np.dot(R, self.start)
            M = np.eye(3) - R
            arc_center = np.linalg.solve(R, b)
            tip_point = self.start.copy().rotate(
                alpha * self.arc_angle * DEGREES,
                about_point = arc_center
            )
        self.pencil.point_to(tip_point)
        n_newly_visible_drops = int(alpha * self.n_drops)
        for drop in self.drops[self.n_visible_drops:n_newly_visible_drops]:
            drop.set_fill(opacity = 1)
        self.n_visible_drops = n_newly_visible_drops


class PencilScene(Scene):

    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle=TAU/8)
        self.add_foreground_mobject(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(2*UP + 3*LEFT)
        
        self.play(
            #Draw(self.pencil, 3*UP + 3*RIGHT, canvas = self.frame, run_time = 5)
            self.pencil.move_to, 3*UP + 3*RIGHT
        )


class TestScene(Scene):

    def construct(self):

        pencil = ImageMobject(filename_or_array='pencil_white2').scale(3)
        pencil.rotate(TAU/8)
        self.add(pencil)
        self.play(
            pencil.move_to, 3*RIGHT + 2*UP
        )



