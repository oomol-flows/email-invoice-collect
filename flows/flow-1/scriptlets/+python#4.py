from email.header import decode_header, make_header
from oocana import Context
import pandas as pd


def main(inputs: dict, context: Context):

    mails = inputs.get("mails")

    titleCol = []
    dateCol = []
    for mail_data in mails:
        envelope = mail_data[b"ENVELOPE"]
        subject = envelope.subject.decode()
        decodedSubject = str(make_header(decode_header(subject)))

        titleCol.append(decodedSubject)
        dateCol.append(envelope.date.strftime("%Y-%m-%d"))

    df= pd.DataFrame({'标题': titleCol, '日期': dateCol})
    context.preview(df)
