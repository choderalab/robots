import sys, os
import pylab
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
from pytecan.util import CollectData, FitGrowth, RowCol2String
from toolbox.util import _mkdir

def get_data(reading_label, plate_id, row, col, MES):
    """
        When the experimental data is broken into more than one XLS sheet, this method
        concatenates the data into one series and returns it as if it was from one source.
    """
    well = (row, col)
    time_list = sorted(MES[plate_id][reading_label].keys())
    if not time_list:
        return None, None
    value_list = [MES[plate_id][reading_label][time][well] for time in time_list]
    time_list = [(time - time_list[0])/3600.0 for time in time_list]
    
    return pylab.array(time_list), pylab.array(value_list)

input_name = '2011-02-28_lycopene1'
MES = CollectData("../res/tecan/%s.tar.gz" % input_name, number_of_plates=2)
pp = PdfPages('../res/tecan/%s.pdf' % input_name)

#pylab.rcParams['text.usetex'] = True
pylab.rcParams['legend.fontsize'] = 6
#pylab.rcParams['font.family'] = 'sans-serif'
#pylab.rcParams['font.size'] = 8
#pylab.rcParams['lines.linewidth'] = 0.3
#pylab.rcParams['lines.markersize'] = 2
#pylab.rcParams['figure.figsize'] = [5, 10]
#pylab.rcParams['figure.subplot.hspace'] = 0.3
#pylab.figure()

linewidth = 2
plot_growth_rate = True
fit_window_size = 3 # hours
fit_start_threshold = 0.03

plots = [] # (title, victor_index, (t_min, t_max), (y_min, y_max), y_label, 
t_max = 26 # in hours
OD_min = 0

colors = ['green', 'cyan', 'blue']
for p in [1]:
    for i in xrange(2):
        for r in xrange(8):
            vlegend = []
            vlegend += [(RowCol2String(r, 3*i+j), colors[j], 'solid', [(p, r, 3*i+j)]) for j in xrange(3)]
            plots.append((RowCol2String(r, 3*i) + '-' + RowCol2String(r, 3*i+2), (0, t_max), (3e-2, 1e0), 'OD600', vlegend))

for plot_title, t_range, y_range, y_label, data_series in plots:
    sys.stderr.write("Plotting %s (%s) ... \n" % (plot_title, y_label))
    fig = pylab.figure()
    pylab.title(plot_title)
    pylab.xlabel('Time (hr)')
    pylab.ylabel(y_label)
    
    label2legend = {}
    label2line = []
    for label, color, linestyle, cells in data_series:
        for plate_id, row, col in cells:
            time, values = get_data(y_label, plate_id, row, col, MES)
            if not len(time):
                continue
            if OD_min:
                values -= OD_min
            line = pylab.plot(time, values, color, linestyle=linestyle, linewidth=linewidth)
            if label not in label2legend:
                label2line.append((line, label))
                label2legend[label] = label
                if plot_growth_rate:
                    label2legend[label] += ", T(min) = "
            
            if plot_growth_rate:
                growth_rate = FitGrowth(time, values, fit_window_size, fit_start_threshold)
                if growth_rate > 1e-10:
                    label2legend[label] += "%.0f  " % (60.0 * pylab.log(2.0) / growth_rate)
                else:
                    label2legend[label] += "0  "

    pylab.legend([a[0] for a in label2line], [label2legend[a[1]] for a in label2line], loc='lower right')
    pylab.yscale('log')
    pylab.axis([t_range[0], t_range[1], y_range[0], y_range[1]])
    pp.savefig(fig)

pp.close()