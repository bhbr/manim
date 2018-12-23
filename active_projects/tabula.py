from big_ol_pile_of_manim_imports import *

PENCIL_WIDTH = 0.03
DROP_DENSITY = 200

class Pencil(ImageMobject):
    CONFIG = {
        'tip': ORIGIN,
        'pointing_angle': 1/8 * TAU, # from the top
        'tip_is_down': False,
        'mode': 'draw'
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
            #self.set_fill(opacity=0)
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


class MovePencilTo(Transform):
    def __init__(self, pencil, target_tip, **kwargs):
        pencil.target = pencil.copy()
        pencil.target.point_to(target_tip)
        MoveToTarget.__init__(self, pencil, **kwargs)




class DrawStroke(Animation):
    CONFIG = {
        'color': BLACK,
        'canvas': None
    }

    def __init__(self, pencil, stroke, **kwargs):
        if stroke.get_length() == 0:
            EmptyAnimation.__init__(self, **kwargs)
            return
        Animation.__init__(self, pencil, **kwargs)
        self.pencil = pencil
        self.stroke = stroke
        self.drops = self.stroke.submobjects

        self.stroke.set_fill(opacity=1)
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
        'canvas': None
    }

    def __init__(self, pencil, drawing, **kwargs):
        anims = []
        for stroke in drawing.get_strokes():
            anims.append(DrawStroke(pencil, stroke, **kwargs))
        Succession.__init__(self, *anims, **kwargs)





class DragPencil(DrawStroke):

    def __init__(self, pencil, stroke, modes = {}, **kwargs):

        def mode_function(alpha):
            if modes == {}:
                return 'draw'
            time_stamps = sorted(modes.keys())
            if alpha < time_stamps[0]:
                return 'draw'
            time_stamps = list(filter(lambda x: x <= alpha, time_stamps))
            return modes[time_stamps[-1]]

        DrawStroke.__init__(self, pencil, stroke, mode_function=mode_function, **kwargs)

        if 'segment' in modes.values():
            self.startDot = Dot().move_to(pencil.tip)
            self.endDot = self.startDot.copy()
            self.segment = Line(pencil.tip, pencil.tip)
            self.canvas.add(self.startDot, self.endDot, self.segment)


    def update_mobject(self, alpha):
        current_mode = self.mode_function(alpha)
        if current_mode == 'draw':
            super(DrawStroke, self).update_mobject(alpha)
        elif current_mode == 'segment':
            for drop in self.drops:
                drop.set_fill(opacity = 0)
            self.endDot.move_to(self.pencil.tip)
            self.segment.end = self.pencil.tip





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
        strokes_to_draw = [stroke for stroke in drawing.get_strokes()
            if stroke.get_length() > 0 and len(stroke.stencil.submobjects) == 0]
        lengths = [stroke.get_length() for stroke in strokes_to_draw]
        total_length = drawing.get_length()
        total_run_time = run_time + PENCIL_MOVE_TIME*len(lengths)
        run_times = [length/total_length*total_run_time for length in lengths]

        for (stroke, run_time) in zip(strokes_to_draw, run_times):
            self.play(
                MovePencilTo(self.pencil, stroke.stencil.point_from_proportion(0),
                run_time = PENCIL_MOVE_TIME
                )
            )
            self.play(
                DrawStroke(self.pencil, stroke,
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
        
        #stencil = Circle()
        #stencil = Annulus(inner_radius = 1, outer_radius = 2)
        #stencil = SVGMobject(file_name='mypi').scale(1)
        stencil = Randolph()

        path = Drawing(stencil, uniform = False)
        lengths = [stroke.get_length() for stroke in path.get_strokes()]
        print(lengths, path.get_length())
        self.play(
            Draw(self.pencil, path, canvas=self.frame) #, modes={0.5: 'segment'})
        )


        # button1 = SegmentButton().move_to(4.2*LEFT + 3*DOWN)
        # self.add(button1)

        # touch = Touch()

        #self.play(TouchDown(touch, run_time = 0.1))


