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


class Button(Circle):
    CONFIG = {
        'fill_color': BLUE_E,
        'fill_opacity': 1,
        'stroke_opacity': 0,
        'radius': 0.3,
        'logo_file': None
    }

    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        if self.logo_file == None:
            self.logo = Mobject()
        else:
            self.logo = ImageMobject(self.logo_file)
        scale_factor = 0.7*2*self.radius / self.logo.get_width()
        self.logo.scale_in_place(scale_factor)
        self.logo.move_to(self)
        self.add(self.logo)

class SegmentButton(Button):
    CONFIG = {
        'logo_file': 'segment'
    }

class Touch(VGroup):
    CONFIG = {
        'radius': 0.35,
        'nb_rings': 30,
        'color': ORANGE,
        'max_opacity': 0.5
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        dr = self.radius/self.nb_rings
        for r in np.arange(0,self.radius,dr):
            alpha = r/self.radius
            ring = Annulus(inner_radius=r, outer_radius=r+dr,
                fill_color = self.color, fill_opacity = alpha * self.max_opacity)
            self.add(ring)

class TouchDown(Animation):
    CONFIG = {
        'rate_func': (lambda x: x)
    }
    def update_mobject(self, alpha):
        nb_rings = len(self.mobject.submobjects)
        total_radius = self.mobject.submobjects[-1].outer_radius
        for (i,ring) in enumerate(self.mobject.submobjects):
            opacity = 0
            if i < alpha*nb_rings:
                opacity = (1 - (alpha*nb_rings - i)/nb_rings) * self.mobject.max_opacity
            ring.set_fill(opacity=opacity)


class PencilScene(Scene):

    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle = 0)
        self.add_foreground_mobject(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(2*UP + 3*LEFT)
        two = SVGMobject(file_name='two').submobjects[0].scale(1)
        #two.resample_by_arc_length(density = DROP_DENSITY)        
        line = DrawnCurve(two)

        button1 = SegmentButton().move_to(4.2*LEFT + 3*DOWN)
        self.add(button1)

        touch = Touch()

        # self.play(
        #     Draw(self.pencil, line,
        #         canvas = self.frame,
        #         run_time = 3,
        #         rate_func = lambda x: x)
        # )

        self.play(TouchDown(touch, run_time = 0.1))

