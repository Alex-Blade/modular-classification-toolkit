from pathlib import Path

import qgis.core as qcore
from mct.mct_processing.qgis_extensions import described
from ..algorithm import Algorithm
import numpy as np
from osgeo import gdal


__all__ = ["Renderer"]


class Renderer(Algorithm):
    name_string = "renderer"
    display_name = "Predict Renderer"
    group_string = "Renderers"
    group_id = "renders"
    help_string = ""

    INPUT_RASTER = "INPUT_RASTER"
    PREDICTIONS_FOLDER = "PREDICTIONS_FOLDER"
    OUTPUT_RASTER = "OUTPUT_RASTER"

    user_inputs = {}

    def tr(self, string) -> str:
        """
        Translation boilerplate
        """
        import sklearn.svm as sss
        return string

    def initAlgorithm(self, config=None):
        self.addParameter(
            qcore.QgsProcessingParameterRasterLayer(
                Renderer.INPUT_RASTER,
                described(Renderer.INPUT_RASTER),
                optional=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterString(
                Renderer.PREDICTIONS_FOLDER,
                described(Renderer.PREDICTIONS_FOLDER)
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterRasterDestination(
                Renderer.OUTPUT_RASTER,
                description=described(Renderer.OUTPUT_RASTER),
                defaultValue=qcore.QgsProcessing.TEMPORARY_OUTPUT,
                createByDefault=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        raster_layer = self.parameterAsRasterLayer(parameters, Renderer.INPUT_RASTER, context)
        predictions = self.parameterAsString(parameters, Renderer.PREDICTIONS_FOLDER, context)
        output_raster = self.parameterAsOutputLayer(parameters, Renderer.OUTPUT_RASTER, context)

        if (p := Path(predictions)).is_dir():
            predictions = str(next(p.glob("*.npz")))
        files = np.load(predictions)
        pred: np.ndarray = files["arr_0"]
        files.close()

        unique_classes = np.unique(pred)
        m = {v: idx + 1 for idx, v in enumerate(unique_classes)}
        l = 255 // len(unique_classes)
        separated_pred = np.zeros_like(pred, dtype='uint8')
        for c in unique_classes:
            separated_pred[pred == c] = l * m[c]
        img = separated_pred.reshape(raster_layer.height(), raster_layer.width())

        orig_file: gdal.Dataset = gdal.Open(raster_layer.dataProvider().dataSourceUri(), gdal.GA_ReadOnly)
        gd_driver: gdal.Driver = gdal.GetDriverByName("MEM")
        gd_raster: gdal.Dataset = gd_driver.Create('', raster_layer.width(), raster_layer.height(), 1, gdal.GDT_Byte)
        gd_raster.SetGeoTransform(orig_file.GetGeoTransform())
        gd_raster.SetProjection(orig_file.GetProjection())
        band: gdal.Band = gd_raster.GetRasterBand(1)
        # band.SetScale(1.0)
        # band.SetOffset(0.0)
        band.WriteArray(img)

        dset_tiff_out = gdal.GetDriverByName('GTiff')

        feedback.pushInfo(str(output_raster))
        dset_tiff_out.CreateCopy(output_raster, gd_raster, 1)
        dset_tiff_out = None
        gd_raster = None
        return {Renderer.OUTPUT_RASTER: output_raster}
