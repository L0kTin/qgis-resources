"""
Model exported as python.
Name : 模型
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class roadLayer(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('railways', 'railways图层', defaultValue=None))
        self.addParameter(QgsProcessingParameterMapLayer('roads', 'roads图层', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Roadsrailsways', 'roads-railsways', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # 提取railways图层
        alg_params = {
            'EXPRESSION': 'code = 6101 OR code = 6102',
            'INPUT': parameters['railways'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Railways'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 提取roads图层
        alg_params = {
            'EXPRESSION': '("code"  >=  5110 AND "code"  <=  5119) OR ("code" >=  5130 AND "code" <= 5139) OR ("code"  >= 5121 AND  "code"  <=  5123)',
            'INPUT': parameters['roads'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Roads'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 合并矢量图层
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['Roads']['OUTPUT'],outputs['Railways']['OUTPUT']],
            'OUTPUT': parameters['Roadsrailsways']
        }
        outputs[''] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Roadsrailsways'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return '道路层制作'

    def displayName(self):
        return '道路层制作'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return roadLayer()

