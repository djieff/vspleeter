"""UI Wrapper script over the "spleeter separate" command
"""
import glob
import os
import sys
import subprocess

import itertools

from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import QApplication, QFileDialog
from PySide2.QtUiTools import QUiLoader

OUTPUT_PATH_SUFFIX = "{rootOutputDir}/{basename}_spleeted/{binaryType}/{stemNum}stems/"


def main():
    """main function
    """
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    app.setOrganizationName("djieffx")
    app.setApplicationName("vspleeter")
    loader = QUiLoader()
    mw = loader.load(os.path.join(os.path.dirname(__file__), "vspleeter_mainWindow.ui"))

    def getBinaries():
        """Create a generator that yield the proper command name if the checkbox is checked.

        :return: generator with command name
        :rtype: generator
        """
        if mw.cpuCheckBox.checkState():
            yield 'spleeter'
        if mw.gpuCheckBox.checkState():
            yield 'spleeter-gpu'

    def getStemsAmount():
        """Create a generator that yield the stems amount if the checkbox is checked.

        :return: generator with stem count
        :rtype: generator
        """
        if mw.stems2CheckBox.checkState():
            yield '2'
        if mw.stems4CheckBox.checkState():
            yield '4'
        if mw.stems5CheckBox.checkState():
            yield '5'

    def createOutputDir(cmdSpecs):
        """Create the output directory from defined output specifications

        :param cmdSpecs: context based variables to execute spleeter command
        :type cmdSpecs: dict

        :return: the output directory
        :rtype: str
        """
        outputDir = OUTPUT_PATH_SUFFIX.format(**cmdSpecs)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir, mode=0o777)
            print('Created the {0} directory'.format(outputDir))

        return outputDir

    def generateCommandsPerElements(binaryGenerator, inputFilePath, stemsCPUGenerator, stemsGPUGenerator,
                                    rootOutputDir):
        """Generate all the commands necessary, per what is selected in the UI, looping on the process type

        :param binaryGenerator: generator with all the binary selections
        :param str inputFilePath: The file to be spleeted
        :param stemsCPUGenerator: generator with the CPU processes flag
        :param stemsGPUGenerator: generator with the GPU processes flag
        :param str rootOutputDir: The output directory

        :return: generator with all command line to spleet the file
        """
        for binaryName in binaryGenerator:
            cmdSpecs = {
                'rootOutputDir': rootOutputDir,
                'basename': os.path.basename(os.path.splitext(inputFilePath)[0]),
                'binaryType': 'CPU',
                'binaryName': binaryName,
                'inputFilePath': inputFilePath,
                'stemsGenerator': stemsCPUGenerator
            }
            if 'gpu' in binaryName:
                cmdSpecs['binaryType'] = 'GPU'
                cmdSpecs['stemsGenerator'] = stemsGPUGenerator
                yield from generateCmdPerStem(cmdSpecs)
            else:
                yield from generateCmdPerStem(cmdSpecs)

    def generateCmdPerStem(cmdSpecs):
        """Generate the command from the stem count

        :param dict cmdSpecs: a dictionary containing all necessary data to generate the command

        :return: a command to execute
        :rtype: list
        """
        stemsGenerator = cmdSpecs['stemsGenerator']
        for stemNum in stemsGenerator:
            cmdSpecs['stemNum'] = stemNum
            outputDir = createOutputDir(cmdSpecs)
            if os.name == 'nt':
                cmd = [
                    "python", "-m",
                    "{}".format(cmdSpecs['binaryName']), "separate",
                    "-i", "{}".format(cmdSpecs['inputFilePath']),
                    "-p", "spleeter:{}stems".format(cmdSpecs['stemNum']),
                    "-o", "{}".format(outputDir)
                ]
            else:
                cmd = [
                    "{}".format(cmdSpecs['binaryName']), "separate",
                    "-i", "{}".format(cmdSpecs['inputFilePath']),
                    "-p", "spleeter:{}stems".format(cmdSpecs['stemNum']),
                    "-o", "{}".format(outputDir)
                ]
            yield cmd

    def browseForInputFile(_):
        """Opens a file browser, and set the input file

        :param _: unused
        """
        inputFile = QFileDialog.getOpenFileName()[0]
        mw.inputFileLineEdit.setText(inputFile)

    def browseForOutputDir(_):
        """Opens a file browser, and set the input file

        :param _: unused
        """
        outputDir = QFileDialog.getExistingDirectory()
        mw.outputDirLineEdit.setText(outputDir)

    def processBatchElements(_):
        """Process all the data from the UI, and execute all the commands generated

        :param _: unused input
        """
        binaryGenerator = getBinaries()
        inputFilePath = mw.inputFileLineEdit.text()
        stemsCPUGenerator = getStemsAmount()
        stemsCPUGenerator, stemsGPUGenerator = itertools.tee(stemsCPUGenerator)
        rootOutputDir = mw.outputDirLineEdit.text()

        generatedCmds = generateCommandsPerElements(
            binaryGenerator, inputFilePath, stemsCPUGenerator, stemsGPUGenerator, rootOutputDir
        )

        generatedCmds, generatedCmdsForLength = itertools.tee(generatedCmds)

        amountOfCommands = 0
        for _ in generatedCmdsForLength:
            amountOfCommands += 1

        mw.progressBar.setRange(0, amountOfCommands)
        mw.progressBar.setValue(0)
        mw.resultTextEdit.setText('')
        mw.resultTextEdit.append('Source File: %s' % inputFilePath)

        for cmd in generatedCmds:
            currentJobCount = mw.progressBar.value()
            subprocess.run(cmd)

            mw.progressBar.setValue(currentJobCount + 1)

            mw.resultTextEdit.append('Output %s:' % cmd[5].split(':')[1])
            outputFiles = glob.glob(os.path.join(cmd[7], '*', '*'))
            for outputFile in outputFiles:
                mw.resultTextEdit.append(outputFile)
            mw.resultTextEdit.append('')

    mw.inputFilePushButton.clicked.connect(browseForInputFile)
    mw.outputDirPushButton.clicked.connect(browseForOutputDir)
    mw.processPushButton.clicked.connect(processBatchElements)
    mw.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
