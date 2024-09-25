from email.header import decode_header, make_header
import os
import email
from oocana import Context
import pandas as pd
import json

# 文件下载到工作空间
temp_file_dir = "/app/workspace/temp_file"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class AttachmentMeta:
    def __init__(self, mail_id, title, attachment_path, date):
        self.mail_id = mail_id
        self.title = title
        self.attachment_path = attachment_path
        self.date = date

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


print("ab path ", os.path.abspath(temp_file_dir))


# allows you to download attachments
def get_attachments(mails_attachments, mail_data):
    ensure_dir(temp_file_dir)
    msg = email.message_from_bytes(mail_data[b"RFC822"])

    # Takes the raw data and breaks it into different 'parts' & python processes it 1 at a time [1]
    for part in msg.walk():
        if (
            part.get_content_maintype() == "multipart"
        ):  # Checks if the email is the correct 'type'.
            # If it's a 'multipart', then it is incorrect type of email that can possible have an attachment
            continue  # Continue command skips the rest of code and checks the next 'part'

        if (
            part.get("Content-Disposition") is None
        ):  # Checks the 'Content-Disposition' field of the message.
            # If it's empty, or "None", then we need to leave and go to the next part
            continue  # Continue command skips the rest of code and checks the next 'part'
        # So if the part isn't a 'multipart' type and has a 'Content-Disposition'...

        file_name = part.get_filename()  # Get the filename
        decoded_file_name = str(make_header(decode_header(file_name)))
        print("file name ", decoded_file_name)
        if bool(decoded_file_name):
            _, file_extension = os.path.splitext(decoded_file_name)
            if file_extension.upper() != ".PDF" and file_extension.upper() != ".ZIP":
                continue

            # TODO 读取 messageId ，用 Id创建文件夹，然后记录 id 和 title，日期 的对象
            # 下一步从通过 id 读取 文件夹内的全部 pdf，然后逐个解析，展示的时候 key 是 title，日志，加上发票号和价格
            envelope = mail_data[b"ENVELOPE"]
            message_id = envelope.message_id.decode()

            mail_attachement_path = os.path.join(temp_file_dir, message_id)
            ensure_dir(mail_attachement_path)

            file_path = os.path.join(
                mail_attachement_path, decoded_file_name
            )  # Combine the save directory and file name to make file_path
            with open(
                file_path, "wb"
            ) as f:  # Opens file, w = creates if it doesn't exist / b = binary mode [2]
                f.write(
                    part.get_payload(decode=True)
                )  # Returns the part is carrying, or it's payload, and decodes [3]

            if file_extension.upper() == ".ZIP":
                # TODO 解压 zip 文件，更新地址
                print("zip file ", file_extension)
            else:
                attachment_meta = {
                    "mail_id": message_id,
                    "title": decoded_file_name,
                    "attachement_path": mail_attachement_path,
                    "date": envelope.date.strftime("%Y-%m-%d"),
                }
                if message_id in mails_attachments:
                    mails_attachments[message_id].append(attachment_meta)
                else:
                    mails_attachments[message_id] = [attachment_meta]


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

    df = pd.DataFrame({"标题": titleCol, "日期": dateCol})
    context.preview(df)

    mails_attachments = {}

    for mail_data in mails:
        get_attachments(mails_attachments, mail_data)

    return {"attachments": json.dumps(mails_attachments)}
