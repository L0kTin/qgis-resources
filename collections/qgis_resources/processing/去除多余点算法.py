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
import numpy as np
import math

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber)
from qgis import processing


class removePointProcessingAlgorithm(QgsProcessingAlgorithm):
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
        return removePointProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '删减四边形多余顶点'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('删减四边形多余顶点')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('QGis-resources')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'QGis-resources'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("输入一个角度，删除三点间角度偏差在输入角度内的点.该算法用于删除四边形上除四个顶点外的多余点。")

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
                self.tr('Input polygon layer'),
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

        self.addParameter(QgsProcessingParameterNumber('angle', '角度偏差值', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=180, defaultValue=5))


    # def geo2xyz(self,lat, lng, r = 6400):
    #     thera = (math.pi * lat) / 180
    #     fie = (math.pi * lng) / 180
    #     x = r * math.cos(thera) * math.cos(fie)
    #     y = r * math.cos(thera) * math.sin(fie)
    #     z = r * math.sin(thera)
    #     return [x,y,z]

    # def haversine(self,pointFirst,pointSecend):
    #     lon1, lat1, lon2, lat2 = map(math.radians, [pointFirst.x(), pointFirst.y(), pointSecend.x(),pointSecend.y()])
    #     dlon = lon2 - lon1 
    #     dlat = lat2 - lat1 
    #     a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    #     c = 2 * math.asin(math.sqrt(a)) 
    #     r = 6371 # 地球平均半径，单位为公里
    #     return c * r * 1000

# 以第一个点为起始值，另外两个点为终点计算两个向量的夹角
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


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
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

        angle = parameters['angle'],
        
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            geom = feature.geometry()
            points = geom.vertices()

            delPointIndexArray = []
            qgisPointArray = []
            for point in points:
                qgisPointArray.append(point)
            

            pointLen = len(qgisPointArray)-1

            if pointLen < 5:
                feature.setGeometry(geom)
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                continue

            # delPointIndexArray.append(0)

            for index in range(pointLen) :
                if index == pointLen-1:
                    includedAngle = self.caculateAngle(qgisPointArray[0],qgisPointArray[index],qgisPointArray[1])
                else:
                    includedAngle = self.caculateAngle(qgisPointArray[index+1],qgisPointArray[index],qgisPointArray[index + 2])
                
                # print(includedAngle)

                if(abs(includedAngle-180) < angle[0] ):
                    if(index == pointLen-1):
                        delPointIndexArray.append(0)
                    else:
                        delPointIndexArray.append(index + 1)
                
        
            
            # print("len qgisPointArray:", len(qgisPointArray),"delPointIndexArra:",len(delPointIndexArray))
            # print(qgisPointArray)
            # print(delPointIndexArray)

            delPointIndexArray = sorted(delPointIndexArray,reverse=True)
            # print(delPointIndexArray)
            # for point in geom.vertices():
            #     print(point)
            distanceDict = {}
            if(len(qgisPointArray) - len(delPointIndexArray) == 5):
                for index in delPointIndexArray:
                    # print("ikndex:",index)
                    geom.deleteVertex(index)
                    # for point in geom.vertices():
                    #     print(point)
                    qgisPointArray.pop(index)
                # for index in range(len(qgisPointArray)-1):
                #     print(qgisPointArray[index])
                #     distance = self.haversine(qgisPointArray[index],qgisPointArray[index+1])
                #     print(index)
                #     print(distance)

                # geom.insertVertex(qgisPointArray[3],0)


            # print("------")
            # for point in geom.vertices():
            #     print(point)
            # print("------")

            feature.setGeometry(geom)
            # for point in feature.geometry().vertices():
            #     print(point)
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
