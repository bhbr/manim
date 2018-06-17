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
















