import pymupdf
from oocana import Context
import json
from io import BytesIO
from PIL import Image
from zbarlight import scan_codes
from datetime import datetime
import pandas as pd

# "in", "out" is the default node key.
# Redefine the name and type of the node, change it manually below.
# Click on the gear(⚙) to configure the input output UI

qrcode_keys = [
    "f0",
    "f1",
    "invoice_code",
    "invoice_number",
    "price",
    "date",
    "f5",
    "f6",
]


def main(inputs: dict, context: Context):
    attachments = json.loads(inputs.get("attachments"))
    total_price = 0
    invoice_number_price_map = {}

    invoice_col = []
    price_col = []

    for mail_id in attachments:
        mail_attachs = attachments[mail_id]
        for attach in mail_attachs:
            title = attach["title"]
            file_path = attach["attachement_path"]
            doc = pymupdf.open(file_path)
            if (doc.page_count == 0):
                continue
            # 仅认为发票只有一页
            pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(3, 3))
            pix.save(file_path + ".png")

            byte = pix.tobytes()
            img = Image.open(BytesIO(byte))
            codes = scan_codes(["qrcode"], img)
            print("QR codes: %s" % codes)

            values = list(codes[0].decode().split(","))
            ret = dict(zip(qrcode_keys, values))

            try:
                price = float(ret["price"])
            except:
                continue
            # invoice_col 中包含ret["invoice_number"]
            if (ret["invoice_number"] in invoice_col):
                continue
            total_price = total_price + price
            invoice_col.append(ret["invoice_number"])
            price_col.append(price)
            invoice_number_price_map[ret["invoice_number"]] = price

    invoice_col.append("合计")
    tp = rounded_number = round(total_price, 2)
    price_col.append(tp)

    invoice_number_price_map["合计"] = tp
    df = pd.DataFrame({"发票号": invoice_col, "金额": price_col})
    context.preview(df)

    return {"invoice_num_price_map": invoice_number_price_map}
