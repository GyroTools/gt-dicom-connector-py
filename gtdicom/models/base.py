import os

from pydicom import Dataset

from gtdicom.connection import gtDicomConnection
from gtdicom.exception import gtDicomException
from gtdicom.scu import Scu


class BaseModel:
    def __init__(self):
        self.connection = None

    def create(self, ds: Dataset, connection: gtDicomConnection = None):
        self.connection = connection
        for attr in self.attributes:
            value = ds.__getattr__(attr)
            setattr(self, attr, value)

    def c_find(self, ds: Dataset):
        return Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)

class DownloadMixin:
    def download(self, output_directory: os.path = None, extension=None, overwrite=True):
        if not self.connection:
            raise gtDicomException('Cannot get the studies. No connection available')

        series = self.get_series()

        for serie in series:
            ds = Dataset()
            ds.QueryRetrieveLevel = 'SERIES'
            ds.PatientID = serie.PatientID
            ds.StudyInstanceUID = serie.StudyInstanceUID
            ds.SeriesInstanceUID = serie.SeriesInstanceUID
            ds.Modality = serie.Modality

            return Scu.c_get(self.connection.host, self.connection.port, ds, output_directory, overwrite, extension, self.connection.calling_aet, self.connection.called_aet)
