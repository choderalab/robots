from util import CollectData, WriteCSV, WriteToDatabase, FitGrowth
from matplotlib.backends.backend_pdf import PdfPages
import sys
import pylab
import logging

################################################################################

import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
import sqlite3

class TkFileDialogExample(Tkinter.Frame):
    def __init__(self, root):
        self.MES = None
        self.N_ROWS = 8
        self.N_COLS = 12
        self.selected_plate_id = None
        
        Tkinter.Frame.__init__(self, root)
    
        self.button_input = Tkinter.Button(self, text='select result file ...', command=self.AskOpenFile)
        self.button_input.grid(row=0, column=1, columnspan=2, pady=15)

        self.label_plate = Tkinter.Label(self, text='select plate ID: ')
        self.label_plate.grid(row=0, column=3, columnspan=2, sticky=Tkconstants.E)
        self.list_plate_ids = Tkinter.Listbox(self, height=3)
        self.list_plate_ids.grid(row=0, column=5, columnspan=2, sticky=Tkconstants.W)
        self.list_plate_ids.bind("<Button-1>", self.SelectPlate)
        
        self.label_label = Tkinter.Label(self, text='select reading label: ')
        self.label_label.grid(row=0, column=7, columnspan=2, sticky=Tkconstants.E)
        self.list_labels = Tkinter.Listbox(self, height=3)
        self.list_labels.grid(row=0, column=9, columnspan=2, sticky=Tkconstants.W)

        
        for c in xrange(self.N_COLS):
            Tkinter.Label(self, text='%d' % (c+1)).grid(row=1, column=c+1)
        for r in xrange(self.N_ROWS):
            Tkinter.Label(self, text=chr(ord('A') + r)).grid(row=r+1, column=0, 
                                                             sticky=Tkconstants.E, padx=10)

        self.text_matrix = {}
        for r in xrange(self.N_ROWS):
            for c in xrange(self.N_COLS):
                self.text_matrix[r,c] = Tkinter.Entry(self, width=10)
                self.text_matrix[r,c].grid(row=r+1, column=c+1, padx=3, pady=3)

        self.button_savepdf = Tkinter.Button(self, text='save to PDF ...',
                                             command=self.asksaveaspdf,
                                             state=Tkconstants.DISABLED)
        self.button_savepdf.grid(row=self.N_ROWS+1, column=1, columnspan=2, pady=5)

        self.button_savecsv = Tkinter.Button(self, text='save to CSV ...',
                                             command=self.asksaveascsv,
                                             state=Tkconstants.DISABLED)
        self.button_savecsv.grid(row=self.N_ROWS+1, column=3, columnspan=2, pady=5)

        self.button_quit = Tkinter.Button(self, text='Quit',
                                             command=self.quit)
        self.button_quit.grid(row=self.N_ROWS+1, column=5, columnspan=2, pady=5)
        
    def AskOpenFile(self):
        """
            Opens and parses the robot result file (.tar or .tar.gz)
        """
        tar_fname = tkFileDialog.askopenfilename(
            filetypes=[('gzip files', '.gz'), ('tar files', '.tar'), ('all files', '.*')])
        if tar_fname:
            logging.debug("Collecting data from: %s" % (tar_fname))
            self.MES = CollectData(tar_fname)
            if self.MES:
                self.button_savepdf.configure(state=Tkconstants.ACTIVE)
                self.button_savecsv.configure(state=Tkconstants.ACTIVE)
                
                # populate the plate ID list
                self.list_plate_ids.delete(0, Tkconstants.END)
                for item in sorted(self.MES.keys()):
                    self.list_plate_ids.insert(Tkconstants.END, item)

    def SelectPlate(self, event=None):
        try:
            selection = int(self.list_plate_ids.curselection()[0])
        except IndexError:
            self.selected_plate_id = None
            return
        
        self.selected_plate_id = self.list_plate_ids.get(selection)
        logging.debug("Selected plate: %s" % self.selected_plate_id)
        
        # populate the reading label list
        self.list_labels.delete(0, Tkconstants.END)
        for item in sorted(self.MES[self.selected_plate_id].keys()):
            self.list_labels.insert(Tkconstants.END, item)
            
    def GetLabel(self):
        selection = int(self.list_labels.curselection()[0])
        return self.list_labels.get(selection)
    
    def asksaveaspdf(self):
        """
            Writes the plots to a PDF file
        """
        f = tkFileDialog.asksaveasfile(mode='w', filetypes=[('PDf file', '.pdf')])
        self.DrawPlots(f)
        f.close()
        if tkMessageBox.askyesno('Job completed', 
                                 'The program has finished writing to the PDF file.\n'
                                 'Would you like to quit?'):
            self.quit()

    def asksaveascsv(self):
        """
            Writes the raw data to a CSV file
        """
        f = tkFileDialog.asksaveasfile(mode='w', filetypes=[('CSV file', '.csv')])
        WriteCSV(self.MES, f)
        f.close()
        if tkMessageBox.askyesno('Job completed', 
                                 'The program has finished writing to the CSV file.\n'
                                 'Would you like to quit?'):
            self.quit()

    def asksaveassqlite(self):
        """
            Writes the raw data to a CSV file
        """
        f = tkFileDialog.asksaveasfile(mode='w', filetypes=[('SQLITE file', '.sqlite')])
        comm = sqlite3.connect(f)
        WriteToDatabase(self.MES, comm)
        f.close()
        if tkMessageBox.askyesno('Job completed', 
                                 'The program has finished writing to the SQLITE file.\n'
                                 'Would you like to quit?'):
            self.quit()

    def GetData(self, plate_id, reading_label, row, col):
        """
            When the experimental data is broken into more than one XLS sheet, this method
            concatenates the data into one series and returns it as if it was from one source.
        """
        well = (row, col)
        time_list = sorted(self.MES[plate_id][reading_label].keys())
        if not time_list:
            return None, None
        value_list = [self.MES[plate_id][reading_label][time][well] for time in time_list]
        time_list = [(time - time_list[0])/3600.0 for time in time_list]
        
        return pylab.array(time_list), pylab.array(value_list)

    def DrawPlots(self, file_handle):
        linewidth = 1
        plot_growth_rate = False
        fit_window_size = 3 # hours
        fit_start_threshold = 0.03

        plots = []  # list of [(title, (t_min, t_max), (y_min, y_max), y_label, vlegend)]
                    # vlegend: list of [(label, color, style (solid/dashed), list of wells [(plate_id, row, col)]]
        t_range = (0, 20) # in hours 
        OD_min = 0
        OD_range = (3e-2, 1e0)
        
        plate_id = self.selected_plate_id
        reading_label = self.GetLabel()

        colors = ['green', 'cyan', 'blue', 'magenta', 'red', 'orange', 'pink']
        vlegend = []
        for row in xrange(self.N_ROWS):
            for col in xrange(self.N_COLS):
                label = self.text_matrix[row, col].get()
                if label:
                    vlegend.append((label, colors.pop(), 'solid', [(plate_id, row, col)]))
                
        plots.append(('plot title', t_range, OD_range, reading_label, vlegend))
                
        pp = PdfPages(file_handle)
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
                    time, values = self.GetData(plate_id, y_label, row, col)
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

################################################################################

if __name__ == "__main__":
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    
    root = Tkinter.Tk()
    TkFileDialogExample(root).pack()
    root.mainloop()
