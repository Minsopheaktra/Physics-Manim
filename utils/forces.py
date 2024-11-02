from manimlib import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import Vect3


def points_to_particle_info(particle, points, radius=None, c=2.0):
    """
    Calculate geometric information between points and a charged particle.

    Args:
        particle: The charged particle object
        points: Array of points to calculate forces at
        radius: Radius around particle where forces are suppressed (defaults to particle radius)
        c: Speed of light parameter for relativistic effects

    Returns:
        tuple containing:
        - unit_diffs: Unit vectors from particle to each point
        - norms: Actual distances from particle to points  
        - adjusted_norms: Modified distances that prevent force blowup near particle
    """
    # Use particle's physical radius if no radius specified
    if radius is None:
        radius = particle.get_radius()

    # For particles tracking position history, account for light delay
    if particle.track_position_history:
        # Calculate approximate light travel time to each point
        approx_delays = np.linalg.norm(points - particle.get_center(), axis=1) / c
        # Get particle's historical positions based on delays
        centers = particle.get_past_position(approx_delays)
    else:
        # If no history tracking, just use current position
        centers = particle.get_center()

    # Calculate vectors from particle positions to field points
    diffs = points - centers
    # Get magnitudes of these vectors
    norms = np.linalg.norm(diffs, axis=1)[:, np.newaxis]
    
    # Calculate unit vectors, handling zero distances
    unit_diffs = np.zeros_like(diffs)
    np.true_divide(diffs, norms, out=unit_diffs, where=(norms > 0))

    # Adjust distances to prevent infinite forces near particle
    adjusted_norms = norms.copy()
    # For points within radius, scale up the distance
    mask = (0 < norms) & (norms < radius)
    adjusted_norms[mask] = radius * radius / norms[mask]
    # Set distance to infinity at particle position
    adjusted_norms[norms == 0] = np.inf

    return unit_diffs, norms, adjusted_norms


def coulomb_force(points, particle, radius=None):
    """
    Calculate Coulomb (electrostatic) force at given points due to particle.
    
    Force follows inverse square law but is suppressed within radius of particle.
    """
    unit_diffs, norms, adjusted_norms = points_to_particle_info(particle, points, radius)
    # F = kq * r_hat / r^2, where k absorbed into charge value
    return particle.get_charge() * unit_diffs / adjusted_norms**2


def lorentz_force(
    points,
    particle,
    radius=None,
    c=2.0,
    epsilon0=0.025,
):
    """
    Calculate Lorentz force at given points due to accelerating charged particle.
    
    Includes relativistic effects from particle acceleration and light speed delay.
    
    Args:
        points: Points to calculate force at
        particle: Source charged particle
        radius: Force suppression radius
        c: Speed of light parameter
        epsilon0: Electric permittivity constant
    """
    # Get geometric info accounting for light speed delay
    unit_diffs, norms, adjusted_norms = points_to_particle_info(particle, points, radius, c)
    # Calculate light travel time to each point
    delays = norms[:, 0] / c

    # Get particle acceleration at delayed times
    acceleration = particle.get_past_acceleration(delays)
    # Project acceleration along radial direction
    dot_prods = (unit_diffs * acceleration).sum(1)[:, np.newaxis]
    # Get perpendicular component of acceleration
    a_perp = acceleration - dot_prods * unit_diffs

    # Calculate denominator with physical constants
    denom = 4 * PI * epsilon0 * c**2 * adjusted_norms
    # Return force proportional to perpendicular acceleration
    return -particle.get_charge() * a_perp / denom