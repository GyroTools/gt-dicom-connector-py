from pydicom import Dataset

from gtdicom.models.base import BaseModel, DownloadMixin


class Series(DownloadMixin, BaseModel):
    attributes = ['PatientID',
                  'StudyInstanceUID',
                  'SeriesInstanceUID',
                  'SeriesDescription',
                  'SeriesDate',
                  'SeriesTime',
                  'Modality',
                  ]

    def __init__(self):
        super(Series, self).__init__()
        for attr in Series.attributes:
            setattr(self, attr, None)

    def get_series(self):
        return [self]
