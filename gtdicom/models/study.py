from pydicom import Dataset

from gtdicom.connection import gtDicomConnection
from gtdicom.exception import gtDicomException
from gtdicom.models.base import BaseModel
from gtdicom.models.series import Series
from gtdicom.scu import Scu


class Study(BaseModel):
    attributes = ['PatientID',
                  'StudyInstanceUID',
                  'StudyDescription',
                  'StudyDate',
                  'StudyTime',
                  'Modality',
                  'AccessionNumber'
                  ]

    def __init__(self):
        super(Study, self).__init__()
        for attr in Study.attributes:
            setattr(self, attr, None)

    def get_series(self):
        if not self.connection:
            raise gtDicomException('Cannot get the studies. No connection available')

        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Series.attributes:
            ds.__setattr__(attr, '')

        ds.PatientID = self.PatientID
        ds.StudyInstanceUID = self.StudyInstanceUID
        ds.QueryRetrieveLevel = 'SERIES'

        identifiers = self.c_find(ds)
        series = []
        for identifier in identifiers:
            serie = Series()
            serie.create(identifier, self.connection)
            series.append(serie)

        return series



