import os
import shutil
from qgis.core import QgsVectorFileWriter, QgsCoordinateTransformContext, QgsWkbTypes


# create geopackage
def _create_gpkg_from_layer(self, lyr, isSelected):
    layer_source = lyr.dataProvider().dataSourceUri()

    (dirLayer, nameLayer) = os.path.split(layer_source)
    self.layerCopyPath_add = os.path.join(
        dirLayer,
        'flexgis_temp_layers',
        'flexgis_edit_layer.gpkg',
    )
    self.folderCopyPath_add = os.path.join(
        dirLayer,
        'flexgis_temp_layers'
    )
    if not os.path.exists(self.folderCopyPath_add):
        os.mkdir(self.folderCopyPath_add)

    transformContext = QgsCoordinateTransformContext()
    options = QgsVectorFileWriter.SaveVectorOptions()
    QgsVectorFileWriter.create(
        self.layerCopyPath_add,
        lyr.fields(),
        QgsWkbTypes.Unknown,
        lyr.crs(),
        transformContext,
        options
    )
    QgsVectorFileWriter.writeAsVectorFormat(lyr,
                                            self.layerCopyPath_add,
                                            'utf-8',
                                            lyr.crs(),
                                            "GPKG",
                                            onlySelected=isSelected
                                            )


# clear temp folder
def _clear_folder(self, folder: str):
    shutil.rmtree(folder, ignore_errors=True)