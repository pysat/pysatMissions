"""Methods to convert orbital information for propagators."""

import numpy as np
import warnings


def _check_orbital_params(kwargs=None):
    """Check that a complete set of unconflicted orbital parameters exist.

    Parameters
    ----------
    kwargs : dict
        Dictionary of optional kwargs passed through upon initialization
        of pysat instrument.

    """

    elements = list(kwargs['load'].keys())

    keplerians = ['alt_periapsis', 'inclination']
    tles = ['TLE1', 'TLE2']
    errmsg = 'Insufficient kwargs.  Kwarg group requires {:}'
    for group in [tles, keplerians]:
        if any(v in elements for v in group):
            if not all(v in elements for v in group):
                raise KeyError(errmsg.format(', '.join(group)))
    if all(v in elements for v in tles) and all(v in elements for v in keplerians):
        warnings.warn(' '.join(['Cannot use both Keplerians and TLEs.',
                                'Defaulting to Keplerians.']))

    return


def _get_constants(planet='Earth'):
    """Retrieve planetary constants for calculations.

    Parameters
    ----------
    planet : str
        The name of the planet of interest.
        (default='Earth')

    Returns
    -------
    radius : float (km)
        The average radius to the surface of a planet.
    mass : float (kg)
        The average mass of the planet.
    gravity : float (m**3 kg / s**2)
        Newton's gravitational constant
    """

    radius = {'Earth': 6371.2}
    mass = {'Earth': 5.9742e24}
    gravity = 6.6743e-11

    if planet not in radius.keys():
        raise KeyError('{:} is not yet a supported planet!'.format(planet))

    return radius[planet], mass[planet], gravity


def convert_to_keplerian(alt_periapsis, alt_apoapsis=None, planet='Earth'):
    """Calculate orbital eccentricity from periapsis and apoapsis.

    Parameters
    ----------
    alt_periapsis : float
        The lowest altitude from the mean planet surface along the orbit (km)
    alt_apoapsis : float or NoneType
        The highest altitude from the mean planet surface along the orbit (km)
        If None, assumed to be equal to periapsis. (default=None)
    planet : str
        The name of the planet of interest.  Used for radial calculations and
        mass.
        (default='Earth')

    Returns
    -------
    eccentricity : float
        The eccentricty of the orbit (unitless)
    mean_motion : float
        The mean angular speed of the orbit (rad/minute)

    """

    radius, mass, gravity = _get_constants(planet)
    if alt_apoapsis is None:
        alt_apoapsis = alt_periapsis

    rad_apoapsis = alt_apoapsis + radius
    rad_periapsis = alt_periapsis + radius
    semimajor = 0.5 * (rad_apoapsis + rad_periapsis)

    eccentricity = ((rad_apoapsis - rad_periapsis)
                    / (rad_apoapsis + rad_periapsis))

    # convert axis to m, mean_motion to rad / minute
    mean_motion = np.sqrt(gravity * mass / (1000 * semimajor)**3) * 60

    return eccentricity, mean_motion


def convert_from_keplerian(eccentricity, mean_motion, planet='Earth'):
    """Calculate orbital eccentricity from periapsis and apoapsis.

    Parameters
    ----------
    eccentricity : float
        The eccentricty of the orbit (unitless)
    mean_motion : float
        The mean angular speed of the orbit (rad/minute)
    planet : string
        The name of the planet of interest.  Used for radial calculations.
        (default='Earth')

    Returns
    -------
    alt_periapsis : float
        The lowest altitude from the mean planet surface along the orbit (km)
    alt_apoapsis : float
        The highest altitude from the mean planet surface along the orbit (km)

    """

    radius, mass, gravity = _get_constants(planet)
    # Convert mean_motion to rad / second before computing
    semimajor = (gravity * mass / (mean_motion / 60)**2)
    # Convert distance to km
    semimajor = semimajor**(1 / 3) / 1000

    rad_apoapsis = semimajor * (1 + eccentricity)
    rad_periapsis = semimajor * (1 - eccentricity)

    alt_apoapsis = rad_apoapsis - radius
    alt_periapsis = rad_periapsis - radius

    return alt_periapsis, alt_apoapsis
