"""
Model exported as python.
Name : 模型
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class RegionMerge(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('', '输入格子图层，合并多个格子为一个图层', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Regionmergeres', 'regionMergeRes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # 聚合
        alg_params = {
            'AGGREGATES': [{'aggregate': 'first_value','delimiter': ',','input': 'regionId','length': 254,'name': 'new_field','precision': 0,'type': 10}],
            'GROUP_BY': 'regionId',
            'INPUT': parameters[''],
            'OUTPUT': parameters['Regionmergeres']
        }
        outputs[''] = processing.run('native:aggregate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Regionmergeres'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return '聚合相同区域的格子'

    def displayName(self):
        return '聚合相同区域的格子'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return RegionMerge()
