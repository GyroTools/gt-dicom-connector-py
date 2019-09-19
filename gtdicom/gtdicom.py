import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from gtdicom.connection import gtDicomConnection
from gtdicom.models.patient import Patient
from gtdicom.models.series import Series
from gtdicom.models.study import Study
from gtdicom.scu import Scu
from gtdicom.utils import to_path_array, get_filelist_from_path_array, is_dicom_file


class gtDicom:
    def __init__(self, connection: gtDicomConnection):
        self.connection = connection

    def echo(self):
        return Scu.c_echo(self.connection.host, self.connection.port, self.connection.calling_aet,
                                 self.connection.called_aet)

    def get_patients(self, search_string='*', modality=None):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Patient.attributes:
            ds.__setattr__(attr, '')

        if modality:
            ds.Modality = modality
        ds.PatientName = search_string
        ds.QueryRetrieveLevel = 'PATIENT'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        patients = []
        for identifier in identifiers:
            patient = Patient()
            patient.create(identifier, self.connection)
            patients.append(patient)

        return patients

    def get_studies(self, search_string=None, patient_id=None, modality=None):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Study.attributes:
            ds.__setattr__(attr, '')

        if modality:
            ds.Modality = modality
        if patient_id:
            ds.PatientID = patient_id
        if search_string:
            ds.StudyDescription = search_string
        ds.QueryRetrieveLevel = 'STUDY'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        studies = []
        for identifier in identifiers:
            study = Study()
            study.create(identifier, self.connection)
            studies.append(study)

        return studies

    def get_series(self, study_uid=None, modality=None):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Series.attributes:
            ds.__setattr__(attr, '')

        if study_uid:
            ds.StudyInstanceUID = study_uid
        if modality:
            ds.Modality = modality
        ds.QueryRetrieveLevel = 'SERIES'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        series = []
        for identifier in identifiers:
            serie = Series()
            serie.create(identifier, self.connection)
            series.append(serie)

        return series

    def get_patient(self, patient_uid):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Patient.attributes:
            ds.__setattr__(attr, '')

        ds.PatientID = patient_uid
        ds.QueryRetrieveLevel = 'PATIENT'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        for identifier in identifiers:
            patient = Patient()
            patient.create(identifier, self.connection)
            return patient

        return None

    def get_study(self, study_uid):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Study.attributes:
            ds.__setattr__(attr, '')

        ds.StudyInstanceUID = study_uid
        ds.QueryRetrieveLevel = 'STUDY'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        for identifier in identifiers:
            study = Study()
            study.create(identifier, self.connection)
            return study

        return None

    def get_serie(self, series_uid):
        # Create our Identifier (query) dataset
        ds = Dataset()

        for attr in Series.attributes:
            ds.__setattr__(attr, '')

        ds.SeriesInstanceUID = series_uid
        ds.QueryRetrieveLevel = 'SERIES'

        identifiers = Scu.c_find(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
        for identifier in identifiers:
            serie = Series()
            serie.create(identifier, self.connection)
            return serie

        return None

    def store(self, files):
        files = to_path_array(files)
        if not files:
            return None

        files = get_filelist_from_path_array(files)

        for file in files:
            if is_dicom_file(file):
                try:
                    f = open(file, 'rb')
                    ds = dcmread(f, force=True)
                    f.close()
                    Scu.c_store(self.connection.host, self.connection.port, ds, self.connection.calling_aet, self.connection.called_aet)
                except IOError:
                    pass



