"""
Model exported as python.
Name : roads-polygon
Group : 
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Roadspolygon(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('roadysrailways', 'roadys-railways', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Roadspolygon', 'roads-polygon', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # 多边形化
        alg_params = {
            'INPUT': parameters['roadysrailways'],
            'KEEP_FIELDS': False,
            'OUTPUT': parameters['Roadspolygon']
        }
        outputs[''] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Roadspolygon'] = outputs['']['OUTPUT']
        return results

    def name(self):
        return '3道路转多边形'

    def displayName(self):
        return '3道路转多边形'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return Roadspolygon()

