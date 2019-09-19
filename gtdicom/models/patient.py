from pydicom import Dataset

from gtdicom.connection import gtDicomConnection
from gtdicom.exception import gtDicomException
from gtdicom.models.base import BaseModel
from gtdicom.models.series import Series
from gtdicom.models.study import Study
from gtdicom.scu import Scu


class Patient(BaseModel):
    attributes = ['PatientID',
                  'PatientName',
                  'PatientBirthDate',
                  'PatientSex',
                  'PatientAge',
                  'PatientWeight',
                  'ScheduledPerformingPhysicianName',
                  'ReferringPhysicianName',
                  'Modality',
                  ]

    def __init__(self):
        super(Patient, self).__init__()
        for attr in Patient.attributes:
            setattr(self, attr, None)

    def get_studies(self):
        if not self.connection:
            raise gtDicomException('Cannot get the studies. No connection available')

        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Study.attributes:
            ds.__setattr__(attr, '')

        ds.PatientID = self.PatientID
        ds.QueryRetrieveLevel = 'STUDY'

        identifiers = self.c_find(ds)
        studies = []
        for identifier in identifiers:
            study = Study()
            study.create(identifier, self.connection)
            studies.append(study)

        return studies

    def get_series(self):
        series = []
        studies = self.get_studies()
        for study in studies:
            cur_series = study.get_series()
            series.extend(cur_series)
        return series






