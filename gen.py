# encoding: utf-8

import os

from api import SwaggerTemplateRender, load_path_wrapper, load_swagger_url
from filters import __filters__
from parse import SwaggerSchema, SwaggerPath

base_dir = os.path.dirname(__file__)
template_dir = os.path.join(base_dir, 'templates')
root_dir = os.path.join(base_dir, 'output')

swagger_url = 'http://192.168.50.136:9900/api/doc/swagger.json'
root_name = 'cn.linkeddt.wisdomwatersystem'
app_name = 'irrms'
package_name = 'monitor'


def gen_java_entity(schema_name_list):
    api = SwaggerTemplateRender(template_dir, __filters__)
    _out_dir = os.path.join(root_dir, 'entitys')

    def rename(schema: SwaggerSchema):
        return f'{schema.name}.java'

    def filter_schema(schema: SwaggerSchema):
        return schema.name in schema_name_list

    swagger_doc = load_swagger_url(swagger_url)
    api.gen_schema_template_file(swagger_doc, 'java_entity.jinja2', _out_dir,
                                 filter_schema, rename,
                                 **{'root_name': root_name, 'app_name': app_name, 'package_name': package_name})


def gen_java_entity_query():
    api = SwaggerTemplateRender(template_dir, __filters__)
    _out_dir = os.path.join(root_dir, 'entitys', 'query')

    def rename(schema: SwaggerSchema):
        return f'{schema.name}.java'

    def filter_schema(schema: SwaggerSchema):
        return 'Monitor' in schema.name and 'Query' in schema.name

    swagger_doc = load_swagger_url(swagger_url)
    api.gen_schema_template_file(swagger_doc, 'java_entity_query.jinja2', _out_dir,
                                 filter_schema, rename,
                                 **{'root_name': root_name, 'app_name': app_name, 'package_name': package_name})


def gen_android_api(path_uri_prefix: str, class_name: str):
    api = SwaggerTemplateRender(template_dir, __filters__)

    def filter_path(path: SwaggerPath):
        return path_uri_prefix in path.uri

    def filter_schema(schema: SwaggerSchema):
        return True

    def _gen_android_service(schemas, paths, request_schemas, response_schemas, out_dir, file_name):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        t = api.get_template('android_service.jinja2')
        d = {'schemas': schemas, 'paths': paths, 'request_schemas': request_schemas,
             'response_schemas': response_schemas}
        d.update({'root_name': root_name, 'app_name': app_name,
                  'package_name': package_name, 'class_name': class_name})

        out_file = os.path.join(out_dir, file_name)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(t.render(d))

    def _gen_android_repo(schemas, paths, request_schemas, response_schemas, out_dir, file_name):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        t = api.get_template('android_repo.jinja2')
        d = {'schemas': schemas, 'paths': paths, 'request_schemas': request_schemas,
             'response_schemas': response_schemas}
        d.update({'root_name': root_name, 'app_name': app_name,
                  'package_name': package_name, 'class_name': class_name})

        out_file = os.path.join(out_dir, file_name)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(t.render(d))

    def _gen_java_entity(t, schemas, out_dir):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for schema in schemas:
            d = {'schema': schema, 'fields': [field for field in schema.parse_field()]}
            d.update({'root_name': root_name, 'app_name': app_name, 'package_name': package_name})
            out_file = os.path.join(out_dir, f'{schema.name}.java')
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(t.render(d))

    swagger_doc = load_swagger_url(swagger_url)
    wrapper = load_path_wrapper(swagger_doc, filter_schema_func=filter_schema, filter_path_func=filter_path)

    _gen_java_entity(api.get_template('java_entity_query.jinja2'), wrapper.request_schemas,
                     os.path.join(root_dir, 'entitys', 'query'))

    _gen_java_entity(api.get_template('java_entity.jinja2'), wrapper.response_schemas,
                     os.path.join(root_dir, 'entitys'))

    _gen_android_service(wrapper.schemas, wrapper.paths, wrapper.request_schemas, wrapper.response_schemas,
                         os.path.join(root_dir, 'services'), f'{class_name}Service.java')

    _gen_android_repo(wrapper.schemas, wrapper.paths, wrapper.request_schemas, wrapper.response_schemas,
                      os.path.join(root_dir, 'repos'), f'{class_name}Repo.java')


def batch_gen_android_repo():
    patrol_table_lst = [('/api/patrol/patrol_category/', 'PatrolCategory'),
                        ('/api/patrol/patrol_object/', 'PatrolObject'),
                        ('/api/patrol/patrol_item/', 'PatrolItem'),
                        ('/api/patrol/patrol_plan/', 'PatrolPlan'),
                        ('/api/patrol/patrol_inspection/', 'PatrolInspection'),
                        ('/api/patrol/patrol_inspection_track/', 'PatrolInspectionTrack'),
                        ('/api/patrol/patrol_report/', 'PatrolReport'),
                        ('/api/patrol/patrol_report_transfer/', 'PatrolReportTransfer'),
                        ('/api/patrol/patrol_report_file/', 'PatrolReportFile'),
                        ('/api/patrol/patrol_report_solve/', 'PatrolReportSolve'),
                        ('/api/patrol/patrol_report_solve_file/', 'PatrolReportSolveFile')]

    monitor_table_lst1 = [('/api/monitor/monitor_wdpstat_new/page', 'MonitorWdpstatNew'), ]

    monitor_table_lst = [('/api/monitor/monitor_station/', 'MonitorStation'),
                         ('/api/monitor/monitor_rain/', 'MonitorRain'),
                         ('/api/monitor/monitor_rain_new/', 'MonitorRainNew'),
                         ('/api/monitor/monitor_rain_hour/', 'MonitorRainHour'),
                         ('/api/monitor/monitor_rain_day/', 'MonitorRainDay'),
                         ('/api/monitor/monitor_rain_month/', 'MonitorRainMonth'),
                         ('/api/monitor/monitor_canal/', 'MonitorCanal'),
                         ('/api/monitor/monitor_canal_new/', 'MonitorCanalNew'),
                         ('/api/monitor/monitor_rsvr/', 'MonitorRsvr'),
                         ('/api/monitor/monitor_rsvr_new/', 'MonitorRsvrNew'),
                         ('/api/monitor/monitor_wdpstat/', 'MonitorWdpstat'),
                         ('/api/monitor/monitor_wdpstat_new/', 'MonitorWdpstatNew'),
                         ('/api/monitor/monitor_wdpstat_hour/', 'MonitorWdpstatHour'),
                         ('/api/monitor/monitor_wdpstat_day/', 'MonitorWdpstatDay'),
                         ('/api/monitor/monitor_wdpstat_month/', 'MonitorWdpstatMonth'),
                         ('/api/monitor/monitor_gate/', 'MonitorGate'),
                         ('/api/monitor/monitor_gate_new/', 'MonitorGateNew'),
                         ('/api/monitor/monitor_gate_log/', 'MonitorGateLog'),
                         ('/api/monitor/monitor_meteorology/', 'MonitorMeteorology'),
                         ('/api/monitor/monitor_meteorology_new/', 'MonitorMeteorologyNew'),
                         ('/api/monitor/monitor_waterquality/', 'MonitorWaterquality'),
                         ('/api/monitor/monitor_waterquality_new/', 'MonitorWaterqualityNew'),
                         ('/api/monitor/monitor_gnss/', 'MonitorGnss'),
                         ('/api/monitor/monitor_gnss_new/', 'MonitorGnssNew'),
                         ('/api/monitor/monitor_tilt/', 'MonitorTilt'),
                         ('/api/monitor/monitor_tilt_new/', 'MonitorTiltNew'),
                         ('/api/monitor/monitor_pressure/', 'MonitorPressure'),
                         ('/api/monitor/monitor_pressure_new/', 'MonitorPressureNew'),
                         ('/api/monitor/monitor_flow/', 'MonitorFlow'),
                         ('/api/monitor/monitor_flow_new/', 'MonitorFlowNew'),
                         ('/api/monitor/warn_record/', 'WarnRecord')]

    for item in monitor_table_lst:
        gen_android_api(item[0], item[1])

    """
    gen_java_entity(['PatrolReportWrapper', 'PatrolReport', 'PatrolReportFile', 'MainPatrolItem', 'PatrolItem',
                     'UploadFileResult'])
    """

    gen_java_entity(['MonitorCanalGroupStation', 'MonitorRsvrDownwaterCapacity',
                     'MonitorRsvrDownwaterOverview', 'WarnRecordAll', 'WaterqualityQualified', 'MonitorGateNewAll'])


if __name__ == '__main__':
    batch_gen_android_repo()
