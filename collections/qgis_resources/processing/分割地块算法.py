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
                       QgsPoint,
                       QgsGeometry,
                       QgsFeature,
                       QgsDistanceArea,
                       QgsWkbTypes,
                       QgsProcessingParameterNumber)
from qgis import processing


class devideBlockProcessingAlgorithm(QgsProcessingAlgorithm):
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
        return devideBlockProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '分割地块'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('分割地块')

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
        return self.tr("输入一个多边形图层与单位划分面积，该算法筛选出图层内所有包含五个点的多边形，并以划分面积为单位将筛选出的多边形进行等分，不符合五个点的多边形则不处理。")

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

        self.addParameter(QgsProcessingParameterNumber('area', '划分单位面积', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=20000, defaultValue=2000))

    # 计算地理坐标两点的距离
    def haversine(self,pointFirst,pointSecend):
        lon1, lat1, lon2, lat2 = map(math.radians, [pointFirst.x(), pointFirst.y(), pointSecend.x(),pointSecend.y()])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        r = 6371 # 地球平均半径，单位为公里
        return c * r * 1000

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
            QgsWkbTypes.MultiLineString,
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

        departArea = parameters['area']
        # print(departArea)
        d = QgsDistanceArea()
        d.setEllipsoid('WGS84')
        seg = QgsFeature()
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            geom = feature.geometry()

            vertices = geom.vertices()
            verticesNum = 0
            for point in vertices:
                verticesNum += 1
            
            featureArea = d.measureArea(geom)
            points = geom.vertices()
            qgisPointArray = []
            for point in points:
                qgisPointArray.append(point)
            if verticesNum == 5 and (featureArea // departArea) > 1 :
                
                
                # maxDistance = 0
                # maxDistanceIndex = 0
                # maxDistanceArray = []
                maxDistanceIndexArray = [-1,-1]
                
                # print(qgisPointArray)
                # for round in range(2):
                #     maxDistance = 0
                #     maxDistanceIndex = 0
                #     for index in range(len(qgisPointArray)-1):
                #         distance = self.haversine(qgisPointArray[index],qgisPointArray[index+1])
                #         if maxDistance < distance and maxDistanceIndexArray[0] != index:
                #             maxDistance = distance
                #             maxDistanceIndex = index
                #     if maxDistanceIndexArray[0] == -1 : 
                #         maxDistanceIndexArray[0] = maxDistanceIndex
                #     else:
                #         maxDistanceIndexArray[1] = maxDistanceIndex
                #     maxDistanceArray.append(maxDistance)

                maxDistance1 = 0
                maxDistance2 = 0
                maxDistance1 = self.haversine(qgisPointArray[0],qgisPointArray[1]) + self.haversine(qgisPointArray[2],qgisPointArray[3])
                maxDistance2 = self.haversine(qgisPointArray[1],qgisPointArray[2]) + self.haversine(qgisPointArray[3],qgisPointArray[0])
                if maxDistance1 > maxDistance2:
                    maxDistanceIndexArray[0] = 0
                    maxDistanceIndexArray[1] = 2
                else:
                    maxDistanceIndexArray[0] = 1
                    maxDistanceIndexArray[1] = 3
                # print(maxDistanceArray)
                # print(maxDistanceIndexArray)
                # 求等分点
                line1array = []
                line2array = []

                dividetimes = featureArea // departArea

                xDistance1 = qgisPointArray[maxDistanceIndexArray[0] + 1].x() - qgisPointArray[maxDistanceIndexArray[0]].x()
                yDistance1 = qgisPointArray[maxDistanceIndexArray[0] + 1].y() - qgisPointArray[maxDistanceIndexArray[0]].y()

                # print(xDistance1)
                # print(yDistance1)

                xDistance2 = qgisPointArray[maxDistanceIndexArray[1] + 1].x() - qgisPointArray[maxDistanceIndexArray[1]].x()
                yDistance2 = qgisPointArray[maxDistanceIndexArray[1] + 1].y() - qgisPointArray[maxDistanceIndexArray[1]].y()

                # print(xDistance2)
                # print(yDistance2)

                xAverageLength1 = xDistance1 / dividetimes
                yAverageLength1 = yDistance1 / dividetimes

                # print(xAverageLength1)
                # print(yAverageLength1)

                xAverageLength2 = xDistance2 / dividetimes
                yAverageLength2 = yDistance2 / dividetimes

                # print(xAverageLength2)
                # print(yAverageLength2)

                for i in range(int(dividetimes)-1):
                    line1array.append(QgsPoint((qgisPointArray[maxDistanceIndexArray[0]].x() + (i+1) * xAverageLength1),(qgisPointArray[maxDistanceIndexArray[0]].y() + (i+1) * yAverageLength1 )))
                    line2array.append(QgsPoint((qgisPointArray[maxDistanceIndexArray[1]].x() + (i+1) * xAverageLength2),(qgisPointArray[maxDistanceIndexArray[1]].y() + (i+1) * yAverageLength2 )))

                # print(line1array)
                # print(line2array)
                for index in range(len(line1array)):
                    # print(line1array[index],":", line2array[len(line2array)-1-i])
                    # seg = QgsFeature()
                    seg.setGeometry(QgsGeometry.fromPolyline([line1array[index], line2array[len(line2array)-index-1]]))
                    sink.addFeature(seg, QgsFeatureSink.FastInsert)
                
                
                for i in range(len(qgisPointArray)-1):
                    if i == maxDistanceIndexArray[0]:
                        seg.setGeometry(QgsGeometry.fromPolyline([qgisPointArray[i], line1array[0]]))
                        sink.addFeature(seg, QgsFeatureSink.FastInsert)
                        for index in range(len(line1array)-1):
                            # seg = QgsFeature()
                            seg.setGeometry(QgsGeometry.fromPolyline([line1array[index], line1array[index+1]]))
                            sink.addFeature(seg, QgsFeatureSink.FastInsert)
                        # seg = QgsFeature()
                        seg.setGeometry(QgsGeometry.fromPolyline([line1array[len(line1array)-1], qgisPointArray[i+1]]))
                        sink.addFeature(seg, QgsFeatureSink.FastInsert)
                    elif i == maxDistanceIndexArray[1]:
                        # seg = QgsFeature()
                        seg.setGeometry(QgsGeometry.fromPolyline([qgisPointArray[i], line2array[0]]))
                        sink.addFeature(seg, QgsFeatureSink.FastInsert)
                        for index in range(len(line2array)-1):
                            # seg = QgsFeature()
                            seg.setGeometry(QgsGeometry.fromPolyline([line2array[index], line2array[index+1]]))
                            sink.addFeature(seg, QgsFeatureSink.FastInsert)
                        # seg = QgsFeature()
                        seg.setGeometry(QgsGeometry.fromPolyline([line2array[len(line2array)-1], qgisPointArray[i+1]]))
                        sink.addFeature(seg, QgsFeatureSink.FastInsert)
                    else:
                        # seg = QgsFeature()
                        seg.setGeometry(QgsGeometry.fromPolyline([qgisPointArray[i], qgisPointArray[i+1]]))
                        sink.addFeature(seg, QgsFeatureSink.FastInsert)
            else:
                for i in range(len(qgisPointArray)-1):
                    seg.setGeometry(QgsGeometry.fromPolyline([qgisPointArray[i], qgisPointArray[i+1]]))
                    sink.addFeature(seg, QgsFeatureSink.FastInsert)

                

                    
                        

                    


                    

    


            # Add a feature in the sink
            # sink.addFeature(feature, QgsFeatureSink.FastInsert)

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
