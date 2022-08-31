# Invoice-Download-SAP

invoinceDownload.py is a script that automates the download of invoices from the afip website. The output is an .xlsx file with the data of each invoice.

rfcSAP.py is used to establish a RFC connection with SAP and use it's well known RFC_READ_TABLE to read data from it's tables. 

The flow consists of getting the invoices and querying SAP to check if they have been processed already. This way you get an early warning of pending invoinces. 

In order to check if the invoice was processed or not , the tables LFA1, BKPF and BSEG are a good alternative if your system doesn't count with an dedicated rfc function for this matter.
