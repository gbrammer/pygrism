import os
import pyfits
import numpy as np
import glob
import shutil

import matplotlib.pyplot as plt

USE_PLOT_GUI=False

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from pyraf import iraf
from iraf import iraf

import threedhst
import threedhst.eazyPy as eazy
import threedhst.catIO as catIO
import unicorn

import re

noNewLine = '\x1b[1A\x1b[1M'

root = None

def throughput():
    os.chdir('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER')
    
    xg141, yg141 = np.loadtxt('g141.dat', unpack=True)
    xf140, yf140 = np.loadtxt('f140w.dat', unpack=True)
    xf814, yf814 = np.loadtxt('f814w.dat', unpack=True)
    xg800l, yg800l = np.loadtxt('g800l.dat', unpack=True)

    fig = unicorn.catalogs.plot_init(square=True, xs=8, aspect=1./3, left=0.12)
    
    plt.plot(xg141, yg141, color='black', linewidth=2, alpha=0.5)
    plt.fill(xg141, yg141, color='red', linewidth=2, alpha=0.1)
    plt.plot(xf140, yf140, color='black', linewidth=2, alpha=0.7)
    
    plt.plot(xg800l, yg800l, color='black', linewidth=2, alpha=0.5)
    plt.fill(xg800l, yg800l, color='blue', linewidth=2, alpha=0.1)
    plt.plot(xf814, yf814, color='black', linewidth=2, alpha=0.7)
    
    

    em_lines = [3727, 4861, 5007, 6563.]
    offset = np.array([0,-0.05,0,0])
    offset = 0.25+np.array([-0.15,-0.1,0.02,-0.1])

    em_names = ['[OII]',r'H$\beta$','[OIII]',r'H$\alpha$']
    
    dlam = 25
    zi = 1
    
    show_spectra = False
    colors=['blue','green','red']    
    if show_spectra:
      for zi in [1,2,3]:
        sedx, sedy = np.loadtxt('templates/EAZY_v1.0_lines/eazy_v1.0_sed4_nolines.dat', unpack=True)
        sedy *= 1.*sedy.max()
        dl = dlam/(1+zi)
        for em_line in em_lines:
            em_gauss = 1./np.sqrt(2*np.pi*dl**2)*np.exp(-1*(sedx-em_line)**2/2/dl**2)
            sedy += em_gauss/em_gauss.max()*0.6

        plt.plot(sedx*(1+zi), sedy*0.4+0.5, color=colors[zi-1], alpha=0.7, linewidth=2)
        plt.text(5500.,1.18-zi*0.13,r'$z=%d$' %(zi), color=colors[zi-1], fontsize=11)
        
      for i in range(4):
        plt.text(em_lines[i]*(1+1), 1+offset[i], em_names[i], horizontalalignment='center', fontsize=10)
    
    show_continuous = True
    if show_continuous:
        em_lines = [3727, 5007, 6563.]
        zgrid = np.arange(1000)/1000.*4
        for line in em_lines:
            plt.plot(line*(1+zgrid), zgrid/4.*0.8+0.5, linewidth=2, alpha=0.5, color='black')
        for zi in [0,1,2,3]:
            plt.plot([0.1,2.e4],np.array([zi,zi])/4.*0.8+0.5, linestyle='--', color='black', alpha=0.2)
            
    
    plt.text(5800, 0.08,'G800L',rotation=33., color='black', alpha=0.7)
    plt.text(5800, 0.08,'G800L',rotation=33., color='blue', alpha=0.4)

    plt.text(7100, 0.03,'F814W',rotation=80., color='black', alpha=0.9)

    plt.text(1.115e4, 0.17,'G141',rotation=15., color='black', alpha=0.7)
    plt.text(1.115e4, 0.17,'G141',rotation=15., color='red', alpha=0.4)

    plt.text(1.21e4, 0.03,'F140W',rotation=88., color='black', alpha=0.9)

    
    plt.xlim(4500, 1.79e4)
    plt.ylim(0,1.4)
    plt.xlabel(r'$\lambda$')
    plt.ylabel('throughput')
    
    fig.savefig('throughput.pdf')
    
def orbit_structure():
    """
    Show the POSTARG offsets in WFC3 / ACS
    """
    
    os.chdir('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER')
    
    fig = unicorn.catalogs.plot_init(square=True, xs=5, aspect=1, left=0.12)
    ax = fig.add_subplot(111)
    
    a11 = 0.1355
    b10 = 0.1211 # arcsec / pix, from instrument HB
    
    #dxs = np.array([0,-20,-13,7]) + np.int(np.round(xsh[0]))*0
    #dys = np.array([0,-7,-20,-13]) + np.int(np.round(ysh[0]))*0
    
    xpostarg = np.array([0, 1.355, 0.881, -0.474])
    ypostarg = np.array([0, 0.424, 1.212, 0.788])
    
    xoff = xpostarg/a11
    yoff = ypostarg/b10
        
    ax.plot(xoff, yoff, marker='o', markersize=10, color='red', alpha=0.8, zorder=10)
    
    if 1 == 1:
        for i in range(4):
            ax.text(xoff[i], yoff[i]+0.5, 'F140W + G141', horizontalalignment='center', backgroundcolor='white', zorder=20)
            
    ax.set_xlabel(r'$x$ offset [pix]')
    ax.set_ylabel(r'$y$ offset [pix]')

    scale = 4
    x0 = -2.9
    y0 = -5.5
    
    ax.fill(np.array([0,1,1,0])*scale+x0, np.array([0,0,1,1])*scale+y0, color='white', zorder=10)
    ax.fill(np.array([0,1,1,0])*scale+x0, np.array([0,0,1,1])*scale+y0, color='black', alpha=0.1, zorder=11)
    ax.plot(np.array([0.5,0.5])*scale+x0, np.array([0,1])*scale+y0, color='black', alpha=0.2, zorder=12)
    ax.plot(np.array([0,1])*scale+x0, np.array([0.5,0.5])*scale+y0, color='black', alpha=0.2, zorder=12)
    
    ax.plot(np.abs(xoff-np.cast[int](xoff))*scale+x0, np.abs(yoff-np.cast[int](yoff))*scale+y0, marker='o', markersize=10, color='red', alpha=0.8, zorder=13)
    ax.text(x0+scale/2., y0-1, 'WFC3 Primary', horizontalalignment='center')
    
    #plt.xlim(-5,11)
    #plt.ylim(-5,11)
    
    #### ACS:
    # XPOS = x*a11 + y*a10
    # YPOS = x*b11 + y*b10
    # 
    #       a10    a11      b10     b11
    # WFC: 0.0000   0.0494  0.0494  0.0040
    a10, a11, b10, b11 =  0.0000,0.0494,0.0494,0.0040
    #xoff = np.cumsum(xpostarg)
    #yoff = np.cumsum(ypostarg)

    acsang = 45.
    acsang = 92.16- -45.123
    xpos_acs, ypos_acs = threedhst.utils.xyrot(xpostarg, ypostarg, acsang)
    xpix_acs = xpos_acs / a11
    ypix_acs = (ypos_acs-xpix_acs*b11)/b10

    x0 = 5.5
    #y0 = -4.5
    
    ax.fill(np.array([0,1,1,0])*scale+x0, np.array([0,0,1,1])*scale+y0, color='white', zorder=10)
    ax.fill(np.array([0,1,1,0])*scale+x0, np.array([0,0,1,1])*scale+y0, color='black', alpha=0.1, zorder=11)
    ax.plot(np.array([0.5,0.5])*scale+x0, np.array([0,1])*scale+y0, color='black', alpha=0.2, zorder=12)
    ax.plot(np.array([0,1])*scale+x0, np.array([0.5,0.5])*scale+y0, color='black', alpha=0.2, zorder=12)

    ax.plot(np.abs(xpix_acs-np.cast[int](xpix_acs))*scale+x0, np.abs(ypix_acs-np.cast[int](ypix_acs))*scale+y0, marker='o', markersize=10, color='blue', alpha=0.8, zorder=13)
    #ax.plot(np.array([0,0.5,1,0.5])*scale+x0, np.array([0,0.5,0.5,1])*scale+y0, marker='o', marker='None', color='blue', linestyle='--', alpha=0.6, zorder=13)
    ax.plot(np.array([0,0.5,0.5,1])*scale+x0, np.array([0,1,0.5,0.5])*scale+y0, marker='o', marker='None', color='blue', linestyle='--', alpha=0.6, zorder=13)
    
    ax.text(x0+scale/2., y0-1, 'ACS Parallel', horizontalalignment='center')
    
    #plt.grid(alpha=0.5, zorder=1, markevery=5)
    
    from matplotlib.ticker import MultipleLocator, FormatStrFormatter

    ax.set_xlim(-5.9,12.5)
    #ax.set_ylim(-5.9,12.5)
    ax.set_ylim(-6.9,11.5)

    majorLocator   = MultipleLocator(5)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator   = MultipleLocator(1)

    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.xaxis.grid(alpha=0.5, zorder=1, which='major')
    ax.xaxis.grid(alpha=0.2, zorder=1, which='minor')

    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_minor_locator(minorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)
    ax.yaxis.grid(alpha=0.5, zorder=1, which='major')
    ax.yaxis.grid(alpha=0.2, zorder=1, which='minor')
        
    fig.savefig('dither_box.pdf')
    
def exptimes():
    """
    Extract the range of exposure times from the formatted Phase-II files
    """
    os.system('grep F814W 12???.pro   |grep " S " > f814w.exptime')
    os.system('grep G800L 12???.pro   |grep " S " > g800l.exptime')
    os.system('grep F140W *.pro |grep MULTIAC |grep NSAMP > f140w.exptime')
    os.system('grep G141 *.pro |grep MULTIAC |grep NSAMP > g141.exptime')
    
    ### G141
    fp = open('g141.exptime')
    lines = fp.readlines()
    fp.close()
    nsamp = []
    object = []
    for line in lines:
        nsamp.append(line.split('NSAMP=')[1][0:2])
        object.append(line.split()[1])
        
    expsamp = np.zeros(17)
    expsamp[12] = 1002.94
    expsamp[13] = 1102.94
    expsamp[14] = 1202.94
    expsamp[15] = 1302.94
    expsamp[16] = 1402.94
    
    nsamp = np.cast[int](nsamp)
    nsamp+=1 ### this seems to be the case for all actual observations !!
    objects = object[::4]
    NOBJ = len(nsamp)/4
    texp = np.zeros(NOBJ)
    for i in range(NOBJ):
        texp[i] = np.sum(expsamp[nsamp[i*4:(i+1)*4]])
        print objects[i], texp[i]
        
    print 'G141:  %.1f - %.1f' %(texp.min(), texp.max())
    
def spectral_features():
    wmin, wmax = 1.1e4, 1.65e4
    
    print '%-8s  %.1f -- %.1f' %('Halpha', wmin/6563.-1, wmax/6563.-1)
    print '%-8s  %.1f -- %.1f' %('OIII', wmin/5007.-1, wmax/5007.-1)
    print '%-8s  %.1f -- %.1f' %('OII', wmin/3727.-1, wmax/3727.-1)
    print '%-8s  %.1f -- %.1f' %('4000', wmin/4000.-1, wmax/4000.-1)

    wmin, wmax = 0.55e4, 1.0e4
    print '\n\nACS\n\n'
    print '%-8s  %.1f -- %.1f' %('Halpha', wmin/6563.-1, wmax/6563.-1)
    print '%-8s  %.1f -- %.1f' %('OIII', wmin/5007.-1, wmax/5007.-1)
    print '%-8s  %.1f -- %.1f' %('OII', wmin/3727.-1, wmax/3727.-1)
    print '%-8s  %.1f -- %.1f' %('4000', wmin/4000.-1, wmax/4000.-1)

def aXe_model():
    import copy
    import scipy.ndimage as nd
    
    os.chdir('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER')
    
    dir = pyfits.open('/research/HST/GRISM/3DHST/GOODS-S/PREP_FLT/UDF-F140W_drz.fits')
    gri = pyfits.open('/research/HST/GRISM/3DHST/GOODS-S/PREP_FLT/UDF-G141_drz.fits.gz')
    mod = pyfits.open('/research/HST/GRISM/3DHST/GOODS-S/PREP_FLT/UDF-FC-G141CONT_drz.fits.gz')

    #### rotate all the images so that dispersion axis is along X
    angle = gri[1].header['PA_APER']#+180
    direct = nd.rotate(dir[1].data, angle, reshape=False)
    grism = nd.rotate(gri[1].data, angle, reshape=False)
    model = nd.rotate(mod[1].data, angle, reshape=False)
    
    
    xc, yc = 1877, 2175
    NX, NY = 1270, 365
    aspect = 3.*NY/NX
    
    xc, yc = 1731, 977
    NX, NY = 882, 467
    
    aspect = 1.*NY/NX
    
    plt.gray()
    
    plt.rcParams['lines.linewidth'] = 2
    
    fig = unicorn.catalogs.plot_init(square=True, xs=8, aspect=aspect, left=0.12)
    
    fig.subplots_adjust(wspace=0.0,hspace=0.0,left=0.01,
                        bottom=0.015,right=0.99,top=0.985)
    
    fs1 = 15 ### Font size of label
    xlab, ylab = 0.04*NX/3., NY-0.02*NY
    
    ax = fig.add_subplot(221)
    ax.imshow(0-direct[yc-NY/2:yc+NY/2, xc-NX/2:xc+NX/2], vmin=-0.2, vmax=0.02, interpolation='nearest')
    ax.set_yticklabels([]); ax.set_xticklabels([])
    xtick = ax.set_xticks([0,NX]); ytick = ax.set_yticks([0,NY])
    ax.text(xlab, ylab, 'a) Direct F140W', fontsize=fs1, backgroundcolor='white', verticalalignment='top')

    #ax.text(xlab, ylab, r'$%d\times\ $$%d^{\prime\prime}$' %(NX*0.06, NY*0.06), fontsize=18, backgroundcolor='white', verticalalignment='top')
    
    ax = fig.add_subplot(222)
    ax.imshow(0-grism[yc-NY/2:yc+NY/2, xc-NX/2:xc+NX/2], vmin=-0.04, vmax=0.004, interpolation='nearest')
    ax.set_yticklabels([]); ax.set_xticklabels([])
    xtick = ax.set_xticks([0,NX]); ytick = ax.set_yticks([0,NY])
    ax.text(xlab, ylab, 'b) Grism G141', fontsize=fs1, backgroundcolor='white', verticalalignment='top')

    ax = fig.add_subplot(223)
    diff = grism-model
        
    ### Flag em lines and 0th order
    dy0 = 20
    
    emx, emy = [223, 272, 487, 754, 520, 850, 565, 558, 51, 834, 345, 495], [122, 189, 83, 240, 148, 124, 336, 418, 338, 225, 197, 268]
    ax.plot(np.array(emx)+(xc-1731), np.array(emy)-dy0+(yc-977), marker='^', markersize=5, linestyle='None', color='green', alpha=0.9)
    
    zx, zy = [301, 393, 648], [183, 321, 446]
    ax.plot(np.array(zx)+(xc-1731), np.array(zy)-dy0+(yc-977), marker='^', markersize=5, linestyle='None', color='red', alpha=0.9)

    ax.text(0.04*NX/3., 0.02*NY, 'Em.', fontsize=fs1*0.8, backgroundcolor='white', verticalalignment='bottom', color='green')
    ax.text(0.3*NX/3., 0.02*NY, r'0th', fontsize=fs1*0.8, backgroundcolor='white', verticalalignment='bottom', color='red')
    
    ax.imshow(0-diff[yc-NY/2:yc+NY/2, xc-NX/2:xc+NX/2], vmin=-0.02, vmax=0.002, interpolation='nearest')
    ax.set_yticklabels([]); ax.set_xticklabels([])
    xtick = ax.set_xticks([0,NX]); ytick = ax.set_yticks([0,NY])
    ax.text(xlab, ylab, r'd) Grism$-$model', fontsize=fs1, backgroundcolor='white', verticalalignment='top')
    
    ax = fig.add_subplot(224)
    ax.imshow(0-model[yc-NY/2:yc+NY/2, xc-NX/2:xc+NX/2], vmin=-0.04, vmax=0.004, interpolation='nearest')
    ax.set_yticklabels([]); ax.set_xticklabels([])
    xtick = ax.set_xticks([0,NX]); ytick = ax.set_yticks([0,NY])
    ax.text(xlab, ylab, r'c) aXe Model', fontsize=fs1, backgroundcolor='white', verticalalignment='top')
    
    fig.savefig('grism_model.pdf')
    
def sync():
    pass
    """
paths="RAW HTML/scripts PREP_FLT"
dirs="AEGIS COSMOS ERS GOODS-N GOODS-S SN-GEORGE SN-MARSHALL SN-PRIMO UDS"
for dir in $dirs; do 
    mkdir ${dir}
    mkdir ${dir}/HTML
    for path in $paths; do 
        # du -sh ${dir}/${path}
        mkdir ${dir}/${path}
        rsync -avz --progress $UNICORN:/3DHST/Spectra/Work/${dir}/${path} ${dir}/${path} 
    done
done


    """
def all_pointings():
    pointings(ROOT='GOODS-SOUTH')
    pointings(ROOT='COSMOS')
    pointings(ROOT='AEGIS')
    pointings(ROOT='UDS')
    pointings(ROOT='GOODS-N')

def all_pointings_width():
    from unicorn.survey_paper import pointings
    
    pointings(ROOT='GOODS-SOUTH', width=7, corner='ll')
    pointings(ROOT='COSMOS', width=6, corner='lr')
    pointings(ROOT='AEGIS', width=7, corner='ll')
    pointings(ROOT='UDS', width=9, corner='lr')
    pointings(ROOT='GOODS-N', width=6, corner='ur')
        
def pointings(ROOT='GOODS-SOUTH', width=None, corner='lr'):
    """ 
    Make a figure showing the 3D-HST pointing poisitions, read from region files
    """
    import unicorn.survey_paper as sup
    
    plt.rcParams['lines.linewidth'] = 0.3
    wfc3_color = 'blue'
    acs_color = 'green'
    
    os.chdir(unicorn.GRISM_HOME+'ANALYSIS/SURVEY_PAPER')
    yticklab = None
    
    dx_ref = (53.314005633802822-52.886197183098595)*np.cos(-27.983151830808076/360*2*np.pi)
    CANDELS_PATH = '/research/HST/GRISM/3DHST/REGIONS/CANDELS/'
    candels_files = []
    candels_alpha = 0.3
    candels_color = '0.1'
    
    
    #### GOODS-S
    if ROOT=='GOODS-SOUTH':
        x0, x1 = 53.314005633802822,  52.886197183098595
        y0, y1 = -27.983151830808076, -27.654474431818176
        xticklab = [r'$3^\mathrm{h}33^\mathrm{m}00^\mathrm{s}$', r'$3^\mathrm{h}32^\mathrm{m}30^\mathrm{s}$', r'$3^\mathrm{h}32^\mathrm{m}00^\mathrm{s}$']
        xtickv = [degrees(3,33,00, hours=True), degrees(3,32,30, hours=True), degrees(3,32,00, hours=True)]
        yticklab = [r'$-27^\circ40^\prime00^{\prime\prime}$', r'$45^\prime00^{\prime\prime}$', r'$-27^\circ50^\prime00^{\prime\prime}$', r'$55^\prime00^{\prime\prime}$']
        ytickv = [degrees(-27, 40, 00, hours=False), degrees(-27, 45, 00, hours=False), degrees(-27, 50, 00, hours=False), degrees(-27, 55, 00, hours=False)]
        candels_files = glob.glob(CANDELS_PATH+'/GOODS-S*reg')
        candels_files.extend(glob.glob(CANDELS_PATH+'/GOODS-W*reg'))
    
    #### COSMOS
    if ROOT=='COSMOS':
        x1, x0 = 149.99120563380279, 150.23823661971829
        y0, y1 = 2.1678109478476815, 2.5996973302980129
        xticklab = [r'$10^\mathrm{h}00^\mathrm{m}30^\mathrm{s}$', r'$00^\mathrm{m}00^\mathrm{s}$']
        xtickv = [degrees(10,00,30, hours=True), degrees(10,00,00, hours=True)]
        yticklab = [r'$+2^\circ15^\prime00^{\prime\prime}$', r'$25^\prime00^{\prime\prime}$', r'$35^\prime00^{\prime\prime}$']
        ytickv = [degrees(02, 15, 00, hours=False), degrees(02, 25, 00, hours=False), degrees(02, 35, 00, hours=False)]
        candels_files = glob.glob(CANDELS_PATH+'/COSMOS*reg')
    
    #### AEGIS
    if ROOT=='AEGIS':
        x1, x0 = 214.49707154104345, 215.12704734584406
        y0, y1 = 52.680946433013482, 53.01597137966467
        xticklab = [r'$18^\mathrm{m}00^\mathrm{s}$', r'$14^\mathrm{h}19^\mathrm{m}00^\mathrm{s}$', r'$20^\mathrm{m}00^\mathrm{s}$']
        xtickv = [degrees(14,18,00, hours=True), degrees(14,19,00, hours=True), degrees(14,20,00, hours=True)]
        yticklab = [r'$+52^\circ45^\prime00^{\prime\prime}$', r'$50^\prime00^{\prime\prime}$', r'$55^\prime00^{\prime\prime}$']
        ytickv = [degrees(52, 45, 00, hours=False), degrees(52, 50, 00, hours=False), degrees(52, 55, 00, hours=False)]
        candels_files = glob.glob(CANDELS_PATH+'/EGS*reg')
    
    #### UDS
    if ROOT=='UDS':
        x1, x0 = 34.116935194128146, 34.51871547581829
        y0, y1 = -5.2957542206957582, -5.0834327182123147+2./3600
        xticklab = [r'$18^\mathrm{m}00^\mathrm{s}$', r'$2^\mathrm{h}17^\mathrm{m}30^\mathrm{s}$', r'$17^\mathrm{m}00^\mathrm{s}$', r'$16^\mathrm{m}30^\mathrm{s}$']
        xtickv = [degrees(2,18,00, hours=True), degrees(2,17,30, hours=True), degrees(2,17,00, hours=True), degrees(2,16,30, hours=True)]
        yticklab = [r'$05^\prime00^{\prime\prime}$', r'$-5^\circ10^\prime00^{\prime\prime}$', r'$15^\prime00^{\prime\prime}$']
        ytickv = [degrees(-5, 05, 00, hours=False), degrees(-5, 10, 00, hours=False), degrees(-5, 15, 00, hours=False)]
        candels_files = glob.glob(CANDELS_PATH+'/UDS*reg')
    
    #### GOODS-N
    if ROOT=='GOODS-N':
        wfc3_color = 'orange'
        acs_color = None
        x1, x0 = 188.9139017749491, 189.44688055895648
        y0, y1 = 62.093791549511998, 62.384068625281309
        xticklab = [r'$12^\mathrm{h}37^\mathrm{m}30^\mathrm{s}$', r'$37^\mathrm{m}00^\mathrm{s}$', r'$36^\mathrm{m}30^\mathrm{s}$', r'$36^\mathrm{m}00^\mathrm{s}$']
        xtickv = [degrees(12,37,30, hours=True), degrees(12,37,00, hours=True), degrees(12,36,30, hours=True), degrees(12,36,00, hours=True)]
        yticklab = [r'$+62^\circ10^\prime00^{\prime\prime}$', r'$15^\prime00^{\prime\prime}$', r'$20^\prime00^{\prime\prime}$']
        ytickv = [degrees(62, 10, 00, hours=False), degrees(62, 15, 00, hours=False), degrees(62, 20, 00, hours=False)]
        candels_files = glob.glob(CANDELS_PATH+'/GOODSN-OR*reg')
        candels_files.extend(glob.glob(CANDELS_PATH+'/GOODSN-SK*reg'))
        
    #### Make square for given plot dimensions
    dx = np.abs(x1-x0)*np.cos(y0/360*2*np.pi)
    dy = (y1-y0)
    
    if width is None:
        width = 7*dx/dx_ref
    
    print '%s: plot width = %.2f\n' %(ROOT, width)
        
    fig = unicorn.catalogs.plot_init(square=True, xs=width, aspect=dy/dx)
    #fig = unicorn.catalogs.plot_init(square=True)
    
    ax = fig.add_subplot(111)
    
    polys = []
    for file in candels_files:
        fp = open(file)
        lines = fp.readlines()
        fp.close()
        #
        polys.append(sup.polysplit(lines[1], get_shapely=True))
        #fi = ax.fill(wfcx, wfcy, alpha=candels_alpha, color=candels_color)
    
    sup.polys = polys
    
    un = polys[0]
    for pp in polys[1:]:
        un = un.union(pp)
    
    if un.geometryType() is 'MultiPolygon':
        for sub_poly in un.geoms:
            x,y = sub_poly.exterior.xy
            ax.plot(x,y, alpha=candels_alpha, color=candels_color, linewidth=1)
            ax.fill(x,y, alpha=0.1, color='0.7')
    else:        
        x,y = un.exterior.xy
        ax.plot(x,y, alpha=candels_alpha, color=candels_color, linewidth=1)
        ax.fill(x,y, alpha=0.1, color='0.7')
    
    files=glob.glob(unicorn.GRISM_HOME+'REGIONS/'+ROOT+'-[0-9]*reg')
    wfc3_polys = []
    for file in files:
        #
        field = re.split('-[0-9]', file)[0]
        pointing = file.split(field+'-')[1].split('.reg')[0]
        fp = open(file)
        lines = fp.readlines()
        fp.close()
        #
        wfc3_polys.append(sup.polysplit(lines[1], get_shapely=True)) 
        #
        wfcx, wfcy = sup.polysplit(lines[1])
        fi = ax.fill(wfcx, wfcy, alpha=0.2, color=wfc3_color)
        #
        if acs_color is not None:
            acsx1, acsy1 = sup.polysplit(lines[2])
            acsx2, acsy2 = sup.polysplit(lines[3])
            #
            fi = ax.fill(acsx1, acsy1, alpha=0.05, color=acs_color)
            fi = ax.fill(acsx2, acsy2, alpha=0.05, color=acs_color)
            pl = ax.plot(acsx1, acsy1, alpha=0.1, color=acs_color)
            pl = ax.plot(acsx2, acsy2, alpha=0.1, color=acs_color)
        #
        xoff, yoff = 0.0, 0.0
        if ROOT=='GOODS-SOUTH':
            #print pointing
            if pointing == '36':
                xoff, yoff = 0.002,0.0075
            if pointing == '37':
                xoff, yoff = -0.005,-0.007
            if pointing == '38':
                xoff, yoff = 0.007,-0.007
        #    
        te = ax.text(np.mean(wfcx[:-1])+xoff, np.mean(wfcy[:-1])+yoff, pointing, va='center', ha='center', fontsize=13)
    
    #### Get field area from full WFC3 polygons
    un = wfc3_polys[0]
    for pp in wfc3_polys[1:]:
        un = un.union(pp)
        
    if un.geometryType() is 'MultiPolygon':
        total_area = 0
        xavg, yavg, wht = 0, 0, 0
        for sub_poly in un.geoms:
            area_i = sub_poly.area*np.cos(y0/360.*2*np.pi)
            total_area += area_i
            x,y = sub_poly.exterior.xy
            xavg += np.mean(x)*area_i**2
            yavg += np.mean(y)*area_i**2
            wht += area_i**2
            #ax.plot(x,y, alpha=0.8, color='orange', linewidth=1)
        xavg, yavg = xavg/wht, yavg/wht
    else:        
        total_area = un.area*np.cos(y0/360.*2*np.pi)
        x,y = un.exterior.xy
        #ax.plot(x,y, alpha=0.8, color='orange', linewidth=1)
        xavg, yavg = np.mean(x), np.mean(y)
    
    #plt.plot([xavg,xavg],[yavg,yavg], marker='x', markersize=20)
    
    #    
    if yticklab is not None:
        ax.set_xticklabels(xticklab)
        xtick = ax.set_xticks(xtickv)
        ax.set_yticklabels(yticklab)
        ytick = ax.set_yticks(ytickv)
    
    ax.set_xlabel(r'$\alpha$')
    ax.set_ylabel(r'$\delta$')
    
    fsi = '20'
    
    if corner=='lr':
        ax.text(0.95, 0.05,r'$\mathit{%s}$' %(ROOT),
            horizontalalignment='right',
            verticalalignment='bottom',
            transform = ax.transAxes, fontsize=fsi)
    #
    if corner=='ll':
        ax.text(0.05, 0.05,r'$\mathit{%s}$' %(ROOT),
            horizontalalignment='left',
            verticalalignment='bottom',
            transform = ax.transAxes, fontsize=fsi)
    #
    if corner=='ur':
        ax.text(0.95, 0.95,r'$\mathit{%s}$' %(ROOT),
            horizontalalignment='right',
            verticalalignment='top',
            transform = ax.transAxes, fontsize=fsi)
    #
    if corner=='ul':
        ax.text(0.05, 0.95,r'$\mathit{%s}$' %(ROOT),
            horizontalalignment='left',
            verticalalignment='top',
            transform = ax.transAxes, fontsize=fsi)
    
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    
    # print 'RA  - ', hexagesimal(x0), hexagesimal(x1)
    # print 'Dec - ', hexagesimal(y0, hours=False), hexagesimal(y1, hours=False)
    print 'RA  - ', hexagesimal(xavg)
    print 'Dec - ', hexagesimal(yavg, hours=False)
    print 'Area: %.1f\n' %(total_area*3600.)
    
    plt.savefig('%s_pointings.pdf' %(ROOT))

def get_UDF_center():
    file='/research/HST/GRISM/3DHST/REGIONS/GOODS-SOUTH-38.reg'
    field = re.split('-[0-9]', file)[0]
    pointing = file.split(field+'-')[1].split('.reg')[0]
    fp = open(file)
    lines = fp.readlines()
    fp.close()
    #
    px, py = sup.polysplit(lines[1], get_shapely=False)
    print 'UDF: ', hexagesimal(np.mean(px[:-1]), hours=True), hexagesimal(np.mean(py[:-1]), hours=False)
    
def degrees(deg, min, sec, hours=True):
    
    adeg = np.abs(deg)
    degrees = adeg + min/60. + sec/3600.
    if deg < 0:
        degrees *= -1
    
    if hours:
        degrees *= 360./24
        
    return degrees
    
def hexagesimal(degrees, hours=True, string=True):
    if hours:
        degrees *= 24/360.
    
    if degrees < 0:
        sign = -1
        si = '-'
    else:
        sign = 1
        si = ''
        
    degrees = np.abs(degrees)
    
    deg = np.int(degrees)
    min = np.int((degrees-deg)*60)
    sec = (degrees-deg-min/60.)*3600
    
    if string:
        return '%s%02d:%02d:%05.2f' %(si, deg, min, sec)
    else:
        return sign*deg, min, sec

def polysplit(region='polygon(150.099223,2.391097,150.086084,2.422515,150.050573,2.407277,150.064586,2.376241)', get_shapely=False):
    
    spl = region[region.find('(')+1:region.find(')')].split(',')
    px = spl[0::2]
    py = spl[1::2]
    px.append(px[0])
    py.append(py[0])
    px, py = np.cast[float](px), np.cast[float](py)
    
    if get_shapely:
        from shapely.geometry import Polygon
        list = []
        for i in range(len(px)):
            list.append((px[i], py[i]))
        
        poly = Polygon(tuple(list))
        return poly
    else:
        return px, py
#
def demo_background_subtract(root='COSMOS-13'):
    """
    Make a figure demonstrating the background subtraction of the grism images
    """
    import threedhst
    import threedhst.prep_flt_files
    import threedhst.grism_sky as bg
    
    import unicorn
    import unicorn.survey_paper as sup
    import pyfits
    import iraf
    
    path = unicorn.analysis.get_grism_path(root)
    os.chdir(path)
    if not os.path.exists('EXAMPLE'):
        os.system('mkdir EXAMPLE')
    
    os.chdir('EXAMPLE')
    files = glob.glob('../PREP_FLT/%s-G141*' %(root))
    files.append('../PREP_FLT/%s-F140W_tweak.fits' %(root))
    
    for file in files: 
        if 'drz.fits' not in file:
            os.system('cp %s .' %(file))
            print file
    
    threedhst.process_grism.fresh_flt_files(root+'-G141_asn.fits')
    asn = threedhst.utils.ASNFile(root+'-G141_asn.fits')
    flt = pyfits.open(asn.exposures[0]+'_flt.fits')
    angle = flt[1].header['PA_APER']
    
    #### First run on uncorrected images
    threedhst.prep_flt_files.startMultidrizzle(root+'-G141_asn.fits', 
            use_shiftfile=True, skysub=False,
            final_scale=0.128254, pixfrac=0.8, driz_cr=True,
            updatewcs=True, median=True, clean=True, final_rot=angle)
        
    os.system('mv %s-G141_drz.fits %s-G141_drz_first.fits' %(root, root))
    
    sup.root = root
    sup.first_prof = []
    for exp in asn.exposures:
        xp, yp = threedhst.grism_sky.profile(exp+'_flt.fits', flatcorr=False, biweight=True)
        sup.first_prof.append(yp)
    
    # for i,exp in enumerate(asn.exposures):
    #     plt.plot(xp, prof[i])
        

    #### Now divide by the flat
    threedhst.process_grism.fresh_flt_files(root+'-G141_asn.fits')
    sup.flat_prof = []
    for exp in asn.exposures:
        bg.remove_grism_sky(flt=exp+'_flt.fits', list=['sky_cosmos.fits', 'sky_goodsn_lo.fits', 'sky_goodsn_hi.fits', 'sky_goodsn_vhi.fits'],  path_to_sky = '../CONF/', out_path='./', verbose=False, plot=False, flat_correct=True, sky_subtract=False, second_pass=False, overall=False)
        xp, yp = threedhst.grism_sky.profile(exp+'_flt.fits', flatcorr=False, biweight=True)
        sup.flat_prof.append(yp)
    
    threedhst.prep_flt_files.startMultidrizzle(root+'-G141_asn.fits', 
            use_shiftfile=True, skysub=False,
            final_scale=0.128254, pixfrac=0.8, driz_cr=True,
            updatewcs=True, median=True, clean=True, final_rot=angle)

    os.system('mv %s-G141_drz.fits %s-G141_drz_flat.fits' %(root, root))
    
    #### Divide by the sky
    threedhst.process_grism.fresh_flt_files(root+'-G141_asn.fits')
    sup.sky_prof = []
    for exp in asn.exposures:
        print exp
        bg.remove_grism_sky(flt=exp+'_flt.fits', list=['sky_cosmos.fits', 'sky_goodsn_lo.fits', 'sky_goodsn_hi.fits', 'sky_goodsn_vhi.fits'],  path_to_sky = '../CONF/', out_path='./', verbose=False, plot=False, flat_correct=True, sky_subtract=True, second_pass=False, overall=False)
        xp, yp = threedhst.grism_sky.profile(exp+'_flt.fits', flatcorr=False, biweight=True)
        sup.sky_prof.append(yp)
    
    threedhst.prep_flt_files.startMultidrizzle(root+'-G141_asn.fits', 
            use_shiftfile=True, skysub=False,
            final_scale=0.128254, pixfrac=0.8, driz_cr=True,
            updatewcs=True, median=True, clean=True, final_rot=angle)

    os.system('mv %s-G141_drz.fits %s-G141_drz_sky.fits' %(root, root))

    #### Last pass along columns
    threedhst.process_grism.fresh_flt_files(root+'-G141_asn.fits')
    sup.final_prof = []
    for exp in asn.exposures:
        print exp
        bg.remove_grism_sky(flt=exp+'_flt.fits', list=['sky_cosmos.fits', 'sky_goodsn_lo.fits', 'sky_goodsn_hi.fits', 'sky_goodsn_vhi.fits'],  path_to_sky = '../CONF/', out_path='./', verbose=False, plot=False, flat_correct=True, sky_subtract=True, second_pass=True, overall=True)
        xp, yp = threedhst.grism_sky.profile(exp+'_flt.fits', flatcorr=False, biweight=True)
        sup.final_prof.append(yp)
    
    threedhst.prep_flt_files.startMultidrizzle(root+'-G141_asn.fits', 
            use_shiftfile=True, skysub=False,
            final_scale=0.128254, pixfrac=0.8, driz_cr=True,
            updatewcs=True, median=True, clean=True, final_rot=angle)
    
    # ##### Make segmentation images
    # run = threedhst.prep_flt_files.MultidrizzleRun(root+'-G141')
    # for i,exp in enumerate(asn.exposures):
    #     run.blot_back(ii=i, copy_new=(i is 0))
    #     threedhst.prep_flt_files.make_segmap(run.flt[i])
    
    os.system('mv %s-G141_drz.fits %s-G141_drz_final.fits' %(root, root))
    
    make_plot(root=root)
    
def make_background_demo(root='AEGIS-11', range1=(0.90,1.08), range2=(-0.02, 0.02)):
    import unicorn.survey_paper as sup
    
    if sup.root != root:
        print "Need to run sup.demo_background_subtract(root='%s')." %(root)
        
    path = unicorn.analysis.get_grism_path(root)
    os.chdir(path+'EXAMPLE')
    
    first = pyfits.open('%s-G141_drz_first.fits' %(root))
    flat = pyfits.open('%s-G141_drz_flat.fits' %(root))
    sky = pyfits.open('%s-G141_drz_sky.fits' %(root))
    final = pyfits.open('%s-G141_drz_final.fits' %(root))
    
    im_shape = first[1].data.shape
    sup.im_shape = im_shape
    
    med = threedhst.utils.biweight(sky[1].data, mean=True)
    
    ysize = 3.
    #fig = plt.figure(figsize=[ysize*im_shape[1]*1./im_shape[0]*4,ysize], dpi=100)
    
    
    top_panel = 0.2
    NPANEL = 4
    
    if USE_PLOT_GUI:
        fig = plt.figure(figsize=[ysize*im_shape[1]*1./im_shape[0]*NPANEL*(1-top_panel)/2,ysize*2],dpi=100)
    else:
        fig = Figure(figsize=[ysize*im_shape[1]*1./im_shape[0]*NPANEL*(1-top_panel)/2.,ysize*2], dpi=100)
    
    fig.subplots_adjust(wspace=0.02,hspace=0.02,left=0.02,
                        bottom=0.07,right=0.99,top=0.97)
    #
    
    plt.rcParams['lines.linewidth'] = 1
    
    vmin, vmax = -0.2, 0.1
    
    x0 = 0.005*2
    y0 = x0/2.
    dx = (1.-(NPANEL+1)*x0)/NPANEL*2
    
    top_panel/=2.
    
    #ax = fig.add_subplot(141)
    ax = fig.add_axes(((x0+(dx+x0)*0), y0+0.5, dx, 0.5-top_panel-y0))
    
    ax.imshow(0-(first[1].data-med), interpolation='nearest',aspect='auto',vmin=vmin-0.1,vmax=vmax+0.15)    
    sup.axis_imshow(ax, text='a)\ Raw')
    ax.text(0.12, 0.85, r'$\mathrm{%s}$' %(root), horizontalalignment='left', verticalalignment='center',
                 transform = ax.transAxes, color='black', fontsize=14)
    #
    #show_limits(ax, -(vmax+0.15)+med, -(vmin-0.1)+med)
    
    #### Show profiles
    ax = fig.add_axes(((x0+(dx+x0)*0), (0.5-top_panel)+0.5, dx, top_panel-2*y0))
    pp = sup.first_prof[0]*0.
    for i in range(4):
        #ax.plot(sup.first_prof[i])
        pp += sup.first_prof[i]
    ax.plot(pp/4., color='black')
    sup.axis_profile(ax, yrange=range1, text='a)\ Raw')
    
    #ax = fig.add_subplot(142)
    ax = fig.add_axes(((x0+(dx+x0)*1), y0+0.5, dx, 0.5-top_panel-y0))
    ax.imshow(0-(flat[1].data-med), interpolation='nearest',aspect='auto',vmin=vmin,vmax=vmax)    
    sup.axis_imshow(ax, text='b)\ Flat')
    #show_limits(ax, -vmax+med, -vmin+med)
    
    #### Show profiles
    ax = fig.add_axes(((x0+(dx+x0)*1), (0.5-top_panel)+0.5, dx, top_panel-2*y0))
    pp = sup.flat_prof[0]*0.
    for i in range(4):
        #ax.plot(sup.flat_prof[i])
        pp += sup.flat_prof[i]
    ax.plot(pp/4., color='black')
    sup.axis_profile(ax, yrange=range1, text='b)\ Flat')
    
    ###########
    #ax = fig.add_subplot(143)
    ax = fig.add_axes(((x0+(dx+x0)*0), y0, dx, 0.5-top_panel-y0))
    ax.imshow(0-(sky[1].data-med), interpolation='nearest',aspect='auto',vmin=vmin,vmax=vmax)    
    sup.axis_imshow(ax, text='c)\ Sky')
    #show_limits(ax, -vmax+med, -vmin+med)
    
    #### Show profiles
    ax = fig.add_axes(((x0+(dx+x0)*0), (0.5-top_panel), dx, top_panel-2*y0))
    pp = sup.sky_prof[0]*0.
    for i in range(4):
        #ax.plot(sup.sky_prof[i])
        pp += sup.sky_prof[i]
    ax.plot(pp/4., color='black')
    sup.axis_profile(ax, yrange=range1, text='c)\ Sky')
    
    #ax = fig.add_subplot(144)
    ax = fig.add_axes(((x0+(dx+x0)*1), y0, dx, 0.5-top_panel-y0))
    ax.imshow(0-(final[1].data), interpolation='nearest',aspect='auto',vmin=vmin,vmax=vmax)    
    sup.axis_imshow(ax, text='d)\ Final')
    #show_limits(ax, -vmax, -vmin)
    
    #### Show profiles
    ax = fig.add_axes(((x0+(dx+x0)*1), (0.5-top_panel), dx, top_panel-2*y0))
    pp = sup.final_prof[0]*0.
    for i in range(4):
        #ax.plot(sup.final_prof[i])
        pp += sup.final_prof[i]
    ax.plot(pp/4., color='black')
    sup.axis_profile(ax, yrange=range2, text='d)\ Final')
    
    outfile = '%s-G141_demo.pdf' %(root)
    
    if USE_PLOT_GUI:
        fig.savefig(outfile,dpi=100,transparent=False)
    else:
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure(outfile, dpi=100, transparent=False)

def show_limits(ax, vmin, vmax):
    ax.text(0.98, -0.02,r'$\mathrm{[%.1f,\ %.1f]}$' %(vmin, vmax),
                 horizontalalignment='right',
                 verticalalignment='top',
                 transform = ax.transAxes, color='black', fontsize=12)

def axis_profile(ax, yrange=None, prof=None, text=''):
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_xlim(0,1000)
    if yrange is not None:
        ax.set_ylim(yrange[0], yrange[1])
        ylimits = yrange
    else:
        ylimits = ax.get_ylim()
    
    #
    if text is  not '':
        ax.text(0.5, 0.06,r'$\mathrm{'+text+'}$',
                     horizontalalignment='center',
                     verticalalignment='bottom',
                     transform = ax.transAxes, color='black', fontsize=10)
    
    ax.text(0.98, 0.08,r'$\mathrm{[%.3f,\ %.3f]}$' %(ylimits[0], ylimits[1]),
                 horizontalalignment='right',
                 verticalalignment='bottom',
                 transform = ax.transAxes, color='black', fontsize=8)
    
        
def axis_imshow(ax, text='', shape=None):
    import numpy as np
    import unicorn.survey_paper as sup
    
    if shape is None:
        shape = sup.im_shape
    
    ax.set_yticklabels([])
    xtick = ax.set_xticks([0,shape[1]])
    ax.set_xticklabels([])
    ytick = ax.set_yticks([0,shape[0]])
    #
    # if text is  not '':
    #     ax.text(0.5, 1.02,r'$\mathrm{'+text+'}$',
    #                  horizontalalignment='center',
    #                  verticalalignment='bottom',
    #                  transform = ax.transAxes, color='black', fontsize=12)

def compare_sky():
    """
    Make a figure showing the aXe default and derived sky images.
    """
    import unicorn.survey_paper as sup
    
    sco = pyfits.open('../CONF/sky_cosmos.fits')
    shi = pyfits.open('../CONF/sky_goodsn_hi.fits')
    slo = pyfits.open('../CONF/sky_goodsn_lo.fits')
    svh = pyfits.open('../CONF/sky_goodsn_vhi.fits')
    
    shape = sco[0].data.shape
    
    figsize = 6
    fig = Figure(figsize=[figsize,figsize], dpi=200)
    #fig = plt.figure(figsize=[figsize,figsize], dpi=100)
    
    fig.subplots_adjust(wspace=0.02,hspace=0.02,left=0.02,
                        bottom=0.02,right=0.98,top=0.98)

    ####### COSMOS
    ax = fig.add_subplot(221)
    ax.imshow(sco[0].data, interpolation='nearest',aspect='auto',vmin=0.95,vmax=1.05)    
    sup.axis_imshow(ax, shape=shape)
    
    ax.fill_between([850,950],[50,50],[150,150], color='white', alpha=0.8)
    ax.text(900/1014., 100./1014,r'$\mathrm{a)}$', horizontalalignment='center', verticalalignment='center', transform = ax.transAxes, color='black', fontsize=12)
    
    ####### GOODS-N Lo
    ax = fig.add_subplot(222)
    ax.imshow(slo[0].data, interpolation='nearest',aspect='auto',vmin=0.95,vmax=1.05)    
    sup.axis_imshow(ax, shape=shape)

    ax.fill_between([850,950],[50,50],[150,150], color='white', alpha=0.8)
    ax.text(900/1014., 100./1014,r'$\mathrm{b)}$', horizontalalignment='center', verticalalignment='center', transform = ax.transAxes, color='black', fontsize=12)

    ####### GOODS-N Hi
    ax = fig.add_subplot(223)
    ax.imshow(shi[0].data, interpolation='nearest',aspect='auto',vmin=0.95,vmax=1.05)    
    sup.axis_imshow(ax, shape=shape)
    
    ax.fill_between([850,950],[50,50],[150,150], color='white', alpha=0.8)
    ax.text(900/1014., 100./1014,r'$\mathrm{c)}$', horizontalalignment='center', verticalalignment='center', transform = ax.transAxes, color='black', fontsize=12)

    ####### GOODS-N Very hi
    ax = fig.add_subplot(224)
    ax.imshow(svh[0].data, interpolation='nearest',aspect='auto',vmin=0.95,vmax=1.05)    
    sup.axis_imshow(ax, shape=shape)
    
    ax.fill_between([850,950],[50,50],[150,150], color='white', alpha=0.8)
    ax.text(900/1014., 100./1014,r'$\mathrm{d)}$', horizontalalignment='center', verticalalignment='center', transform = ax.transAxes, color='black', fontsize=12)
    
    #### Done
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure('sky_backgrounds.pdf', dpi=100, transparent=False)

def grism_flat_dependence():
    """
    Compute the higher order terms for the grism flat-field
    """
    
    import unicorn
    import threedhst
    
    # f140 = threedhst.grism_sky.flat_f140[1].data[5:-5, 5:-5]
    # 
    # flat = pyfits.open(unicorn.GRISM_HOME+'CONF/WFC3.IR.G141.flat.2.fits')
    # wmin, wmax = flat[0].header['WMIN'], flat[0].header['WMAX']
    # 
    # a0 = flat[0].data
    # 
    # lam = 1.1e4
    # x = (lam-wmin)/(wmax-wmin)
    # 
    # aX = a0*0.
    # for i,ext in enumerate(flat[1:]):
    #     print i
    #     aX += ext.data*x**(i+1)
        
    f105 = pyfits.open(os.getenv('iref')+'/uc72113oi_pfl.fits')[1].data[5:-5,5:-5]
    #f105 = pyfits.open(os.getenv('iref')+'/uc72113ni_pfl.fits')[1].data[5:-5,5:-5] # F098M
    f140 = pyfits.open(os.getenv('iref')+'/uc721143i_pfl.fits')[1].data[5:-5,5:-5]
    ref = 'F140W'
    f160 = pyfits.open(os.getenv('iref')+'/uc721145i_pfl.fits')[1].data[5:-5,5:-5]
    
    #### Narrow bands
    f140 = pyfits.open(os.getenv('iref')+'/PFL/uc72113si_pfl.fits')[1].data[5:-5,5:-5]
    REF = 'F127M'
    
    #f140 = pyfits.open(os.getenv('iref')+'/PFL/uc721140i_pfl.fits')[1].data[5:-5,5:-5]
    #f160 = pyfits.open(os.getenv('iref')+'/PFL/uc721146i_pfl.fits')[1].data[5:-5,5:-5]
    
    xs = 8
    fig = plt.figure(figsize=(xs,xs/3.), dpi=100)
    fig.subplots_adjust(wspace=0.01,hspace=0.01,left=0.01, bottom=0.01,right=0.99,top=0.99)        
    
    vmin, vmax = 0.95, 1.05
    ### put scale within the box
    NX = 100
    y0, y1 = 1014-1.5*NX, 1014-1*NX
    y0 -= NX; y1 -= NX
    
    ### F140W flat
    ax = fig.add_subplot(131)
    ax.imshow(f140, vmin=0.95, vmax=1.05, interpolation='nearest')
    ax.text(50,950, REF, verticalalignment='top', fontsize=14, backgroundcolor='white')
    ax.set_xlim(0,1014)
    ax.set_ylim(0,1014)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    ### F105W/F140W, with label
    ratio = f105/f140
    x0 = 300
    ratio[y0:y1,x0-2.5*NX:x0-1.5*NX] = vmin
    ratio[y0:y1,x0-1.5*NX:x0-0.5*NX] = (vmin+1)/2.
    ratio[y0:y1,x0-0.5*NX:x0+0.5*NX] = 1.
    ratio[y0:y1,x0+0.5*NX:x0+1.5*NX] = (vmax+1)/2.
    ratio[y0:y1,x0+1.5*NX:x0+2.5*NX] = vmax
    xbox = np.array([0,1,1,0,0])*NX
    ybox = np.array([0,0,1,1,0])*NX/2
    
    ax = fig.add_subplot(132)
    ax.imshow(ratio, vmin=0.95, vmax=1.05, interpolation='nearest')
    ax.plot(xbox+x0-0.5*NX, ybox+y1-0.5*NX, color='0.6', alpha=0.1)
    
    fs = 9
    ax.text(x0-2*NX, y0-0.5*NX, '%.2f' %(vmin), horizontalalignment='center', verticalalignment='center', fontsize=fs)
    ax.text(x0-0*NX, y0-0.5*NX, '%.2f' %(1), horizontalalignment='center', verticalalignment='center', fontsize=fs)
    ax.text(x0+2*NX, y0-0.5*NX, '%.2f' %(vmax), horizontalalignment='center', verticalalignment='center', fontsize=fs)

    ax.text(50,950, 'F105W / '+REF, verticalalignment='top', fontsize=14)
    ax.set_xlim(0,1014)
    ax.set_ylim(0,1014)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
        
    ### F160W/F140W
    ax = fig.add_subplot(133)
    ax.imshow(f160/f140, vmin=0.95, vmax=1.05, interpolation='nearest')
    ax.text(50,950, 'F160W / '+REF, verticalalignment='top', fontsize=14)
    ax.set_xlim(0,1014)
    ax.set_ylim(0,1014)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    fig.savefig('compare_flats.pdf')

def process_sky_background():
    import threedhst.catIO as catIO
    import re
    
    info = catIO.Readfile('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER/sky_background.dat')
    
    field = []
    for targ in info.targname:
        targ = targ.replace('GNGRISM','GOODS-NORTH-')
        field.append(re.split('-[1-9]',targ)[0].upper())
    
    field = np.array(field)   
    is_UDF = field == 'xxx'
    for i,targ in enumerate(info.targname):
        m = re.match('GOODS-SOUTH-3[4678]',targ)
        if m is not None:
            is_UDF[i] = True
            
    fields = ['AEGIS','COSMOS','GOODS-SOUTH','GOODS-NORTH','UDS']
    colors = ['red','blue','green','purple','orange']
    
    for i in range(len(fields)):
        match = (field == fields[i]) & (info.filter == 'G141')
        h = plt.hist(info.bg_mean[match], range=(0,5), bins=50, color=colors[i], alpha=0.5)
        bg = threedhst.utils.biweight(info.bg_mean[match], both=True)
        print '%-14s %.3f %.3f ' %(fields[i], bg[0], bg[1])
        
    match = is_UDF & (info.filter == 'G141')
    bg = threedhst.utils.biweight(info.bg_mean[match], both=True)
    print '%-14s %.3f %.3f ' %('HUDF09', bg[0], bg[1])
    
    plt.xlim(0,3.5)
    
def get_background_level():
    """
    Get the sky background levels from the raw FLT images, with an object and dq mask
    """
    
    xi, yi = np.indices((1014, 1014))
    DPIX = 300
    
    flat = pyfits.open(os.getenv('iref')+'uc721143i_pfl.fits')[1].data[5:-5,5:-5]
    
    fp = open(unicorn.GRISM_HOME+'ANALYSIS/sky_background.dat','w')
    fp.write('# file targname filter date_obs bg_mean bg_sigma\n')
    
    for path in ['AEGIS','COSMOS','GOODS-S','GOODS-N','UDS']:
        os.chdir(unicorn.GRISM_HOME+path+'/PREP_FLT')
        info = catIO.Readfile('files.info')
        print '\n\n%s\n\n' %(path)
        for ii, file in enumerate(info.file):
            file = file.replace('.gz','')
            print file
            #
            try:
                flt_raw = pyfits.open(threedhst.utils.find_fits_gz('../RAW/'+file))
                flt_fix = pyfits.open(threedhst.utils.find_fits_gz(file))
                seg = pyfits.open(threedhst.utils.find_fits_gz(file.replace('fits','seg.fits')))
            except:
                continue
            #    
            mask = (seg[0].data == 0) & ((flt_fix[3].data & (4+32+16+512+2048+4096)) == 0) & (np.abs(xi-507) < DPIX) & (np.abs(yi-507) < DPIX)
            #
            if info.filter[ii].startswith('G'):
                flt_raw[1].data /= flat
            #    
            background = threedhst.utils.biweight(flt_raw[1].data[mask], both=True)
            fp.write('%s   %16s   %5s   %s   %.3f %.3f\n' %(file, info.targname[ii], info.filter[ii], info.date_obs[ii], background[0], background[1]))
        
    fp.close()
    
def get_spec_signal_to_noise():
    """
    Measure the S/N directly from the spectrum of all objects.
    """
    
    fp = open(unicorn.GRISM_HOME+'ANALYSIS/spec_signal_to_noise.dat','w')
    fp.write('# object mag_auto flux_radius sig_noise n_bins\n')

    for path in ['AEGIS','COSMOS','GOODS-S','GOODS-N','UDS']:
        os.chdir(unicorn.GRISM_HOME+path)
        SPC_files = glob.glob('DRIZZLE_G141/*opt.SPC.fits')
        for file in SPC_files:
            pointing = os.path.basename(file).split('_2_opt')[0]
            #
            SPC = threedhst.plotting.SPCFile(file,axe_drizzle_dir='./')
            cat = threedhst.sex.mySexCat('DATA/%s_drz.cat' %(pointing))
            try:
                mag_auto = np.cast[float](cat.MAG_F1392W)
                flux_radius = np.cast[float](cat.FLUX_RADIUS)
            except:
                continue
            #
            for id in SPC._ext_map:
                print noNewLine+'%s_%05d' %(pointing, id)
                #
                spec = SPC.getSpec(id)
                mask = (spec.LAMBDA > 1.15e4) & (spec.LAMBDA < 1.6e4) & (spec.CONTAM/spec.FLUX < 0.1) & np.isfinite(spec.FLUX)
                if len(mask[mask]) > 1:
                    signal_noise = threedhst.utils.biweight(spec.FLUX[mask]/spec.FERROR[mask], mean=True)
                    mat = cat.id == id
                    fp.write('%s_%05d %8.3f %8.3f   %13.3e %-0d\n' %(pointing, id, mag_auto[mat][0], flux_radius[mat][0], signal_noise, len(mask[mask])))
                #   
                else:
                    continue
    
    fp.close()
          
def process_signal_to_noise():
    import threedhst.catIO as catIO
    import re

    os.chdir('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER/')
    
    info = catIO.Readfile('spec_signal_to_noise.dat')

    field = []
    for targ in info.object:
        targ = targ.replace('GNGRISM','GOODS-NORTH-')
        field.append(re.split('-[1-9]',targ)[0].upper())

    field = np.array(field)   
    
    snscale = 2.5 ### aXe errors too large
    
    ma = 'o'
    ms = 5
    
    ##### S/N vs mag.
    fig = unicorn.catalogs.plot_init(square=True, xs=5, aspect=1, left=0.12)
    fig.subplots_adjust(wspace=0.2,hspace=0.24,left=0.12, bottom=0.09,right=0.975,top=0.99)
    
    ax = fig.add_subplot(211)
    
    ff = (field == 'COSMOS') & (info.sig_noise > 0)
    ax.plot(info.mag_auto[ff], info.sig_noise[ff]*snscale, marker=ma, markersize=ms, color='red', alpha=0.1, linestyle='None')
    xm, ym, ys, ns = threedhst.utils.runmed(info.mag_auto[ff], info.sig_noise[ff]*snscale, NBIN=30)

    ff = (field == 'AEGIS') & (info.sig_noise > 0)
    ax.plot(info.mag_auto[ff], info.sig_noise[ff]*snscale, marker=ma, markersize=ms, color='blue', alpha=0.1, linestyle='None')

    ax.plot(xm,ym,color='white',linewidth=6,alpha=0.5)
    ax.plot(xm,ym,color='red',linewidth=3,alpha=0.9)

    xm, ym, ys, ns = threedhst.utils.runmed(info.mag_auto[ff], info.sig_noise[ff]*snscale, NBIN=30)
    ax.plot(xm,ym,color='white',linewidth=6,alpha=0.5)
    ax.plot(xm,ym,color='blue',linewidth=3,alpha=0.9)

    ax.semilogy()
    ax.plot([12,30],[3,3], linewidth=3, alpha=0.4, color='black', linestyle='--')
    ax.set_ylim(0.2,300)
    ax.set_xlim(16,25)
    ax.set_yticklabels(['1','3','10','100']) #; ax.set_xticklabels([])
    ytick = ax.set_yticks([1,3,10,100]) #; xtick = ax.set_xticks([0,NX]); 
    if plt.rcParams['text.usetex']:
        ax.set_xlabel('MAG\_AUTO (F140W)')
    else:
        ax.set_xlabel('MAG_AUTO (F140W)')
                
    ax.set_ylabel('S / N')
    
    ax.text(16.5,1,'AEGIS',color='blue', fontsize=12)
    ax.text(16.5,0.5,'COSMOS',color='red', fontsize=12)
    
    ##### S/N vs size for a mag bin
    ax = fig.add_subplot(212)
    
    m0, m1 = 22., 22.5
    
    mm = (info.mag_auto > m0) & (info.mag_auto < m1) & (info.sig_noise > 0)
    
    ax.plot(info.flux_radius[mm & (field == 'COSMOS')], info.sig_noise[mm & (field == 'COSMOS')]*snscale, marker=ma, markersize=ms, color='red', alpha=0.3, linestyle='None')
    xm, ym, ys, ns = threedhst.utils.runmed(info.flux_radius[mm & (field == 'COSMOS')], info.sig_noise[mm & (field == 'COSMOS')]*snscale, NBIN=5)
    
    ax.plot(info.flux_radius[mm & (field == 'AEGIS')], info.sig_noise[mm & (field == 'AEGIS')]*snscale, marker=ma, markersize=ms, color='blue', alpha=0.3, linestyle='None')

    ax.plot(xm,ym,color='white',linewidth=6,alpha=0.5)
    ax.plot(xm,ym,color='red',linewidth=3,alpha=0.9)
    
    xm, ym, ys, ns = threedhst.utils.runmed(info.flux_radius[mm & (field == 'AEGIS')], info.sig_noise[mm & (field == 'AEGIS')]*snscale, NBIN=5)
    ax.plot(xm,ym,color='white',linewidth=6,alpha=0.5)
    ax.plot(xm,ym,color='blue',linewidth=3,alpha=0.9)
    #plt.plot(xm,ym/np.sqrt(2),color='blue',linewidth=3,alpha=0.5)
    
    ax.semilogy()
    #ax.plot([0,30],[3,3], linewidth=3, alpha=0.5, color='black')
    ax.set_ylim(2,15)
    ax.set_xlim(1.5,12)
    ax.set_yticklabels(['3','5','10']) #; ax.set_xticklabels([])
    ytick = ax.set_yticks([3,5,10]) #; xtick = ax.set_xticks([0,NX]); 
    ax.set_xlabel(r'R$_{50}$ [0.06$^{\prime\prime}$ pix]')
    
    ax.set_ylabel('S / N')
    if plt.rcParams['text.usetex']:
        ax.text(11.8,13, r'$%.1f < m_{140} < %.1f$' %(m0, m1), horizontalalignment='right', verticalalignment='top')
    else:
        ax.text(11.8,13, r'%.1f < $m_{140}$ < %.1f' %(m0, m1), horizontalalignment='right', verticalalignment='top')
        
    fig.savefig('spec_signal_to_noise.pdf')
    
def run_empty_apertures_fields():
    import glob
    import os
    import unicorn
    os.chdir(unicorn.GRISM_HOME+'ANALYSIS/EMPTY_APERTURES/')
    
    files = glob.glob('/3DHST/Spectra/Work/COSMOS/PREP_FLT/COSMOS-*-F140W_drz.fits')
    files = glob.glob('/3DHST/Spectra/Work/GOODS-N/PREP_FLT/GOODS-N-*-F140W_drz.fits')
    
    for file in files[1:]:
        unicorn.survey_paper.empty_apertures(SCI_IMAGE=file, SCI_EXT=1, WHT_IMAGE=file, WHT_EXT=2, aper_params=(1,17,1), NSIM=1000, ZP=26.46, make_plot=True)
    
def empty_apertures(SCI_IMAGE='PRIMO_F125W_drz.fits', SCI_EXT=1, WHT_IMAGE='PRIMO_F125W_drz.fits', WHT_EXT=2, aper_params=(1,17,0.5), NSIM=1000, ZP=26.25, make_plot=True, verbose=True):
    """
    1) Run SExtractor on the input image to generate a segmentation map.
    
    2) Place `NSIM` empty apertures on the image, avoiding objects and areas with 
       zero weight as defined in the `WHT_IMAGE`.  
       
       The list of aperture radii used are np.arange(`aper_params`).
    
    3) Store the results in a FITS file `SCI_IMAGE`_empty.fits.
    
    Circular apertures are placed on the science image with the fractional pixel 
    coverage determined with a polygon approximation, and this can take a while.
    
    """
    
    from shapely.geometry import Point, Polygon
    
    if SCI_EXT == 0:
        SCI_EXT_SEX = 1
    else:
        SCI_EXT_SEX = SCI_EXT
        
    if WHT_EXT == 0:
        WHT_EXT_SEX = 1
    else:
        WHT_EXT_SEX = WHT_EXT
        
    ROOT = os.path.basename(SCI_IMAGE).split('.fits')[0]
    
    #### Open the science image
    if verbose:
        print 'Read images...'
        
    img = pyfits.open(SCI_IMAGE)
    img_data = img[SCI_EXT].data
    img_head = img[SCI_EXT].header
    img_shape = img_data.shape
    
    #### Setup SExtractor and run to generate a segmentation image
    se = threedhst.sex.SExtractor()
    se.aXeParams()
    se.copyConvFile()
    se.overwrite = True
    se.options['CATALOG_NAME']    = '%s_empty.cat' %(ROOT)
    se.options['CHECKIMAGE_NAME'] = '%s_empty_seg.fits' %(ROOT)
    se.options['CHECKIMAGE_TYPE'] = 'SEGMENTATION'
    
    if WHT_IMAGE is None:
        se.options['WEIGHT_TYPE']     = 'NONE'
        img_wht = img_data*0.
        img_wht[img_data != 0] = 1
    else:
        se.options['WEIGHT_TYPE']     = 'MAP_WEIGHT'
        se.options['WEIGHT_IMAGE']    = '%s[%d]' %(WHT_IMAGE, WHT_EXT_SEX-1)
        wht = pyfits.open(WHT_IMAGE)
        img_wht = wht[WHT_EXT].data
        
    se.options['FILTER']    = 'Y'
    se.options['DETECT_THRESH']    = '1.4'
    se.options['ANALYSIS_THRESH']  = '1.4'
    se.options['MAG_ZEROPOINT'] = '%.2f' %(ZP)  ### arbitrary, actual mags don't matter
    status = se.sextractImage('%s[%d]' %(SCI_IMAGE, SCI_EXT_SEX-1))
    
    #### Read the Segmentation image
    segim = pyfits.open('%s_empty_seg.fits' %(ROOT))
    seg = segim[0].data
    segim.close()
    
    #### Set up the apertures
    
    #NSIM = 1000
    #apertures = np.arange(1,17,0.5)
    apertures = np.arange(aper_params[0], aper_params[1], aper_params[2])
    fluxes = np.zeros((NSIM, len(apertures)))
    
    #### Loop throuth the desired apertures and randomly place NSIM of them
    aper = np.zeros(img_shape, dtype=np.float)
    for iap, ap in enumerate(apertures):
        #aper_image = np.zeros(img_shape)
        icount = 0
        print 'Aperture radius: %.2f pix\n' %(ap)
        while icount < NSIM:
            #### Random coordinate
            xc = np.random.rand()*(img_shape[1]-4*ap)+2*ap
            yc = np.random.rand()*(img_shape[0]-4*ap)+2*ap
            
            #### Quick test to see if the coordinate is within an object or 
            #### where weight is zero
            if (seg[int(yc), int(xc)] != 0) | (img_wht[int(yc), int(xc)] <= 0):
                continue
            
            #### Shapely point + buffer to define the aperture
            point = Point(xc, yc)
            buff = point.buffer(ap, resolution=16)
            
            #### initialize the aperture
            aper*=0
            
            #### Loop through pixels to compute fractional pixel coverage within
            #### the circular aperture using the intersection of Shapely polygons
            smax = 0
            wmin = 1.e10
            for i in range(int(np.floor(xc-ap)),int(np.ceil(xc+ap))):
                for j in range(int(np.floor(yc-ap)),int(np.ceil(yc+ap))):
                    pix = Polygon(((i+0.5,j+0.5), (i+1.5,j+0.5), (i+1.5,j+1.5), (i+0.5,j+1.5)))
                    isect = pix.intersection(buff)
                    aper[j,i] = isect.area
                    if isect.area > 0:
                        smax = np.array([smax, seg[j,i]]).max()
                        wmin = np.array([wmin, img_wht[j,i]]).min()
                        
            #### Only keep the result if the aperture doesn't intersect with an object
            #### as defined in the segmention image and if all weights within the 
            #### aperture are greater than zero
            if (smax == 0) & (wmin > 0):
                fluxes[icount, iap] = (aper*img_data).sum()
                #aper_image += aper
                print noNewLine+'%d' %(icount)
                icount += 1
            else:
                print noNewLine+'Skip: %f %f' %((seg*aper).max(), (img_wht*aper).min())
                continue
    
    #### Make the output FITS file.  List of aperture radii in extension 1, aperture
    #### fluxes in extension 2.
    
    ap_head = pyfits.Header()
    ap_head.update('NSIM',NSIM, comment='Number of apertures')
    ap_head.update('SCI_IMG',SCI_IMAGE, comment='Science image')
    ap_head.update('SCI_EXT',SCI_EXT, comment='Science extension')
    ap_head.update('WHT_IMG',WHT_IMAGE, comment='Weight image')
    ap_head.update('WHT_EXT',WHT_EXT, comment='Weight extension')
    
    prim = pyfits.PrimaryHDU(header=ap_head)
    ap_hdu = pyfits.ImageHDU(data=apertures)
    fl_hdu = pyfits.ImageHDU(data=fluxes)
    pyfits.HDUList([prim, ap_hdu, fl_hdu]).writeto('%s_empty.fits' %(ROOT), clobber='True')
    
    if make_plot is True:
        make_empty_apertures_plot(empty_file='%s_empty.fits' %(ROOT), ZP=ZP)
        
def make_empty_apertures_plot(empty_file='PRIMO_F125W_drz_empty.fits', ZP=26.25, NSIG=5):
    """
    Plot the results from the `empty_apertures` routine.
    """
    
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy import polyfit, polyval

    import threedhst
    import unicorn
    
    im = pyfits.open(empty_file)
    apertures = im[1].data
    fluxes = im[2].data
    
    ROOT = empty_file.split('_empty')[0]
    
    sigma = apertures*0.
    means = apertures*0.
    for iap, ap in enumerate(apertures):
        sigma[iap] = threedhst.utils.biweight(fluxes[:,iap])
        means[iap] = threedhst.utils.biweight(fluxes[:,iap], mean=True)
    
    #plt.plot(apertures, means/np.pi/apertures**2)
    #plt.ylim(0,1.5*np.max(means/np.pi/apertures**2))
    #threedhst.utils.biweight(img_data[(seg == 0) & (img_wht > 0)], both=True)

    fig = unicorn.catalogs.plot_init(xs=6, aspect=0.5, left=0.12)
    
    fig.subplots_adjust(wspace=0.24,hspace=0.0,left=0.095,
                        bottom=0.17,right=0.97,top=0.97)
    
    ax = fig.add_subplot(121)
    
    ################################## plot sigma vs radius  
    ax.plot(apertures, sigma, marker='o', linestyle='None', color='black', alpha=0.8, markersize=5)
    
    coeffs = polyfit(np.log10(apertures), np.log10(sigma), 1)
    ax.plot(apertures, 10**polyval(coeffs, np.log10(apertures)), color='red')
    
    xint = 1
    y2 = apertures**2
    y2 = y2*np.interp(xint,apertures,sigma) / np.interp(xint,apertures,y2)
    ax.plot(apertures, y2, linestyle='--', color='black', alpha=0.3)         
    
    y1 = apertures**1
    y1 = y1*np.interp(xint,apertures,sigma) / np.interp(xint,apertures,y1)
    ax.plot(apertures, y1, linestyle='--', color='black', alpha=0.3)         
    
    ax.set_xlabel(r'$R_\mathrm{aper}$ [pix]')
    ax.set_ylabel(r'$\sigma_\mathrm{biw}$')
    #ax.text(apertures.max(), 0.1*sigma.max(), r'$\beta=%.2f$' %(coeffs[0]), horizontalalignment='right')
    ax.text(0.08, 0.85, r'$N_\mathrm{ap}=%d$' %(im[0].header['NSIM']), transform=ax.transAxes)
    ax.set_ylim(0,2)
    
    ################################# Plot AB depth
    ax = fig.add_subplot(122)
    
    ax.plot(apertures, ZP-2.5*np.log10(sigma*NSIG), marker='o', linestyle='None', color='black', alpha=0.8, markersize=5)
    
    ax.plot(apertures, ZP-2.5*np.log10(10**polyval(coeffs, np.log10(apertures))*NSIG), color='red')
    
    ax.plot(apertures, ZP-2.5*np.log10(y2*NSIG), linestyle='--', color='black', alpha=0.3)         
    
    ax.plot(apertures, ZP-2.5*np.log10(y1*NSIG), linestyle='--', color='black', alpha=0.3)         
    
    ax.set_xlabel(r'$R_\mathrm{aper}$ [pix]')
    ax.set_ylabel(r'Depth AB mag (%d$\sigma$)' %(NSIG))
    
    ax.text(0.95, 0.9, ROOT, horizontalalignment='right', verticalalignment='top', transform=ax.transAxes)
    
    ax.text(0.95, 0.8, r'$\beta=%.2f$' %(coeffs[0]), horizontalalignment='right', verticalalignment='top', transform=ax.transAxes)
    
    ax.set_ylim(23, 30)
    
    ################################## Save the result
    outfile = ROOT+'_empty.pdf'
    if USE_PLOT_GUI:
        fig.savefig(outfile,dpi=100,transparent=False)
    else:
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure(outfile, dpi=100, transparent=False)
    
    print ROOT+'_empty.pdf'

def make_star_thumbnails():
    """ 
    Extract thumbnails for isolated stars in COSMOS
    """
    os.chdir(unicorn.GRISM_HOME+'ANALYSIS/SURVEY_PAPER')
    
    ######### Make full COSMOS catalog    
    file=unicorn.GRISM_HOME+'COSMOS/PREP_FLT/COSMOS-F140W_drz.fits'
    ROOT_GRISM = os.path.basename(file).split('_drz.fits')[0]
    se = threedhst.sex.SExtractor()
    se.aXeParams()
    se.copyConvFile()
    se.overwrite = True
    se.options['CATALOG_NAME']    = ROOT_GRISM+'_drz.cat'
    se.options['CHECKIMAGE_NAME'] = ROOT_GRISM+'_seg.fits'
    se.options['CHECKIMAGE_TYPE'] = 'SEGMENTATION'
    se.options['WEIGHT_TYPE']     = 'MAP_WEIGHT'
    se.options['WEIGHT_IMAGE']    = file+'[1]'
    se.options['FILTER']    = 'Y'
    se.options['DETECT_THRESH']    = '1.4'
    se.options['ANALYSIS_THRESH']  = '1.4'
    se.options['MAG_ZEROPOINT'] = '26.46'
    status = se.sextractImage(file+'[0]', mode='direct')
    
    cat = threedhst.sex.mySexCat('COSMOS-F140W_drz.cat')
        
    mag, radius = np.cast[float](cat.MAG_AUTO), np.cast[float](cat.FLUX_RADIUS)
    xpix, ypix = np.cast[float](cat.X_IMAGE), np.cast[float](cat.Y_IMAGE)
    ra, dec = np.cast[float](cat.X_WORLD), np.cast[float](cat.Y_WORLD)
    
    #### Find isolated point sources
    points = (mag > 17) & (mag < 22) & (radius < 2.7)
    # plt.plot(mag, radius, marker='o', linestyle='None', alpha=0.5, color='blue')
    # plt.plot(mag[points], radius[points], marker='o', linestyle='None', alpha=0.8, color='red')
    # plt.ylim(0,20)
    # plt.xlim(14,26)
    
    idx = np.arange(len(points))
    isolated = mag > 1.e10
    
    buff = 3 ## buffer, in arcsec
    dmag = 2.5
    scale = 0.06
    
    for i in idx[points]:
        dr = np.sqrt((xpix[i]-xpix)**2+(ypix[i]-ypix)**2)*scale
        near = (dr > 0) & (dr < buff) & (mag < (mag[i]+dmag))
        if len(near[near]) == 0:
            isolated[i] = True
        else:
            isolated[i] = False
    
    #### Make thumbnails
    img = pyfits.open(unicorn.GRISM_HOME+'COSMOS/PREP_FLT/COSMOS-F140W_drz.fits')
    img_data = img[1].data
    img_wht = img[2].data
    
    NPIX = int(np.ceil(buff/scale))

    prim = pyfits.PrimaryHDU()
    list_d = [prim]
    list_w = [prim]
    
    head = img[1].header
    head['CRPIX1'], head['CRPIX2'] = NPIX, NPIX
    
    for i in idx[points & isolated]:
        print noNewLine+'%d' %(i)
        id = np.int(cat.NUMBER[i])
        xi, yi = int(np.round(xpix[i])), int(np.round(ypix[i]))
        sub_data = img_data[yi-NPIX:yi+NPIX, xi-NPIX: xi+NPIX]
        sub_wht = img_wht[yi-NPIX:yi+NPIX, xi-NPIX: xi+NPIX]
        #
        head['CRVAL1'], head['CRVAL2'] = ra[i], dec[i]
        head.update('MAG',mag[i])
        head.update('RADIUS',radius[i])
        head.update('XCENTER',xpix[i]-xi+NPIX)
        head.update('YCENTER',ypix[i]-yi+NPIX)
        #
        list_d.append(pyfits.ImageHDU(sub_data, header=head))
        list_w.append(pyfits.ImageHDU(sub_wht, header=head))
    
    pyfits.HDUList(list_d).writeto('stars_sci.fits', clobber=True)
    pyfits.HDUList(list_w).writeto('stars_wht.fits', clobber=True)
    
def curve_of_growth():
    """
    Some code to evaluate the curve of growth of the F140W PSF, the 
    optimal aperture taken to be the ratio of the CoG divided by the empty aperture
    sigmas, and the overall depth within some aperture.
    """
    import threedhst
    import unicorn
    
    sci = pyfits.open('stars_sci.fits')
    wht = pyfits.open('stars_wht.fits')
    
    apers = np.arange(1,25,0.5)
    lstep = np.arange(0, np.log10(25), 0.05)
    apers = 10**lstep
        
    NOBJ = len(sci)-1
    count = 0
    average_fluxes = apers*0.
    stack = sci[1].data*0.
    
    for i in range(NOBJ):
        print noNewLine+'%d' %(i)
        star = sci[i+1].data
        yy, xx = np.indices(star.shape)
        center = (np.abs(xx-50) < 5) & (np.abs(yy-50) < 5)
        xc = np.sum((star*xx)[center])/np.sum(star[center])
        yc = np.sum((star*yy)[center])/np.sum(star[center])
        #xc, yc = sci[i+1].header['XCENTER'], sci[i+1].header['YCENTER']
        #
        bg = threedhst.utils.biweight(star, both=True)
        bg = threedhst.utils.biweight(star[star < (bg[0]+4*bg[1])], both=True)
        star = star-bg[0]
        stack = stack + star
        #        
        NAP = len(apers)
        fluxes = np.zeros(apers.shape)
        for i in range(NAP):
            #print noNewLine+'%.2f' %(apers[i])
            fluxes[i] = unicorn.survey_paper.aper_phot(star, xc, yc, apers[i])
        #
        pp = plt.plot(apers, fluxes/fluxes[20], alpha=0.2, color='blue')
        average_fluxes += fluxes/fluxes[20]
        count = count + 1
    
    stack = stack / count
    stack_fluxes = np.zeros(apers.shape)
    for i in range(NAP):
        print noNewLine+'%.2f' %(apers[i])
        stack_fluxes[i] = unicorn.survey_paper.aper_phot(star, xc, yc, apers[i])
    
    plt.xlabel(r'$R_\mathrm{aper}$')
    plt.ylabel(r'$f/f_{10}$')
    plt.text(15,0.4,'$N=%d$' %(count))
    
    plt.savefig('curve_of_growth.pdf')
    plt.close()
    
    #plt.plot(apers, average_fluxes/count, color='black', linewidth=2)
    #plt.plot(apers, stack_fluxes/stack_fluxes[20], color='red', linewidth=2)
    # plt.plot(apers, average_fluxes/count / (stack_fluxes/stack_fluxes[20]))
    
    fp = open('curve_of_growth.dat','w')
    for i in range(len(apers)):
        fp.write('%.2f %.3f\n' %(apers[i], (average_fluxes/count)[i]))
    
    fp.close()
    
    #### optimal color aperture:
    empty = pyfits.open('../../EMPTY_APERTURES/COSMOS-1-F140W_drz_empty.fits')
    files = glob.glob('../../EMPTY_APERTURES/*empty.fits')
    for file in files:
        empty = pyfits.open(file)
        apertures = empty[1].data
        fluxes = empty[2].data
        #
        sigma = apertures*0.
        means = apertures*0.
        for iap, ap in enumerate(apertures):
            sigma[iap] = threedhst.utils.biweight(fluxes[:,iap])
            means[iap] = threedhst.utils.biweight(fluxes[:,iap], mean=True)
        #
        ycog = np.interp(apertures, apers, (average_fluxes/count))
        pp = plt.plot(apertures, ycog/(sigma/np.interp(6, apertures, sigma)), alpha=0.5)
    
    plt.xlabel(r'$R_\mathrm{aper}$')
    plt.ylabel(r'CoG / $\sigma$')
    
    plt.plot(apertures, ycog/ycog.max(), color='black', linewidth=2)
    plt.plot(apertures, (sigma/np.interp(6, apertures, sigma))*0.3, color='black', alpha=0.4, linewidth=2)
    plt.savefig('optimal_aperture.pdf', dpi=100)
    plt.close()
    
    #### Actual calculation of the depth    
    from scipy import polyfit, polyval
    
    APER = 0.5 # arcsec, diameter
    
    ycog = average_fluxes/count
    ycog = ycog / ycog.max()
    
    print 'Aperture, D=%.2f"' %(APER)
    
    files = glob.glob('../../EMPTY_APERTURES/[CG]*empty.fits')
    for file in files:
        empty = pyfits.open(file)
        apertures = empty[1].data
        fluxes = empty[2].data
        #
        sigma = apertures*0.
        means = apertures*0.
        for iap, ap in enumerate(apertures):
            sigma[iap] = threedhst.utils.biweight(fluxes[:,iap])
            means[iap] = threedhst.utils.biweight(fluxes[:,iap], mean=True)
        #
        #plt.plot(apertures, 26.46-2.5*np.log10(5*sigma), marker='o', color='black', linestyle='None')
        coeffs = polyfit(np.log10(apertures), np.log10(sigma), 1)
        yfit = 10**polyval(coeffs, np.log10(apertures))
        pp = plt.plot(apertures, 26.46-2.5*np.log10(5*yfit), color='red')
        #
        apcorr = -2.5*np.log10(np.interp(APER/0.06/2, apers, ycog))
        #
        sig_at_aper = 10**polyval(coeffs, np.log10(APER/0.06/2))
        depth = 26.46-2.5*np.log10(5*sig_at_aper)-apcorr
        print '%s - %.2f' %(os.path.basename(file).split('-F14')[0], depth)
        
    plt.ylim(23,30)
    
def aper_phot(array, xc, yc, aper_radius):
    """
    Aperture photometry on an array
    """
    from shapely.geometry import Point, Polygon
    
    point = Point(xc, yc)
    buff = point.buffer(aper_radius, resolution=16)
        
    #### Make the aperture
    im_aper = array*0.
    
    yy, xx = np.indices(array.shape)
    dr = np.sqrt((xx-xc)**2+(yy-yc)**2)
    
    #### these are obviously in the aperture
    solid = dr < (aper_radius-1.5)
    im_aper[solid] = 1.
    
    #### This is the edge
    edge = (dr <= (aper_radius+1.5)) & (dr >= (aper_radius-1.5))
    # for i in range(int(np.floor(xc-aper_radius)),int(np.ceil(xc+aper_radius))):
    #     for j in range(int(np.floor(yc-aper_radius)),int(np.ceil(yc+aper_radius))):
    for i, j in zip(xx[edge], yy[edge]):
        pix = Polygon(((i+0.5,j+0.5), (i+1.5,j+0.5), (i+1.5,j+1.5), (i+0.5,j+1.5)))
        isect = pix.intersection(buff)
        im_aper[j,i] = isect.area
    
    return np.sum(array*im_aper)
    
def make_examples():
    import unicorn
    unicorn.survey_paper.redshift_fit_example(id='COSMOS-18-G141_00485')
    unicorn.survey_paper.redshift_fit_example(id='COSMOS-14-G141_00100')
    unicorn.survey_paper.redshift_fit_example(id='GOODS-N-33-G141_00946')
    unicorn.survey_paper.redshift_fit_example(id='GOODS-N-17-G141_00573')
    unicorn.survey_paper.redshift_fit_example(id='GOODS-N-33-G141_01028')
    unicorn.survey_paper.redshift_fit_example(id='COSMOS-1-G141_00252')
    unicorn.survey_paper.redshift_fit_example(id='AEGIS-4-G141_00266')
    unicorn.survey_paper.redshift_fit_example(id='COSMOS-5-G141_00751')

    unicorn.survey_paper.redshift_fit_example(id='PRIMO-1101-G141_01022')
    unicorn.survey_paper.redshift_fit_example(id='GOODS-S-24-G141_00029')
    
    
    import unicorn
    import unicorn.catalogs
    
    unicorn.catalogs.read_catalogs()
    from unicorn.catalogs import zout, phot, mcat, lines, rest, gfit
    
    mat = lines.id == 'COSMOS-14-G141_00100'
    print lines.id[mat][0], lines.halpha_eqw[mat][0], lines.halpha_eqw_err[mat][0], lines.halpha_flux[mat][0]

    mat = lines.id == 'COSMOS-18-G141_00485'
    print lines.id[mat][0], lines.halpha_eqw[mat][0], lines.halpha_eqw_err[mat][0], lines.halpha_flux[mat][0]
    
def redshift_fit_example(id='COSMOS-18-G141_00485', force=False):
    """ 
    Make a big plot showing how the whole redshift fitting works
    """    
    #id = 'COSMOS-14-G141_00100'  ### aligned along dispersion axis, weak line
    #id = 'GOODS-N-33-G141_00946' ### classic spiral
    #id = 'GOODS-N-17-G141_00573'
    #id = 'COSMOS-18-G141_00485' ### asymmetric line, spiral
    
    os.chdir('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER/EXAMPLE_FITS')
    
    #### Get the necessary files from unicorn
    if (not os.path.exists('%s_thumb.fits.gz' %(id))) | force:
        os.system('wget http://3dhst:getspecs@unicorn.astro.yale.edu/P/GRISM_v1.6/images/%s_thumb.fits.gz' %(id))
        os.system('wget http://3dhst:getspecs@unicorn.astro.yale.edu/P/GRISM_v1.6/images/%s_2D.fits.gz' %(id))
        os.system('wget http://3dhst:getspecs@unicorn.astro.yale.edu/P/GRISM_v1.6/ascii/%s.dat' %(id))
        os.system('rsync -avz --progress $UNICORN:/3DHST/Spectra/Work/ANALYSIS/REDSHIFT_FITS/OUTPUT/%s* OUTPUT/ ' %(id))
        os.system('rsync -avz --progress $UNICORN:/3DHST/Spectra/Work/ANALYSIS/REDSHIFT_FITS/%s* ./ ' %(id))
    
    zo = threedhst.catIO.Readfile('OUTPUT/%s.zout' %(id))
    
    fig = plt.figure(figsize=(6,6))
    dsep = 0.05
    xsep = 0.6
    left = 0.08
    bottom = 0.07
    spec_color = 'purple'
    dy2d = 0.13
    #spec_color = 'blue'
    spec_color = (8/255.,47/255.,101/255.)
    spec_color = 'red'
    phot_color = 'orange'
    #phot_color = (78/255.,97/255.,131/255.)
    #phot_color = '0.7'
    
    spec_color = 'black'
    phot_color = '0.7'
    temp_color = (8/255.,47/255.,101/255.)
    
    ########### Full spectrum
    
    ax = fig.add_axes((left, 0.5+bottom+dy2d, 0.98-left-(1-xsep), 0.49-bottom-dy2d))

    lambdaz, temp_sed, lci, obs_sed, fobs, efobs = eazy.getEazySED(0, MAIN_OUTPUT_FILE='%s' %(id), OUTPUT_DIRECTORY='OUTPUT', CACHE_FILE = 'Same')
    
    tempfilt, coeffs, temp_seds, pz = eazy.readEazyBinary(MAIN_OUTPUT_FILE=id, OUTPUT_DIRECTORY='OUTPUT', CACHE_FILE = 'Same')
    
    dlam_spec = lci[-1]-lci[-2]
    is_spec = np.append(np.abs(1-np.abs(lci[1:]-lci[0:-1])/dlam_spec) < 0.05,True)
    
    ymax = max(fobs[is_spec & (fobs > 0)])
        
    ax.semilogx([1],[1])
    
    ## photometry
    ax.plot(lci[~is_spec], obs_sed[~is_spec], marker='o', color='black', linestyle='None', markersize=6, alpha=0.2)
    ## best-fit SED
    ## Spectrum + convolved fit
    #ax.plot(lci[is_spec], obs_sed[is_spec], color='black', markersize=6, alpha=0.7, linewidth=1)
    ax.plot(lci[is_spec], fobs[is_spec], marker='None', alpha=0.8, color=spec_color, linewidth=4)
    ax.plot(lambdaz, temp_sed, color='white', linewidth=3, alpha=0.6)
    ax.plot(lambdaz, temp_sed, color=temp_color, alpha=0.6)
    ax.errorbar(lci[~is_spec], fobs[~is_spec], efobs[~is_spec], marker='o', linestyle='None', alpha=0.6, color=phot_color, markersize=10)
        
    ax.set_yticklabels([])
    ax.set_ylabel(r'$f_\lambda$')
    ax.set_xlabel(r'$\lambda$')
    xtick = ax.set_xticks(np.array([0.5, 1., 2, 4])*1.e4)
    ax.set_xticklabels(np.array([0.5, 1., 2, 4]))
    #ax.set_xlim(3000,9.e4)
    ax.set_xlim(3290,2.5e4)
    ax.set_ylim(-0.1*ymax, 1.2*ymax)
    
    ############# Sub spectrum
    ax = fig.add_axes((left, bottom, 0.98-left, 0.49-bottom))
    
    obs_sed_continuum = np.dot(tempfilt['tempfilt'][:,0:7,coeffs['izbest'][0]],coeffs['coeffs'][0:7,0])/(lci/5500.)**2
    temp_sed_continuum = np.dot(temp_seds['temp_seds'][:,0:7],coeffs['coeffs'][0:7,0])/(1+zo.z_peak[0])**2
    
    ymax = max(fobs[is_spec & (fobs > 0)]-obs_sed_continuum[is_spec & (fobs > 0)])
    #ymin = min(fobs[is_spec & (fobs > 0)])
    
    # ax.semilogx([1],[1])
    
    ## photometry
    ax.plot(lci[~is_spec], obs_sed[~is_spec]-obs_sed_continuum[~is_spec], marker='o', color='black', linestyle='None', markersize=6, alpha=0.2, zorder=10)
    ## best-fit SED
    ax.plot(lci[is_spec], fobs[is_spec]-obs_sed_continuum[is_spec], marker='None', alpha=0.8, color=spec_color, linewidth=5, zorder=10)
    ax.plot(lambdaz, temp_sed-temp_sed_continuum, color=temp_color, alpha=0.3, zorder=10)
    ## Spectrum + convolved fit
    ax.plot(lci[is_spec], obs_sed[is_spec]-obs_sed_continuum[is_spec], color='white', markersize=6, alpha=0.7, linewidth=4, zorder=10)
    ax.plot(lci[is_spec], obs_sed[is_spec]-obs_sed_continuum[is_spec], color=temp_color, markersize=6, alpha=0.7, linewidth=1, zorder=10)
    #ax.plot(lci[is_spec], obs_sed_continuum[is_spec]-obs_sed_continuum[is_spec], color='black', markersize=6, alpha=0.3, linewidth=2)
    
    ax.errorbar(lci[~is_spec], fobs[~is_spec]-obs_sed_continuum[~is_spec], efobs[~is_spec], marker='o', linestyle='None', alpha=0.6, color=phot_color, markersize=10)
    
    ax.set_yticklabels([])
    ax.set_ylabel(r'$f_\lambda-\ \mathrm{continuum}$')
    ax.set_xlabel(r'$\lambda$')
    xtick = ax.set_xticks(np.array([1.2, 1.4,1.6])*1.e4)
    ax.set_xticklabels(np.array([1.2, 1.4,1.6]))
    #ax.set_xlim(3000,9.e4)
    ax.set_xlim(1.05e4,1.7e4)
    ax.set_ylim(-0.2*ymax, 1.2*ymax)
        
    ########### p(z)
    ax = fig.add_axes((xsep+left, 0.5+bottom+dy2d, 0.98-left-xsep, 0.49-bottom-dy2d))
    
    colors = [spec_color,phot_color,'blue']
    alpha = [0.5, 0.5, 0.2]
    zmin = 4
    zmax = 0
    ymax = 0
    for i in range(2):
        zgrid, pz = eazy.getEazyPz(i, MAIN_OUTPUT_FILE='%s' %(id), 
                          OUTPUT_DIRECTORY='./OUTPUT', 
                          CACHE_FILE='Same')
        ax.fill_between(zgrid, pz, pz*0., color=colors[i], alpha=alpha[i], edgecolor=colors[i])
        ax.fill_between(zgrid, pz, pz*0., color=colors[i], alpha=alpha[i], edgecolor=colors[i])
        #
        if pz.max() > ymax:
            ymax = pz.max()
        #
        if zgrid[pz > 1.e-3].min() < zmin:
            zmin = zgrid[pz > 1.e-2].min()
        #
        if zgrid[pz > 1.e-6].max() > zmax:
            zmax = zgrid[pz > 1.e-2].max()
    
    ax.plot(zo.z_spec[0]*np.array([1,1]),[0,1.e4], color='green', linewidth=1)
    
    ax.set_yticklabels([])
    ax.set_xlabel(r'$z$')
    ax.set_ylabel(r'$p(z)$')
    ax.xaxis.set_major_locator(unicorn.analysis.MyLocator(4, prune='both'))
    
    ### Plot labels
    #ax.text(0.5, 0.9, '%s' %(id), transform = ax.transAxes, horizontalalignment='center')
    ax.text(0.95, 0.8, r'$z_\mathrm{phot}=$'+'%5.3f' %(zo.z_peak[1]), transform = ax.transAxes, horizontalalignment='right', fontsize=9)
    ax.text(0.95, 0.7, r'$z_\mathrm{gris}=$'+'%5.3f' %(zo.z_peak[0]), transform = ax.transAxes, horizontalalignment='right', fontsize=9)
    if zo.z_spec[0] > 0:
        ax.text(0.95, 0.6, r'$z_\mathrm{spec}=$'+'%5.3f' %(zo.z_spec[0]), transform = ax.transAxes, horizontalalignment='right', fontsize=9)
        
    ax.set_xlim(zmin, zmax)
    #ax.set_xlim(zgrid.min(), zgrid.max())
    ax.set_ylim(0,1.1*ymax)
    
    #################### 2D spectrum
    thumb = pyfits.open('%s_thumb.fits.gz' %(id))
    thumb_data = thumb[0].data
    #thumb_data[10,:] = 1000
    profile = np.sum(thumb_data, axis=1)
        
    NSUB = int(np.round(0.5*thumb_data.shape[0]))/2
    yc = thumb_data.shape[0]/2
     
    dx = NSUB*2*22/(ax.get_xlim()[1]-ax.get_xlim()[0])*(0.98-left)
    dx = dy2d

    ax = fig.add_axes((left, 0.49, 0.98-left, dy2d))
    #ax.errorbar(lci[~is_spec], fobs[~is_spec]-obs_sed_continuum[~is_spec], efobs[~is_spec], marker='o', linestyle='None', alpha=0.6, color=phot_color, markersize=10)
    twod_file = '%s_2D.fits.gz' %(id)
    twod = pyfits.open(twod_file)
    spec2d = twod[1].data-twod[4].data
    
    head = twod[1].header
    lam_idx = np.arange(head['NAXIS1'])
    lam = (lam_idx+1-head['CRPIX1'])*head['CDELT1']+head['CRVAL1']
    lam_mima = np.cast[int](np.round(np.interp(np.array([1.05e4,1.7e4]), lam, lam_idx)))
    tick_int = np.interp(np.array([1.2,1.4,1.6])*1.e4, lam, lam_idx)-np.interp(1.05e4, lam, lam_idx)
    
    spec2d_sub = spec2d[yc-NSUB:yc+NSUB,lam_mima[0]:lam_mima[1]]
    ax.imshow(0-spec2d_sub, aspect='auto', vmin=-0.1, vmax=0.01, interpolation='nearest')
    ax.set_yticklabels([]); ax.set_xticklabels([])
    xtick = ax.set_xticks(tick_int); ytick = ax.set_yticks([0,2*NSUB])
    
    ########### Thumbnail
    
    #ax = fig.add_axes((left+left*0.3, 0.49-dx-left*0.3, dx, dx))
    ax = fig.add_axes((left, 0.49, dx, dx))
    #ax.imshow(thumb_data[yc-NSUB:yc+NSUB, yc-NSUB:yc+NSUB], vmin=-0.05, vmax=0.5, interpolation='nearest')
    ax.imshow(0-thumb_data[yc-NSUB:yc+NSUB, yc-NSUB:yc+NSUB], vmin=-0.7, vmax=0.05, interpolation='nearest', zorder=2)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    #ax = fig.add_axes((left+left*0.3*2+dx, 0.49-dx-left*0.3, dx, dx))

    #profile = np.sum(thumb_data[yc-NSUB:yc+NSUB, yc-NSUB:yc+NSUB], axis=0)
    #ax.plot(profile/profile.max(), color='black', alpha=0.4)

    size = thumb[0].data.shape
    twod_file = '%s_2D.fits.gz' %(id)
    twod = pyfits.open(twod_file)
    model1D = np.matrix(twod[5].data.sum(axis=1))
    model1D /= np.max(model1D)
    model2D = np.array(np.dot(np.transpose(model1D),np.ones((1,size[0]))))
    thumb_data *= model2D
    
    profile = np.sum(thumb_data[yc-NSUB:yc+NSUB, yc-NSUB:yc+NSUB], axis=0)
    ax.plot(profile/profile.max()*2*NSUB*0.8, color='black', alpha=0.3, zorder=2)
    ax.set_xlim(0,2*NSUB); ax.set_ylim(0,2*NSUB)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    xtick = ax.set_xticks([0,2*NSUB]); ytick = ax.set_yticks([0,2*NSUB])
    
    fig.savefig('%s_example.pdf' %(id))
    
def equivalent_width_errors():
    """
    Compute the limiting equivalent widths as a function of magnitude or mass
    or something
    """
    import unicorn
    import unicorn.catalogs
    
    unicorn.catalogs.read_catalogs()
    from unicorn.catalogs import zout, phot, mcat, lines, rest, gfit
    
    os.chdir('/research/HST/GRISM/3DHST/ANALYSIS/SURVEY_PAPER')
    
    keep = unicorn.catalogs.run_selection(zmin=0.8, zmax=5.5, fcontam=0.2, qzmin=0., qzmax=0.1, dr=1.0, has_zspec=False, fcovermin=0.9, fcovermax=1.0, massmin=8.5, massmax=15, magmin=17, magmax=23.5)
    keep_22 = unicorn.catalogs.run_selection(zmin=0.8, zmax=5.5, fcontam=0.2, qzmin=0., qzmax=0.1, dr=1.0, has_zspec=False, fcovermin=0.9, fcovermax=1.0, massmin=8.5, massmax=15, magmin=21.7, magmax=22.3)
    
    halpha_sn = lines.halpha_eqw / lines.halpha_eqw_err
    #halpha_sn[(halpha_sn > 0) & (halpha_sn < 1)] = 2
    keep_ha = keep & (halpha_sn[lines.idx] > 0)
    
    oiii_sn = lines.oiii_eqw / lines.oiii_eqw_err
    keep_oiii = keep & (oiii_sn[lines.idx] > 0)
    
    #plt.scatter(phot.mag_f1392w[phot.idx][keep], phot.flux_radius[phot.idx][keep], marker='o')
    marker_size = phot.flux_radius[phot.idx]**1.5
    colors = 'purple'
    # colors = (phot.mag_f1392w[phot.idx]-17)
    # colors[colors < 0] = 0
    # colors[colors > 5] = 5
    
    ##### FLux
    fig = unicorn.catalogs.plot_init(square=True, xs=5, aspect=5/4., left=0.12)
    fig.subplots_adjust(wspace=0.20,hspace=0.24,left=0.12,
                        bottom=0.08,right=0.98,top=0.98)
    
    plt.rcParams['patch.edgecolor'] = 'k'
    ax = fig.add_subplot(211)

    ax.scatter(lines.halpha_flux[lines.idx][keep_ha], halpha_sn[lines.idx][keep_ha], marker='o', c='purple', alpha=0.1, s=marker_size[keep_ha])
    ax.scatter(lines.oiii_flux[lines.idx][keep_oiii], oiii_sn[lines.idx][keep_oiii], marker='o', c='orange', alpha=0.1, s=marker_size[keep_oiii])

    ## label
    for si in [2,4,8,16]:
        ax.scatter(np.array([1,1])*2.e-17, np.array([1,1])*25*si**0.4, s=si**1.5, color='black', alpha=0.2)
        ax.text(2.e-17*1.3, 25*si**0.4, '%.1f' %(si*0.06), verticalalignment='center')
    
    nha = len(lines.halpha_flux[lines.idx][keep_ha])
    noiii = len(lines.halpha_flux[lines.idx][keep_oiii])
    ax.text(2.e-17*1.15, 25*(0.5)**0.4, r'$N_\mathrm{H\alpha}=%d$' %(nha), color='purple', horizontalalignment='center')
    ax.text(2.e-17*1.15, 25*(0.5/3)**0.4, r'$N_\mathrm{O III}=%d$' %(noiii), color='orange', horizontalalignment='center')
    
    
    ax.semilogy()
    ax.semilogx()
    ax.set_ylim(1,100)
    ax.set_xlim(1.e-17,2.e-15)
    ax.set_yticklabels([1,3,10,30,100])
    ytick = ax.set_yticks([1,3,10,30,100])
    ax.set_ylabel('line S / N')
    ax.set_xlabel(r'line flux $\mathrm{[ergs\ s^{-1}\ cm^{-2}]}$')
        
    #### EqW
    #fig = unicorn.catalogs.plot_init(square=True, xs=5, aspect=1, left=0.12)
    #plt.rcParams['patch.edgecolor'] = 'k'
    ax = fig.add_subplot(212)
    
    marker_size = 10**(-0.4*(18-phot.mag_f1392w[phot.idx]))**0.8
    
    ax.scatter(lines.halpha_eqw[lines.idx][keep_ha], halpha_sn[lines.idx][keep_ha], marker='o', c='purple', alpha=0.1, s=marker_size[keep_ha])
    ax.scatter(lines.oiii_eqw[lines.idx][keep_oiii], oiii_sn[lines.idx][keep_oiii], marker='o', c='orange', alpha=0.1, s=marker_size[keep_oiii])
    
    for si, mag in enumerate([19, 21, 23]):
        ax.scatter(np.array([1,1])*10, np.array([1,1])*25*(2**(si+1))**0.4, s=10**(-0.4*(18-mag))**0.8, color='black', alpha=0.2)
        ax.text(10*1.3, 25*(2**(si+1))**0.4, '%d' %(mag), verticalalignment='center')
    
    ax.semilogy()
    ax.semilogx()
    ax.set_ylim(1,100)
    ax.set_xlim(5,500)
    ax.set_yticklabels([1,3,10,30,100])
    ytick = ax.set_yticks([1,3,10,30,100])
    ax.set_xticklabels([5,10,100])
    ytick = ax.set_xticks([5,10,100])
    ax.set_ylabel('line S / N')
    ax.set_xlabel(r'Equivalent width $[\AA]$')
        
    fig.savefig('equivalent_width_errors.pdf')
    
def zphot_zspec_plot():
    
    import unicorn
    import unicorn.catalogs
    import copy
    
    os.chdir(unicorn.GRISM_HOME+'/ANALYSIS/SURVEY_PAPER')
        
    unicorn.catalogs.read_catalogs()
    from unicorn.catalogs import zout, phot, mcat, lines, rest, gfit
    
    if unicorn.catalogs.zsp is None:
        unicorn.catalogs.make_specz_catalog()
    
    zsp = unicorn.catalogs.zsp
    
    maglim = 24
    qzmax = 0.2
    
    keep = (phot.mag_f1392w[phot.idx] < maglim) & (phot.fcontam[phot.idx] < 0.05) & (zout.q_z[0::3] < qzmax) & (phot.fcover[phot.idx] > 0.9) & (mcat.logm[mcat.idx] > 0) & (mcat.rmatch[mcat.idx] < 0.5) & (zsp.zspec[zsp.mat_idx] > 0) & (zsp.dr < 1)
    
    #### Same selection but nothing on specz
    keep_nospec = (phot.mag_f1392w[phot.idx] < maglim) & (phot.fcontam[phot.idx] < 0.05) & (zout.q_z[0::3] < qzmax) & (phot.fcover[phot.idx] > 0.9) & (mcat.logm[mcat.idx] > 0) & (mcat.rmatch[mcat.idx] < 0.5) & (zout.z_peak[0::3] > 0.7)
    keep_hasspec = (phot.mag_f1392w[phot.idx] < maglim) & (phot.fcontam[phot.idx] < 0.05) & (zout.q_z[0::3] < qzmax) & (phot.fcover[phot.idx] > 0.9) & (mcat.logm[mcat.idx] > 0) & (mcat.rmatch[mcat.idx] < 0.5) & (zout.z_peak[0::3] > 0.7) & (zsp.zspec[zsp.mat_idx] > 0) & (zsp.dr < 1)
    
    print len(keep[keep_hasspec])*1./len(keep[keep_nospec]), len(keep[keep_nospec])
    
    #### Only way to get out a few objects where the photometry wasn't found for the fit
    keep = keep & (zout.q_z[0::3] != zout.q_z[2::3])
            
    fig = unicorn.catalogs.plot_init(left=0.08, xs=4)
    ax = fig.add_subplot(111)
    
    zsplit = 0.7
    ax.plot(np.log10(1+zsp.zspec[zsp.mat_idx][keep & (zsp.zspec[zsp.mat_idx] > zsplit)]), np.log10(1+zout.z_peak[0::3][keep & (zsp.zspec[zsp.mat_idx] > zsplit)]), marker='o', linestyle='None', alpha=0.2, color='black', markersize=5)
    ax.plot(np.log10(1+zsp.zspec[zsp.mat_idx][keep & (zsp.zspec[zsp.mat_idx] < zsplit)]), np.log10(1+zout.z_peak[0::3][keep & (zsp.zspec[zsp.mat_idx] < zsplit)]), marker='o', linestyle='None', alpha=0.2, color='0.9', markersize=5)
    
    ax.plot([0,5],[0,5], color='white', alpha=0.2, linewidth=3)
    ax.plot([0,5],[0,5], color='black', alpha=0.5, linewidth=1)
    
    zz = np.array([0,4])
    ax.plot(np.log10(1+zz), np.log10(1+zz+0.1*(1+zz)), linestyle='--', color='0.8', alpha=0.5)
    ax.plot(np.log10(1+zz), np.log10(1+zz-0.1*(1+zz)), linestyle='--', color='0.8', alpha=0.5)
    
    ax.set_xticklabels(['0','1','2','3','4'])
    ax.set_xticks(np.log10(1+np.array([0,1,2,3,4])))
    ax.set_yticklabels(['0','1','2','3','4'])
    ax.set_yticks(np.log10(1+np.array([0,1,2,3,4])))
    ax.set_xlim(np.log10(1),np.log10(4+1))
    ax.set_ylim(np.log10(1),np.log10(4+1))
    
    ax.set_xlabel(r'$z_\mathrm{spec}$')
    ax.set_ylabel(r'$z_\mathrm{G141+phot}$')
    
    dz = (zout.z_peak[0::3] - zsp.zspec[zsp.mat_idx])/(1+zsp.zspec[zsp.mat_idx])
    clip = np.abs(dz) < 0.1
    sigma_gt1 = threedhst.utils.nmad(dz[keep & (zout.z_spec[0::3] > 1)])
    sigma_gt1_clip = threedhst.utils.nmad(dz[keep & (zout.z_spec[0::3] > 1) & clip])
    sigma_gt0_biw = threedhst.utils.biweight(dz[keep & (zout.z_spec[0::3] > 0.7)])
    sigma_gt0 = threedhst.utils.nmad(dz[keep & (zout.z_spec[0::3] > 0.7)])
    sigma_gt0_clip = threedhst.utils.nmad(dz[keep & (zout.z_spec[0::3] > 0.7) & clip])
    NOUT = len(dz[keep & (zout.z_spec[0::3] > 0.7) & ~clip])*1./len(dz[keep & (zout.z_spec[0::3] > 0.7)])
    
    print sigma_gt0, sigma_gt0_clip, sigma_gt1, sigma_gt1_clip, NOUT
    ax.text(0.1,0.9,r'$m_{140} <\ %.1f,\ z_\mathrm{spec} >\ 0.7,\ Q_z >\ %.2f$' %(maglim, qzmax), transform=ax.transAxes, fontsize=12)
    ax.text(0.1,0.81,r'$N=%d$' %(len(dz[keep & (zout.z_spec[0::3] > 0.7)])), transform=ax.transAxes, fontsize=12)
    ax.text(0.1,0.72,r'$\sigma_\mathrm{NMAD}=%.4f$' %(sigma_gt0), transform=ax.transAxes, fontsize=12)
    pct = '\%'
    ax.text(0.1,0.63,r'$f_\mathrm{>0.1}=%.1f%s$' %(NOUT*100,pct), transform=ax.transAxes, fontsize=12)
    
    fig.savefig('zphot_zspec.pdf')
    
    ##### Show line misidentifications
    # zha = np.log10(np.array([1.05e4,1.68e4])/6563.)
    # ax.plot(zha, zha+np.log10(6563./5007), color='green', alpha=0.5)
    # ax.plot(zha, zha+np.log10(6563./3727), color='purple', alpha=0.5)
    # ax.plot(zha, zha+np.log10(6563./4863), color='orange', alpha=0.5)
    # zhb = np.log10(np.array([1.05e4,1.68e4])/4861.)
    # ax.plot(zhb, zhb+np.log10(4861./3727), color='blue', alpha=0.5)
    # zoiii = np.log10(np.array([1.05e4,1.68e4])/3727.)
    # ax.plot(zoiii, zoiii+np.log10(3727./4861), color='blue', alpha=0.5)
    
    # plt.xlim(0,np.log10(1+5))
    # plt.ylim(0,np.log10(1+5))
    
    #### Offset near z=1, appears to be due to the tilted slope of the spectrum being a bit too steep.  If you just use a 0th order offset correction to the spectrum (TILT_ORDER=0), the redshifts for many of these objects become correct
    #keep = keep & (np.array(zsp.source)[zsp.mat_idx] == 'Barger')
    
    if (1==0):
        dzlog = np.log10(1+zout.z_peak[0::3]) - np.log10(1+zsp.zspec[zsp.mat_idx])
    
        bad = (dzlog > 0.027) & (dzlog < 0.047 ) & (np.log10(1+zsp.zspec[zsp.mat_idx]) > 0.2) & keep

        bad = (dzlog > 0.18) & keep
        bad = (np.abs(dz) > 0.1) & (zsp.zspec[zsp.mat_idx] > 0.7) & keep

        print np.array(zsp.source)[zsp.mat_idx][bad]
        print phot.id[phot.idx][bad]

        for id in phot.id[phot.idx][bad]:
            os.system('wget http://3dhst:getspecs@unicorn.astro.yale.edu/P/GRISM_v1.6/EAZY/%s_eazy.png' %(id))
        
        fig = unicorn.catalogs.plot_init(left=0.12)
        ax = fig.add_subplot(111)
        ax.plot(np.log10(1+zsp.zspec[zsp.mat_idx][keep]), dzlog[keep], marker='o', linestyle='None', alpha=0.5, color='black', markersize=5)
        ax.set_xlim(0,np.log10(4+1))
        ax.set_ylim(-1,1)

        #### nearby offset at z~1 ~ 0.035 in log(1+z)
        offset = 0.036
        print 6563*10**(-offset), 5007*10**(-offset), 4861*10**(-offset), 3727*10**(-offset)
    
def find_brown_dwarf():
    import unicorn
    import unicorn.catalogs
    import copy
    
    os.chdir(unicorn.GRISM_HOME+'/ANALYSIS/SURVEY_PAPER')
        
    unicorn.catalogs.read_catalogs()
    from unicorn.catalogs import zout, phot, mcat, lines, rest, gfit, zsp
    
    int_lam = np.array([0.77e4, 1.25e4, 2.1e4])
    
    
    fp = open('stars_ijk.dat','w')
    fp.write('# id ii jj kk\n')
    
    ##### Known Brown dwarf
    object = 'AEGIS-3-G141_00195'
    lambdaz, temp_sed, lci, obs_sed, fobs, efobs = eazy.getEazySED(0, MAIN_OUTPUT_FILE='%s' %(object), OUTPUT_DIRECTORY=unicorn.GRISM_HOME+'/ANALYSIS/REDSHIFT_FITS_v1.6/OUTPUT/', CACHE_FILE = 'Same')
    dlam_spec = lci[-1]-lci[-2]
    is_spec = np.append(np.abs(1-np.abs(lci[1:]-lci[0:-1])/dlam_spec) < 0.05,True)
    so = np.argsort(lci[~is_spec])
    yint = np.interp(int_lam, lci[~is_spec][so], fobs[~is_spec][so])/(int_lam/5500.)**2
    fp.write('%s %.3e %.3e %.3e\n' %(object, yint[0], yint[1], yint[2]))
    
    ###### Loop through all point sources
    stars = (phot.flux_radius[phot.idx] < 3) & (phot.mag_f1392w[phot.idx] < 24) & (mcat.rmatch[mcat.idx] < 0.5)
    for object in phot.id[phot.idx][stars]:
        print noNewLine+'%s' %(object)
        try:
            lambdaz, temp_sed, lci, obs_sed, fobs, efobs = eazy.getEazySED(0, MAIN_OUTPUT_FILE='%s' %(object), OUTPUT_DIRECTORY=unicorn.GRISM_HOME+'/ANALYSIS/REDSHIFT_FITS_v1.6/OUTPUT/', CACHE_FILE = 'Same')
        except:
            pass
        #
        dlam_spec = lci[-1]-lci[-2]
        is_spec = np.append(np.abs(1-np.abs(lci[1:]-lci[0:-1])/dlam_spec) < 0.05,True)
        so = np.argsort(lci[~is_spec])
        yint = np.interp(int_lam, lci[~is_spec][so], fobs[~is_spec][so])/(int_lam/5500.)**2
        fp.write('%s %.3e %.3e %.3e\n' %(object, yint[0], yint[1], yint[2]))
        
    fp.close()
    
    
    
def example_objects():
    
    ########   AGN/Quasars
    ### Binary quasar: GOODS-N-42-G141_00388/384
    ### z=2.2 quasar: COSMOS-1-G141_00206	
    ### very broad H-a line, z=1.22: PRIMO-1101-G141_00993
    ### Even more interesting merger/quasar, z=1.778: GOODS-N-36-G141_00991	
    ### Another mess: COSMOS-3-G141_01156, z=1.34
    ### Multiple components, z=1.27 GOODS-N-33-G141_01028/1073/1069/1055
    
    ######## Brown dwarf
    ###  AEGIS-3-G141_00195
    
    pass
    