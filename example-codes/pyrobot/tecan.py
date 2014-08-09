import time, calendar, csv
import tarfile
import pylab
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from xml.dom.minidom import parse

COLORS = ['g',
          'r',
          'b',
          'c',
          'm',
          'y',
          'k',
          'burlywood',
          'blueviolet',
          'cadetblue',
          'chartreuse',
          'crimson',
          'darkgoldenrod']


def GetColor(i):
    index = i % len(COLORS)
    return COLORS[index]


def ColorMap(items):
    return dict((item, GetColor(i)) for i, item in enumerate(items))


fmt = "%Y-%m-%dT%H:%M:%S"

def RowCol2String(row, col):
    return "%s%02d" % (chr(ord('A') + row), col+1)

def GetPlateFiles(tar_fname, number_of_plates=None):
    PL = {}
    L = []
    
    tar = tarfile.open(tar_fname, 'r')
    
    for fname in tar.getnames():
        if fname[-3:] == 'xml':
            ts = fname[-23:-3] # take only the postfix of the filename - a timestamp
            f = tar.extractfile(fname)
            L.append((ts, f))
        elif number_of_plates is None and fname[-3:] == 'txt': # this is a 'tag' file that only the number of plates
            f = tar.extractfile(fname)
            try:
                number_of_plates = int(f.read())
            except TypeError:
                raise Exception("the .txt file indicating the number of plates is corrupt")
            f.close()
    
    if number_of_plates is None:
        raise Exception("cannot determine the number of plates")
    
    for i, (_t, f) in enumerate(sorted(L)):    
        PL.setdefault(i % number_of_plates, []).append(f)
    
    return PL    

def ParseReaderFile(fname):
    dom = parse(fname)
    header_dom = dom.getElementsByTagName('Header')[0]
    script_dom = dom.getElementsByTagName('Script')[0]
    section_doms = dom.getElementsByTagName('Section')
    plate_values = ParseReaderMeasurementSections(section_doms)
    return header_dom, script_dom, plate_values

def ParseReaderMeasurementSections(section_doms):
    plate_values = {}
    for e in section_doms:
        reading_label = e.getAttribute('Name')
        TIME = e.getAttribute('Time_Start')
        TIME = TIME[:19]
        TS = time.strptime(TIME, fmt)
        time_in_sec = calendar.timegm(TS)
        plate_values[reading_label] = {}
        plate_values[reading_label][time_in_sec] = {}
        data_dom = e.getElementsByTagName('Data')[0]
        for well_dom in data_dom.getElementsByTagName('Well'):
            W = well_dom.getAttribute('Pos')
            well_row = ord(W[0]) - ord('A')
            well_col = int(W[1:]) - 1
            well = (well_row, well_col)
            if well_dom.getAttribute('Type') == 'Single':
                meas_dom = well_dom.getElementsByTagName('Single')[0]
                measurement = meas_dom.firstChild.data
                if measurement == "OVER":
                    plate_values[reading_label][time_in_sec][well] = None
                else:
                    plate_values[reading_label][time_in_sec][well] = float(measurement)
            elif well_dom.getAttribute('Type') == 'Multiple':
                meas_dom = well_dom.getElementsByTagName('Multiple')[0]
                if meas_dom.getAttribute('MRW_Position') == 'Mean':
                    measurement = meas_dom.firstChild.data
                    plate_values[reading_label][time_in_sec][well] = float(measurement)
            
    return plate_values

# Legacy code (parsing a TAR of XML files from the reader is not used anymore)
#
#def CollectData(tar_fname, number_of_plates=None):
#    PL = GetPlateFiles(tar_fname, number_of_plates)
#    MES = {}
#    
#    serial_numbers = set()
#    
#    for plate_id in PL:
#        MES[plate_id] = None
#        for f in PL[plate_id]:
#            serial_number, _header_dom, _script_dom, plate_values = ParseReaderFile(f)
#            serial_numbers.add(serial_number)
#            if MES[plate_id] == None:
#                MES[plate_id] = plate_values
#            else:
#                for reading_label, label_values in plate_values.iteritems():
#                    for time_in_sec, time_values in label_values.iteritems():
#                        MES[plate_id][reading_label][time_in_sec] = time_values
#                        
#    if len(serial_numbers) > 0:
#        if len(serial_numbers) > 1:
#            sys.stderr('WARNING: not all serial numbers are the same in the provided XML files')
#        serial_number = serial_numbers.pop()
#    else:
#        sys.stderr('WARNING: there are no serial numbers in the provided XML files')
#        serial_number = ''
#    return serial_number, MES
#

def CollectDataFromSingleFile(xml_fname):
    header_dom, script_dom, plate_values = ParseReaderFile(xml_fname)
    return header_dom, script_dom, {plate_id: plate_values}

def GetSerialNumber(header_dom):
    return header_dom.getElementsByTagName('SerialNumber')[0].firstChild.data

def WriteCSV(MES, f):
    """
        Write the data into a directory, each reading-label in its own CSV file.
        The columns of the CSV file are: reading-label, plate, well, time, measurement.
        The rows is ordered according to these columns.
    """
    init_time = GetExpInitTime(MES)
    csv_writer = csv.writer(f)
    csv_writer.writerow(['plate', 'reading label', 'row', 'col', 
                         'time', 'measurement'])
    for plate_id, plate_values in sorted(MES.iteritems()):
        for reading_label, label_values in sorted(plate_values.iteritems()):
            for time_in_sec, time_values in sorted(label_values.iteritems()):
                relative_time_in_hr = (time_in_sec - init_time)/3600.0
                for well, value in sorted(time_values.iteritems()):
                    csv_writer.writerow([plate_id, reading_label, 
                        well[0], well[1], "%.3f" % relative_time_in_hr, value])

def GetExpInitTime(MES):
    all_time_values = []
    for plate_values in sorted(MES.values()):
        for label_values in sorted(plate_values.values()):
            all_time_values += label_values.keys()
    if all_time_values:
        return min(all_time_values)
    else:
        raise ValueError("The experiment has no data, cannot find the init time")
                    
def GetCurrentExperimentID(db, serial_number=None):
    query = "SELECT max(exp_id) e FROM tecan_experiments"
    if serial_number is not None:
        query += " WHERE serial_number = \"%s\"" % serial_number
    for row in db.Execute(query):
        return row[0]
    raise ValueError("Database Error: no experiments present in tecan_experiments table")
            
def GetExpDate(MES):
    init_time = GetExpInitTime(MES)
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(init_time))
                    
def WriteToDatabase(MES, db, exp_id):
    for plate_id, plate_values in sorted(MES.iteritems()):
        for reading_label, label_values in sorted(plate_values.iteritems()):
            for time_in_sec, time_values in sorted(label_values.iteritems()):
                for well, value in sorted(time_values.iteritems()):
                    db.Insert('tecan_readings', [exp_id, plate_id, 
                        reading_label, well[0], well[1], time_in_sec, value])
    return exp_id

def FitGrowth(time, cell_count, window_size, start_threshold=0.01, plot_figure=False):
    """Compute growth rate.
    
    Args:
        time: list of data point time measurements (whatever time units you like).
        cell_count: list of cell counts at each time point.
        window_size: the size of the time window (same time units as above).
        start_threshold: minimum cell count to consider.
        plot_figure: whether or not to plot.
    
    Returns:
        growth rate in 1/(time unit) where "time unit" is the unit used above.
    """
    
    def get_frame_range(times, mid_frame, window_size):
        T = times[mid_frame]
        i_range = []
        for i in range(1, len(times)):
            if (times[i-1] > T - window_size/2.0 and times[i] < T + window_size/2.0):
                i_range.append(i)

        if (len(i_range) < 2): # there are not enough frames to get a good estimation
            raise ValueError()
        return i_range

    N = len(cell_count)
    #if (N < window_size):
    #    raise Exception("The measurement time-series is too short (smaller than the windows-size)")

    t_mat = pylab.matrix(time).T
    
    # normalize the cell_count data by its minimum
    count_matrix = pylab.matrix(cell_count).T
    norm_counts = count_matrix - min(cell_count)
    c_mat = pylab.matrix(norm_counts)
    if c_mat[-1, 0] == 0:
        c_mat[-1, 0] = min(c_mat[pylab.find(c_mat > 0)])

    for i in pylab.arange(N-1, 0, -1):
        if c_mat[i-1, 0] <= 0:
            c_mat[i-1, 0] = c_mat[i, 0]

    c_mat = pylab.log(c_mat)
    
    res_mat = pylab.zeros((N, 4)) # columns are: slope, offset, error, avg_value
    for i in range(N):
        try:
            # calculate the indices covered by the window
            i_range = get_frame_range(time, i, window_size)
            x = pylab.hstack([t_mat[i_range, 0], pylab.ones((len(i_range), 1))])
            y = c_mat[i_range, 0]
            if min(pylab.exp(y)) < start_threshold: # the measurements are still too low to use (because of noise)
                raise ValueError()
            (a, residues) = pylab.lstsq(x, y)[0:2]
            res_mat[i, 0] = a[0]
            res_mat[i, 1] = a[1]
            res_mat[i, 2] = residues
            res_mat[i, 3] = pylab.mean(count_matrix[i_range,0])
        except ValueError:
            pass

    max_i = res_mat[:,0].argmax()
    
    abs_res_mat = pylab.array(res_mat)
    abs_res_mat[:,0] = pylab.absolute(res_mat[:,0])
    order = abs_res_mat[:,0].argsort(axis=0)
    stationary_indices = pylab.array(filter(lambda x: x >= max_i, order))
    stationary_level = res_mat[stationary_indices[0], 3]
    
    if plot_figure:
        pylab.hold(True)
        pylab.plot(time, norm_counts)
        pylab.plot(time, res_mat[:,0])
        pylab.plot([0, time.max()], [start_threshold, start_threshold], 'r--')
        i_range = get_frame_range(time, max_i, window_size)
        
        x = pylab.hstack([t_mat[i_range, 0], pylab.ones((len(i_range), 1))])
        y = x * pylab.matrix(res_mat[max_i, 0:2]).T
        pylab.plot(x[:,0], pylab.exp(y), 'k:', linewidth=4)
                
        pylab.plot([0, max(time)], [stationary_level, stationary_level])
        
        pylab.yscale('log')
        pylab.legend(['OD', 'growth rate', 'threshold', 'fit', 'stationary'])
    
    return res_mat[max_i, 0], stationary_level


def PlotGrowthCurves(data, pdf_fname, t_max=None,
                     plot_growth_rate=False,
                     growth_rate_window_size=5):
    """
    Plot growth curves for all data and save as PDF with given filename.
    
    Args:
        data: a dictionary whose keys are reading-labels, and values are:
            (cell_label, [(time0, value0), (time1, value1), ...])
        pdf_fname: the filename to write the PDF to.
        plot_growth_rate: if True, plot histogram of growth rates for repeats
            with the same name.
        growth_rate_window_size: the size (in hours) of the time window to consider
            when calculating the growth rate.
    """
    linewidth = 0.5
    fit_window_size = 3 # hours
    fit_start_threshold = 0.03
    size8 = FontProperties(size=8)

    pp = PdfPages(pdf_fname)
    for reading_label in data.keys():
        norm_growth_fig = pylab.figure()
        norm_growth_fig.hold(True)
        pylab.xlabel('Time (Min)', figure=norm_growth_fig)
        pylab.ylabel(reading_label, figure=norm_growth_fig)
        
        unique_labels = dict((l, []) for l, _ in data[reading_label])
        seen_labels = set()
        colormap = ColorMap(sorted(unique_labels.keys()))
        for cell_label, measurements in data[reading_label]:
            time_vec = pylab.array([t for (t, _) in measurements])
            time_vec = (time_vec - min(time_vec)) / 60.0
            value_vec = [value for (_, value) in measurements]
            norm_values = pylab.array(value_vec)
            norm_values = norm_values - min(norm_values) 
            
            # Only calculate growth rate when required.
            growth_rate = (None, None)
            if plot_growth_rate:
                window_size = time_vec[growth_rate_window_size] - time_vec[0]
                growth_rate = FitGrowth(time_vec, value_vec,
                                        window_size=window_size,
                                        start_threshold=0.015)
            
            unique_labels.setdefault(cell_label, []).append(growth_rate)
            
            label = None
            if cell_label not in seen_labels:
                seen_labels.add(cell_label)
                label = cell_label
                
            pylab.plot(time_vec, norm_values, '-', label=label,
                       color=colormap[cell_label], figure=norm_growth_fig)
            
        pylab.yscale('log', figure=norm_growth_fig)
        pylab.legend(prop=size8, loc="upper left")
        if t_max:    
            pylab.xlim((0, t_max), figure=norm_growth_fig)
        pp.savefig(norm_growth_fig)
        
        if plot_growth_rate:
            names = sorted(unique_labels.keys())
            tuples_per_name = [unique_labels[k] for k in names]
            rates = [[t[0] for t in l]
                     for l in tuples_per_name]
            stationaries = [[t[1] for t in l]
                            for l in tuples_per_name]
            
            average_rates = [pylab.mean(r) for r in rates]
            average_stationaries = [pylab.mean(s) for s in stationaries]
            rate_errors = [pylab.std(r) for r in rates]
            stationary_errors = [pylab.std(s) for s in stationaries]
        
            fig2 = pylab.figure()
            pylab.errorbar(average_stationaries, average_rates,
                           xerr=stationary_errors, yerr=rate_errors,
                           fmt='b.', ecolor='g', figure=fig2)
            pylab.xlabel('Stationary Level', figure=fig2)
            pylab.ylabel('Growth Rate (Gen/Min)', figure=fig2)
            
            for x, y, name in zip(average_stationaries, average_rates, names):
                pylab.text(x, y, name, fontsize=6, rotation=30, figure=fig2)
            pp.savefig(fig2)
            
            fig3 = pylab.figure()
            left = pylab.arange(len(names))    
            pylab.bar(left, average_rates, yerr=rate_errors, color='b', ecolor='g', figure=fig3)
            pylab.xticks(left, names, rotation=35, fontsize=6, figure=fig3)
            pp.savefig(fig3)
    
    pylab.show()
    pp.close()


    
