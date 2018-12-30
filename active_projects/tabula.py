from big_ol_pile_of_manim_imports import *

PENCIL_WIDTH = 0.03
DROP_DENSITY = 200
IPAD_WIDTH = 9.2
IPAD_HEIGHT = 6.9

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
        self.path = VMobject()

    def point_to(self, target):
        center_offset = self.get_width()/2 * RIGHT + self.get_height()/2 * DOWN
        self.move_to(target + center_offset)
        self.tip = target
        return self

    def pen_down(self):
        if self.tip_is_up:
            self.tip_is_down = True
            self.clear_path()

    def pen_up(self):
        if self.tip_is_down:
            self.tip_is_down = False
            self.clear_path()

    def add_path(self, new_path):
        if len(self.path.points) == 0:
            self.path.points = new_path.points
        else:
            self.path.add_control_points(new_path.points[1:])

    def drawn_stroke(self):
        return Stroke(self.path)

    def clear_path(self):
        self.path.points = []

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

        #self.stroke.set_fill(opacity=1)
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

    def clean_up(self, surrounding_scene = None):
        self.pencil.add_path(self.stroke.stencil)




class MovePencilAlongPath(Animation):

    def __init__(self, pencil, path, **kwargs):
        if path.get_length() == 0:
            EmptyAnimation.__init__(self, **kwargs)
            return
        Animation.__init__(self, pencil, **kwargs)
        self.pencil = pencil
        self.path = path

    def update_mobject(self, alpha):
        if alpha == 0 or alpha > 1:
            return
        tip_point = self.path.point_from_proportion(alpha)
        self.pencil.point_to(tip_point)


    def clean_up(self, surrounding_scene=None):
        self.pencil.add_path(self.path)




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
        for (stroke, draw_run_time, move_run_time) \
            in zip(drawing.get_strokes(), draw_run_times, move_run_times):
            anims.append(ScheduledAnimation(MovePencilTo, pencil, stroke.get_start(),
                run_time = move_run_time, **kwargs_here))
            anims.append(ScheduledAnimation(DrawStroke, pencil, stroke,
                run_time = draw_run_time, **kwargs_here))

        Succession.__init__(self, *anims, **kwargs_here)







class Button(Circle):
    CONFIG = {
        'fill_color': BLUE_C,
        'fill_opacity': 1,
        'stroke_opacity': 0,
        'radius': 0.3,
        '_logo_file': None
    }

    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        if 'logo_file' in kwargs:
            self.logo_file = kwargs['logo_file']
        else:
            self.logo_file = self.logo_file
        self.add(self.logo)

    @property
    def logo_file(self):
        return self._logo_file
    
    @logo_file.setter
    def logo_file(self, new_file):
        self._logo_file = new_file
        if new_file == None:
            self.logo = Mobject()
        else:
            self.logo = ImageMobject(new_file)
            scale_factor = 0.7*2*self.radius / self.logo.get_width()
            self.logo.scale_in_place(scale_factor)
        self.logo.move_to(self)


class SegmentButton(Button):
    CONFIG = {
        '_logo_file': 'segment'
    }

class RayButton(Button):
    CONFIG = {
        '_logo_file': 'ray'
    }

class Touch(VGroup):
    CONFIG = {
        'radius': 0.5,
        'nb_rings': 30,
        'color': ORANGE,
        'max_opacity': 0.75
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
        'run_time': 0.2
    }
    def update_mobject(self, alpha):
        nb_rings = len(self.mobject.submobjects)
        total_radius = self.mobject.submobjects[-1].outer_radius
        for (i,ring) in enumerate(self.mobject.submobjects):
            opacity = 0
            if i < alpha*nb_rings:
                opacity = (1 - (alpha*nb_rings - i)/nb_rings) * self.mobject.max_opacity
            ring.set_fill(opacity=opacity)

class TouchUp(TouchDown):
    CONFIG = {
        'run_time': 0.2
    }
    def update_mobject(self, alpha):
        nb_rings = len(self.mobject.submobjects)
        total_radius = self.mobject.submobjects[-1].outer_radius
        for (i,ring) in enumerate(self.mobject.submobjects):
            opacity = 0
            if i < (1-alpha)*nb_rings:
                opacity = (1 - ((1-alpha)*nb_rings - i)/nb_rings) * self.mobject.max_opacity
            ring.set_fill(opacity=opacity)


class ConstructedLine(VGroup):
    CONFIG = {
        '_mode': 'segment'
    }

    def __init__(self, start, end, **kwargs):

        VGroup.__init__(self, **kwargs)
        self.start, self.end = start, end
        self.start_point = Dot(start, fill_color = BLACK)
        self.end_point = Dot(end, fill_color = BLACK)
        self.line = Line(start, end, stroke_color = BLACK)
        self.add(self.start_point, self.end_point, self.line)

        front_t, back_t = self.get_front_and_back_t()
        self.outer_line_front = Line(end, end + front_t*self.direction)
        self.outer_line_back = Line(end, end + back_t*self.direction)

        if 'mode' in kwargs:
            self.mode = kwargs['mode']


    @property
    def mode(self):
        return self._mode
    
    @property
    def direction(self):
        return self.end - self.start
    
    @mode.setter
    def mode(self,new_mode):
        if new_mode == 'segment':
            self.remove(self.outer_line_front, self.outer_line_back)
        elif new_mode == 'ray':
            self.add(self.outer_line_front)
            self.remove(self.outer_line_back)
        elif new_mode == 'line':
            self.add(self.outer_line_front, self.outer_line_back)
        self._mode = new_mode

    def get_front_and_back_t(self):

        direction = self.end - self.start

        # find the t-values in P = end + t*direction that cross the frame
        t1 = (IPAD_WIDTH - self.end[0])/self.direction[0]
        t2 = (-IPAD_WIDTH - self.end[0])/self.direction[0]
        t3 = (IPAD_HEIGHT - self.end[1])/self.direction[1]
        t4 = (-IPAD_HEIGHT - self.end[1])/self.direction[1]
        #print(t1,t2,t3,t4)

        front_t = min([t for t in [t1,t2,t3,t4] if t > 0])
        back_t = max([t for t in [t1,t2,t3,t4] if t < 0])
        #print(front_t, back_t)

        return front_t, back_t

    def get_outer_point_front(self):
        front_t, back_t = self.get_front_and_back_t()
        return self.end + front_t*self.direction

    def get_outer_point_back(self):
        front_t, back_t = self.get_front_and_back_t()
        return self.end + back_t*self.direction


class AnimateConstructedLine(Animation):

    def __init__(self, mobject, path, **kwargs):
        self.path = path
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        new_end_point = self.path.point_from_proportion(alpha)
        self.mobject.end_point.move_to(new_end_point)
        self.mobject.end = new_end_point
        self.mobject.line.set_start_and_end(self.mobject.line.get_start(), new_end_point)
        self.mobject.outer_line_front.set_start_and_end(
            self.mobject.end, self.mobject.get_outer_point_front()
        )
        self.mobject.outer_line_back.set_start_and_end(
            self.mobject.end, self.mobject.get_outer_point_back()
        )
        self.mobject.line.generate_points()
        self.mobject.outer_line_front.generate_points()
        self.mobject.outer_line_back.generate_points()





class PencilScene(Scene):
    CONFIG = {
        'camera_config' : { "background_color": WHITE }
    }

    def construct(self):
        self.frame = ImageMobject(filename_or_array='ipad_frame').scale(4)
        self.pencil = Pencil(pointing_angle = 0)

        background = Rectangle(width=FRAME_WIDTH, height=FRAME_HEIGHT,
            fill_color = WHITE, fill_opacity = 1, stroke_opacity=0)
        background.move_to(ORIGIN)
        cutout = Rectangle(width=IPAD_WIDTH, height=IPAD_HEIGHT).flip()
        background.add_subpath(cutout.points)

        self.add_foreground_mobject(background)
        self.add_foreground_mobject(self.frame)
        self.add_foreground_mobject(self.pencil)
        self.pencil.point_to(2*UP + 3*LEFT)
        


        button1 = SegmentButton().move_to(4.2*LEFT + 3*DOWN)
        self.add(button1)

        path0 = ArcBetweenPoints(self.pencil.tip, self.pencil.tip + 0.2*DOWN + 0.1*LEFT)
        constructed_line = ConstructedLine(self.pencil.tip, self.pencil.tip + 0.2*DOWN + 0.1*LEFT,
            mode = 'segment')
        stroke0 = Stroke(path0)

        self.play(
            DrawStroke(self.pencil, stroke0, canvas = self.frame,
                run_time = 0.1)
        )

        touch = Touch().move_to(button1)

        self.play(TouchDown(touch))
        self.frame.remove(stroke0)
        path1 = ArcBetweenPoints(self.pencil.tip, ORIGIN, angle=TAU/4)

        self.play(
            AnimateConstructedLine(constructed_line, path1),
            MovePencilAlongPath(self.pencil, path1)
        )
        self.remove(constructed_line)
        stroke = self.pencil.drawn_stroke()
        self.add(stroke)

        self.play(TouchUp(touch))
        self.wait()

        path2 = ArcBetweenPoints(ORIGIN, 3*DOWN+LEFT, angle=-TAU/4)

        self.remove(stroke)
        self.add(constructed_line)

        self.play(TouchDown(touch))
        self.play(
            touch.shift, 0.3*UP,
            button1.shift, 0.3*UP
        )
        self.remove(button1)
        button1 = RayButton().move_to(button1.get_center())
        self.add(button1)
        constructed_line.mode = 'ray'
        self.play(
            AnimateConstructedLine(constructed_line, path2),
            MovePencilAlongPath(self.pencil ,path2)
        )
        self.play(TouchUp(touch))
        self.remove(constructed_line)
        stroke2 = self.pencil.drawn_stroke()
        self.add(stroke2)

        self.wait()


        self.play(TouchDown(touch))
        self.remove(stroke2)
        self.add(constructed_line)

        self.wait()
        self.play(
            MovePencilTo(self.pencil, ORIGIN),
            TouchUp(touch)
        )
        self.add_foreground_mobject(self.pencil)

class TestScene(Scene):

    def construct(self):

        c = Circle(stroke_color=BLUE)
        self.add(c)
        anim1 = ScheduledAnimation(ApplyMethod, c.move_to, UP)
        anim2 = ScheduledAnimation(ApplyMethod, c.move_to, RIGHT)
        self.play(
            Succession(anim1, anim2)
        )









