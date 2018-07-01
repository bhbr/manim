from big_ol_pile_of_manim_imports import *


class MinkowskiDiagram(VMobject):

    CONFIG = {
        "radius" : 2.0,
        "stroke_width" : 10,
        "axis_color": GREEN_E,
        "light_cone_color": RED_E,
        "light_cone_stroke_width": 2,
        "should_show_axes": False,
        "should_show_frame": True,
        "should_show_light_cone": True,
    }

    def generate_points(self):

        self.submobjects = []

        self.x_axis = Line(self.radius * LEFT, self.radius * RIGHT,
            color = self.axis_color,
            stroke_width = self.stroke_width)
        self.t_axis = Line(self.radius * DOWN, self.radius * UP,
            color = self.axis_color,
            stroke_width = self.stroke_width)

        self.frame = Square(side_length = 2 * self.radius,
            color = self.axis_color,
            stroke_width = self.stroke_width)

        self.light_cone = VGroup(
            DashedLine(self.radius * (DOWN + LEFT), self.radius * (UP + RIGHT),
                color = self.light_cone_color,
                stroke_width = self.light_cone_stroke_width),
            DashedLine(self.radius * (DOWN + RIGHT), self.radius * (UP + LEFT),
                color = self.light_cone_color,
                stroke_width = self.light_cone_stroke_width)
        )

        if self.should_show_axes:
            self.add(self.x_axis, self.t_axis)
        if self.should_show_frame:
            self.add(self.frame)
        if self.should_show_light_cone:
            self.add(self.light_cone)

    def show_axes(self):
        self.add(self.t_axis)
        self.add(self.x_axis)
        self.should_show_axes = True

    def hide_axes(self):
        self.remove(self.t_axis, x_axis)
        self.should_show_axes = False

    def show_frame(self):
        self.add(self.frame)
        self.should_show_frame = True

    def hide_frame(self):
        self.remove(self.frame)
        self.should_show_frame = False

    def show_light_cone(self):
        self.add(self.light_cone)
        self.should_show_light_cone = True

    def hide_light_cone(self):
        self.remove(self.light_cone)
        self.should_show_light_cone = False


class TransformedMinkowskiDiagram(MinkowskiDiagram):
    CONFIG = {
        "beta": 0.0,
        "scale_factor" : 1.0
    }

    def gamma(self):
        return (1 - self.beta**2)**(-0.5)
    
    def boost(self):
        return (lambda r: [self.gamma() * (r[0] - self.beta * r[1]),
                            self.gamma() * (r[1] - self.beta * r[0]),
                            0])

    def generate_points(self):

        super(TransformedMinkowskiDiagram,self).generate_points()
        self.hide_light_cone()
        self.show_frame()
        self.apply_function(self.boost())
        self.scale(self.scale_factor)




class DoubleMinkowskiDiagram(VMobject):

    CONFIG = {
        "radius": 2.0,
        "stroke_width" : 7,
        "transformed_stroke_width" : 2,
        "left_color": GREEN_E,
        "right_color": DARK_BLUE,
        "light_cone_color": RED_E,
        "beta": 0.25,
        "scale_factor": 0.7
    }

    def gamma(self):
        return (1 - self.beta**2)**(-0.5)
    
    def boost(self):
        return (lambda r: [self.gamma() * (r[0] - self.beta * r[1]),
                            self.gamma() * (r[1] - self.beta * r[0]),
                            0])
    def antiboost(self):
        return (lambda r: [self.gamma() * (r[0] + self.beta * r[1]),
                            self.gamma() * (r[1] + self.beta * r[0]),
                            0])



    def generate_points(self):

        self.left_diagram = MinkowskiDiagram(
            radius = self.radius,
            stroke_width = self.stroke_width,
            axis_color = self.left_color,
            light_cone_color = self.light_cone_color
        )

        self.right_diagram = MinkowskiDiagram(
            radius = self.radius,
            stroke_width = self.stroke_width,
            axis_color = self.right_color,
            light_cone_color = self.light_cone_color
        )

        self.left_diagram.next_to(ORIGIN, direction = LEFT, buff = 1)
        self.right_diagram.next_to(ORIGIN, direction = RIGHT, buff = 1)

        self.transformed_left_diagram = self.left_diagram.copy()
        self.transformed_left_diagram.__class__ = TransformedMinkowskiDiagram
        self.transformed_left_diagram.beta = self.beta
        self.transformed_left_diagram.scale_factor = self.scale_factor
        self.transformed_left_diagram.should_show_axes = False
        self.transformed_left_diagram.should_show_frame = True
        self.transformed_left_diagram.should_show_light_cone = False
        self.transformed_left_diagram.stroke_width = self.transformed_stroke_width
        self.transformed_left_diagram.generate_points()
        self.transformed_left_diagram.move_to(self.right_diagram)

        self.transformed_right_diagram = self.right_diagram.copy()
        self.transformed_right_diagram.__class__ = TransformedMinkowskiDiagram
        self.transformed_right_diagram.beta = -self.beta
        self.transformed_right_diagram.scale_factor = self.scale_factor
        self.transformed_right_diagram.should_show_axes = False
        self.transformed_right_diagram.should_show_frame = True
        self.transformed_right_diagram.should_show_light_cone = False
        self.transformed_right_diagram.stroke_width = self.transformed_stroke_width
        self.transformed_right_diagram.generate_points()
        self.transformed_right_diagram.move_to(self.left_diagram)
        
        
        self.add(self.left_diagram, self.right_diagram,
            self.transformed_left_diagram, self.transformed_right_diagram)


class Clockface(VMobject):
    CONFIG = {
        "radius": 0.7,
        "hour_tick_rel_length": 0.3,
        "minute_tick_rel_length": 0.1,
        "hour_tick_rel_width": 0.05,
        "minute_tick_rel_width": 0.025,
        "color": YELLOW
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        hour_tick = Rectangle(
            height = self.hour_tick_rel_width * self.radius,
            width = self.hour_tick_rel_length * self.radius,
            fill_color = self.color,
            stroke_color = self.color,
            fill_opacity = 1.0,
        )
        hour_tick.move_to(self.radius * RIGHT + 0.5 * self.hour_tick_rel_length * LEFT)

        for i in range(12):
            new_tick = hour_tick.copy().rotate_about_origin(float(i)/12 * TAU)
            self.add(new_tick)

        # minute_tick = Rectangle(
        #     height = self.minute_tick_rel_width * self.radius,
        #     width = self.minute_tick_rel_length * self.radius,
        #     fill_color = self.color,
        #     stroke_color = self.color,
        #     fill_opacity = 1.0,
        # )
        # minute_tick.move_to(self.radius * RIGHT + 0.5 * self.minute_tick_rel_length * LEFT)

        # for i in range(60):
        #     if i % 5 == 0:
        #         continue
        #     new_tick = minute_tick.copy().rotate_about_origin(float(i)/60 * TAU)
        #     self.add(new_tick)









class Clock(Mobject):
    CONFIG = {
        "prop": 0.5
    }

class CircularClock(VGroup):
    CONFIG = {
        "radius": 0.8,
        "prop": 0,
        "color": YELLOW,
    }

    def __init__(self, **kwargs):

        digest_config(self, kwargs)
        self.angle = TAU * self.prop
        self.clockface = Clockface()
        self.clockface.set_fill(color = self.color)
        self.time_sector = Sector(
            outer_radius = 0.9 * self.radius,
            angle = self.clock_angle(),
            fill_opacity = 1,
            fill_color = self.color,
            stroke_width = 0
        ).rotate(TAU/4).flip(UP)
        self.time_sector.move_arc_center_to(self.clockface.get_center())

        VGroup.__init__(self, **kwargs)
        self.add(self.clockface, self.time_sector)

    def generate_points(self):
        new_angle = self.clock_angle()
        if len(self.submobjects) == 2:
            self.remove(self.time_sector)
        self.time_sector = Sector(
            outer_radius = 0.9 * self.radius,
            angle = new_angle,
            fill_opacity = 0.5,
            fill_color = self.color,
            stroke_width = 0
        ).rotate(TAU/4).flip(UP)
        self.add(self.time_sector)
        self.time_sector.move_arc_center_to(self.clockface.get_center())

    def clock_angle(self):
        return self.prop * TAU


class LinearClock(Mobject):
    CONFIG = {
        "thickness": 0.1,
        "length": 1.0,
        "prop": 0,
        "color": YELLOW,
        "background_bar_opacity": 0.1,
    }

    def generate_points(self):

        self.center = self.get_center()
        self.filled_length = self.length * self.prop

        self.submobjects = []
        self.background_bar = Rectangle(
            width = self.length,
            height = self.thickness,
            color = self.color,
            fill_opacity = self.background_bar_opacity,
            stroke_width = 0
        )

        self.time_bar = Rectangle(
            width = self.filled_length,
            height = self.thickness,
            color = self.color,
            fill_opacity = 1,
            stroke_width = 0
        ).align_to(self.background_bar, LEFT)



        self.add(self.background_bar, self.time_bar)
        self.move_to(self.center)


class PropagateClock(Animation):

    CONFIG = {
        "start_prop": 0,
        "added_prop": 0.1,
        "rate_func": linear
    }

    def __init__(self, mobject, added_prop, **kwargs):
        self.start_prop = mobject.prop
        self.added_prop = added_prop
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        new_prop = self.start_prop + alpha * self.added_prop
        while new_prop >= 1:
            new_prop -= 1
        self.mobject.prop = new_prop
        self.mobject.generate_points()





class ForceArrow(Arrow):
    CONFIG = {
        "origin": ORIGIN,
        "length": 1.0,
        "direction": UP,
        "buff": 0,
        "stroke_width": 5
    }

    def force_tip(self):
        return self.origin + self.length * self.direction

    def __init__(self, origin, direction, length, **kwargs):
        self.origin = origin
        self.direction = direction
        self.length = length
        Arrow.__init__(self, self.origin, self.force_tip(), **kwargs)
        self.stroke_color = self.color
        self.fill_color = self.color
        self.add_tip()

        


class AnimateForceArrow(Animation):
    CONFIG = {
        "length_function": lambda x : x,
        "rate_func": linear
    }

    def update_mobject(self, alpha):
        self.mobject.length = self.length_function(alpha)
        new_arrow = ForceArrow(
            self.mobject.origin,
            self.mobject.direction,
            self.mobject.length,
            color = RED
        )
        self.mobject.points = new_arrow.points
        self.mobject.submobjects = new_arrow.submobjects
        self.mobject.stroke_width = 5
        self.mobject.stroke_color = RED
        self.mobject.fill_color = RED







class WindowedGraph(VGroup):
    CONFIG = {
        "function": lambda x: x**2,
        "x_scale" : 1.0,
        "y_scale" : 1.0,
        "height" : 2.0,
        "t_min": 0.0,
        "t_max": 1.0,
        "color": RED,
        "alpha": 0.5,
        "subdivs": 30,
        "show_labels": False
    }

    def get_width(self):
        return (self.t_max - self.t_min) * self.x_scale

    def __init__(self, function, **kwargs):

        digest_config(self, kwargs)
        self.function = function
        self.rect = Rectangle(width = self.get_width(), height = self.height)
        self.graph = VMobject(stroke_color = self.color, stroke_width = 10)
        self.time_line = self.get_time_line()
        if self.show_labels:
            self.time_text = TextMobject("Zeit", color = YELLOW)
            self.time_text.next_to(self.rect, DOWN)
            self.force_text = TextMobject("Kraft", color = self.color)
            self.force_text.next_to(self.rect, UP)
            self.force_text.shift(0.7 * DOWN)

        VGroup.__init__(self, **kwargs)
        
        self.add(self.rect, self.graph, self.time_line)
        if self.show_labels:
            self.add(self.time_text, self.force_text)

    def get_time_line(self):
        ll_corner = self.rect.get_critical_point(DOWN + LEFT)
        lr_corner = self.rect.get_critical_point(DOWN + RIGHT)
        time_line_coord = (1 - self.alpha) * self.t_min + self.alpha * self.t_max
        time_line_point = self.get_point_from_t(time_line_coord)
        time_line_point[1] = ll_corner[1]
        return Line(ll_corner, time_line_point, color = YELLOW, stroke_width = 10)


    def get_point_from_t(self, t):
        x = self.x_scale * (t - self.t_min)
        y = self.y_scale * self.function(t)
        ll_corner = self.rect.get_critical_point(DOWN + LEFT)
        return ll_corner + x * RIGHT + y * UP

    def generate_points(self):
        t_end = (1 - self.alpha) * self.t_min + self.alpha * self.t_max
        n_points = 3 * self.subdivs - 2
        dt = (self.t_max - self.t_min)/n_points
        points = [self.get_point_from_t(t) for t in np.arange(self.t_min, t_end, dt)]
        self.graph.set_points_as_corners(points)
        self.time_line.set_points_as_corners(self.get_time_line().points)

           





class DrawWindowedGraph(Animation):
    
    def __init__(self, graph, **kwargs):
        mobject = graph
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        self.mobject.alpha = alpha
        self.mobject.generate_points()







