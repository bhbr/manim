from big_ol_pile_of_manim_imports import *
from active_projects.lorentz import *

class LorentzTransformScene(Scene):

    CONFIG = {
        "beta" : 0.55
    }

    def construct(self):

        double_diagram = DoubleMinkowskiDiagram(beta = self.beta)
        self.add(double_diagram)
        self.wait()

        particle_radius = 0.2
        particle1_color = double_diagram.right_color
        particle2_color = YELLOW

        left_diagram = double_diagram.left_diagram
        right_diagram = double_diagram.right_diagram

        cm_beta = self.beta
        transformed_beta = 2 * self.beta / (1 + self.beta**2)

        left_particle1 = Dot(radius = particle_radius, fill_color = particle1_color).move_to(
            left_diagram.get_bottom() + cm_beta * left_diagram.radius * LEFT
        )
        left_particle2 = Dot(radius = particle_radius, fill_color = particle2_color).move_to(
            left_diagram.get_bottom() + cm_beta * left_diagram.radius * RIGHT
        )
        right_particle1 = Dot(radius = particle_radius, fill_color = particle1_color).move_to(
            right_diagram.get_bottom()
        )
        right_particle2 = Dot(radius = particle_radius, fill_color = particle2_color).move_to(
            right_diagram.get_bottom() +transformed_beta * right_diagram.radius * RIGHT
        )
        self.add(left_particle1, left_particle2, right_particle1, right_particle2)

        self.play(
            ApplyMethod(left_particle1.move_to,left_diagram.get_center(), rate_func = linear),
            ApplyMethod(left_particle2.move_to,left_diagram.get_center(), rate_func = linear),
            ApplyMethod(right_particle1.move_to,right_diagram.get_center(), rate_func = linear),
            ApplyMethod(right_particle2.move_to,right_diagram.get_center(), rate_func = linear),
        )

        lp1_target = left_diagram.get_top() + cm_beta * left_diagram.radius * LEFT
        lp2_target = left_diagram.get_top() + cm_beta * left_diagram.radius * RIGHT
        rp1_target = right_diagram.get_top() + transformed_beta * left_diagram.radius * LEFT
        rp2_target = right_diagram.get_top()

        self.play(
            ApplyMethod(left_particle1.move_to,lp1_target, rate_func = linear),
            ApplyMethod(left_particle2.move_to,lp2_target, rate_func = linear),
            ApplyMethod(right_particle1.move_to,rp1_target, rate_func = linear),
            ApplyMethod(right_particle2.move_to,rp2_target, rate_func = linear),
        )









