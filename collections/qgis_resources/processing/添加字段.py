"""
Model exported as python.
Name : 添加字段
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class tianjiaziduan(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('parcel4326', 'parcel', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Parcel_removepoint', 'parcel_removepoint', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # 字段计算器
        alg_params = {
            'FIELD_LENGTH': 15,
            'FIELD_NAME': 'fclass',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 2,  # 字符串
            'FORMULA': '@layer_name',
            'INPUT': parameters['parcel4326'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 字段计算器2
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'next_id',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # 整型
            'FORMULA': '@row_number + 1190000001',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 字段计算器3
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'sellparcel',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # 整型
            'FORMULA': '1',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 删减四边形多余顶点
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'angle': 5,
            'OUTPUT': parameters['Parcel_removepoint']
        }
        outputs[''] = processing.run('script:删减四边形多余顶点', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Parcel_removepoint'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return '6添加字段'

    def displayName(self):
        return '6添加字段'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return tianjiaziduan()
