"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import numpy as np
import math
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsPoint
                       )
from qgis import processing
from PyQt5.QtCore import QVariant


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'myscriptdoor'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('My Script door')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def caculateAngle(self,pointStart,pointEnd1,pointEnd2):
        dx1 = pointEnd1.x() - pointStart.x()
        dy1 = pointEnd1.y() - pointStart.y()

        dx2 = pointEnd2.x() - pointStart.x()
        dy2 = pointEnd2.y() - pointStart.y()


        angle1 = int(math.atan2(dy1,dx1) * 180 / math.pi)
        angle2 = int(math.atan2(dy2,dx2) * 180 / math.pi)


        if(angle1 * angle2 >= 0):
            includedAngle = abs(angle1-angle2)
        else:
            includedAngle = abs(angle1) + abs(angle2)
            if includedAngle > 180:
                includedAngle = 360 - includedAngle
        
        return includedAngle


    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )
        self.addParameter(QgsProcessingParameterString('next_id', '输入next_id(若为数组用、分割)',defaultValue="1190002287"))
        self.addParameter(QgsProcessingParameterString('xPos', '输入点x坐标(若为数组用、分割)', defaultValue="-73.99097708"))
        self.addParameter(QgsProcessingParameterString('yPos', '输入点y坐标(若为数组用、分割)', defaultValue="40.73900185"))


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # layer.dataProvider().addAttributes([QgsField('dpIndex', QVariant.Int)])
        # layer.updateFields()

        # layer.selectAll()
        # source = processing.run("native:saveselectedfeatures", {'INPUT': layer, 'OUTPUT': 'memory:'})['OUTPUT']
        # layer.removeSelection()


        # AttrIndex = layer.fields().indexFromName('dpIndex')
        # layer.dataProvider().deleteAttributes([AttrIndex])
        # layer.updateFields()


        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        nextId = parameters['next_id'].split("、")
        xPos = parameters['xPos'].split("、")
        yPos = parameters['yPos'].split("、")


        
            
        for current, feature in enumerate(features):
            
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            for i in range(0,len(nextId)):
                if str(feature['next_id']) == nextId[i] :
                    # print(nextId[i])
                    # print(float(xPos[i]))
                    # print(float(yPos[i]))
                    geom = feature.geometry()
                    vertices = geom.vertices()
                    verticesNum = 0
                    qgisPointArray = []
                    for point in vertices:
                        verticesNum += 1
                        qgisPointArray.append(point)
                    pointLen = len(qgisPointArray)-1
                    for index in range(pointLen) :
                        includedAngle = self.caculateAngle(QgsPoint(float(xPos[i]),float(yPos[i])),qgisPointArray[index],qgisPointArray[index+1])
                        if(abs(includedAngle-180) < 5 ):
                            geom.insertVertex(float(xPos[i]),float(yPos[i]),index+1)
                            feature['dpIndex'] = index+1
                            break
                    # print(qgisPointArray)
                    # geom.insertVertex(parameters['xPos'],parameters['yPos'],verticesNum-1)

                    feature.setGeometry(geom)
                    

                    # geom = feature.geometry()
                    # vertices = geom.vertices()
                    # verticesNum = 0
                    # qgisPointArray = []
                    # for point in vertices:
                    #     verticesNum += 1
                    #     qgisPointArray.append(point)


            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)
        if False:
            buffered_layer = processing.run("native:buffer", {
                'INPUT': dest_id,
                'DISTANCE': 1.5,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
