"""
Model exported as python.
Name : 计算地块朝向与相邻数据
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class jisuandikuaichaoxiangyuxianglin(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('parcel', 'parcel', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Parcel', 'parcel', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # 字段计算器
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'newid',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # 整型
            'FORMULA': '@row_number + 1',
            'INPUT': parameters['parcel'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 计算地块相邻地块
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('script:计算地块相邻地块', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 计算建筑物朝向角度
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('script:计算建筑物朝向角度', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 按表达式排序
        alg_params = {
            'ASCENDING': True,
            'EXPRESSION': 'next_id',
            'INPUT': outputs['']['OUTPUT'],
            'NULLS_FIRST': False,
            'OUTPUT': parameters['Parcel']
        }
        outputs[''] = processing.run('native:orderbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Parcel'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return '7计算地块朝向与相邻数据'

    def displayName(self):
        return '7计算地块朝向与相邻数据'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return jisuandikuaichaoxiangyuxianglin()
