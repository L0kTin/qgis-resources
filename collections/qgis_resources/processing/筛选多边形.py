"""
Model exported as python.
Name : 筛选多边形
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class shaixuanduobianxing(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('parcelfengexian', 'parcel_fengexian', defaultValue=None))
        self.addParameter(QgsProcessingParameterMapLayer('parcelxiuzheng', 'parcel_xiuzheng', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Parcel4326', 'parcel-4326', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # 缓冲区
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': -0.0001,
            'END_CAP_STYLE': 1,  # 扁平
            'INPUT': parameters['parcelxiuzheng'],
            'JOIN_STYLE': 1,  # 尖角
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 用线分割
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'LINES': parameters['parcelfengexian'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:splitwithlines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 重投影图层
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:900913'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 字段计算器
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'area900913',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 1,  # 整型
            'FORMULA': 'area($geometry)',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 按表达式提取
        alg_params = {
            'EXPRESSION': '"area900913"  >= 4000',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 重投影图层
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': parameters['Parcel4326']
        }
        outputs[''] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Parcel4326'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return '5筛选多边形'

    def displayName(self):
        return '5筛选多边形'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return shaixuanduobianxing()
