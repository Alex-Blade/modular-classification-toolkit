from typing import Iterator

import processing
import qgis.core as qcore
import rasterio as rio

from .raster_loader import RasterLoader, Band, Label, ListOfBands
from ..qgis_extensions import described


__all__ = ["UnlabeledTiffLoader", "LabeledTiffLoader"]


class UnlabeledTiffLoader(RasterLoader):
    INPUT_RASTER = "INPUT_RASTER"
    PROCESSED_BANDS = "PROCESSED_BANDS"
    OUTPUT_FOLDER = "UNLABELED_DATA"
    _display_name = "Unlabeled Tiff Raster"

    user_inputs = {INPUT_RASTER, PROCESSED_BANDS}

    def init_parameters_single_input(self):
        self.addParameter(
            qcore.QgsProcessingParameterRasterLayer(
                UnlabeledTiffLoader.INPUT_RASTER,
                described(UnlabeledTiffLoader.INPUT_RASTER),
                optional=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterBand(
                UnlabeledTiffLoader.PROCESSED_BANDS,
                described(UnlabeledTiffLoader.PROCESSED_BANDS),
                parentLayerParameterName=UnlabeledTiffLoader.INPUT_RASTER,
                allowMultiple=True,
                optional=True
            )
        )

    def init_parameters_multi_input(self):
        self.addParameter(
            qcore.QgsProcessingParameterMultipleLayers(
                UnlabeledTiffLoader.INPUT_RASTER,
                described(UnlabeledTiffLoader.INPUT_RASTER),
                layerType=qcore.QgsProcessing.SourceType.TypeRaster
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterString(
                UnlabeledTiffLoader.PROCESSED_BANDS,
                described(UnlabeledTiffLoader.PROCESSED_BANDS),
                optional=True
            )
        )

    def convert_to_numpy(self, parameters, context, feedback, multi_file) -> Iterator[ListOfBands]:
        raster_layers: list[qcore.QgsRasterLayer] = []
        if multi_file:
            raster_layers = self.parameterAsLayerList(parameters, UnlabeledTiffLoader.INPUT_RASTER, context)
            orig_str = self.parameterAsString(parameters, UnlabeledTiffLoader.PROCESSED_BANDS, context)
            bands = [int(i) for i in orig_str.split(',')]
        else:
            raster_layers.append(
                self.parameterAsRasterLayer(parameters, UnlabeledTiffLoader.INPUT_RASTER, context))
            bands = self.parameterAsInts(parameters, UnlabeledTiffLoader.PROCESSED_BANDS, context)

        if bands == [0]:
            bands = []

        feedback.pushDebugInfo(f"Expecting {len(bands)} in each source")

        for layer in raster_layers:
            source_file = layer.dataProvider().dataSourceUri()
            feedback.pushInfo(f"Source file: {source_file}")
            if not source_file.endswith(".tiff") and not source_file.endswith(".tif"):
                raise ValueError("Expected tiff file as source of the layer")

            with rio.open(source_file) as dataset:
                if bands:
                    result: ListOfBands = [Band(dataset.read(b)) for b in bands]
                else:
                    result: ListOfBands = [Band(dataset.read(b)) for b in dataset.indexes]
            yield result


class LabeledTiffLoader(RasterLoader):
    INPUT_RASTER = "INPUT_RASTER"
    PROCESSED_BANDS = "PROCESSED_BANDS"
    LABELS_VECTOR = "LABELS_VECTOR"
    POLYGON_ID_FIELD = "POLYGON_ID_FIELD"
    POLYGON_CLASS_FIELD = "POLYGON_CLASS_FIELD"
    OUTPUT_FOLDER = "LABELED_DATA"
    _display_name = "Labeled Tiff Loader"

    user_inputs = {INPUT_RASTER, PROCESSED_BANDS, LABELS_VECTOR, POLYGON_ID_FIELD, POLYGON_CLASS_FIELD}

    def init_parameters_single_input(self):
        self.addParameter(
            qcore.QgsProcessingParameterRasterLayer(
                LabeledTiffLoader.INPUT_RASTER,
                described(LabeledTiffLoader.INPUT_RASTER),
                optional=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterBand(
                LabeledTiffLoader.PROCESSED_BANDS,
                described(LabeledTiffLoader.PROCESSED_BANDS),
                parentLayerParameterName=LabeledTiffLoader.INPUT_RASTER,
                allowMultiple=True,
                optional=True
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterVectorLayer(
                LabeledTiffLoader.LABELS_VECTOR,
                described(LabeledTiffLoader.LABELS_VECTOR),
                types=[qcore.QgsProcessing.SourceType.TypeVectorPolygon],
                optional=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterField(
                LabeledTiffLoader.POLYGON_ID_FIELD,
                described(LabeledTiffLoader.POLYGON_ID_FIELD),
                parentLayerParameterName=LabeledTiffLoader.LABELS_VECTOR,
                optional=False
            )
        )

        self.addParameter(
            qcore.QgsProcessingParameterField(
                LabeledTiffLoader.POLYGON_CLASS_FIELD,
                described(LabeledTiffLoader.POLYGON_CLASS_FIELD),
                parentLayerParameterName=LabeledTiffLoader.LABELS_VECTOR,
                optional=False
            )
        )

    def init_parameters_multi_input(self):
        raise NotImplementedError("We do not know how to deal with that yet")

    def convert_to_numpy(self, parameters, context, feedback, multi_file: bool) -> Iterator[ListOfBands]:
        raster_layers: list[qcore.QgsRasterLayer] = []
        if multi_file:
            raise NotImplementedError("We do not know how to deal with that yet")
        else:
            raster_layers.append(
                self.parameterAsRasterLayer(parameters, LabeledTiffLoader.INPUT_RASTER, context))
            bands = self.parameterAsInts(parameters, LabeledTiffLoader.PROCESSED_BANDS, context)

        if bands == [0]:
            bands = []

        vector_layer: qcore.QgsVectorLayer = self.parameterAsVectorLayer(parameters,
                                                                             LabeledTiffLoader.LABELS_VECTOR,
                                                                             context)
        id_field = self.parameterAsString(parameters, LabeledTiffLoader.POLYGON_ID_FIELD, context)
        class_field = self.parameterAsString(parameters, LabeledTiffLoader.POLYGON_CLASS_FIELD, context)

        feedback.pushDebugInfo(f"Expecting {len(bands)} in each source")
        feedback.pushDebugInfo(f"Vector: {vector_layer.dataProvider().dataSourceUri()}")
        feedback.pushDebugInfo(f"ID Field: {id_field}, Class Field: {class_field}")

        for feature in vector_layer.getFeatures():
            feature: qcore.QgsFeature
            if feature.hasGeometry():
                if not multi_file:
                    _id = feature.attribute(id_field)
                    _class = feature.attribute(class_field)
                    bands_opts = ' '.join([f"-b {b}" for b in bands])
                    raster_layers[0].subLayers()
                    res = processing.run("gdal:cliprasterbymasklayer",
                                         {'INPUT': raster_layers[0].dataProvider().dataSourceUri(),
                                          'MASK': vector_layer.dataProvider().dataSourceUri(), 'SOURCE_CRS': None, 'TARGET_CRS': None,
                                          'TARGET_EXTENT': None, 'NODATA': None, 'ALPHA_BAND': False,
                                          'CROP_TO_CUTLINE': True,
                                          'KEEP_RESOLUTION': False, 'SET_RESOLUTION': False, 'X_RESOLUTION': None,
                                          'Y_RESOLUTION': None, 'MULTITHREADING': False, 'OPTIONS': '', 'DATA_TYPE': 0,
                                          'EXTRA': f'-cwhere "Id=\'{_id}\'" {bands_opts}', 'OUTPUT': 'TEMPORARY_OUTPUT'})
                    feedback.pushInfo(f"{res}")
                    with rio.open(res["OUTPUT"]) as dataset:
                        if bands:
                            result: ListOfBands = [Band(dataset.read(b)) for b in bands]
                        else:
                            result: ListOfBands = [Band(dataset.read(b)) for b in dataset.indexes]
                    result.append(Label(_id, _class))
                    yield result
