from manimlib import *
from objects.waves import *
from objects.particles import ChargedParticle
from objects.fields import LorentzField

class EFieldByMovingCharge(InteractiveScene):
    # Oscillation parameters
    amplitude = 0.25  # How far the particle moves
    frequency = 0.5   # How fast the particle oscillates
    direction = UP    # Direction of oscillation

    # Whether to show acceleration vector
    show_acceleration_vector = True
    origin = None  # Origin point, if None uses default axes origin

    # Configuration for the 3D axes
    axes_config = dict(
        axis_config=dict(stroke_opacity=0.7),
        x_range=(-10, 10),
        y_range=(-5, 5),
        z_range=(-3, 3),
    )

    # Configuration for the charged particle
    particle_config = dict(
        track_position_history=True,  # Keep track of past positions
        radius=0.15,  # Size of particle
    )

    # Configuration for acceleration vector display
    acceleration_vector_config = dict()

    # Configuration for the electromagnetic field
    field_config = dict(
        max_vect_len=0.35,          # Maximum length of field vectors
        stroke_opacity=0.75,         # Opacity of field lines
        radius_of_suppression=1.0,   # Radius around particle where field is suppressed
        height=10,                   # Height of field
        x_density=4.0,              # Density of field vectors in x direction
        y_density=4.0,              # Density of field vectors in y direction
        c=2.0,                      # Speed of light parameter
        norm_to_opacity_func=lambda n: np.clip(2 * n, 0, 0.8)  # Function to map field strength to opacity
    )
    field_class = LorentzField  # Type of field to use

    def setup(self):
        """Initialize the scene with axes, particles, field and vectors"""
        super().setup()
        self.add_axes()
        self.add_axis_labels(self.axes)
        self.add_particles(self.axes)
        self.add_field(self.particles)
        # if self.show_acceleration_vector:
        #     self.add_acceleration_vectors(self.particles)

    def add_axes(self):
        """Create and add 3D axes to the scene"""
        self.axes = ThreeDAxes(**self.axes_config)
        if self.origin is not None:
            self.axes.shift(self.origin - self.axes.get_origin())
        self.add(self.axes)

    def add_axis_labels(self, axes):
        """Add x, y, z labels to the axes"""
        axis_labels = label = Tex("xyz")
        if axes.z_axis.get_stroke_opacity() > 0:
            # 3D view
            axis_labels.rotate(PI / 2, RIGHT)
            axis_labels[0].next_to(axes.x_axis.get_right(), OUT)
            axis_labels[1].next_to(axes.y_axis.get_top(), OUT)
            axis_labels[2].next_to(axes.z_axis.get_zenith(), RIGHT)
        else:
            # 2D view
            axis_labels[1].clear_points()
            axis_labels[0].next_to(axes.x_axis.get_right(), UP)
            axis_labels[2].next_to(axes.y_axis.get_top(), RIGHT)

        self.axis_labels = axis_labels
        self.add(self.axis_labels)

    def add_particles(self, axes):
        """Create charged particles and add them to the scene"""
        self.particles = self.get_particles()
        self.particles.add_updater(lambda m: m.move_to(
            axes.c2p(*self.oscillation_function(self.time))
        ))
        for particle in self.particles:
            particle.ignore_last_motion()
        self.add(self.particles)

    def get_particles(self):
        """Create and return a group of charged particles"""
        return Group(ChargedParticle(**self.particle_config))

    def add_field(self, particles):
        """Create and add electromagnetic field to the scene"""
        self.field = self.field_class(*particles, **self.field_config)
        self.add(self.field, particles)

    def add_acceleration_vectors(self, particles):
        """Add acceleration vectors to show particle motion"""
        self.acceleration_vectors = VGroup(*(
            AccelerationVector(particle)
            for particle in particles
        ))
        self.add(self.acceleration_vectors, self.particles)

    def oscillation_function(self, time):
        """Calculate particle position as a function of time"""
        return self.amplitude * np.sin(TAU * self.frequency * time) * self.direction
    
    def construct(self):
        """Main animation sequence"""
        self.play(
            self.frame.animate.reorient(15, 70, 0),
            run_time=12
        )
        self.wait(5)


# Alternative implementation with improved structure and flexibility
class EFieldByMovingChargeV2(InteractiveScene):
    def __init__(self, **kwargs):
        # Initialize with default configs that can be overridden
        self.oscillation = dict(
            amplitude=0.25,
            frequency=0.5, 
            direction=UP
        )
        
        self.field_setup = dict(
            field_class=LorentzField,
            field_config=dict(
                max_vect_len=0.35,
                stroke_opacity=0.75,
                radius_of_suppression=1.0,
                height=10,
                x_density=4.0,
                y_density=4.0,
                c=2.0,
                norm_to_opacity_func=lambda n: np.clip(2 * n, 0, 0.8)
            )
        )

        self.visualization = dict(
            show_acceleration=True,
            axes_config=dict(
                axis_config=dict(stroke_opacity=0.7),
                x_range=(-10, 10), 
                y_range=(-5, 5),
                z_range=(-3, 3)
            ),
            particle_config=dict(
                track_position_history=True,
                radius=0.15
            )
        )
        
        # Override defaults with any provided kwargs
        self._update_config(kwargs)
        super().__init__()

    def _update_config(self, updates):
        """Helper to recursively update nested config dictionaries"""
        for key, value in updates.items():
            if key in self.__dict__ and isinstance(value, dict):
                self.__dict__[key].update(value)
            else:
                self.__dict__[key] = value

    def setup_scene(self):
        """Initialize all scene components"""
        self.setup_axes()
        self.setup_particles() 
        self.setup_field()
        if self.visualization['show_acceleration']:
            self.setup_acceleration_vectors()

    def setup_axes(self):
        """Setup coordinate system"""
        self.axes = ThreeDAxes(**self.visualization['axes_config'])
        self.add_axis_labels()
        self.add(self.axes)

    def setup_particles(self):
        """Setup oscillating charged particles"""
        self.particles = Group(
            ChargedParticle(**self.visualization['particle_config'])
        )
        self.particles.add_updater(self.update_particle_positions)
        self.add(self.particles)

    def setup_field(self):
        """Setup electromagnetic field"""
        self.field = self.field_setup['field_class'](
            *self.particles,
            **self.field_setup['field_config']
        )
        self.add(self.field)

    def update_particle_positions(self, particles):
        """Update particle positions based on oscillation"""
        t = self.time
        pos = (
            self.oscillation['amplitude'] * 
            np.sin(TAU * self.oscillation['frequency'] * t) * 
            self.oscillation['direction']
        )
        particles.move_to(self.axes.c2p(*pos))

    def construct(self):
        """Main animation sequence"""
        self.setup_scene()
        self.play(
            self.frame.animate.reorient(15, 70, 0),
            run_time=12
        )
        self.wait(5)