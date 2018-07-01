from big_ol_pile_of_manim_imports import *
from active_projects.lorentz import *

TIME_SCALE = 0.5
FORCE_SCALE = 0.6
FORCE_COLOR = RED


class Train(VGroup):

    CONFIG = {
        "file_name": "train",
        "train_height": 1.0,
        "observer_location": 0.7, # btw 0 and 1
        "observer_color": RED,
        "fill_color": BLUE_C,
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


        self.beta2 = 2 * self.beta / (1 + self.beta **2)
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
        horizontal_offset = 5.5
        cm_origin = 1.5*LEFT + DOWN

        train1_start = cm_origin + 0.5 * vertical_distance * DOWN + 0.5 * horizontal_offset * LEFT
        train2_start = cm_origin + 0.5 * vertical_distance * UP + 0.5 * horizontal_offset * RIGHT

        train1 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            )
        train1.squeeze(1.0/self.gamma)
        train1.flip().move_to(train1_start)
        self.add(train1)


        train2 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            )
        train2.squeeze(1.0/self.gamma)
        train2.move_to(train2_start)
        self.add(train2)


        force_function_cm = lambda t: 1.3 * np.exp(-t**2 * 100)
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
        clock.move_to(cm_origin + 4 * UP)
        self.add(clock)
        
        graph1 = WindowedGraph(
            function = force_function_cm,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min,
            t_max = t_max,
            color = RED,
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
            color = RED,
            alpha = 0.0,
            show_labels = True
        )

        graph1.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * DOWN)
        graph2.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * UP)

        self.add(graph1, graph2)


        self.play(
            ApplyMethod(
                train1.shift, horizontal_offset * RIGHT,
                rate_func = linear, run_time = self.train_pass_cm_time
            ),
            ApplyMethod(
                train2.shift, horizontal_offset * LEFT,
                rate_func = linear, run_time = self.train_pass_cm_time
            ),
            PropagateClock(clock, self.measured_cm_time, run_time = self.train_pass_cm_time),
            AnimateForceArrow(force1, length_function = force_function_cm, run_time = self.train_pass_cm_time),
            AnimateForceArrow(force2, length_function = force_function_cm, run_time = self.train_pass_cm_time),
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
        horizontal_offset = 5.5
        cm_origin = 1.5*LEFT + DOWN

        self.train_shortened_length = self.train_proper_length / self.gamma2 # one train's length relative to the other
        
        train1_start = cm_origin + 0.5 * vertical_distance * DOWN
        train1 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            )
        train1.flip().move_to(train1_start)
        self.add(train1)


        train2 = Train(
            train_height = 1.0,
            observer_location = 0.5,
            )
        train2.squeeze(1.0/self.gamma2)

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

        force_function_cm = lambda t: 1.3 * np.exp(-t**2 * 100)/np.exp(-0.25)
        force_function_1 = lambda t: force_function_cm(t*self.gamma) * self.gamma
        force_function_2 = lambda t: force_function_cm(t*self.gamma2) * self.gamma2

        t_min1 = -0.5 * self.measured_proper_time
        t_max1 = -t_min1
        t_min2 = -0.5 * self.measured_shortened_time
        t_max2 = -t_min2

        force1 = ForceArrow(
            train1.get_center(),
            UP,
            force_function_1(t_min1),
            color = RED,)
        force2 = ForceArrow(
            train2.get_center(),
            DOWN,
            force_function_2(t_min2),
            color = RED,)

        self.add(force1, force2)


        
        graph1 = WindowedGraph(
            function = force_function_1,
            x_scale = TIME_SCALE,
            y_scale = FORCE_SCALE,
            height = 2.0,
            t_min = t_min1,
            t_max = t_max1,
            color = RED,
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
            color = RED,
            alpha = 0.0,
            show_labels = True
        )

        graph1.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * DOWN)
        graph2.move_to(cm_origin + 7 * RIGHT + 0.5 * vertical_distance * UP)

        self.add(graph1, graph2)

        self.play(
            ApplyMethod(
                train2.shift, (train1.get_width() + train2.get_width()) * LEFT,
                rate_func = linear, run_time = self.measured_proper_time
            ),
            PropagateClock(clock1, self.measured_proper_time, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(clock1, train1, run_time = self.measured_proper_time),
            PropagateClock(clock2, self.measured_shortened_time, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(clock2, train2, run_time = self.measured_proper_time),
            AnimateForceArrow(force1, length_function = force_function_1, run_time = self.measured_proper_time),
            AnimateForceArrow(force2, length_function = force_function_2, run_time = self.measured_proper_time),
            MaintainPositionRelativeTo(force1, train1, run_time = self.measured_proper_time,
                tracked_critical_point = DOWN),
            MaintainPositionRelativeTo(force2, train2, run_time = self.measured_proper_time,
                tracked_critical_point = UP),
            DrawWindowedGraph(graph1, run_time = self.measured_proper_time),
            DrawWindowedGraph(graph2, run_time = self.measured_proper_time),
        )











