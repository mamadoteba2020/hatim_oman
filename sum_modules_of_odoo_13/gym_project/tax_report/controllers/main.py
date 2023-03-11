#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class Binary(http.Controller):

    @http.route('/web/binary/download_document/<model("tax.report"):tax>', type='http', auth="user")
    @serialize_exception
    def download_document(self, tax, **kw):
        res = tax.print_report_excel_data()
        data = res and res[0] or ''
        filename = len(res) == 2 and res[1] or 'Report'
        filecontent = base64.b64decode(data)
        if not filecontent:
            return request.not_found()
        else:
            return request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename + '.xls'))])
