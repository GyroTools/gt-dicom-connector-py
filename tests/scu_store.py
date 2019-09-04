from gtdicom.connection import gtDicomConnection
from gtdicom.gtdicom import gtDicom

addr = 'www.dicomserver.co.uk'
port = 104

connection = gtDicomConnection(addr, port)
gt_dicom = gtDicom(connection)

if not gt_dicom.echo():
    print('ERROR: Cannot establish a connection to the DICOM node. Please check the hostname and port')
    exit()

#gt_dicom.store('C:/Users/martin/Desktop/temp/dicom/')
gt_dicom.store('C:/Users/martin/Desktop/temp/dicom/IM_0001')

