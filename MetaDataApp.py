import random
import math
import os
import numpy as np
from tkinter import *
from tkinter import font
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfilename
from PIL import ImageTk, Image
import wave
import struct

class MetaDataApp:
    def __init__(self, root):
        frame = Frame(root)
        frame.pack()
        textSize = 30
        defaultFont = font.nametofont("TkDefaultFont")
        defaultFont.configure(size=textSize)

        root.title("Meta Data Modifier") 
        maxColumns=6
        maxRows=8
        root.columnconfigure(maxColumns)
        root.rowconfigure(maxRows)
        
        self.data = []
        
        mainLabel = Label(frame, text="Convert To:")
        mainLabel.grid(column=0, row=0, pady=1, sticky='e')

        
        self.txtButton=Button(frame, text="Text", command=self.textButtonCmd)
        self.txtButton.grid(column=1, row=0, pady=1, padx=1, sticky='nesw')

        self.gifButton=Button(frame, text="GIF", command=self.gifButtonCmd)
        self.gifButton.grid(column=2, row=0, pady=1, padx=1, sticky='nesw')

        self.gifButton=Button(frame, text="WAV", command=self.wavButtonCmd)
        self.gifButton.grid(column=3, row=0, pady=1, padx=1, sticky='nesw')

        self.gifButton=Button(frame, text="EXE", command=self.exeButtonCmd)
        self.gifButton.grid(column=4, row=0, pady=1, padx=1, sticky='nesw')

        self.initRandomSizeWidgets(frame, 2) 


        textRow=3
        textEndColumn=maxColumns-2

        
        self.binaryDisplay=scrolledtext.ScrolledText(frame, wrap='word', font=("consolas", textSize), height=5, width=10*4)
        self.binaryDisplay.grid(column=0, columnspan=maxColumns-1, row=textRow, rowspan=maxRows-textRow)

        self.randomizeData("32")

        
    def initRandomSizeWidgets(self, frame, rowNum):
        dropDownLabel=Label(frame, text="Bytes To Create:")
        dropDownLabel.grid(column=0, row = rowNum, pady=1, sticky='e')

        self.variable = IntVar()
        sizes=[]
        size = 32
        while(size < 0x2000):
            sizes.append(str(size))
            size = size<<1
        self.variable.set(sizes[0])

        self.sizeDrop=OptionMenu(frame, self.variable, *sizes, command=self.randomizeData)
        self.sizeDrop.grid(column=1, row=rowNum, pady=1, sticky='ew')

        #createBytesButton = Button(frame, text="GO", command=self.randomizeData)
        #createBytesButton.grid(column=2, row=rowNum, pady=1, sticky='ew')

    def randomizeData(self, choice):
        self.data=[]
        numBytes = int(choice)
        firstByte=[0x4, 0x5, 0x80, 0x81, 0x83, 0x00, 0x01, 0x02, 0x03]
        self.data.append( firstByte[random.randrange(len(firstByte))])

        while(len(self.data) < numBytes):
            self.data.append(random.randrange(0,256))
        self.binaryDisplay.delete('0.0', 'end')
            
        self.binaryDisplay.insert('end', format(self.data[0], "08b"))
        for index in range(1,len(self.data)):
            self.binaryDisplay.insert('end', " " + format(self.data[index], "08b"))  

    
    def textButtonCmd(self):
        files=[("Text", "*.txt")]
        f = asksaveasfilename(defaultextension=".txt", filetypes=files) 
        if f is None or len(f) == 0:
            return
        txtFile = open(f, 'w+b')
        txtFile.write(bytearray(self.data))
        txtFile.close()

    def gifButtonCmd(self):
        files=[("Gif", "*.gif")]
        f = asksaveasfilename(defaultextension=".gif", filetypes=files) 
        if f is None or len(f) == 0:
            return
        gifPixels = []
        numPixels = len(self.data) / 3
        size = int(math.sqrt(numPixels))
        
        for row in range(0, size * size * 3, size * 3):
            tempList = []
            for index in range(row, row + size * 3, 3):
                tempList.append((self.data[index], self.data[index + 1], self.data[index + 2]))
            gifPixels.append(tempList)

        pixelArray=np.array(gifPixels, dtype=np.uint8)
        gifImage = Image.fromarray(pixelArray)
        gifImage.save(f) 

    def wavButtonCmd(self):
        files=[("wav", "*.wav")]
        f = asksaveasfilename(defaultextension=".wav", filetypes=files) 
        if f is None or len(f) == 0:
            return
        

        waveFile = wave.open(f, mode='wb')
        waveFile.setnchannels(1)
        waveFile.setsampwidth(2)
        waveFile.setframerate(500)
        for index in range(0, len(self.data), 2):
            value = (self.data[index] << 8) | self.data[index + 1]
            value = value & 0x7fff
            if (self.data[index] & 0x80) != 0:
                value = value * -1
            sound = struct.pack('<h', value)
            waveFile.writeframesraw(sound)
        waveFile.close()



    def exeButtonCmd(self):
        files=[("exe", "*.exe")]
        f = asksaveasfilename(defaultextension=".exe", filetypes=files) 
        if f is None or len(f) == 0:
            return
        fileName=f.replace('.exe','.cpp')
        cFile = open(fileName, 'w')
        main="#include <stdio.h>\n"
        main=main+"int main(int argc, char **argv) {\n"
        main=main+"  try{\n";
        main=main+"    __asm__(\".byte "
        main=main+str(self.data[0])
        for index in range(1, len(self.data)):
            main = main + ",\"\n   \"" + str(self.data[index])
        main = main+"\");\n"
        main = main+"    printf(\"Inexplicably the code ran without crashing\\n\");\n"
        main = main+"  }catch(...){\n";
        main = main+"    printf(\"%s performed an illegal operation, terminating program.\", argv[0]);\n"
        main = main+"  }\n"
        main = main+"    return 0;\n"
        main = main+"}"
        cFile.write(main)
        cFile.close()
        os.system("g++ " + fileName + " -o " + f)


root = Tk()
app = MetaDataApp(root)
root.mainloop()
