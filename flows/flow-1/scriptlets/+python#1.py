from datetime import datetime
from email.header import decode_header, make_header
from imapclient import IMAPClient
from oocana import Context


def mail_may_include_invoice_by_subject(subject: str):
    if "发票" not in subject and "invoice" not in subject:
        return False
    return True


def main(inputs: dict, context: Context):
    server = IMAPClient("imap.163.com", port=993, use_uid=True, ssl=True)
    server.login(inputs.get("email"), inputs.get("password"))
    server.id_({"name": "IMAPClient", "version": "3.0.1"})
    server.select_folder("INBOX", readonly=True)

    from_date_str = datetime.strptime(inputs.get("from_date"), "%Y-%m-%d").strftime(
        "%d-%b-%Y"
    )
    to_date_str = datetime.strptime(inputs.get("to_date"), "%Y-%m-%d").strftime(
        "%d-%b-%Y"
    )

    mail_ids = server.search(
        ["SINCE", from_date_str, ["NOT", ["SINCE", to_date_str]]], "UTF-8"
    )

    # for mail_id in mail_ids:
    response = server.fetch(mail_ids, ["ENVELOPE", "BODY[TEXT]", 'RFC822'])

    mails_may_not_include_invoice = []
    mails_may_include_invoice = []

    for message_id, data in response.items():
        envelope = data[b"ENVELOPE"]
        subject = envelope.subject.decode()
        decodedSubject = str(make_header(decode_header(subject)))
        print(decodedSubject)
        if mail_may_include_invoice_by_subject(decodedSubject):
            mails_may_include_invoice.append(data)
            continue
        mails_may_not_include_invoice.append(data)

    return {
        "mails_may_not_include_invoice": mails_may_not_include_invoice,
        "mails_may_include_invoice": mails_may_include_invoice,
    }
