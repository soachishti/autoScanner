from gi.repository import Gtk, Gdk, GLib, GObject
from includes.pyScanLib import pyScanLib
import time
import os
import threading
import sys
import logging

# PROBLEMS TO SOLVE
# - sanitize if input size is greater than scanner limit in scanAreaOkButton()


class autoScanner:

    def __init__(self):

        self.log = logging.getLogger('autoScanner')
        os.remove('includes/autoScanner.log')
        handler = logging.FileHandler('includes/autoScanner.log')
        formatter = logging.Formatter(
            '%(asctime)s %(thread)d %(lineno)d %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)
        self.log.info('autoScanner Initializing')

        self.scanFileName = "Scan"
        self.scannerList = {}
        self.scanning = False
        self.imageType = "JPG"
        self.fileCounter = 0
        self.scannerSize = None

        self.pause = False

        self.builder = Gtk.Builder()
        self.builder.add_from_file("includes/autoScanner.gui")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("autoScanner")
        self.window.show_all()
        self.log.info('GUI loaded')
        self.scan = self.builder.get_object("scan")
        self.pause = self.builder.get_object("pause")
        self.resolutionInput = self.builder.get_object("resolutionValue")
        self.imageTypeInput = self.builder.get_object("imageTypeValue")
        self.scannerListBox = self.builder.get_object("scannerList")
        self.statusLabel = self.builder.get_object("statusLabel")
        self.delayScale = self.builder.get_object("delayScale")
        self.delayValue = self.builder.get_object("delayValue")
        self.scrolledWindow = self.builder.get_object("scrolledWindow")
        self.treeView = self.builder.get_object("treeView")
        self.infoBox = self.builder.get_object("infoBox")
        self.contactDialog = self.builder.get_object("contact")
        self.scanArea = self.builder.get_object("scanArea")
        self.outputType = self.builder.get_object("outputType")
        self.scanAreaTreeView = self.builder.get_object("scanAreaTreeView")
        self.directoryChooser = self.builder.get_object("directoryLocPath")
        self.loadScannerButton = self.builder.get_object("loadScanner")
        self.scanButton = self.builder.get_object("scan")

        self.delayValue.changed()

        # Creating Default folder for scanned files
        if sys.platform == "win32":
            defaultDirectory = os.getenv(
                "HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop\\ScannedFiles\\"
        else:
            defaultDirectory = "/home/ScanFiles/"

        if not os.path.exists(defaultDirectory):
            os.makedirs(defaultDirectory)
        self.directoryChooser.set_current_folder(defaultDirectory)
        # Directory created

        self.treeView.set_visible(False)
        self.log.info('Widget Binded')

        # scannerListBox should be empty
        self.scannerListBox.append_text("None")
        self.scannerListBox.set_active(0)
        self.resolutionInput.set_active(2)
        self.imageTypeInput.set_active(0)
        self.outputType.set_active(0)
        self.infoBox.clear()

        # loading scanners
        scannerLoadingThread = threading.Thread(target=self.loadScanner)
        scannerLoadingThread.daemon = True
        scannerLoadingThread.start()

        self.log.info('autoScanner Initialized')

    def scanFunc(self, button):
        """Triggered when scan button is pressed
        """
        self.scanning = True
        self.log.info('scanFunc Called')
        self.scanButton.set_sensitive(False)  # Block clicking of scan button
        # Block clicking of Refresh Scanner list
        self.scannerListBox.set_sensitive(False)
        # Block selected of scanners
        self.loadScannerButton.set_sensitive(False)

        if self.scannerListBox.get_active_text() != "None":
            self.log.info('Scanners are available')

            # Receiving directory from GUI
            self.directory = self.directoryChooser.get_uri()
            if self.directory != None:
                self.log.info('Scanned image location set')
                self.directory = self.directory[8:] + "/"
                self.directory = self.directory.replace("\\", "/")
                self.treeView.set_visible(True)

                self.log.info('Treeview visible')

                # Start scanning from another thread
                Gdk.threads_enter()
                scanningThread = threading.Thread(target=self.startScanning)
                scanningThread.daemon = True
                scanningThread.start()
                Gdk.threads_leave()

                self.log.info('Scanning thread started')
            else:
                self.log.error('Scanned image location not set')
                self.statusLabel.set_text("Directory not set.")
                self.dialogBox("Directory not set", "Please set directory")

        else:
            self.log.error('Scanner not Found')
            self.dialogBox("Scanner Not Found", "Please connect scanner")
            self.statusLabel.set_text("Scanner Not Found")

    def startScanning(self):
        """This is main function for handling runtime scanning 
        """
        self.log.info('startScanning function called')
        counter = 1
        self.iter = None
        listStoreCounter = 0
        self.log.warning("Going in infinite loop")

        while True:

            if self.pause == True:
                # Stop to notify scanning is paused
                self.log.info('Scanning Paused')
                GObject.idle_add(
                    self.addRow, [counter, "", "Scanning Paused"])
                GObject.idle_add(self.statusLabel.set_text, "Scanning Paused")

            # wait until scanning is paused
            while self.pause == True:
                time.sleep(1)
            else:
                self.log.info('Initializing Again')
                GObject.idle_add(
                    self.statusLabel.set_text, "Initializing Again")

            # get scanner from GUI and set it for use
            activeScanner = self.scannerListBox.get_active_text()
            self.loadScanLib.setScanner(activeScanner)

            # gathering import vairalbe from GUI
            timeDelay = int(self.delayScale.get_value())
            imageType = self.imageTypeInput.get_active_text().lower()
            resolution = self.resolutionInput.get_active_text()
            outputTypeData = self.outputType.get_active_text()
            scanAreaSelectedIndex = self.scanArea.get_active()

            # Revceving file location for saving scanned image
            fileLocation = self.fileName(
                self.directory, self.scanFileName, imageType, counter)

            # Get scanAreaModel
            scanAreaModel = self.scanArea.get_model()
            item = scanAreaModel[scanAreaSelectedIndex]
            # Check whether scan Entire area or Custom
            if item[1] != "Entire":
                self.log.info('Scanning selected area')
                inches = item[0].split(' ')

                if float(inches[2]) <= self.scannerSize[2] and float(inches[3]) <= self.scannerSize[2]:
                    self.loadScanLib.setScanArea(
                        inches[0], inches[1], inches[2], inches[3])
                else:
                    self.scanButton.set_sensitive(True)
                    self.log.error('Setting Area value were wrong')
                    self.log.error("Stopped")
                    GObject.idle_add(
                        self.statusLabel.set_markup, '<span color="red">Custom setting out of range</span>')
                    self.loadScanLib.closeScanner()
                    return -1
            else:
                self.log.info('Scanning Entire Area')

            GObject.idle_add(self.statusLabel.set_text, "Scanning...")
            if not self.iter:
                GObject.idle_add(
                    self.addRow, [counter, fileLocation, "Scanning..."])
            else:
                GObject.idle_add(self.addRowData, listStoreCounter, 0, counter)
                GObject.idle_add(
                    self.addRowData, listStoreCounter, 1, fileLocation)
                GObject.idle_add(
                    self.addRowData, listStoreCounter, 2, "Scanning...")

            # setting DPI to scanners
            self.loadScanLib.setDPI(float(resolution))  # DPI

            if outputTypeData == "Black & White":
                outputTypeData = "bw"
            elif outputTypeData == "Grayscale":
                outputTypeData = "gray"
            elif outputTypeData == "Color":
                outputTypeData = "color"

            # setting image type to scanner
            self.loadScanLib.setPixelType(
                outputTypeData.lower())  # bw/gray/color

            # Scanning
            self.log.info('Scanning started ID = %s', counter)
            PIL = self.loadScanLib.scan()
            self.log.info('Scanning #%s finished', counter)
            self.loadScanLib.closeScanner()

            GObject.idle_add(
                self.addRowData, listStoreCounter, 2, "Saving Image")

            # Saving Image
            PIL.save(fileLocation)
            self.log.info('Scanned Image Saved')
            del PIL

            GObject.idle_add(
                self.addRowData, listStoreCounter, 2, "Scanning Complete")

            counter += 1
            listStoreCounter += 1
            if self.pause != True:
                self.log.info('Time Delay')
                GObject.idle_add(
                    self.addRow, [counter, "", "Time Delay " + str(timeDelay) + " second(s)"])

                GObject.idle_add(self.statusLabel.set_text, "Time Delay")
                time.sleep(timeDelay)  # Time delay between scanning

    def addRow(self, row):
        """Special function for startScanning.
        Implemented because by appending value it return True which 
        re-queue GObject.idle_add which is not wanted
        """
        self.iter = self.infoBox.append(row)
        # 'False' because idle_add would re-queue
        return False

    def addRowData(self, index, column, value):
        """Special function for startScanning.
        Implemented because by default setting value 
        to variable return True which re-queue 
        GObject.idle_add which is not wanted
        """
        self.infoBox[index][column] = value
        return False  # requirement for GObject.idle_add

    def scanAreaChanged(self, widget):
        """Triggered when scanArea Combo Box value change
        """
        scanAreaSelectedIndex = self.scanArea.get_active()
        self.scanAreaModel = self.scanArea.get_model()

        item = self.scanAreaModel[scanAreaSelectedIndex]

        # If selected item is Custom
        if item[1] == "Custom":
            self.customIter = self.scanAreaModel.get_iter(
                scanAreaSelectedIndex)

            # show scanAreaWindows
            self.scanAreaWindow = self.builder.get_object("scanAreaWindow")
            self.scanAreaWindow.show_all()

            self.scanAreaStore = self.builder.get_object("scanAreaStore")
            self.widthData = self.builder.get_object("width")
            self.heightData = self.builder.get_object("height")
            self.topData = self.builder.get_object("top")
            self.leftData = self.builder.get_object("left")
            self.unit = self.builder.get_object("unit")
            self.unit.set_active(0)

            if item[0] != "Custom":
                # If value are already set place them
                self.topData.set_text(str(self.scanAreaData[0]))
                self.leftData.set_text(str(self.scanAreaData[1]))
                self.widthData.set_text(str(self.scanAreaData[2]))
                self.heightData.set_text(str(self.scanAreaData[3]))
                self.unit.set_active(self.activeUnit)
            elif self.scannerSize:
                # Default values generated from loadScanner()
                self.widthData.set_text(str(self.scannerSize[2]))
                self.heightData.set_text(str(self.scannerSize[3]))

    def scanAreaOkButton(self, widget):
        """This function would set scanArea data receive from custom windows to column '0' of scanAreaModel
        """
        unit = self.unit.get_active_text()
        width = float(self.widthData.get_text())
        height = float(self.heightData.get_text())
        top = float(self.topData.get_text())
        left = float(self.leftData.get_text())
        self.scanAreaData = (left, top, width, height)

        if unit == "pixels":
            # If unit is pixel then convert data to Inches
            width = self.loadScanLib.pixelToInch(width)
            height = self.loadScanLib.pixelToInch(height)
            top = self.loadScanLib.pixelToInch(top)
            left = self.loadScanLib.pixelToInch(left)

        elif unit == "cm":
            # If unit is cm then convert data to Inches
            width = self.loadScanLib.cmToInch(width)
            height = self.loadScanLib.cmToInch(height)
            top = self.loadScanLib.cmToInch(top)
            left = self.loadScanLib.cmToInch(left)

        self.activeUnit = self.unit.get_active()
        customLayout = "%s %s %s %s" % (left, top, width, height)
        # Setting data to column '0' and self.customIter is generated in
        # scanAreaChanged()
        self.scanAreaModel.set_value(self.customIter, 0, customLayout)
        self.scanAreaWindow.hide()

    def fileName(self, directory, fileName, fileExt, count=1):
        """This would check for fileName whether available in directory or not 
        It add concatenate number to fileName
        Return file name which doesn't exit
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Returning file should not have 1
        if count == 1 and not self.fileCounter:
            # first filename without no and another  from 2
            self.fileCounter = count + 1
            fullFileName = fileName + "." + fileExt
        else:
            fullFileName = fileName + "-" + \
                str(self.fileCounter) + "" + "." + fileExt

        while os.path.isfile(directory + fullFileName):
            fullFileName = fileName + "-" + \
                str(self.fileCounter) + "" + "." + fileExt
            self.fileCounter += 1

        return directory + fullFileName

    def pauseFunc(self, button):
        """Trigger when 'Pause' or resume button pressed
        It set self.pause to False to pause and True to resume
        It changes button sensitivity of scannerListBox and loadScannerButton(Refresh Scanner List)
        """
        if self.scanning == True:
            if self.scannerListBox.get_sensitive() == False:
                self.loadScannerButton.set_sensitive(True)
                self.scannerListBox.set_sensitive(True)
            else:
                self.loadScannerButton.set_sensitive(False)
                self.scannerListBox.set_sensitive(False)

            self.pauseButton = self.builder.get_object("pause")
            if self.pauseButton.get_label() == "Pause":
                # Just status label message
                self.statusLabel.set_text("Pause in next turn")
                self.pause = True
                # Change button text to Resume
                self.pauseButton.set_label("Resume")
            else:
                self.pause = False
                # Change button text to Pause
                self.pauseButton.set_label("Pause")
                self.statusLabel.set_text("Resuming")

    def loadScannerButton(self, button):
        """Triggered when 'Refresh Scanner List' is pressed
        It started another thread for loadScanner otherwise window would freezes for moment
        """
        scannerLoadingThread = threading.Thread(target=self.loadScanner)
        scannerLoadingThread.daemon = True
        scannerLoadingThread.start()

    def loadScanner(self):
        """Load Scanner and add them to Scanners combox Box (scannerListBox)
        """
        self.log.info("Loading Scanner")
        if len(self.scannerList) == 0:
            self.loadScanLib = pyScanLib()
            scanners = self.loadScanLib.getScanners()

            if scanners:
                self.scannerListBox.remove(0)
            for scanner in scanners:
                self.scannerListBox.append_text(scanner)
                self.scannerList[scanner] = scanner

            noOfScanner = len(scanners)
            if noOfScanner > 0:
                self.scannerListBox.set_active(0)

        # Selected first scanner available and get its size and save it to self.scannerSize
        # then close the scanner
        #
        # This is needed for 'Custom' window default values (width and height)
        self.log.info("Receving scanner size")
        activeScanner = self.scannerListBox.get_active_text()
        if activeScanner != None:
            self.loadScanLib.setScanner(activeScanner)
            self.scannerSize = self.loadScanLib.getScannerSize()[0]
            self.loadScanLib.closeScanner()
            self.log.info("Scanner Size Received")
            self.log.info("Current Scanner instance destroyed")
        else:
            self.log.info("Scanner Size couldn't be received")

    def dialogBox(self, message, explanation=""):
        """Create dailog box and show 'message' given in parameter
        """
        dialog = Gtk.MessageDialog(
            self.window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, message)
        dialog.format_secondary_text(explanation)
        response = dialog.run()
        dialog.destroy()

    def exit(self, *args):
        """Close pyScanLib and quit program
        """
        # self.loadScanLib.close()
        self.log.info('Program Terminated')
        Gtk.main_quit()

    def onlyInt(self, widget):
        """Triggered when person enter no integer value to Custom windows input box
        """
        str = widget.get_text().strip()
        if str == "":
            widget.set_text('0')
        else:
            widget.set_text(''.join([i for i in str if i in '0123456789.']))

    def autoScroll(self, widget, event, data=None):
        """Auto scroll infoBox(status treeview) to the end
        """
        try:
            adj = self.scrolledWindow.get_vadjustment()
            adj.set_value(adj.get_upper() - adj.get_page_size())
        except:
            pass

    def contactDialog(self, button):
        """Show dailog box when receive 'About' button clicked signal
        """
        self.dialogBox("Report Issue", "Email: soachishti@outlook.com")


GObject.threads_init()
window = autoScanner()
Gtk.main()
