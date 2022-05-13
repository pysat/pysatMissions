"""Default routines for projecting values onto vectors for pysat instruments."""

import numpy as np
import OMMBV


def add_ram_pointing_sc_attitude_vectors(inst):
    """Add attitude vectors for spacecraft assuming ram pointing.

    Presumes spacecraft is pointed along the velocity vector (x), z is
    generally nadir pointing (positive towards Earth), and y completes the
    right handed system (generally southward).

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument object

    Returns
    -------
    None
        Modifies pysat.Instrument object in place to include S/C attitude
        unit vectors, expressed in ECEF basis. Vectors are named
        sc_(x,y,z)hat_ecef_(x,y,z).
        sc_xhat_ecef_x is the spacecraft unit vector along x (positive along
        velocity vector) reported in ECEF, ECEF x-component.

    Notes
    -----
        Expects velocity and position of spacecraft in Earth Centered
        Earth Fixed (ECEF) coordinates to be in the instrument object
        and named velocity_ecef_* (*=x,y,z) and position_ecef_* (*=x,y,z)

        Adds attitude vectors for spacecraft in the ECEF basis by calculating
        the scalar product of each attitude vector with each component of ECEF.

    """

    # Ram pointing is along velocity vector
    inst['sc_xhat_ecef_x'], inst['sc_xhat_ecef_y'], inst['sc_xhat_ecef_z'] = \
        OMMBV.vector.normalize(inst['velocity_ecef_x'],
                               inst['velocity_ecef_y'],
                               inst['velocity_ecef_z'])

    # Begin with z along Nadir (towards Earth)
    # if orbit isn't perfectly circular, then the s/c z vector won't
    # point exactly along nadir. However, nadir pointing is close enough
    # to the true z (in the orbital plane) that we can use it to get y,
    # and use x and y to get the real z
    inst['sc_zhat_ecef_x'], inst['sc_zhat_ecef_y'], inst['sc_zhat_ecef_z'] = \
        OMMBV.vector.normalize(-inst['position_ecef_x'],
                               -inst['position_ecef_y'],
                               -inst['position_ecef_z'])

    # get y vector assuming right hand rule
    # Z x X = Y
    inst['sc_yhat_ecef_x'], inst['sc_yhat_ecef_y'], inst['sc_yhat_ecef_z'] = \
        OMMBV.vector.cross_product(inst['sc_zhat_ecef_x'],
                                   inst['sc_zhat_ecef_y'],
                                   inst['sc_zhat_ecef_z'],
                                   inst['sc_xhat_ecef_x'],
                                   inst['sc_xhat_ecef_y'],
                                   inst['sc_xhat_ecef_z'])
    # Normalize since Xhat and Zhat from above may not be orthogonal
    inst['sc_yhat_ecef_x'], inst['sc_yhat_ecef_y'], inst['sc_yhat_ecef_z'] = \
        OMMBV.vector.normalize(inst['sc_yhat_ecef_x'],
                               inst['sc_yhat_ecef_y'],
                               inst['sc_yhat_ecef_z'])

    # Strictly, need to recalculate Zhat so that it is consistent with RHS
    # just created
    # Z = X x Y
    inst['sc_zhat_ecef_x'], inst['sc_zhat_ecef_y'], inst['sc_zhat_ecef_z'] = \
        OMMBV.vector.cross_product(inst['sc_xhat_ecef_x'],
                                   inst['sc_xhat_ecef_y'],
                                   inst['sc_xhat_ecef_z'],
                                   inst['sc_yhat_ecef_x'],
                                   inst['sc_yhat_ecef_y'],
                                   inst['sc_yhat_ecef_z'])

    # Adding metadata
    for v in ['x', 'y', 'z']:
        for u in ['x', 'y', 'z']:
            inst.meta['sc_{:}hat_ecef_{:}'.format(v, u)] = {
                inst.meta.labels.units: '',
                inst.meta.labels.name: 'SC {:}-unit vector, ECEF-{:}'.format(v, u),
                inst.meta.labels.desc: ' '.join(('S/C attitude ({:}'.format(v),
                                                 '-direction, ram) unit vector,',
                                                 'expressed in ECEF basis,',
                                                 '{:}-component'.format(u)))}

    # check what magnitudes we get
    mag = np.sqrt(inst['sc_zhat_ecef_x']**2 + inst['sc_zhat_ecef_y']**2
                  + inst['sc_zhat_ecef_z']**2)
    idx, = np.where((mag < .999999999) | (mag > 1.000000001))
    if len(idx) > 0:
        print(mag[idx])
        raise RuntimeError(' '.join(('Unit vector generation failure. Not',
                                     'sufficently orthogonal.')))

    return


def calculate_ecef_velocity(inst):
    """Calculate spacecraft velocity in ECEF frame.

    Presumes that the spacecraft velocity in ECEF is in
    the input instrument object as position_ecef_*. Uses a symmetric
    difference to calculate the velocity thus endpoints will be
    set to NaN. Routine should be run using pysat data padding feature
    to create valid end points.

    Parameters
    ----------
    inst : pysat.Instrument
        Instrument object

    Returns
    -------
    None
        Modifies pysat.Instrument object in place to include ECEF velocity
        using naming scheme velocity_ecef_* (*=x,y,z)

    """

    def get_vel_from_pos(x):
        vel = (x.values[2:] - x.values[0:-2]) / 2.
        return vel

    vel_x = get_vel_from_pos(inst['position_ecef_x'])
    vel_y = get_vel_from_pos(inst['position_ecef_y'])
    vel_z = get_vel_from_pos(inst['position_ecef_z'])

    inst[1:-1, 'velocity_ecef_x'] = vel_x
    inst[1:-1, 'velocity_ecef_y'] = vel_y
    inst[1:-1, 'velocity_ecef_z'] = vel_z

    for v in ['x', 'y', 'z']:
        inst.meta['velocity_ecef_{:}'.format(v)] = {
            inst.meta.labels.units: 'km/s',
            inst.meta.labels.name: 'ECEF {:}-velocity'.format(v),
            inst.meta.labels.desc: ' '.join(('Velocity of satellite calculated',
                                             'with respect to ECEF frame.'))}
    return


def project_ecef_vector_onto_sc(inst, x_label, y_label, z_label,
                                new_x_label, new_y_label, new_z_label,
                                meta=None):
    """Express input vector using s/c attitude directions.

    x - ram pointing
    y - generally southward
    z - generally nadir

    Parameters
    ----------
    x_label : string
        Label used to get ECEF-X component of vector to be projected
    y_label : string
        Label used to get ECEF-Y component of vector to be projected
    z_label : string
        Label used to get ECEF-Z component of vector to be projected
    new_x_label : string
        Label used to set X component of projected vector
    new_y_label : string
        Label used to set Y component of projected vector
    new_z_label : string
        Label used to set Z component of projected vector
    meta : array_like of dicts (None)
        Dicts contain metadata to be assigned.
    """

    # TODO(#65): add checks for existence of ecef labels in inst

    x, y, z = OMMBV.vector.project_onto_basis(
        inst[x_label], inst[y_label], inst[z_label],
        inst['sc_xhat_ecef_x'], inst['sc_xhat_ecef_y'], inst['sc_xhat_ecef_z'],
        inst['sc_yhat_ecef_x'], inst['sc_yhat_ecef_y'], inst['sc_yhat_ecef_z'],
        inst['sc_zhat_ecef_x'], inst['sc_zhat_ecef_y'], inst['sc_zhat_ecef_z'])
    inst[new_x_label] = x
    inst[new_y_label] = y
    inst[new_z_label] = z

    if meta is not None:
        inst.meta[new_x_label] = meta[0]
        inst.meta[new_y_label] = meta[1]
        inst.meta[new_z_label] = meta[2]

    return
