from big_ol_pile_of_manim_imports import *
import random


class OverFittingScene(Scene):
    CONFIG = {
        'random_seed' : 5
    }


    def construct(self):

        red_point_center = 2 * DOWN + 2 * RIGHT
        blue_point_center = UP + 4 * LEFT

        for i in range(1):
            dots = VGroup()

            for i in range(1000):
                v = (-7 + 14 * np.random.random()) * RIGHT + (-4 + 8 * np.random.random()) * UP
                dot = Dot(v)
                v2 = v + 0.25 * np.random.normal() * RIGHT + np.random.normal() * UP
                if (v2[1] < 0.25 * v2[0]**2 - 2):
                    dot.set_fill(RED_E)
                else:
                    dot.set_fill(BLUE_E)




                dots.add(dot)




            self.play(ShowCreation(dots, run_time = 20, rate_func = lambda x: x))

