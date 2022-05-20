"""
Model exported as python.
Name : StreetLampRotation
Group : Next
With QGIS : 32203
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Streetlamprotation(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('1', '待处理traffic图层', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('2', 'roads图层', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('streetlamp', '路灯到道路的最大距离', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=10, defaultValue=5))
        self.addParameter(QgsProcessingParameterFeatureSink('3', 'traffic-newyork-point', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
        results = {}
        outputs = {}

        # traffic图层转换坐标系
        alg_params = {
            'INPUT': parameters['1'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:900913'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Traffic'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # road图层转换坐标系
        alg_params = {
            'INPUT': parameters['2'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Road'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 抽取street_lamp
        alg_params = {
            'FIELD': 'code',
            'INPUT': outputs['Traffic']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '5209',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Street_lamp'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # road图层打散
        alg_params = {
            'INPUT': outputs['Road']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Road'] = processing.run('native:explodelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 计算street_lamp朝向
        alg_params = {
            'APPLY_SYMBOLOGY': True,
            'FIELD_NAME': 'rotation_street_lamp',
            'INPUT': outputs['Street_lamp']['OUTPUT'],
            'MAX_DISTANCE': parameters['streetlamp'],
            'REFERENCE_LAYER': outputs['Road']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Street_lamp'] = processing.run('native:angletonearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 添加路灯朝向字段
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'osm_id',
            'FIELDS_TO_COPY': ['rotation_street_lamp'],
            'FIELD_2': 'osm_id',
            'INPUT': outputs['Traffic']['OUTPUT'],
            'INPUT_2': outputs['Street_lamp']['OUTPUT'],
            'METHOD': 1,  # 仅获取第一个匹配要素的属性（一对一）
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # 删除X坐标字段
        alg_params = {
            'COLUMN': ['X'],
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['X'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # 删除Y坐标字段
        alg_params = {
            'COLUMN': ['Y'],
            'INPUT': outputs['X']['OUTPUT'],
            'OUTPUT': parameters['3']
        }
        outputs['Y'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Trafficnewyorkpoint'] = outputs['Y']['OUTPUT']
        return results

    def name(self):
        return '计算路灯朝向'

    def displayName(self):
        return '计算路灯朝向'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return Streetlamprotation()

    def shortHelpString(self):
        return self.tr("")
