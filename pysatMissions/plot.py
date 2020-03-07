# -*- coding: utf-8 -*-
"""Provides default plotting routines for simulated pysat instruments.

"""

import numpy as np


def plot_simulated_data(inst, filename=None):

    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    if filename is None:
        out_fname = './summary_orbit_simulated_data.png'
    else:
        out_fname = filename

    # make monotonically increasing longitude signal
    diff = inst['glong'].diff()

    idx, = np.where(diff < 0.)
    for item in idx:
        inst[item:, 'glong'] += 360.

    fig = plt.figure(figsize=(8.5, 7))

    time1 = inst.data.index[0].strftime('%Y-%h-%d %H:%M:%S')
    if inst.data.index[0].date() == inst.data.index[-1].date():
        time2 = inst.data.index[-1].strftime('%H:%M:%S')
    else:
        time2 = inst.data.index[-1].strftime('%Y-%h-%d %H:%M:%S')
    # Overall Plot Title
    plt.suptitle(''.join(('Simulated inst ', time1, ' -- ', time2)),
                 fontsize=18)

    # create grid for plots
    gs = gridspec.GridSpec(5, 2, width_ratios=[12, 1])

    ax = fig.add_subplot(gs[0, 0])
    plt.plot(np.log10(inst['ion_dens']), 'k', label='total')
    plt.plot(np.log10(inst['ion_dens']*inst['frac_dens_o']), 'r', label='O+')
    plt.plot(np.log10(inst['ion_dens']*inst['frac_dens_h']), 'b', label='H+')
    plt.legend(loc=(01.01, 0.15))
    ax.set_title('Log Ion Density')
    ax.set_ylabel('Log Density (N/cc)')
    ax.set_ylim([1., 6.])
    ax.axes.get_xaxis().set_visible(False)

    ax2 = fig.add_subplot(gs[1, 0], sharex=ax)
    plt.plot(inst['ion_temp'])
    plt.legend(loc=(1.01, 0.15))
    ax2.set_title('Ion Temperature')
    ax2.set_ylabel('Temp (K)')
    ax2.set_ylim([500., 1500.])
    ax2.axes.get_xaxis().set_visible(False)

    ax3 = fig.add_subplot(gs[2, 0], sharex=ax)
    plt.plot(inst['sim_wind_sc_x'], color='b', linestyle='--')
    plt.plot(inst['sim_wind_sc_y'], color='r', linestyle='--')
    plt.plot(inst['sim_wind_sc_z'], color='g', linestyle='--')
    ax3.set_title('Neutral Winds in S/C X, Y, and Z')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_ylim([-200., 200.])
    ax3.axes.get_xaxis().set_visible(False)
    plt.legend(loc=(1.01, 0.15))
    ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))

    ax4 = fig.add_subplot(gs[3, 0], sharex=ax)
    plt.plot(inst['B_sc_x']*1e5, color='b', linestyle='--')
    plt.plot(inst['B_sc_y']*1e5, color='r', linestyle='--')
    plt.plot(inst['B_sc_z']*1e5, color='g', linestyle='--')
    ax4.set_title('Magnetic Field in S/C X, Y, and Z')
    ax4.set_ylabel('Gauss')
    ax4.set_ylim([-3.5, 3.5])
    plt.legend(loc=(1.01, 0.15))
    ax4.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=20, ha='right')

    fig.add_subplot(gs[4, 0])
    # do long time plot
    inst['glat'].plot(label='glat')
    inst['mlt'].plot(label='mlt')
    plt.title('Satellite Position')
    plt.legend(['mlat', 'mlt'], loc=(1.01, 0.15))

    fig.tight_layout()
    # buffer for overall title
    fig.subplots_adjust(bottom=0.06, top=0.91, right=.91)
    plt.subplots_adjust(hspace=0.44)

    plt.savefig(out_fname)

    return
