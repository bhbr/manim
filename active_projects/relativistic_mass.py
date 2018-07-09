from big_ol_pile_of_manim_imports import *
from active_projects.lorentz import *
import math

TIME_SCALE = 0.5
TIME_CLOCK_SCALE = 0.166666
FORCE_SCALE = 1.0
TRAIN_ONE_COLOR = RED_E
TRAIN_TWO_COLOR = BLUE_E
FORCE_COLOR = GREEN
FORCE_FUNCTION = lambda t: 0.5 * np.exp(-t**2 * 1)/np.exp(-0.25)


class Train(VGroup):

    CONFIG = {
        "file_name": "train",
        "train_height": 0.75,
        "observer_location": 0.6, # btw 0 and 1
        "observer_color": FORCE_COLOR,
        "fill_color": YELLOW,
        "fill_opacity": 1,
        "stroke_width": 0
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.train = SVGMobject(file_name=self.file_name, **kwargs)
        self.train.set_fill(color = self.fill_color)
        scale_factor = self.train_height / self.train.get_height()
        self.train.scale(scale_factor)
        self.observer = Dot(color = self.observer_color)
        self.add(self.train)
        self.add(self.observer)


    def squeeze(self, factor):
        self.train.stretch(factor, 0)



class TrainScene(Scene):

    CONFIG = {
        "beta" : 0.6,
    }

    def construct(self):


        self.beta2 = 2 * self.beta / (1 + self.beta ** 2)
        self.gamma = (1 - self.beta**2)**(-0.5) # both trains relative to CM
        self.gamma2 = (1 - (self.beta2)**2)**(-0.5) # right train relative to left

        self.train_proper_length = 6
        self.train_pass_cm_time = 5.0


        self.frame_width_factor = 1 # ratio frame width : train length
        self.frame_height = 1.5

        self.measured_cm_time = self.train_pass_cm_time
        self.measured_proper_time = self.measured_cm_time / self.gamma
        self.measured_shortened_time = self.measured_cm_time / self.gamma2



class FromCMScene(TrainScene):


    def construct(self):

        super(FromCMScene, self).construct()

        self.train_cm_length = self.train_proper_length / self.gamma
        vertical_distance = 3
        horizontal_offset = self.train_cm_length
        cm_origin = 1.2*LEFT

        train1_start = cm_origin + 0.5 * vertical_distance * DOWN + 0.5 * horizontal_offset * RIGHT
        train2_start = cm_origin + 0.5 * vertical_distance * UP + 0.5 * horizontal_offset * LEFT

        train1 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            fill_color = TRAIN_ONE_COLOR
            )
        train1.squeeze(self.train_cm_length/train1.get_width())
        train1.move_to(train1_start)
        self.add(train1)

        train2 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            fill_color = TRAIN_TWO_COLOR
            )
        train2.squeeze(self.train_cm_length/train2.get_width())
        train2.flip().move_to(train2_start)
        self.add(train2)


        force_function_cm = FORCE_FUNCTION
        scaled_shifted_ff_cm = lambda t: force_function_cm((t - 0.5) * self.train_pass_cm_time)
        t_min = -0.5 * self.train_pass_cm_time
        t_max = -t_min

        force1 = ForceArrow(
            train1.get_center(),
            UP,
            force_function_cm(t_min),
            color = FORCE_COLOR)
        force2 = ForceArrow(
            train2.get_center(),
            DOWN,
            force_function_cm(t_min),
            color = FORCE_COLOR)

        self.add(force1, force2)


        clock = CircularClock()
        clock.to_corner(UL)
        self.add(clock)
        
        graph1 = WindowedGraph(
            function = force_function_cm,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min,
            t_max = t_max,
            color = FORCE_COLOR,
            alpha = 0.0,
            show_labels = False
        )
        
        graph2 = WindowedGraph(
            function = force_function_cm,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min,
            t_max = t_max,
            color = FORCE_COLOR,
            alpha = 0.0,
            show_labels = True
        )

        graph1.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * DOWN)
        graph2.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * UP)

        self.add(graph1, graph2)


        self.play(
            ApplyMethod(
                train1.shift, horizontal_offset * LEFT,
                rate_func = linear, run_time = self.train_pass_cm_time
            ),
            ApplyMethod(
                train2.shift, horizontal_offset * RIGHT,
                rate_func = linear, run_time = self.train_pass_cm_time
            ),
            PropagateClock(clock, TIME_CLOCK_SCALE * self.measured_cm_time, run_time = self.train_pass_cm_time),
            AnimateForceArrow(force1, length_function = scaled_shifted_ff_cm, run_time = self.train_pass_cm_time),
            AnimateForceArrow(force2, length_function = scaled_shifted_ff_cm, run_time = self.train_pass_cm_time),
            MaintainPositionRelativeTo(force1, train1, run_time = self.train_pass_cm_time,
                tracked_critical_point = DOWN),
            MaintainPositionRelativeTo(force2, train2, run_time = self.train_pass_cm_time,
                tracked_critical_point = UP),
            DrawWindowedGraph(graph1, run_time = self.train_pass_cm_time),
            DrawWindowedGraph(graph2, run_time = self.train_pass_cm_time),
        )






class FromLeftScene(TrainScene):



    def construct(self):

        super(FromLeftScene, self).construct()

        self.train_cm_length = self.train_proper_length / self.gamma
        vertical_distance = 3
        self.train_shortened_length = self.train_proper_length / self.gamma2 # one train's length relative to the other
        horizontal_offset = 0.5 * (self.train_proper_length + self.train_shortened_length)
        cm_origin = 1.2 * LEFT

        train1_start = cm_origin + 0.5 * vertical_distance * DOWN
        train1 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            fill_color = TRAIN_ONE_COLOR
            )
        train1.squeeze(self.train_proper_length/train1.get_width())
        train1.move_to(train1_start)
        self.add(train1)


        train2 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            fill_color = TRAIN_TWO_COLOR
            )
        train2.flip().squeeze(self.train_shortened_length/train2.get_width())

        train2_start = cm_origin + 0.5 * vertical_distance * UP
        train2_start += 0.5 * (train1.get_width() + train2.get_width()) * LEFT

        train2.move_to(train2_start)
        self.add(train2)

        self.add(train1, train2)

        
        clock1 = CircularClock()
        clock2 = CircularClock()
        
        clock1.move_to(train1).shift(DOWN)
        clock2.move_to(train2).shift(UP)
        self.add(clock1, clock2)

        force_function_cm = FORCE_FUNCTION
        force_function_1 = lambda t: force_function_cm(t*self.gamma) * self.gamma
        force_function_2 = lambda t: force_function_cm(t*self.gamma2) * self.gamma2

        scaled_shifted_ff_cm = lambda t: force_function_cm((t - 0.5) * self.train_pass_cm_time)
        scaled_shifted_ff_1 = lambda t: force_function_1((t - 0.5) * self.measured_proper_time)
        scaled_shifted_ff_2 = lambda t: force_function_2((t - 0.5) * self.measured_shortened_time)

        t_min1 = -0.5 * self.measured_proper_time
        t_max1 = -t_min1
        t_min2 = -0.5 * self.measured_shortened_time
        t_max2 = -t_min2

        force1 = ForceArrow(
            train1.get_center(),
            UP,
            force_function_1(t_min1),
            color = FORCE_COLOR
        )
        force2 = ForceArrow(
            train2.get_center(),
            DOWN,
            force_function_2(t_min2),
            color = FORCE_COLOR
        )

        self.add(force1, force2)


        
        graph1 = WindowedGraph(
            function = force_function_1,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min1,
            t_max = t_max1,
            color = FORCE_COLOR,
            alpha = 0.0,
            show_labels = False
        )
        
        graph2 = WindowedGraph(
            function = force_function_2,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min2,
            t_max = t_max2,
            color = FORCE_COLOR,
            alpha = 0.0,
            show_labels = True
        )

        graph1.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * DOWN)
        graph2.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * UP)

        self.add(graph1, graph2)

        self.play(
            ApplyMethod(
                train2.shift, (train1.get_width() + train2.get_width()) * RIGHT,
                rate_func = linear, run_time = self.measured_proper_time
            ),
            PropagateClock(clock1, TIME_CLOCK_SCALE * self.measured_proper_time, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(clock1, train1, run_time = self.measured_proper_time),
            PropagateClock(clock2, TIME_CLOCK_SCALE * self.measured_shortened_time, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(clock2, train2, run_time = self.measured_proper_time),
            AnimateForceArrow(force1, length_function = scaled_shifted_ff_1, run_time = self.measured_proper_time),
            AnimateForceArrow(force2, length_function = scaled_shifted_ff_2, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(force1, train1, run_time = self.measured_proper_time,
                tracked_critical_point = DOWN),
            MaintainPositionRelativeTo(force2, train2, run_time = self.measured_proper_time,
                tracked_critical_point = UP),
            DrawWindowedGraph(graph1, run_time = self.measured_proper_time),
            DrawWindowedGraph(graph2, run_time = self.measured_proper_time),
        )






class FromRightScene(TrainScene):



    def construct(self):

        super(FromRightScene, self).construct()

        self.train_cm_length = self.train_proper_length / self.gamma
        vertical_distance = 3
        self.train_shortened_length = self.train_proper_length / self.gamma2 # one train's length relative to the other
        horizontal_offset = 0.5 * (self.train_proper_length + self.train_shortened_length)
        cm_origin = 5.5*LEFT

        train1_start = cm_origin + 0.5 * vertical_distance * DOWN + \
            (self.train_proper_length + self.train_shortened_length) * RIGHT
        train1 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            fill_color = TRAIN_ONE_COLOR
            )
        train1.squeeze(self.train_shortened_length/train1.get_width())
        train1.move_to(train1_start)
        self.add(train1)


        train2 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            fill_color = TRAIN_TWO_COLOR
            )
        train2.flip().squeeze(self.train_proper_length/train2.get_width())

        train2_start = cm_origin + 0.5 * vertical_distance * UP
        train2_start += 0.5 * (train1.get_width() + train2.get_width()) * RIGHT

        train2.move_to(train2_start)
        self.add(train2)

        self.add(train1, train2)

        
        clock1 = CircularClock()
        clock2 = CircularClock()
        
        clock1.move_to(train1).shift(DOWN)
        clock2.move_to(train2).shift(UP)
        self.add(clock1, clock2)

        force_function_cm = FORCE_FUNCTION
        force_function_1 = lambda t: force_function_cm(t*self.gamma2) * self.gamma2
        force_function_2 = lambda t: force_function_cm(t*self.gamma) * self.gamma

        scaled_shifted_ff_cm = lambda t: force_function_cm((t - 0.5) * self.train_pass_cm_time)
        scaled_shifted_ff_1 = lambda t: force_function_1((t - 0.5) * self.measured_shortened_time)
        scaled_shifted_ff_2 = lambda t: force_function_2((t - 0.5) * self.measured_proper_time)

        t_min1 = -0.5 * self.measured_shortened_time
        t_max1 = -t_min1
        t_min2 = -0.5 * self.measured_proper_time
        t_max2 = -t_min2

        force1 = ForceArrow(
            train1.get_center(),
            UP,
            force_function_1(t_min1),
            color = FORCE_COLOR
        )
        force2 = ForceArrow(
            train2.get_center(),
            DOWN,
            force_function_2(t_min2),
            color = FORCE_COLOR
        )

        self.add(force1, force2)


        
        graph1 = WindowedGraph(
            function = force_function_1,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min1,
            t_max = t_max1,
            color = FORCE_COLOR,
            alpha = 0.0,
            show_labels = False
        )
        
        graph2 = WindowedGraph(
            function = force_function_2,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min2,
            t_max = t_max2,
            color = FORCE_COLOR,
            alpha = 0.0,
            show_labels = True
        )

        graph1.move_to(cm_origin + 11 * RIGHT + 0.5 * vertical_distance * DOWN)
        graph2.move_to(cm_origin + 11 * RIGHT + 0.5 * vertical_distance * UP)

        self.add(graph1, graph2)

        self.play(
            ApplyMethod(
                train1.shift, (train1.get_width() + train2.get_width()) * LEFT,
                rate_func = linear, run_time = self.measured_proper_time
            ),
            PropagateClock(clock1, TIME_CLOCK_SCALE * self.measured_shortened_time, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(clock1, train1, run_time = self.measured_proper_time),
            PropagateClock(clock2, TIME_CLOCK_SCALE * self.measured_proper_time, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(clock2, train2, run_time = self.measured_proper_time),
            AnimateForceArrow(force1, length_function = scaled_shifted_ff_1, run_time = self.measured_proper_time),
            AnimateForceArrow(force2, length_function = scaled_shifted_ff_2, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(force1, train1, run_time = self.measured_proper_time,
                tracked_critical_point = DOWN),
            MaintainPositionRelativeTo(force2, train2, run_time = self.measured_proper_time,
                tracked_critical_point = UP),
            DrawWindowedGraph(graph1, run_time = self.measured_proper_time),
            DrawWindowedGraph(graph2, run_time = self.measured_proper_time),
        )











