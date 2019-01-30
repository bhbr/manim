from big_ol_pile_of_manim_imports import *

PENCIL_WIDTH = 0.03
DROP_DENSITY = 200
PENCIL_LIFT_ANGLE = TAU/40
PENCIL_LIFT_TIME = 0.2

class Pencil(ImageMobject):
    CONFIG = {
        'tip': ORIGIN,
        'pointing_angle': 1/8 * TAU, # from the top
        'tip_is_down': False
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

    def pen_down(self):
        self.tip_is_down = True

    def pen_up(self):
        self.tip_is_down = False

    @property
    def tip_is_up(self):
        return not self.tip_is_down

    @tip_is_up.setter
    def tip_is_up(self, new_value):
        self.tip_is_down = not new_value

class Stroke(VMobject):
    CONFIG = {
        'fill_color': BLACK,
        'fill_opacity': 1.0,
        'stroke_opacity': 1.0,
        'stroke_width': 0,
        'width': PENCIL_WIDTH,
        'drop_density': DROP_DENSITY, # per unit length
        'uniform': False # resample by arc length?
    }

    def __init__(self, stencil, **kwargs):
        self.stencil = stencil.copy() # own copy for modifications
        self.stencil.submobjects = []
        VMobject.__init__(self, stencil = self.stencil, **kwargs)
        self.length = self.get_length()
        if self.uniform:
            self.stencil.resample_by_arc_length(density = self.drop_density)
        nb_anchors = int(self.drop_density * self.length) + 1
        nb_new_anchors = nb_anchors - len(self.stencil.get_anchors())

        if len(self.stencil.points) != 0:
            self.stencil.insert_n_anchor_points(nb_new_anchors)
            for point in self.stencil.get_anchors():
                drop = Dot(
                    radius=0.5*self.width,
                    fill_color=self.fill_color,
                    fill_opacity=self.fill_opacity
                )
                drop.move_to(point + self.width/10 * np.random.randn(3))
                self.add(drop)

    def get_length(self):
        return self.stencil.get_proper_length()

    def get_proper_length(self):
        return self.stencil.get_proper_length()

    def get_proportional_length(self, alpha):
        return self.stencil.get_proportional_length(alpha)
    
    def get_proportional_proper_length(self, alpha):
        return self.stencil.get_proportional_proper_length(alpha)

    def point_from_proportion(self, alpha):
        return self.stencil.point_from_proportion(alpha)

    def get_start(self):
        return self.stencil.point_from_proportion(0)

    def get_end(self):
        return self.stencil.point_from_proportion(1)

class DrawnArc(Stroke):
    CONFIG = {
        'arc_angle': TAU/4 # if it's a circular arc, = 0 if it's a straight line
    }

    def __init__(self, start, end, **kwargs):
        self_as_line = Line(start, end, **kwargs)
        Stroke.__init__(self, self_as_line.points, **kwargs)

class DrawnLine(DrawnArc):
    CONFIG = {
        'arc_angle': 0 # if it's a circular arc, = 0 if it's a straight line
    }

class Drawing(VGroup): # a group of Strokes
    CONFIG = {
        'fill_color': BLACK,
        'fill_opacity': 1.0,
        'stroke_opacity': 1.0,
        'width': PENCIL_WIDTH,
        'drop_density': DROP_DENSITY, # per unit length
        'uniform': False
    }

    def __init__(self, mobject, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.stencil = mobject
        for mob in mobject.get_family():
            if (len(mob.points) != 0):
                stroke = Stroke(mob, uniform = self.uniform)
                self.add(stroke)

    def get_length(self):
        lengths = [stroke.get_length() for stroke in self.get_strokes()]
        return sum(lengths)

    def get_strokes(self):
        return self.submobjects


class MovePencilTo(MoveToTarget):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }
    def __init__(self, pencil, target_tip, **kwargs):
        pencil.target = pencil.copy()
        pencil.target.point_to(target_tip)
        MoveToTarget.__init__(self, pencil, **kwargs)




class DrawStroke(Animation):
    CONFIG = {
        'color': BLACK,
        'canvas': None,
        'rate_func': (lambda x: x)
    }

    def __init__(self, pencil, stroke, **kwargs):
        if stroke.get_length() == 0:
            EmptyAnimation.__init__(self, **kwargs)
            return
        Animation.__init__(self, pencil, **kwargs)
        self.pencil = pencil
        self.stroke = stroke
        self.drops = self.stroke.submobjects

        for drop in self.drops:
            drop.set_stroke(opacity=0, width=0)
            drop.set_fill(opacity=0, color=self.color)
        self.canvas.add(self.stroke)
        self.n_drops = len(self.drops)
        self.n_visible_drops = 0

    def update_mobject(self, alpha):
        if alpha == 0 or alpha > 1:
            return
        tip_point = self.stroke.stencil.point_from_proportion(alpha)
        self.pencil.point_to(tip_point)
        n_newly_visible_drops = int(alpha * self.n_drops)
        for drop in self.drops[:n_newly_visible_drops]:
            drop.set_fill(opacity = 1)
        self.n_visible_drops = n_newly_visible_drops

    def cleanup(self):
        for drop in self.drops:
            drop.set_fill(opacity = 1)


class Draw(Succession):
    CONFIG = {
        'color': BLACK,
        'canvas': None,
        'rate_func': (lambda x: x)
    }

    def __init__(self, pencil, drawing, **kwargs):
        draw_lengths = [stroke.get_length() for stroke in drawing.get_strokes()]
        move_lengths = []
        p0 = pencil.tip
        for stroke in drawing.get_strokes():
            p1 = stroke.get_start()
            move_lengths.append(np.linalg.norm(p1 - p0))
            p0 = p1

        total_length = sum(draw_lengths) + sum(move_lengths)
        draw_time_proportions = [length/total_length for length in draw_lengths]
        move_time_proportions = [length/total_length for length in move_lengths]
        kwargs_here = kwargs.copy()
        run_time = kwargs_here.pop('run_time', 1)
        draw_run_times = [prop * run_time for prop in draw_time_proportions]
        move_run_times = [prop * run_time for prop in move_time_proportions]

        anims = []
        #anims.append(ScheduledAnimation(PencilUp, pencil,
        #    run_time = PENCIL_LIFT_TIME, **kwargs_here))
        for (stroke, draw_run_time, move_run_time) \
            in zip(drawing.get_strokes(), draw_run_times, move_run_times):
            anims.append(ScheduledAnimation(MovePencilTo, pencil, stroke.get_start(),
                run_time = move_run_time, **kwargs_here))
            #anims.append(ScheduledAnimation(PencilDown, pencil,
            #    run_time = PENCIL_LIFT_TIME, **kwargs_here))
            anims.append(ScheduledAnimation(DrawStroke, pencil, stroke,
                run_time = draw_run_time, **kwargs_here))
            #anims.append(ScheduledAnimation(PencilUp, pencil,
            #    run_time = PENCIL_LIFT_TIME, **kwargs_here))

        Succession.__init__(self, *anims, **kwargs_here)


class PencilDown(Rotate):
    # does not work bc of jittering
    CONFIG = {
        'in_place': True,
        'run_time': 0.2
    }
    def __init__(self, pencil, **kwargs):
        if pencil.tip_is_up:
            Rotate.__init__(self, pencil, angle=PENCIL_LIFT_ANGLE, **kwargs)
            pencil.pen_down()
        else:
            Rotate.__init__(self, pencil, angle=0, run_time=0, empty=True)

class PencilUp(Rotate):
    # does not work bc of jittering
    CONFIG = {
        'in_place': True,
        'run_time': 0.2
    }

    def __init__(self, pencil, **kwargs):
        if pencil.tip_is_down:
            Rotate.__init__(self, pencil, angle=-PENCIL_LIFT_ANGLE, **kwargs)
            pencil.pen_up()
        else:
            Rotate.__init__(self, pencil, angle=0, run_time=0, empty=True)



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
        'logo_file': 'segment.png'
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
        self.add(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(2*UP + 3*LEFT)
        #self.pencil.rotate(-PENCIL_LIFT_ANGLE) # starts lifted up
        
        #stencil = Circle()
        #stencil = Annulus(inner_radius = 1, outer_radius = 2)
        #stencil = SVGMobject(file_name='mypi').scale(1)
        # stencil = Randolph()
        # path = Drawing(stencil, uniform = True)

        # self.play(
        #     PencilDown(self.pencil),
        # )



        # self.play(
        #     PencilUp(self.pencil),
        # )

        self.segment_button = SegmentButton().move_to(3*DOWN + 4.2*LEFT)
        self.frame.add(self.segment_button)

        path1 = ArcBetweenPoints(3*UP, RIGHT + 2*UP, angle = -TAU/8)
        self.move_along_path(path1, 'draw', run_time = 1, rate_func = slow_into)


    def move_along_path(self, path, mode, run_time = 1, rate_func = linear):

        self.play(
            MovePencilTo(path.get_start(), run_time = 0.3)
        )

        if mode == 'draw':
            stroke = Stroke(path)
            self.play(
                DrawStroke(self.pencil, stroke, canvas = self.frame,
                run_time = run_time, rate_func = rate_func)
            )
        elif mode == 'segment':
            if not hasattr(self, 'segment_start'):
                self.segment_start = pencil.tip
                self.segment_end = pencil.tip
            self.play(
                
            )






