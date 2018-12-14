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
        center_offset = self.get_width()/2 * RIGHT + self.get_height()/2 * DOWN
        self.move_to(target + center_offset)
        self.tip = target
        return self

class Drawing(VMobject):
    CONFIG = {
        'fill_color': BLACK,
        'stroke_opacity': 0,
        'width': 0.02,
        'drop_density': 100, # per unit length
        'uniform': False
    }

    def __init__(self, stencil, **kwargs):
        VMobject.__init__(self, **kwargs)
        if self.uniform:
            self.resample_by_arc_length(density = self.drop_density)
        self.length = stencil.get_length()
        nb_anchors = int(self.drop_density * self.length) + 1
        self.points = stencil.points

        if len(self.points) != 0:
            self.insert_n_anchor_points(nb_anchors)
            self.set_fill(opacity=0)
            for point in self.get_anchors():
                circle = Dot(
                    radius=0.5*self.width,
                    fill_color=self.fill_color
                )
                circle.move_to(point + self.width/10 * np.random.randn(3))
                self.add(circle)

        for submob in stencil.submobjects:
            self.add(Drawing(submob, **kwargs))

    def get_curve_family(self):
        sub_curve_families = list(map(Drawing.get_curve_family, self.submobjects))
        all_curves = [self] + list(it.chain(*sub_curve_families))
        all_curves = list(filter(lambda x: isinstance(x, Drawing), all_curves))
        return remove_list_redundancies(all_curves)

class DrawnLine(Drawing):
    CONFIG = {
        'arc_angle': 0 # if it's a circular arc, = 0 if it's a straight line
    }

    def __init__(self, start, end, **kwargs):
        self_as_line = Line(start, end, **kwargs)
        Drawing.__init__(self, self_as_line, **kwargs)


class MovePencilTo(Transform):
    def __init__(self, pencil, target_tip, **kwargs):
        pencil.target = pencil.copy()
        pencil.target.point_to(target_tip)
        MoveToTarget.__init__(self, pencil, **kwargs)


class ContinuousDraw(Animation):
    CONFIG = {
        'color': BLACK,
        'canvas': None
    }

    def __init__(self, pencil, curve, **kwargs):
        if len(curve.submobjects) == 0:
            EmptyAnimation.__init__(self, **kwargs)
            return
        Animation.__init__(self, pencil, **kwargs)
        self.pencil = pencil
        self.curve = curve
        self.drops = self.curve.submobjects
        for drop in self.drops:
            drop.set_fill(opacity=0)
        self.canvas.add(self.curve)
        self.n_drops = len(self.drops)
        self.n_visible_drops = 0
        self.update(0)

    def update_mobject(self, alpha):
        if alpha == 0 or alpha > 1:
            return
        if len(self.curve.points) == 0:
            return
        tip_point = self.curve.point_from_proportion(alpha)
        self.pencil.point_to(tip_point)
        n_newly_visible_drops = int(alpha * self.n_drops)
        for drop in self.drops[self.n_visible_drops:n_newly_visible_drops]:
            drop.set_fill(opacity = 1)
        self.n_visible_drops = n_newly_visible_drops

    def cleanup(self):
        for drop in self.drops:
            drop.set_fill(opacity = 1)



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

    def play_drawing(self, drawing, run_time = 1):
        PENCIL_MOVE_TIME = 0.5
        curves_to_draw = drawing.get_curve_family()
        lengths = [curve.length for curve in curves_to_draw]
        total_length = sum(lengths)
        total_run_time = run_time + PENCIL_MOVE_TIME*len(lengths)
        run_times = [length/total_length*total_run_time for length in lengths]

        for (curve, run_time) in zip(curves_to_draw, run_times):
            self.play(
                MovePencilTo(self.pencil, curve.point_from_proportion(0),
                canvas = self.frame,
                run_time = PENCIL_MOVE_TIME
                )
            )
            self.play(
                ContinuousDraw(self.pencil, curve,
                    canvas = self.frame,
                    run_time = run_time
                )
            )


    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle = 0)
        self.add_foreground_mobject(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(2*UP + 3*LEFT)
        stencil = Annulus(inner_radius = 1, outer_radius = 2)
        #stencil = SVGMobject(file_name='mypi').scale(1)
        print(stencil.get_length())
        print(stencil.get_proportional_length(1))
        drawing = Drawing(stencil, uniform = True)
        #return
        # button1 = SegmentButton().move_to(4.2*LEFT + 3*DOWN)
        # self.add(button1)

        # touch = Touch()

        #self.play(TouchDown(touch, run_time = 0.1))

        self.play_drawing(drawing)



