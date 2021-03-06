# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 16:56:46 2015

@author: Alexander Hoch
"""

import Tkinter as tk
import numpy as np
import tkMessageBox
import colorsys
from GridEyeKit import GridEYEKit

# Grid Eye related numbers
import bruteForceSearch as bts
import kdNeighborSearch as kds
import neuralSearch as ns
import cv2
import perceptronSearch as ps

class GridEYE_Viewer():

    def __init__(self,root):
        
        """ Initialize Window """
        self.tkroot = root
        self.tkroot.protocol('WM_DELETE_WINDOW', self.exitwindow) # Close serial connection and close window

        """ Initialize variables for color interpolation """
        self.HUEstart= 0.5 #initial color for min temp (0.5 = blue)
        self.HUEend = 1 #initial color for max temp (1 = red)
        self.HUEspan = self.HUEend - self.HUEstart
        
        """ Grid Eye related variables"""
        self. MULTIPLIER = 0.25 # temp output multiplier
        
        """ Initialize Loop bool"""
        self.START = False
              
        """Initialize frame tor temperature array (tarr)"""
        self.frameTarr = tk.Frame(master=self.tkroot, bg='white')
        self.frameTarr.place(x=5, y=5, width = 400, height = 400)
        
        """Initialize pixels tor temperature array (tarr)"""
        self.tarrpixels = []
        for i in range(8):
            #frameTarr.rowconfigure(i,weight=1) # self alignment
            #frameTarr.columnconfigure(i,weight=1) # self alignment
            for j in range(8):
                pix = tk.Label(master=self.frameTarr, bg='gray', text='11')
                spacerx = 1
                spacery = 1
                pixwidth = 40
                pixheight = 40
                pix.place(x=spacerx+j*(spacerx+pixwidth), y=spacery+i*(pixheight+spacery),  width = pixwidth, height = pixheight)
                print 
                self.tarrpixels.append(pix) # attache all pixels to tarrpixel list

        """Initialize frame tor Elements"""
        self.frameElements = tk.Frame(master=self.tkroot, bg='white')
        self.frameElements.place(x=410, y=5, width = 100, height = 400)
        

        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()

        """Initialize controll buttons"""
        self.buttonStart = tk.Button(master=self.frameElements, text='start', bg='white',
                                 command=self.start_update)
        self.buttonStart.pack()
        self.buttonPause = tk.Button(master=self.frameElements, text='pause', bg='white',
                                     command=self.pause_update)
        self.buttonPause.pack()
        self.buttonStop = tk.Button(master=self.frameElements, text='stop', bg='white',
                                 command=self.stop_update)
        self.buttonStop.pack()
        
        """Initialize temperature adjustment"""
        self.lableTEMPMAX = tk.Label(master=self.frameElements, text='Max Temp (red)')
        self.lableTEMPMAX.pack()
        self.MAXTEMP = tk.Scale(self.frameElements, from_=-20, to=120, resolution =0.25)
        self.MAXTEMP.set(31)
        self.MAXTEMP.pack()
        self.lableMINTEMP = tk.Label(master=self.frameElements, text='Min Temp (blue)')
        self.lableMINTEMP.pack()
        self.MINTEMP = tk.Scale(self.frameElements, from_=-20, to=120, resolution =0.25)
        self.MINTEMP.set(27)
        self.MINTEMP.pack()


        """Initialize data collection buttons and input boxes"""
        self.dataCollectionElements = tk.Frame(master=self.tkroot, bg='white')
        self.dataCollectionElements.place(x=520, y=5, width=450, height=400)

        # Label Name
        self.labelDataName = tk.Label(master=self.dataCollectionElements, text="Name")
        self.labelDataName.grid(row=0)
        self.labelEntry = tk.Entry(master=self.dataCollectionElements)
        self.labelEntry.grid(row=0, column=1)

        # Height from ground
        self.labelHeight = tk.Label(master=self.dataCollectionElements, text="Height from ground (y)")
        self.labelHeight.grid(row=1)
        self.labelHeightEntry = tk.Entry(master=self.dataCollectionElements)
        self.labelHeightEntry.grid(row=1, column=1)

        # Average Temp
        self.averageTempInfoLable = tk.Label(master=self.dataCollectionElements, text="Average Temperature")
        self.averageTempInfoLable.grid(row=2)
        self.averageTempLable = tk.Label(master=self.dataCollectionElements, text="NA")
        self.averageTempLable.grid(row=2, column=1)
        self.averageTempCalcButton = tk.Button(master=self.dataCollectionElements, text='Calculate', bg='white',
                                 command=self.calculateAvgTemp)
        self.averageTempCalcButton.grid(row=2, column=2)

        # Distance to object vert, hor
        self.distanceToObjectInfoLabel = tk.Label(master=self.dataCollectionElements, text="Distane to the object")
        self.distanceToObjectInfoLabel.grid(row=3)

        self.distanceZLabel = tk.Label(master=self.dataCollectionElements, text="z:")
        self.distanceZLabel.grid(row=4)
        self.distanceZEntry = tk.Entry(master=self.dataCollectionElements)
        self.distanceZEntry.grid(row=4, column=1)

        self.distanceXLabel = tk.Label(master=self.dataCollectionElements, text="x:")
        self.distanceXLabel.grid(row=5)
        self.distanceXEntry = tk.Entry(master=self.dataCollectionElements)
        self.distanceXEntry.grid(row=5, column=1)

        # save
        self.saveButton = tk.Button(master=self.dataCollectionElements, text='Save Data', bg='white',
                                 command=self.saveData)
        self.saveButton.grid(row=6, column=2)
        # Clear Button
        self.clearButton = tk.Button(master=self.dataCollectionElements, text='Reset', bg='white',
                                 command=self.resetEntries)
        self.clearButton.grid(row=6, column=1)
        self.kit = GridEYEKit()

        # Table Labels
        self.calculateButtonLabel = tk.Label(master=self.dataCollectionElements, text='Calculate', bg='white')
        self.calculateButtonLabel.grid(row=7)

        self.calculateButtonInfoLabel = tk.Label(master=self.dataCollectionElements, text='Results', bg='white')
        self.calculateButtonInfoLabel.grid(row=7, column=1)

        self.checkboxLabel = tk.Label(master=self.dataCollectionElements, text='Is Correct?', bg='white')
        self.checkboxLabel.grid(row=7, column=2)

        # Brute Force button
        self.bruteForce = tk.Button(master=self.dataCollectionElements, text='Brute', bg='white',
                                    command=self.bruteForceSearch)
        self.bruteForce.grid(row=8)
        self.bruteLabel = tk.Label(master=self.dataCollectionElements)
        self.bruteLabel.grid(row=8, column=1)

        self.bruteForceCheckboxVal = tk.IntVar()
        self.bruteForceCheckbox = tk.Checkbutton(master=self.dataCollectionElements, variable=self.bruteForceCheckboxVal)
        self.bruteForceCheckbox.grid(row=8, column=2)

        # KD-search
        self.kdSearch = tk.Button(master=self.dataCollectionElements, text='KdSearch', bg='white',
                                  command=self.kdtSearch)
        self.kdSearch.grid(row=9)
        self.kdSearchLabel = tk.Label(master=self.dataCollectionElements)
        self.kdSearchLabel.grid(row=9, column=1)

        self.kdCheckboxVal = tk.IntVar()
        self.kdCheckbox = tk.Checkbutton(master=self.dataCollectionElements,
                                                 variable=self.kdCheckboxVal)
        self.kdCheckbox.grid(row=9, column=2)

        # Neural- Search
        self.nSearch = tk.Button(master=self.dataCollectionElements, text='NeuralSearch', bg='white',
                                 command=self.neuralSearch)
        self.nSearch.grid(row=10)
        self.nSearchLabel = tk.Label(master=self.dataCollectionElements)
        self.nSearchLabel.grid(row=10, column=1)

        self.nSearchCheckboxVal = tk.IntVar()
        self.nSearchCheckbox = tk.Checkbutton(master=self.dataCollectionElements,
                                                 variable=self.nSearchCheckboxVal)
        self.nSearchCheckbox.grid(row=10, column=2)

        # Perceptron- Search
        self.pSearch = tk.Button(master=self.dataCollectionElements, text='PerceptronSearch', bg='white',
                                 command=self.perceptronSearch)
        self.pSearch.grid(row=11)
        self.pSearchLabel = tk.Label(master=self.dataCollectionElements)
        self.pSearchLabel.grid(row=11, column=1)

        self.pSearchCheckboxVal = tk.IntVar()
        self.pSearchCheckbox = tk.Checkbutton(master=self.dataCollectionElements,
                                                 variable=self.pSearchCheckboxVal)
        self.pSearchCheckbox.grid(row=11, column=2)

        # Save results
        self.resultDescriptionLabel = tk.Label(master=self.dataCollectionElements, text="Decription: ")
        self.resultDescriptionLabel.grid(row=12)

        self.resultDescriptionEntry = tk.Entry(master=self.dataCollectionElements)
        self.resultDescriptionEntry.grid(row=12, column=1)

        self.saveResultButton = tk.Button(master=self.dataCollectionElements, text='Save results', bg='white',
                                          command=self.saveResults)
        self.saveResultButton.grid(row=12, column=2)

        # Load tarr
        self.loadEntry = tk.Entry(master=self.dataCollectionElements)
        self.loadEntry.grid(row=13, column=1)
        self.loadEntryButton = tk.Button(master=self.dataCollectionElements, text='Load the data on the left', bg='white',
                                         command=self.loadData)
        self.loadEntryButton.grid(row=13, column=2)

    def loadData(self):
        self.START = True
        tarr = map(float, self.loadEntry.get().split(','))
        self.save_get_tarr = self.get_tarr
        self.get_tarr = lambda: tarr
        self.update_tarrpixels()
        self.buttonPause.config(text='resume')
        self.START = False

    def saveResults(self):
        with open("results.csv", "a") as results:
            results.write(self.resultDescriptionEntry.get() + "," +
                          str(self.bruteForceCheckboxVal.get()) + "," +
                          str(self.kdCheckboxVal.get()) + "," +
                          str(self.nSearchCheckboxVal.get()) + "," +
                          str(self.pSearchCheckboxVal.get()) + "," +
                          ",".join(map(str, self.get_tarr())) + "\n")
        print "Saved Result"

    def perceptronSearch(self):
        self.pSearchLabel.config(text=ps.getMostSimilar(self.get_tarr()))

    def neuralSearch(self):
        self.nSearchLabel.config(text=ns.getMostSimilar(self.get_tarr()))

    def kdtSearch(self):
        self.kdSearchLabel.config(text=', '.join(kds.getMostSimilar(self.get_tarr())))

    def bruteForceSearch(self):
        self.bruteLabel.config(text=', '.join(bts.getMostSimilar(self.get_tarr())))

    def calculateAvgTemp(self):
        self.averageTempLable.config(text=np.average(self.get_tarr()))

    def saveData(self):
        with open("dataset.csv", "a") as dataset:
            dataset.write(self.labelEntry.get() + "," +
                          self.labelHeightEntry.get() + "," +
                          str(self.averageTempLable.cget("text")) + "," +
                          self.distanceZEntry.get() + "," +
                          self.distanceXEntry.get() + "," +
                          ",".join(map(str, self.get_tarr())) + "\n")

    def resetEntries(self):
        asd = 5

    def exitwindow(self):
        """ if windwow is clsoed, serial connection has to be closed!"""
        self.kit.close()
        self.tkroot.destroy()
        
    def stop_update(self):
        """ stop button action - stops infinite loop """
        self.START = False
        self.update_tarrpixels()

    def pause_update(self):
        if self.START:
            self.START = False
            tarr = self.get_tarr()
            self.save_get_tarr = self.get_tarr
            self.get_tarr = lambda: tarr
            self.buttonPause.config(text='resume')
        else:
            self.START = True
            self.get_tarr = self.save_get_tarr
            self.buttonPause.config(text='pause')
            self.update_tarrpixels()

    def start_update(self):
        if self.kit.connect():
            """ start button action -start serial connection and start pixel update loop"""
            self.START = True
            """ CAUTION: Wrong com port error is not handled"""
            self.update_tarrpixels()  
        else:
            tkMessageBox.showerror("Not connected", "Could not find Grid-EYE Eval Kit - please install driver and connect")
            
        
    def get_tarr(self):
        """ unnecessary function - only converts numpy array to tuple object"""
        tarr = []
        for temp in self.kit.get_temperatures(): # only fue to use of old rutines
            for temp2 in temp:
                tarr.append(temp2)
        return tarr
        
    def update_tarrpixels(self):
        """ Loop for updating pixels with values from funcion "get_tarr" - recursive function with exit variable"""
        if self.START == True:
            tarr = self.get_tarr() # Get temerature array
            i = 0 # counter for tarr
            if len(tarr) == len(self.tarrpixels): # check if problem with readout
                for tarrpix in self.tarrpixels:
                    tarrpix.config(text=tarr[i]) # Update Pixel text
                    if tarr[i] < self.MINTEMP.get(): # For colors, set borders to min/max temp
                        normtemp = 0
                    elif tarr[i] > self.MAXTEMP.get(): # For colors, set borders to min/max temp
                        normtemp = 1
                    else:
                        TempSpan = self.MAXTEMP.get() - self.MINTEMP.get()
                        if TempSpan <= 0:   # avoid division by 0 and negative values
                            TempSpan = 1
                        normtemp = (float(tarr[i])-self.MINTEMP.get())/TempSpan #Normalize temperature 0...1
                    h = normtemp*self.HUEspan+self.HUEstart # Convert to HSV colors (only hue used)
                    if h>1:
                        print h
                        print normtemp
                        print self.HUEspan
                        print self.HUEstart
                    bgrgb = tuple(255*j for j in colorsys.hsv_to_rgb(h,1,1)) # convert to RGB colors
                    tarrpix.config(bg=('#%02x%02x%02x' % bgrgb)) # Convert to Hex String
                    i +=1  # incement tarr counter
            else:
                print "Error - temperarure array lenth wrong"
            self.frameTarr.after(10,self.update_tarrpixels) # recoursive function call all 10 ms (get_tarr will need about 100 ms to respond)



root = tk.Tk()
root.title('Grid-Eye Viewer')
root.geometry('900x600')
Window = GridEYE_Viewer(root)
root.mainloop()
