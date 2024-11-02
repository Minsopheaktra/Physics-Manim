from manimlib import *
from utils.forces import coulomb_force, lorentz_force

class ChargeBasedVectorField(VectorField):
    """Base class for vector fields that depend on charged particles"""
    # Default color for the vector field visualization
    default_color = BLUE

    def __init__(self, *charges, **kwargs):
        # Store the list of charges that generate the field
        self.charges = list(charges)
        
        # Initialize parent VectorField with the force calculation function
        # Allow color override through kwargs, otherwise use default
        super().__init__(
            self.get_forces,
            color=kwargs.pop("color", self.default_color),
            **kwargs
        )
        
        # Add automatic vector updating when charges move
        self.add_updater(lambda m: m.update_vectors())

    def get_forces(self, points):
        """Calculate forces at given points. To be implemented by subclasses."""
        # Default implementation returns zero vectors
        return np.zeros_like(points)


class CoulombField(ChargeBasedVectorField):
    """Vector field representing electrostatic Coulomb forces"""
    # Use yellow color for electric fields
    default_color = YELLOW

    def get_forces(self, points):
        """Calculate total Coulomb force at each point"""
        # Sum up Coulomb forces from all charges
        return sum(
            coulomb_force(points, charge)
            for charge in self.charges
        )


class LorentzField(ChargeBasedVectorField):
    """Vector field representing electromagnetic Lorentz forces"""
    
    def __init__(
        self, *charges,
        radius_of_suppression=None,  # Radius within which forces are suppressed
        c=2.0,                       # Speed of light constant
        **kwargs
    ):
        # Store field-specific parameters
        self.radius_of_suppression = radius_of_suppression
        self.c = c
        # Initialize parent with charges
        super().__init__(*charges, **kwargs)

    def get_forces(self, points):
        """Calculate total Lorentz force at each point"""
        # Sum up Lorentz forces from all charges
        # Include suppression radius and light speed in calculation
        return sum(
            lorentz_force(
                points, charge,
                radius=self.radius_of_suppression,
                c=self.c
            )
            for charge in self.charges
        )