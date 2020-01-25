# -*- coding: utf-8 -*-
"""Provides default plotting routines for simulated pysat instruments.

"""

import numpy as np
import pandas as pds


def plot_simulated_data(inst, filename=None):

    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.collections import LineCollection
    from mpl_toolkits.basemap import Basemap

    if filename is None:
        out_fname = './summary_orbit_simulated_data.png'
    else:
        out_fname = filename

    # make monotonically increasing longitude signal
    diff = inst['glong'].diff()

    idx, = np.where(diff < 0.)
    for item in idx:
        inst[item:, 'glong'] += 360.

    f = plt.figure(figsize=(8.5, 7))

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

    ax = f.add_subplot(gs[0, 0])
    plt.plot(np.log10(inst['ion_dens']), 'k', label='total')
    plt.plot(np.log10(inst['ion_dens']*inst['frac_dens_o']), 'r', label='O+')
    plt.plot(np.log10(inst['ion_dens']*inst['frac_dens_h']), 'b', label='H+')
    plt.legend(loc=(01.01, 0.15))
    ax.set_title('Log Ion Density')
    ax.set_ylabel('Log Density (N/cc)')
    ax.set_ylim([1., 6.])
    ax.axes.get_xaxis().set_visible(False)

    ax2 = f.add_subplot(gs[1, 0], sharex=ax)
    plt.plot(inst['ion_temp'])
    plt.legend(loc=(1.01, 0.15))
    ax2.set_title('Ion Temperature')
    ax2.set_ylabel('Temp (K)')
    ax2.set_ylim([500., 1500.])
    ax2.axes.get_xaxis().set_visible(False)

    # determine altitudes greater than 770 km
    # idx, = np.where(inst['alt'] > 770.)

    ax3 = f.add_subplot(gs[2, 0], sharex=ax)
    plt.plot(inst['sim_wind_sc_x'], color='b', linestyle='--')
    plt.plot(inst['sim_wind_sc_y'], color='r', linestyle='--')
    plt.plot(inst['sim_wind_sc_z'], color='g', linestyle='--')
    ax3.set_title('Neutral Winds in S/C X, Y, and Z')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_ylim([-200., 200.])
    ax3.axes.get_xaxis().set_visible(False)
    plt.legend(loc=(1.01, 0.15))
    ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    # # xlabels = [label[0:6] for label in xlabels]
    # plt.setp(ax3.xaxis.get_majorticklabels(), rotation=20, ha='right')

    ax4 = f.add_subplot(gs[3, 0], sharex=ax)
    plt.plot(inst['B_sc_x']*1e5, color='b', linestyle='--')
    plt.plot(inst['B_sc_y']*1e5, color='r', linestyle='--')
    plt.plot(inst['B_sc_z']*1e5, color='g', linestyle='--')
    ax4.set_title('Magnetic Field in S/C X, Y, and Z')
    ax4.set_ylabel('Gauss')
    ax4.set_ylim([-3.5, 3.5])
    # ax3.axes.get_xaxis().set_visible(False)
    plt.legend(loc=(1.01, 0.15))
    ax4.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    # # xlabels = [label[0:6] for label in xlabels]
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=20, ha='right')

    # inst info
    ax6 = f.add_subplot(gs[4, 0])

    # do world plot if time to be plotted is less than 285 minutes, less than
    # 3 orbits
    time_diff = inst.data.index[-1] - inst.data.index[0]
    if time_diff > pds.Timedelta(minutes=285):
        # do long time plot
        inst['glat'].plot(label='glat')  # legend=True, label='mlat')
        inst['mlt'].plot(label='mlt')  # legend=True, label='mlt')
        plt.title('Satellite Position')
        plt.legend(['mlat', 'mlt'], loc=(1.01, 0.15))
    #    inst['glong'].plot(secondary_y = True, label='glong')#legend=True,
    #       secondary_y = True, label='glong')

    else:

        # make map the same size as the other plots
        s1pos = plt.get(ax, 'position').bounds
        s6pos = plt.get(ax6, 'position').bounds
        ax6.set_position([s1pos[0], s6pos[1]+.008, s1pos[2], s1pos[3]])

        # fix longitude range for plot. Pad longitude so that first sample
        # aligned with inst measurement sample
        lon0 = inst[0, 'glong']
        lon1 = inst[-1, 'glong']

        # enforce minimal longitude window, keep graphics from being too
        # disturbed
        if (lon1-lon0) < 90:
            lon0 -= 45.
            lon1 += 45.
        if lon1 > 720:
            lon0 -= 360.
            lon1 -= 360.
            inst[:, 'glong'] -= 360.

        m = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=60.,
                    urcrnrlon=lon1.copy(), llcrnrlon=lon0.copy(),
                    resolution='c', ax=ax6, fix_aspect=False)
        # m is an object which manages drawing to the map
        # it also acts as a transformation function for geo coords to
        # plotting coords

        # coastlines
        m.drawcoastlines(ax=ax6)
        # get first longitude meridian to plot
        plon = np.ceil(lon0/60.)*60.
        m.drawmeridians(np.arange(plon, plon+360.-22.5, 60),
                        labels=[0, 0, 0, 1], ax=ax6)
        m.drawparallels(np.arange(-20, 20, 20))
        # time midway through inst to plot terminator locations
        midDate = inst.data.index[len(inst.data.index)//2]

        # plot day/night terminators
        try:
            _ = m.nightshade(midDate)
        except ValueError:
            pass

        x, y = m(inst['glong'].values, inst['glat'].values)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        plot_norm = plt.Normalize(300, 500)
        plot_cmap = plt.get_cmap('viridis')

        lc = LineCollection(segments, cmap=plot_cmap, norm=plot_norm,
                            linewidths=5.0)
        lc.set_array(inst['alt'].values)
        sm = plt.cm.ScalarMappable(cmap=plot_cmap, norm=plot_norm)
        sm._A = []

        ax6.add_collection(lc)

        ax6_bar = f.add_subplot(gs[4, 1])
        # plt.colorbar(sm)
        plt.colorbar(cax=ax6_bar, ax=ax6, mappable=sm,
                     orientation='vertical',
                     ticks=[300., 400., 500.])
        plt.xlabel('Altitude')
        plt.ylabel('km')

    f.tight_layout()
    # buffer for overall title
    f.subplots_adjust(bottom=0.06, top=0.91, right=.91)
    plt.subplots_adjust(hspace=0.44)

    plt.savefig(out_fname)

    return
