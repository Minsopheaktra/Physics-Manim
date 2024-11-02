from manimlib import *
import numpy as np 
from typing import Callable 
from numpy.typing import ArrayLike as Vect3 

class ChargedParticle(Group):
    """A class representing a charged particle that can interact with fields and forces"""
    def __init__(
        self,
        point=ORIGIN,         # Initial position of particle
        charge=1.0,           # Electric charge value
        mass=1.0,             # Mass of the particle
        color=RED,            # Visual color of particle
        show_sign=True,       # Whether to show + or - sign
        sign="+",             # Which sign to show if show_sign is True
        radius=0.2,           # Visual radius of particle
        rotation=0,           # Rotation of the sign
        sign_stroke_width=2,  # Thickness of sign outline
        track_position_history=True,  # Whether to store position history
        history_size=7200,           # How many past positions to store
        euler_steps_per_frame=10,    # Number of integration steps per frame
    ):
        # Store basic physical properties
        self.charge = charge
        self.mass = mass

        # Create visual sphere representation
        sphere = TrueDot(radius=radius, color=color)
        sphere.make_3d()  # Enable 3D rendering
        sphere.move_to(point)
        self.sphere = sphere

        # Initialize tracking variables
        self.track_position_history = track_position_history
        self.history_size = history_size
        self.velocity = np.zeros(3)  # 3D velocity vector, used for force calculations
        self.euler_steps_per_frame = euler_steps_per_frame
        self.init_clock(point)

        # Initialize as Group (parent class)
        super().__init__(sphere)

        # Add charge sign indicator if requested
        if show_sign:
            sign = Tex(sign)  # Create sign text
            sign.set_width(radius)  # Scale sign to particle size
            sign.rotate(rotation, RIGHT)  # Apply rotation
            sign.set_stroke(WHITE, sign_stroke_width)  # Set sign appearance
            sign.move_to(sphere)  # Position sign on particle
            self.add(sign)
            self.sign = sign

    # Related to updaters

    def update(self, dt: float = 0, recurse: bool = True):
        """Update particle state for each frame"""
        super().update(dt, recurse)
        # Update clock directly instead of using updater to avoid
        # requiring suspend_mobject_updating=false flag
        self.increment_clock(dt)

    def init_clock(self, start_point):
        """Initialize time tracking and position history"""
        self.time = 0
        self.time_step = 1 / 30  # Default time step, will be updated
        # Store last 3 positions for acceleration calculation
        self.recent_positions = np.tile(start_point, 3).reshape((3, 3))
        if self.track_position_history:
            # Initialize arrays for storing history
            self.position_history = np.zeros((self.history_size, 3))
            self.acceleration_history = np.zeros((self.history_size, 3))
            self.history_index = -1

    def increment_clock(self, dt):
        """Update time and position tracking for each time step"""
        if dt == 0:
            return self
        self.time += dt
        self.time_step = dt
        # Shift positions back and add current position
        self.recent_positions[0:2] = self.recent_positions[1:3]
        self.recent_positions[2] = self.get_center()
        if self.track_position_history:
            self.add_to_position_history()

    def add_to_position_history(self):
        """Record current position and acceleration in history"""
        self.history_index += 1
        hist_size = self.history_size
        # Handle buffer overflow by shifting history
        if self.history_index >= hist_size:
            for arr in [self.position_history, self.acceleration_history]:
                arr[:hist_size // 2, :] = arr[hist_size // 2:, :]
            self.history_index = (hist_size // 2) + 1

        # Record current state
        self.position_history[self.history_index] = self.get_center()
        self.acceleration_history[self.history_index] = self.get_acceleration()
        return self

    def ignore_last_motion(self):
        """Reset recent position history to current position"""
        self.recent_positions[:] = self.get_center()
        return self

    def add_force(self, force_func: Callable[[Vect3], Vect3]):
        """Add a continuous force to the particle using Euler integration"""
        espf = self.euler_steps_per_frame

        def update_from_force(particle, dt):
            if dt == 0:
                return
            # Perform multiple integration steps per frame for stability
            for _ in range(espf):
                acc = force_func(particle.get_center()) / self.mass
                self.velocity += acc * dt / espf
                self.shift(self.velocity * dt / espf)

        self.add_updater(update_from_force)
        return self

    def add_spring_force(self, k=1.0, center=None):
        """Add a spring force toward a center point"""
        center = center if center is not None else self.get_center().copy()
        self.add_force(lambda p: k * (center - p))
        return self

    def add_field_force(self, field):
        """Add force from an electromagnetic field"""
        charge = self.get_charge()
        self.add_force(lambda p: charge * field.get_forces([p])[0])
        return self

    def fix_x(self):
        """Constrain particle to current x position"""
        x = self.get_x()
        self.add_updater(lambda m: m.set_x(x))

    # Getters

    def get_charge(self):
        """Return particle's charge value"""
        return self.charge

    def get_radius(self):
        """Return visual radius of particle"""
        return self.sphere.get_radius()

    def get_internal_time(self):
        """Return particle's internal time counter"""
        return self.time

    def scale(self, factor, *args, **kwargs):
        """Scale particle and its visual representation"""
        super().scale(factor, *args, **kwargs)
        self.sphere.set_radius(factor * self.sphere.get_radius())
        return self

    def get_acceleration(self):
        """Calculate acceleration from recent positions using finite difference"""
        p0, p1, p2 = self.recent_positions
        # Check if particle is stationary to avoid artificial acceleration
        if np.isclose(p0, p1).all() or np.isclose(p1, p2).all():
            return np.zeros(3)
        # Calculate acceleration using second derivative approximation
        return (p0 + p2 - 2 * p1) / self.time_step**2

    def get_info_from_delays(self, info_arr, delays):
        """Get historical information at specified time delays"""
        if not hasattr(self, "acceleration_history"):
            raise Exception("track_position_history is not turned on")

        if len(info_arr) == 0:
            return np.zeros((len(delays), 3))

        # Calculate indices for requested delays
        pre_indices = self.history_index - delays / self.time_step
        indices = np.clip(pre_indices, 0, self.history_index).astype(int)

        return info_arr[indices]

    def get_past_acceleration(self, delays):
        """Get acceleration values from past times"""
        return self.get_info_from_delays(self.acceleration_history, delays)

    def get_past_position(self, delays):
        """Get position values from past times"""
        return self.get_info_from_delays(self.position_history, delays)
