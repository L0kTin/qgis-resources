"""
Model exported as python.
Name : comepareLayer
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class comepareLayer(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('landuse', 'landuse图层', defaultValue=None))
        self.addParameter(QgsProcessingParameterMapLayer('water', 'water', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Landusenorewater', 'landuse-nore-water', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # 提取water
        alg_params = {
            'FIELD': 'layer',
            'INPUT': parameters['water'],
            'OPERATOR': 1,  # 不等于（≠）
            'VALUE': 'NULL',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Water'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 提取code≠7203
        alg_params = {
            'FIELD': 'code',
            'INPUT': parameters['landuse'],
            'OPERATOR': 1,  # 不等于（≠）
            'VALUE': '7203',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Code7203'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 合并矢量图层
        alg_params = {
            'CRS': None,
            'LAYERS': [outputs['Code7203']['OUTPUT'],outputs['Water']['OUTPUT']],
            'OUTPUT': parameters['Landusenorewater']
        }
        outputs['landuse-nore-water'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Landusenorewater'] = outputs['landuse-nore-water']['OUTPUT']
        return results

    def name(self):
        return '对比层制作'

    def displayName(self):
        return '对比层制作'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return comepareLayer()
