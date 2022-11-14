"""
Model exported as python.
Name : 创建网格图层
Group : 
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


class chuangjianquyuwangge(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('', '输入划分区域的图层', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('tile', 'tile大小', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=50))
        self.addParameter(QgsProcessingParameterFeatureSink('Regiongrid', 'regionGrid', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}

        # 创建网格
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:900913'),
            'EXTENT': parameters[''],
            'HOVERLAY': 0,
            'HSPACING': parameters['tile'],
            'TYPE': 1,  # 线
            'VOVERLAY': 0,
            'VSPACING': parameters['tile'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 多边形化
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 按位置提取
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'INTERSECT': parameters[''],
            'PREDICATE': [0],  # 相交
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # x字段计算器
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'xCoord',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # 浮点型
            'FORMULA': 'x( centroid($geometry))',
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['X'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # y字段计算器
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'yCoord',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # 浮点型
            'FORMULA': 'y( centroid($geometry))',
            'INPUT': outputs['X']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Y'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 添加Id字段
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'blockId',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # 字符串
            'FORMULA': 'NULL',
            'INPUT': outputs['Y']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Id'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # 添加regionId
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'regionId',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # 字符串
            'FORMULA': 'NULL',
            'INPUT': outputs['Id']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Regionid'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # 地块区域划分
        alg_params = {
            'INPUT': outputs['Regionid']['OUTPUT'],
            'tileSize': 50,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('script:地块区域划分', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # 计算块所属区域
        alg_params = {
            'INPUT': outputs['']['OUTPUT'],
            'INPUT2': parameters[''],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs[''] = processing.run('script:计算块所属区域', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # 删除字段xCoord
        alg_params = {
            'COLUMN': ['xCoord'],
            'INPUT': outputs['']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Xcoord'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # 删除字段yCoord
        alg_params = {
            'COLUMN': ['yCoord'],
            'INPUT': outputs['Xcoord']['OUTPUT'],
            'OUTPUT': parameters['Regiongrid']
        }
        outputs['Ycoord'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Regiongrid'] = outputs['Ycoord']['OUTPUT']
        return results

    def name(self):
        return '创建区域网格'

    def displayName(self):
        return '创建区域网格'

    def group(self):
        return 'QGis-resources'

    def groupId(self):
        return 'QGis-resources'

    def createInstance(self):
        return chuangjianquyuwangge()
