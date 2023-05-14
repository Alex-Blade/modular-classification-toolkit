"""
Model exported as python.
Name : FullPipeline
Group :
With QGIS : 33001
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterBand
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterDestination
import processing


class FullPipeline(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterField('class_field', 'Class Field', type=QgsProcessingParameterField.Any, parentLayerParameterName='training_data', allowMultiple=False, defaultValue='Class'))
        self.addParameter(QgsProcessingParameterField('id_field', 'ID Field', type=QgsProcessingParameterField.Any, parentLayerParameterName='training_data', allowMultiple=False, defaultValue='Id'))
        self.addParameter(QgsProcessingParameterRasterLayer('input_map', 'Input Map', defaultValue=None))
        self.addParameter(QgsProcessingParameterBand('processed_bands', 'Processed Bands', parentLayerParameterName='input_map', allowMultiple=True, optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer('training_data', 'Training Data', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Predicted', 'predicted', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Labeled Tiff Loader
        alg_params = {
            'INPUT_RASTER': parameters['input_map'],
            'LABELS_VECTOR': parameters['training_data'],
            'POLYGON_CLASS_FIELD': parameters['class_field'],
            'POLYGON_ID_FIELD': parameters['id_field'],
            'PROCESSED_BANDS': parameters['processed_bands'],
            'OUTPUT_FOLDER': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LabeledTiffLoader'] = processing.run('yourplugin:labeledtiffloader', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Unlabeled Tiff Raster
        alg_params = {
            'INPUT_RASTER': parameters['input_map'],
            'PROCESSED_BANDS': parameters['processed_bands'],
            'OUTPUT_FOLDER': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UnlabeledTiffRaster'] = processing.run('yourplugin:unlabeledtiffloader', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # SVM Fit
        alg_params = {
            'INPUT_DATA_FOLDER': outputs['LabeledTiffLoader']['OUTPUT_FOLDER'],
            'INPUT_DATA_IS_LABELED': True,
            'INPUT_MODEL_FILE': '',
            'MODEL_MODE': 0,  # Fit
            'OUTPUT_MODEL_FILE': '/tmp/model.gz',
            'OUTPUT_MODEL_FILE': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SvmFit'] = processing.run('yourplugin:svm', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # SVM Predict
        alg_params = {
            'INPUT_DATA_FOLDER': outputs['UnlabeledTiffRaster']['OUTPUT_FOLDER'],
            'INPUT_DATA_IS_LABELED': False,
            'INPUT_MODEL_FILE': outputs['SvmFit']['OUTPUT_MODEL_FILE'],
            'MODEL_MODE': 1,  # Predict
            'OUTPUT_MODEL_FILE': '/tmp/model.gz',
            'OUTPUT_DATA_FOLDER': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SvmPredict'] = processing.run('yourplugin:svm', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Predict Renderer
        alg_params = {
            'INPUT_RASTER': parameters['input_map'],
            'PREDICTION_FILE': outputs['SvmPredict']['OUTPUT_DATA_FOLDER'],
            'OUTPUT_RASTER': parameters['Predicted']
        }
        outputs['PredictRenderer'] = processing.run('yourplugin:renderer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Predicted'] = outputs['PredictRenderer']['OUTPUT_RASTER']
        return results

    def name(self):
        return 'FullPipeline'

    def displayName(self):
        return 'FullPipeline'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return FullPipeline()
