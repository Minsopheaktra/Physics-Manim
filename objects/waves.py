from manimlib import *
from utils.styles import get_spectral_color
from utils.axes_and_planes import *

# PropagatingRings creates expanding circular waves, inherits from VGroup (group of VMobjects)
class PropagatingRings(VGroup):
    def __init__(
        self, line,          # Line along which rings will propagate
        n_rings=5,           # Number of rings to create
        start_width=3,       # Initial stroke width of rings
        width_decay_rate=0.1,# How quickly stroke width decays over time
        stroke_color=WHITE,  # Color of the rings
        growth_rate=2.0,     # How fast rings expand
        spacing=0.2,         # Time delay between rings
    ):
        # Create initial tiny circle with many points for smooth animation
        ring = Circle(radius=1e-3, n_components=101)
        ring.set_stroke(stroke_color, start_width)
        # Orient ring perpendicular to the given line
        ring.apply_matrix(z_to_vector(line.get_vector()))
        ring.move_to(line)
        ring.set_flat_stroke(False)  # Enable 3D lighting

        # Create n_rings copies of the ring and initialize parent class
        super().__init__(*ring.replicate(n_rings))

        # Store parameters as instance variables
        self.growth_rate = growth_rate
        self.spacing = spacing
        self.width_decay_rate = width_decay_rate
        self.start_width = start_width
        self.time = 0

        # Add update function that will be called each frame
        self.add_updater(lambda m, dt: self.update_rings(dt))

    def update_rings(self, dt):
        # Skip if no time passed
        if dt == 0:
            return
        # Increment time counter
        self.time += dt
        space = 0
        # Update each ring
        for ring in self.submobjects:
            # Calculate time since this ring started, accounting for spacing delay
            effective_time = max(self.time - space, 0)
            # Calculate target radius based on time
            target_radius = max(effective_time * self.growth_rate, 1e-3)
            # Scale ring to target radius
            ring.scale(target_radius / ring.get_radius())
            # Increment spacing for next ring
            space += self.spacing
            # Update stroke width based on exponential decay
            ring.set_stroke(width=np.exp(-self.width_decay_rate * effective_time))
        return self
    
# Demo scene showing PropagatingRings
class PropagatingRingsDemo(InteractiveScene):
    def construct(self):
        # Create 3D axes
        axes = ThreeDAxes()
        add_axis_labels(self, axes)
        # Create propagating rings along z-axis
        wave = PropagatingRings(axes.z_axis)
        # Add to scene and wait
        self.add(axes, wave)
        self.wait(5)


# OscillatingWave creates a sinusoidal wave that can oscillate in y and z
class OscillatingWave(VMobject):
    def __init__(
        self,
        axes,               # 3D axes to place wave in
        y_amplitude=0.0,    # Amplitude of y-component
        z_amplitude=0.75,   # Amplitude of z-component
        z_phase=0.0,        # Phase offset for z-component
        y_phase=0.0,        # Phase offset for y-component
        wave_len=0.5,       # Wavelength of oscillation
        twist_rate=0.0,     # How much wave rotates around x-axis per unit distance
        speed=1.0,          # Speed of wave propagation
        sample_resolution=0.005,  # Distance between sample points
        stroke_width=2,     # Width of wave line
        offset=ORIGIN,      # Offset from origin
        color=None,         # Color of wave (defaults to spectral color)
        **kwargs,
    ):
        # Store parameters as instance variables
        self.axes = axes
        self.y_amplitude = y_amplitude
        self.z_amplitude = z_amplitude
        self.z_phase = z_phase
        self.y_phase = y_phase
        self.wave_len = wave_len
        self.twist_rate = twist_rate
        self.speed = speed
        self.sample_resolution = sample_resolution
        self.offset = offset

        # Initialize parent class
        super().__init__(**kwargs)

        # Set color and stroke properties
        color = color or self.get_default_color(wave_len)
        self.set_stroke(color, stroke_width)
        self.set_flat_stroke(False)

        # Initialize time tracking
        self.time = 0
        self.clock_is_stopped = False

        # Add update function
        self.add_updater(lambda m, dt: m.update_points(dt))

    def update_points(self, dt):
        # Update time if clock running
        if not self.clock_is_stopped:
            self.time += dt
        # Generate x coordinates along axis
        xs = np.arange(
            self.axes.x_axis.x_min,
            self.axes.x_axis.x_max,
            self.sample_resolution
        )
        # Update wave points
        self.set_points_as_corners(
            self.offset + self.xt_to_point(xs, self.time)
        )

    def stop_clock(self):
        # Stop time updates
        self.clock_is_stopped = True

    def start_clock(self):
        # Resume time updates
        self.clock_is_stopped = False

    def xt_to_yz(self, x, t):
        # Calculate phase based on time and speed
        phase = TAU * t * self.speed / self.wave_len
        # Calculate y and z components before twist
        y_outs = self.y_amplitude * np.sin(TAU * x / self.wave_len - phase - self.y_phase)
        z_outs = self.z_amplitude * np.sin(TAU * x / self.wave_len - phase - self.z_phase)
        # Calculate twist angles
        twist_angles = x * self.twist_rate * TAU
        # Apply twist rotation to y,z components
        y = np.cos(twist_angles) * y_outs - np.sin(twist_angles) * z_outs
        z = np.sin(twist_angles) * y_outs + np.cos(twist_angles) * z_outs

        return y, z

    def xt_to_point(self, x, t):
        # Convert x,t coordinates to 3D points
        y, z = self.xt_to_yz(x, t)
        return self.axes.c2p(x, y, z)

    def get_default_color(self, wave_len):
        # Get color from spectrum based on wavelength
        return get_spectral_color(inverse_interpolate(
            1.5, 0.5, wave_len
        ))

# Demo scene showing OscillatingWave
class OscillatingWaveDemo(InteractiveScene):
    def construct(self):
        # Create axes
        axes = ThreeDAxes()
        # Create wave with default parameters
        wave = OscillatingWave(
            axes=axes,
            z_amplitude=0.75,
            wave_len=0.5,
            speed=1.0
        )
        # Add to scene and wait
        self.add(axes)
        self.add(wave)
        self.wait(5)


# AccelerationVector shows acceleration of a particle as an arrow
class AccelerationVector(Vector):
    def __init__(
        self,
        particle,           # Particle to track
        stroke_color=PINK,  # Color of vector
        stroke_width=4,     # Width of vector line
        flat_stroke=False,  # Whether to use 3D lighting
        norm_func=lambda n: np.tanh(n),  # Function to scale vector length
        **kwargs
    ):
        self.norm_func = norm_func

        # Initialize as right-pointing vector
        super().__init__(
            RIGHT,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            flat_stroke=flat_stroke,
            **kwargs
        )
        # Add updater to track particle
        self.add_updater(lambda m: m.pin_to_particle(particle))

    def pin_to_particle(self, particle):
        # Get acceleration vector
        a_vect = particle.get_acceleration()
        norm = get_norm(a_vect)
        # Scale vector length if needed
        if self.norm_func is not None and norm > 0:
            a_vect *= self.norm_func(norm) / norm
        # Get particle position
        center = particle.get_center()
        # Update vector position and direction
        self.put_start_and_end_on(center, center + a_vect)