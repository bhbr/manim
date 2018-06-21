from big_ol_pile_of_manim_imports import *
from active_projects.lorentz import *

class Train(Rectangle):

    CONFIG = {
        "width": 0.3,
        "height": 2,
        "observer_location": 0.7, # btw 0 and 1
        "observer_color": RED,
        "fill_color": BLUE_C,
        "fill_opacity": 1,
        "stroke_width": 0
    }

    @property
    def length(self):
        return self.height

    @length.setter
    def length(self, new_length):
        self.height = new_length


    def get_length(self):
        return self.height

    def set_length(self, new_length):
        self.height = new_length

    def generate_points(self):
        super(Train,self).generate_points()
        self.observer = Dot(color = self.observer_color)
        self.add(self.observer)


class TrainCrossScene(Scene):

    CONFIG = {
        "beta" : 0.6,
        "run_angle" : TAU/2
    }

    def construct(self):


        origin_left = 2 * UP
        origin_right = 2 * DOWN
        beta = self.beta
        beta2 = 2 * beta / (1 + beta **2)
        gamma = (1 - beta**2)**(-0.5) # both trains relative to CM
        gamma2 = (1 - (beta2)**2)**(-0.5) # right train relative to left

        train_proper_length = 2
        train_cm_length = train_proper_length / gamma
        train_shortest_length = train_proper_length / gamma2 # one train's length relative to the other
        frame_width_factor = 1 # ratio frame width : train length
        frame_height = 1.5

        train_pass_proper_time = 3
        train_pass_cm_time = train_pass_proper_time * gamma

        measured_proper_time = TAU/2
        measured_cm_time = measured_proper_time * gamma
        measured_shortest_time = measured_proper_time/gamma



        train1_left = Train(
            height = train_cm_length,
            observer_location = 0.5,
            ).rotate(TAU/4).next_to(origin_left, DOWN)
        train2_left = Train(
            height = train_cm_length,
            observer_location = 0.5
            ).rotate(TAU/4).next_to(origin_left, UP)
        train1_left.shift(0.5 * train_cm_length * LEFT)
        train2_left.shift(0.5 * train_cm_length * RIGHT)

        train1_left_frame = Rectangle(
            stroke_color = GREEN_C,
            stroke_width = 2,
            width = frame_width_factor * train1_left.height,
            height = frame_height,
        )
        train1_left_frame.move_to(train1_left).shift(0.4 * UP)



        train1_right = Train(
            height = train_proper_length,
            observer_location = 0.5,
            ).rotate(TAU/4).next_to(origin_right, DOWN)
        train2_right = Train(
            height = train_shortest_length,
            observer_location = 0.5
            ).rotate(TAU/4).next_to(origin_right, UP)
        train2_right.align_to(train1_right, RIGHT)
        train2_right.shift(train_shortest_length * RIGHT)

        train1_right_frame = Rectangle(
            stroke_color = GREEN_C,
            stroke_width = 2,
            width = frame_width_factor * train1_right.height,
            height = train1_left_frame.height,
        )
        train1_right_frame.move_to(train1_right).shift(0.4 * UP)

        self.add(train1_left, train1_left_frame, train2_left,
            train1_right, train1_right_frame, train2_right)

        clock_left = Clock()
        clock1_right = Clock()
        clock2_right = Clock()
        clock_left.move_to(3.2 * UP)
        clock1_right.move_to(train1_right)
        clock2_right.move_to(train2_right)
        self.add(clock_left, clock1_right, clock2_right)



        self.play(
            ApplyMethod(
                train1_left.shift, train_cm_length * RIGHT,
                rate_func = linear, run_time = train_pass_cm_time
            ),
            ApplyMethod(
                train1_left_frame.shift, train_cm_length * RIGHT,
                rate_func = linear, run_time = train_pass_cm_time
            ),
            ApplyMethod(
                train2_left.shift, train_cm_length * LEFT,
                rate_func = linear, run_time = train_pass_cm_time
            ),
            PropagateClock(clock_left, measured_cm_time, run_time = train_pass_cm_time)
        )


        self.play(
            ApplyMethod(
                train2_right.shift, (train1_right.height + train2_right.height) * LEFT,
                rate_func = linear, run_time = train_pass_proper_time
            ),
            PropagateClock(clock1_right, measured_proper_time, run_time = train_pass_proper_time),
            MaintainPositionRelativeTo(clock1_right, train1_right, run_time = train_pass_proper_time),
            PropagateClock(clock2_right, measured_shortest_time, run_time = train_pass_proper_time),
            MaintainPositionRelativeTo(clock2_right, train2_right, run_time = train_pass_proper_time)
        )



















