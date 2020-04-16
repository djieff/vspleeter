"""
"""
import os
import sys
import subprocess

import itertools

from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader

BASE_COMMAND = "{binaryName} separate -i {inputFilePath} -p spleeter:{stemNum}stems -o {outputDir}"
OUTPUT_PATH_SUFFIX = "{rootOutputDir}/{basename}_spleeted/{binaryType}/{stemNum}stems/"

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("vspleeter")
    loader = QUiLoader()
    mw = loader.load(os.path.join(os.path.dirname(__file__), "vspleeter_mainWindow.ui"))

    def getBinaries():
        if mw.cpuCheckBox.checkState():
            yield 'spleeter'
        if mw.gpuCheckBox.checkState():
            yield 'spleeter-gpu'

    def getStemsAmount():
        if mw.stems2CheckBox.checkState():
            yield '2'
        if mw.stems4CheckBox.checkState():
            yield '4'
        if mw.stems5CheckBox.checkState():
            yield '5'

    def createOutputDir(outputSpecs):

        outputDir = OUTPUT_PATH_SUFFIX.format(**outputSpecs)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir, mode=0o777)
            print('Created the {0} directory'.format(outputDir))

        return outputDir

    def generateCommandsPerElements(binaryGenerator, inputFilePath, stemsCPUGenerator, stemsGPUGenerator,
                                    rootOutputDir):
        basename = os.path.basename(os.path.splitext(inputFilePath)[0])
        binaryType = 'CPU'
        stemsGenerator = stemsCPUGenerator
        for binaryName in binaryGenerator:
            if 'gpu' in binaryName:
                binaryType = 'GPU'
                stemsGenerator = stemsGPUGenerator
                yield from generateCmdPerStem(binaryName, binaryType, basename, inputFilePath, rootOutputDir,
                                              stemsGenerator)
            else:
                yield from generateCmdPerStem(binaryName, binaryType, basename, inputFilePath, rootOutputDir,
                                              stemsGenerator)

    def generateCmdPerStem(binaryName, binaryType, basename, inputFilePath, rootOutputDir, stemsGenerator):
        for stemNum in stemsGenerator:
            outputSpecs = {'rootOutputDir': rootOutputDir,
                           'basename': basename,
                           'binaryType': binaryType,
                           'stemNum': stemNum
                           }
            outputDir = createOutputDir(outputSpecs)
            cmdSpecs = {'binaryName': binaryName,
                        'inputFilePath': inputFilePath,
                        'stemNum': stemNum,
                        'outputDir': outputDir
                        }
            cmd = BASE_COMMAND.format(**cmdSpecs)
            cmd = cmd.split(' ')
            yield cmd

    def processBatchElements(index):

        binaryGenerator = getBinaries()
        inputFilePath = mw.inputFileLineEdit.text()
        stemsCPUGenerator = getStemsAmount()
        stemsCPUGenerator, stemsGPUGenerator = itertools.tee(stemsCPUGenerator)
        rootOutputDir = mw.outputDirLineEdit.text()

        generatedCmds = generateCommandsPerElements(binaryGenerator, inputFilePath, stemsCPUGenerator,
                                                    stemsGPUGenerator, rootOutputDir)

        for cmd in generatedCmds:
            prettyCmd = ' '.join(cmd)
            print("######### executing: ##########\n\n{0}\n\n@@@@@@@@@@".format(prettyCmd))
            subprocess.run(cmd)
            print("Command Success\n\n")



    mw.processPushButton.clicked.connect(processBatchElements)
    mw.show()
    app.exec_()
    main()
