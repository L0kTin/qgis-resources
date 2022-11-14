# -*- coding: utf-8 -*-

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
from asyncio.windows_events import NULL
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
        return '8计算地块大门位置'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('8计算地块大门位置')

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

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
                [QgsProcessing.TypeVectorAnyGeometry]
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

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        layer = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        layer.dataProvider().addAttributes([QgsField('dpIndex', QVariant.Int)])
        layer.updateFields()

        layer.selectAll()
        source = processing.run("native:saveselectedfeatures", {'INPUT': layer, 'OUTPUT': 'memory:'})['OUTPUT']
        layer.removeSelection()


        AttrIndex = layer.fields().indexFromName('dpIndex')
        layer.dataProvider().deleteAttributes([AttrIndex])
        layer.updateFields()


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
        # features = sorted(source.getFeatures(), key='newid')
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break


            geom = feature.geometry()

            vertices = geom.vertices()

            verticesNum = 0
            for point in vertices:
                verticesNum += 1

            if verticesNum == 5:
                if feature['neighbor'] != 0:
                    geom = feature.geometry()
                    vertices = geom.vertices()
                    pointarray = []
                    for point in vertices:
                        pointarray.append(point)
                    neighbor = source.getFeature(feature['neighbor'])
                    neighborvertice = neighbor.geometry().vertices()
                    neighborarray = []
                    for point in neighborvertice:
                        neighborarray.append(point)
                    neighborpoint = []
                    neighborpointindex = []
                    neipointLen = len(neighborarray)-1
                    poinlen = len(pointarray) - 1
                    for index in range(poinlen):
                        for index2 in range(neipointLen) :
                            if pointarray[index].x() == neighborarray[index2].x() and pointarray[index].y() == neighborarray[index2].y():
                                neighborpoint.append(pointarray[index])
                                neighborpointindex.append(index)
                                break
                        if len(neighborpointindex) == 2:
                            break
                    
                    # print(len(neighborpointindex))
                    if len(neighborpointindex) == 2:
                        sidepoint = []
                        if(neighborpointindex[0] == 0):
                            sidepoint.append(pointarray[3])
                        else:
                            sidepoint.append(pointarray[neighborpointindex[0]-1])
                        if(neighborpointindex[1] == 4):
                            sidepoint.append(pointarray[1])
                        else:
                            sidepoint.append(pointarray[neighborpointindex[1]+1])
                        # print(feature['newid'])
                        # print(sidepoint)
                        sidepoint1 = QgsPoint((neighborpoint[0].x() + sidepoint[0].x())/2,(neighborpoint[0].y() + sidepoint[0].y())/2)
                        sidepoint2 = QgsPoint((neighborpoint[1].x() + sidepoint[1].x())/2,(neighborpoint[1].y() + sidepoint[1].y())/2)

                        angle = feature['angle']
                        # 南北朝向
                        if angle < 45 or 135 < angle < 225 or 315 < angle < 360:  
                            if sidepoint1.x() < sidepoint2.x():
                                if neighborpointindex[0] == 0 :
                                    geom.insertVertex(sidepoint1.x(),sidepoint1.y(),4)
                                    feature['dpIndex'] = 4
                                else:
                                    geom.insertVertex(sidepoint1.x(),sidepoint1.y(),neighborpointindex[0])
                                    feature['dpIndex'] = neighborpointindex[0]
                            else:
                                if neighborpointindex[1] == 4:
                                    geom.insertVertex(sidepoint2.x(),sidepoint2.y(),1)
                                    feature['dpIndex'] = 1
                                else:
                                    geom.insertVertex(sidepoint2.x(),sidepoint2.y(),neighborpointindex[1]+1)
                                    feature['dpIndex'] = neighborpointindex[1]+1

                        else:
                            if 45 < angle < 90 or 225 < angle < 270:
                                if sidepoint1.y()  < sidepoint2.y():
                                    if neighborpointindex[0] == 0 :
                                        geom.insertVertex(sidepoint1.x(),sidepoint1.y(),4)
                                        feature['dpIndex'] = 4
                                    else:
                                        geom.insertVertex(sidepoint1.x(),sidepoint1.y(),neighborpointindex[0])
                                        feature['dpIndex'] = neighborpointindex[0]
                                else:
                                    if neighborpointindex[1] == 4:
                                        geom.insertVertex(sidepoint2.x(),sidepoint2.y(),1)
                                        feature['dpIndex'] = 1
                                    else:
                                        geom.insertVertex(sidepoint2.x(),sidepoint2.y(),neighborpointindex[1]+1)
                                        feature['dpIndex'] = neighborpointindex[1]+1

                            else:
                                if sidepoint1.y()  > sidepoint2.y():
                                    if neighborpointindex[0] == 0 :
                                        geom.insertVertex(sidepoint1.x(),sidepoint1.y(),4)
                                        feature['dpIndex'] = 4
                                    else:
                                        geom.insertVertex(sidepoint1.x(),sidepoint1.y(),neighborpointindex[0])
                                        feature['dpIndex'] = neighborpointindex[0]
                                else:
                                    if neighborpointindex[1] == 4:
                                        geom.insertVertex(sidepoint2.x(),sidepoint2.y(),1)
                                        feature['dpIndex'] = 1
                                    else:
                                        geom.insertVertex(sidepoint2.x(),sidepoint2.y(),neighborpointindex[1]+1)
                                        feature['dpIndex'] = neighborpointindex[1]+1

                # 四周为道路 找最南的点
                else:

                    # southindex = 0
                    geom = feature.geometry()
                    vertices = geom.vertices()
                    pointarray = []
                    for point in vertices:
                        pointarray.append(point)
                    pointlen = len(pointarray) - 1
                    southPointminy = 1000
                    southPointmaxy = 1000
                    southPointindexmin = 0
                    southPointindexmax = 0
                    for index in range(pointlen) :
                        # print(qgisPointArray[index].x())
                        if pointarray[index].y() < southPointminy:
                            if pointarray[index].y() < southPointmaxy:
                                southPointminy = southPointmaxy
                                southPointmaxy = pointarray[index].y()
                                southPointindexmin = southPointindexmax
                                southPointindexmax = index
                            else:
                                southPointminy = pointarray[index].y()
                                southPointindexmin = index
                    
                    # print('start')
                    # print(southPointindexmax)
                    # print(southPointindexmin)
                    if (southPointindexmax == 0 and southPointindexmin ==3) or (southPointindexmax == 3 and southPointindexmin ==0):
                        position = 4
                        sidepoint = QgsPoint((pointarray[southPointindexmax].x() + pointarray[southPointindexmin].x())/2,(pointarray[southPointindexmax].y() + pointarray[southPointindexmin].y())/2)
                        geom.insertVertex(sidepoint.x(),sidepoint.y(),position)
                        feature['dpIndex'] = position
                    elif southPointindexmax == southPointindexmin+1 or southPointindexmin == southPointindexmax + 1:
                        if southPointindexmax > southPointindexmin:
                            position = southPointindexmax
                        else:
                            position = southPointindexmin
                        sidepoint = QgsPoint((pointarray[southPointindexmax].x() + pointarray[southPointindexmin].x())/2,(pointarray[southPointindexmax].y() + pointarray[southPointindexmin].y())/2)
                        geom.insertVertex(sidepoint.x(),sidepoint.y(),position)
                        feature['dpIndex'] = position

            feature.setGeometry(geom)   

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
