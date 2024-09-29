from oocana import Context
import json

# "in", "out" is the default node key.
# Redefine the name and type of the node, change it manually below.
# Click on the gear(⚙) to configure the input output UI


def main(inputs: dict, context: Context):
    attachments = json.loads(inputs.get("attachments"))
    for mail_id in attachments:
        mail_attachs = attachments[mail_id]
        for attach in mail_attachs:
            title = attach["title"]
            file_path = attach["attachement_path"]
            print(title)
            print(file_path)

        # title = attachment["title"]
        # print(title)
        # attachment_path = attachment["attachement_path"]


    # preview pandas dataframe
    # context.preview(df)

    # context.preview({
    #   # type can be "image", "video", "audio", "markdown", "table", "iframe"
    #   "type": "image",
    #   # data can be file path, base64, pandas dataframe
    #   "data": "",
    # })

    return {"out": None}
