from . import Mongo


class Lagou(Mongo):
    @classmethod
    def _fields(cls):
        fields = [
            ('job_name', str, ''),
            ('job_tags', str, ''),
            ('addr', str, ''),
            ('money', str, ''),
            ('experience', str, ''),
            ('education', str, ''),
            ('company', str, ''),
            ('company_industry', str, ''),
            ('company_good_point', str, ''),
            ('format_time', str, ''),
            ('url', str, ''),
        ]
        fields.extend(super()._fields())
        return fields
