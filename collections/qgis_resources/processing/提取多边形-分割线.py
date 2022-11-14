"""
Model exported as python.
Name : 提取可用多边形
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class fengexian (QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('roadspolygon', 'roads-polygon', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Parcel_xiuzheng', 'parcel_xiuzheng', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Parcel_fengexian', 'parcel_fengexian', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # 删减四边形多余顶点
        alg_params = {
            'INPUT': parameters['roadspolygon'],
            'angle': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('script:删减四边形多余顶点', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 修正几何图形
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': parameters['Parcel_xiuzheng']
        }
        outputs[''] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Parcel_xiuzheng'] = outputs['']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 分割地块
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'area': 4000,
            'OUTPUT': parameters['Parcel_fengexian']
        }
        outputs[''] = processing.run('script:分割地块', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Parcel_fengexian'] = outputs['']['OUTPUT']
        return results



    def name(self):
        return '4提取可用多边形-制作分割线'

    def displayName(self):
        return '4提取多边形-分割线'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return fengexian()

