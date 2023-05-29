from .qgis_plugin import QGisPlugin


def classFactory(iface):
    return QGisPlugin(iface)
