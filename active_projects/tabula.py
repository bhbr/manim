from big_ol_pile_of_manim_imports import *

DROP_DENSITY = 100

class Pencil(ImageMobject):
    CONFIG = {
        'tip': ORIGIN,
        'pointing_angle': 1/8 * TAU, # from the top
    }

    def __init__(self, **kwargs):
        ImageMobject.__init__(self, filename_or_array='pencil_white2_rotated', **kwargs)
        self.scale(3.1)
        self.next_to(self.tip, DR, buff = 0)
        self.rotate(self.pointing_angle, about_point = self.tip)

    def point_to(self, target):
        dv = target - self.tip
        self.shift(dv)
        self.tip = target


class DrawnCurve(VMobject):
    CONFIG = {
        'fill_color': BLACK,
        'stroke_opacity': 0,
        'width': 0.02,
        'drop_density': 5, # per unit length
    }

    def __init__(self, stencil, **kwargs):
        VMobject.__init__(self, **kwargs)
        length = stencil.get_length()
        nb_anchors = int(self.drop_density * length) + 1
        self.points = stencil.points
        self.insert_n_anchor_points(nb_anchors)
        print(self.get_num_anchor_points())
        self.set_fill(opacity=0)
        for point in self.get_anchors():
            circle = Dot(
                radius=0.5*self.width,
                fill_color=self.fill_color
            )
            circle.move_to(point + self.width/10 * np.random.randn(3))
            self.add(circle)    


class DrawnLine(DrawnCurve):
    CONFIG = {
        'arc_angle': 0 # if it's a circular arc, = 0 if it's a straight line
    }

    def __init__(self, start, end, **kwargs):
        self_as_line = Line(start, end, **kwargs)
        DrawnCurve.__init__(self, self_as_line, **kwargs)


class Draw(Animation):
    CONFIG = {
        'color': BLACK,
        'canvas': None
    }

    def __init__(self, mobject, stencil, **kwargs):
        Animation.__init__(self, mobject, **kwargs)
        self.pencil = mobject
        self.stencil = stencil
        self.start = stencil.points[0]
        self.end = stencil.points[0]
        self.canvas.add(self.stencil)
        self.drops = self.stencil.submobjects
        for drop in self.drops:
            drop.set_fill(opacity = 0)
        self.n_drops = len(self.drops)
        print(self.n_drops)
        self.n_visible_drops = 0

    def update_mobject(self, alpha):
        if alpha == 0:
            return
        tip_point = self.stencil.point_from_proportion(alpha)
        self.pencil.point_to(tip_point)
        n_newly_visible_drops = int(alpha * self.n_drops)
        for drop in self.drops[self.n_visible_drops:n_newly_visible_drops]:
            drop.set_fill(opacity = 1)
        self.n_visible_drops = n_newly_visible_drops


class PencilScene(Scene):

    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle = 0)
        self.add_foreground_mobject(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(2*UP + 3*LEFT)
        pi = TexMobject('\pi', stroke_width = 0).scale(12).submobjects[0].submobjects[0]

        pi.resample_by_arc_length(density = DROP_DENSITY)
        line = DrawnCurve(pi)

#        self.add(line)        
        self.play(
            Draw(self.pencil, line,
                canvas = self.frame,
                run_time = 6,
                rate_func = lambda x: x)
        )


