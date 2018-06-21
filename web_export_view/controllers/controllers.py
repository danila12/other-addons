# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013:
#        Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
import re
import os
from cStringIO import StringIO
try:
    import json
except ImportError:
    import simplejson as json

try:
    import xlwt
except ImportError:
    xlwt = None

import openerp.http as http
from openerp.http import request
from openerp.addons.web.controllers.main import ExcelExport
# from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import osv


class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    @http.route('/web/export/xls_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        # uid = request
        if request.env.user.has_group('base.export'):
            pass
        else:
            # raise Warning('You can not have authorization to confirm sale order.')
            raise osv.except_osv(('Error'), ('Utilizator fara drepturi de export: %s') % request.env.user.name)
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    def from_data(self, fields, rows):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        offset = 5 #minimum 3, for header data
        #header
        image = os.path.join( os.path.dirname ( __file__), os.path.pardir,'static','img','logo.bmp')
        worksheet.insert_bitmap(image,0,0)
        for i, fieldname in enumerate(fields):
            if (fieldname.find('Selected records') < 0):
                worksheet.write(offset-1, i, fieldname)
            # worksheet.col(i).width = 8000 # around 220 pixels

        bold_style = xlwt.easyxf('font: bold on')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')
        now = datetime.datetime.now()
        crt_date = now.strftime("%d/%m/%Y")
        worksheet.write(0,5,'Data: '+crt_date)
        lastindex = len(fields)-1
        model_name = fields[lastindex]
        worksheet.write(offset - 2, 0, model_name[18:],bold_style)
        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                cell_style = base_style
                if isinstance(cell_value, basestring):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = datetime_style
                elif isinstance(cell_value, datetime.date):
                    cell_style = date_style
                worksheet.write(row_index + offset, cell_index, cell_value, cell_style)

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data



