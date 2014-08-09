import sys, os
from pylab import *
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
from pytecan.ReaderXML import CollectData
from toolbox.util import _mkdir

def get_data(reading_label, plate_id, row, col, MES):
    """
        When the experimental data is broken into more than one XLS sheet, this method
        concatenates the data into one series and returns it as if it was from one source.
    """
    well = (row, col)
    time_list = []
    value_list = []
    for time, value in sorted(MES[reading_label][plate_id][well].iteritems()):
         time_list.append(time)
         value_list.append(value)
         
    time_array = array(time_list)
    if len(time_list):
        time_array = (time_array - time_list[0])/3600 
    return time_array, array(value_list)

MES = CollectData("../data/tecan/PL6-96.tar.gz", number_of_plates=4)
_mkdir('../res/tecan')
pp = PdfPages('../res/tecan/2011-02-06_PL6-96.pdf')

#rcParams['text.usetex'] = True
rcParams['legend.fontsize'] = 12
#rcParams['font.family'] = 'sans-serif'
#rcParams['font.size'] = 8
#rcParams['lines.linewidth'] = 0.3
#rcParams['lines.markersize'] = 2
#rcParams['figure.figsize'] = [5, 10]
#rcParams['figure.subplot.hspace'] = 0.3
#figure()

plot_growth_rate = False
fit_window_size = 1.5 # hours
fit_start_threshold = 0.01

plots = [] # (title, victor_index, (t_min, t_max), (y_min, y_max), y_label, 
t_max = 42
OD_min = 0.036

#for r in [0, 1, 2, 3, 4, 5, 6, 7]:
colors = ['gray', 'red', 'magenta', 'blue', 'cyan', 'green', 'pink', 'orange', 'black', 'r:', 'g:', 'b:', 'c:']
plate_id = 0
for r in [0, 1, 2, 3, 4, 5]:
    vlegend = []
    for c in [0, 1, 2, 3, 4, 5, 6, 7]:
        vlegend += [('%s%d' % (chr(ord('A') + r), c+1), colors[c], [(plate_id, r, c)])]
    plots.append(('Serine Growth row %s' % chr(ord('A') + r), (0, t_max), (1e-3, 3e-1), 'OD600', vlegend))

for (plot_title, t_range, y_range, y_label, data_series) in plots:
    sys.stderr.write("Plotting %s (%s) ... \n" % (plot_title, y_label))
    fig = figure()
    title(plot_title)
    xlabel('Time (hr)')
    ylabel(y_label)
    
    label2legend = {}
    label2line = []
    for (label, color, cells) in data_series:
        for (plate_id, row, col) in cells:
            (time, values) = get_data(y_label, plate_id, row, col, MES)
            if OD_min:
                values -= OD_min
            line = plot(time, values, color)
            if (label not in label2legend):
                label2line.append((line, label))
                label2legend[label] = label
                if plot_growth_rate:
                    label2legend[label] += ", T(hr) = "
            
            if plot_growth_rate:
                try:
                    growth_rate = vp.fit_growth(time, values, fit_window_size, fit_start_threshold)
                except Exception:
                    sys.stderr.write("WARNING: cannot calculate the growth rate in cell (%d, %d)\n" % (row, col))
                if (growth_rate > 1e-10):
                    label2legend[label] += "%.1f  " % (log(2.0) / growth_rate)
                else:
                    label2legend[label] += "0  "

    rcParams['legend.fontsize'] = 6
    legend([a[0] for a in label2line], [label2legend[a[1]] for a in label2line], loc='lower right')
    yscale('log')
    axis([t_range[0], t_range[1], y_range[0], y_range[1]])
    pp.savefig(fig)

pp.close()