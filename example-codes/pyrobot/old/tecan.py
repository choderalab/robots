import time, calendar, csv
from xml.etree.ElementTree import ElementTree
import tarfile
import pylab
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties


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
    xml_reader = ElementTree()
    xml_reader.parse(fname)
    reading_label = None
    time_in_sec = None
    well = (0, 0)
    measurement = None
    plate_values = {}
    for e in xml_reader.getiterator():
        if e.tag == 'Section':
            reading_label = e.attrib['Name']
            TIME = e.attrib['Time_Start']
            TIME = TIME[:19]
            TS = time.strptime(TIME, fmt)
            time_in_sec = calendar.timegm(TS)
            plate_values[reading_label] = {}
            plate_values[reading_label][time_in_sec] = {}
        elif e.tag == 'Well':
            W = e.attrib['Pos']
            well_row = ord(W[0]) - ord('A')
            well_col = int(W[1:]) - 1
            well = (well_row, well_col)
        elif e.tag == 'Multiple':
            if e.attrib['MRW_Position'] == 'Mean':
                measurement = e.text
                plate_values[reading_label][time_in_sec][well] = float(measurement)
        elif e.tag == 'Single':
            measurement = e.text
            if measurement == "OVER":
                plate_values[reading_label][time_in_sec][well] = None
            else:
                plate_values[reading_label][time_in_sec][well] = float(measurement)
    return plate_values

def CollectData(tar_fname, number_of_plates=None):
    PL = GetPlateFiles(tar_fname, number_of_plates)
    MES = {}
    
    for plate_id in PL:
        MES[plate_id] = None
        for f in PL[plate_id]:
            plate_values = ParseReaderFile(f)
            if MES[plate_id] == None:
                MES[plate_id] = plate_values
            else:
                for reading_label, label_values in plate_values.iteritems():
                    for time_in_sec, time_values in label_values.iteritems():
                        MES[plate_id][reading_label][time_in_sec] = time_values
    return MES

def CollectDataFromSingleFile(xml_fname, plate_id):
    return {plate_id: ParseReaderFile(xml_fname)}

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
                    
def GetCurrentExperimentID(db):
    for row in db.Execute("SELECT max(exp_id) e FROM tecan_experiments"):
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
    
    def get_frame_range(times, mid_frame, windows_size):
        T = times[mid_frame]
        i_range = []
        for i in range(1, len(times)):
            if (times[i-1] > T - window_size/2.0 and times[i] < T + window_size/2.0):
                i_range.append(i)

        if (len(i_range) < 2): # there are not enough frames to get a good estimation
            raise ValueError()
        return i_range

    N = len(cell_count)
    if (N < window_size):
        raise Exception("The measurement time-series is too short (smaller than the windows-size)")

    t_mat = pylab.matrix(time).T
    
    # normalize the cell_count data by its minimum (
    c_mat = pylab.matrix(cell_count).T - min(cell_count)
    if c_mat[-1, 0] == 0:
        c_mat[-1, 0] = min(c_mat[pylab.find(c_mat > 0)])

    for i in pylab.arange(N-1, 0, -1):
        if c_mat[i-1, 0] <= 0:
            c_mat[i-1, 0] = c_mat[i, 0]

    c_mat = pylab.log(c_mat)
    
    res_mat = pylab.zeros((N, 3)) # columns are: slope, offset, error
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
        except ValueError:
            pass

    max_i = res_mat[:,0].argmax()
    
    if plot_figure:
        pylab.hold(True)
        pylab.plot(time, cell_count-min(cell_count))
        pylab.plot(time, res_mat[:,0])
        pylab.plot([0, time.max()], [start_threshold, start_threshold], 'r--')
        i_range = get_frame_range(time, max_i, window_size)
        
        x = pylab.hstack([t_mat[i_range, 0], pylab.ones((len(i_range), 1))])
        y = x * pylab.matrix(res_mat[max_i, 0:2]).T
        
        pylab.plot(x[:,0], pylab.exp(y), 'k:', linewidth=4)
        #plot(time, errors / errors.max())
        pylab.yscale('log')
        #legend(['OD', 'growth rate', 'error'])
        pylab.legend(['OD', 'growth rate', 'threshold', 'fit'])
    
    return res_mat[max_i, 0]

def PlotGrowthCurves(data, pdf_fname, t_max=None,
                     plot_growth_rate=False,
                     growth_rate_window_size=4):
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
        fig = pylab.figure()
        fig.hold(True)
        pylab.xlabel('Time (hr)', figure=fig)
        pylab.ylabel(reading_label, figure=fig)
        
        unique_labels = {}
        for cell_label, measurements in data[reading_label]:
            #begin_time = measurements[0][0]
            #time_vec = [(time-begin_time)/3600.0 for (time, _) in measurements]
            #time_vec = [int(time) for (time, _) in measurements]
            time_vec = range(len(measurements))
            value_vec = [value for (_, value) in measurements]
            
            # Only calculate growth rate when required.
            growth_rate = None
            if plot_growth_rate:
                growth_rate = FitGrowth(time_vec, value_vec,
                                        window_size=growth_rate_window_size)
                
            unique_labels.setdefault(cell_label, []).append(growth_rate)
            pylab.plot(time_vec, value_vec, '-', label=cell_label, figure=fig)
        pylab.yscale('log')
        pylab.legend(sorted(unique_labels.keys()), prop=size8)
        if t_max:    
            pylab.xlim((0, t_max))
        pp.savefig(fig)
        
        if plot_growth_rate:
            names = sorted(unique_labels.keys())
            averages = sorted([pylab.mean(unique_labels[k]) for k in names])
            errors = sorted([pylab.std(unique_labels[k]) for k in names])
            left = pylab.arange(len(names))
        
            fig2 = pylab.figure()
            pylab.bar(left, averages, yerr=errors, color='b', ecolor='g', figure=fig2)
            pylab.xticks(left, names, rotation=35, fontsize=6)
            pp.savefig(fig2)
                
    pp.close()


    
