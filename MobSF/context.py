# -*- coding: utf_8 -*-
"""
Generate UIs of dynamic engines
"""

engines_name = [
    "STATIC",
    "HARDCODED",
    "DATABASE",
    "CONFIG_MANIPULATION",
    "SOURCE_MANIPULATION",
    "DATABASE_MANIPULATION",
    "COMMUNICATION_PLAIN",
    "CERTCONFIG",
    "CERT_LOCKED",
    "REPLAY",
    "TIMEOUT",
    "HIJACK",
    "MSG_DOS",
    "NETWORK",
    "REGISTER_LOGIN",
    "PHONE_CLOUD",
    "DEVICE_CLOUD",
    ]

item_steps = [
    # can't locate package correctly before static analysis as reject to 'adb's
    ['download', 'zip', 'dex2jar', 'jdgui', 'openso'],  # 敏感数据硬编码
    ['adb-pull'],
    ['adb-pull'],
    ['apktool_d', 'change_adb', 'apktool_b', 'manual'],  # 资源文件篡改检测
    ['adb-pull'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual'],
    ['burpsuite', 'manual', 'wireshark', 'manual', 'tcpdump', 'manual', 'tcpdata', 'manual'],  # 设备配网安全检测
    ['burpsuite', 'manual', 'wireshark', 'manual'],  # 用户注册与登陆安全
    ['jmeter', 'manual'],
    ['jmeter', 'manual']

]

auto_steps = ['download', 'zip', 'dex2jar', 'apktool_d', 'apktool_b', 'burpsuite', 'wireshark']


dynamic_attr = [
    "HARDCODED",
    "DATABASE",
    "CONFIG_MANIPULATION",
    "SOURCE_MANIPULATION",
    "DATABASE_MANIPULATION",
    "COMMUNICATION_PLAIN",
    "CERTCONFIG",
    "CERT_LOCKED",
    "REPLAY",
    "TIMEOUT",
    "HIJACK",
    "MSG_DOS",
    "NETWORK",
    "REGISTER_LOGIN",
    "PHONE_CLOUD",
    "DEVICE_CLOUD",
    ]


def generate_row(engine, dynamic):
    finishes = dynamic.FINISHES.split(",")
    row = '<div class="row" id="dynamic-anaylsis-' + engine + '''"> 
                    <div class="col-md-12">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <i class="fa fa-cog"></i>&nbsp;&nbsp;''' + engines_name[int(engine)] + '''</div>

                            <div class="panel-body">
                                <p>
                                    <button type="button" class="btn btn-primary" id="dynamic-start-''' + engine + '''">Start</button>
                                    <button type="button" class="btn btn-primary" id="dynamic-instruction-''' + engine + '''">Instruction</button>
                                    <button type="button" class="btn btn-primary" id="edit-report-''' + engine + '''">Edit</button>
                                </p>
                                <div class="panel panel-info">
                                    <div class="panel-heading">
                                        <h3 class="panel-title">Report</h3>
                                    </div>
                                    <div class="panel-body">
                                        <p>''' + (getattr(dynamic, dynamic_attr[int(engine)-1]) if engine in finishes else "null") + '''</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>'''
    return row.replace('\n', '')


# type defines whether this step is manual of automatic
# startOrEnd defines whether this step is end or start of the test
def choose_modal(engine, step, type, end):
    return '''<div class="modal fade" id="modal-test-''' + engine + '-' + str(step) + '''" tabindex="-1" role="dialog" aria-labelledby="gridSystemModalLabel">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 class="modal-title">''' + engines_name[int(engine)] + 'Project' + str(step + 1) + '''</h4>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6 col-md-offset-3">''' + 'Use ' + item_steps[int(engine) - 1][step] + '''</div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            ''' + (('''<button type="button" class="btn btn-primary" id="next-''' + engine + '-' + str(step) + '''" disabled="disabled">Next</button>''' if not end else '''<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>''') if not type else "") + '''
                        </div>
                    </div>
                </div>
            </div>'''


def generate_modal(engine):
    modal = ''' 
                <div class="modal fade" id="modal-instruction-''' + engine + '''" tabindex="-1" role="dialog" aria-labelledby="gridSystemModalLabel">
                    <div class="modal-dialog" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h4 class="modal-title" >''' + engines_name[int(engine)] + "Instruction" + '''</h4>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6 col-md-offset-3">''' + ".........." + '''</div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
                '''
    for i in range(len(item_steps[int(engine)-1]) - 1):
        modal += choose_modal(engine, i, item_steps[int(engine) - 1][i] in auto_steps, False)
    modal += choose_modal(engine, len(item_steps[int(engine)-1])-1, item_steps[int(engine) - 1][len(item_steps[int(engine)-1]) - 1] in auto_steps, True)

    return modal.replace('\n', '')


def generate_js(engine):
    js = '''
    $("#dynamic-instruction-''' + engine + '''").click(function () {
        $("#modal-instruction-''' + engine + '''").modal('show');
    });
    
    $("#dynamic-start-''' + engine + '''").click(function () {
        $("#modal-test-''' + engine + '-0' + '''").modal({backdrop: 'static', keyboard: false, show: true});
    });
    '''

    for i in range(len(item_steps[int(engine) - 1])):
        js += '''
        if($("#next-''' + engine + '-' + str(i) + '''") != null) {
            $("#next-''' + engine + '-' + str(i) + '''").click(function () {
                $("#modal-test-''' + engine + '-' + str(i) + '''").modal('hide');
                $("#modal-test-''' + engine + '-' + str(i+1) + '''").modal({backdrop: 'static', keyboard: false, show: true});

            });
        }
        '''

    for i in range(len(item_steps[int(engine) - 1])):
        js += '''
        $("#modal-test-''' + engine + '-' + str(i) + '''").on('shown.bs.modal', function () {
            Dynamic.''' + item_steps[int(engine) - 1][i] + '''(md5, function() {''' + ('''
                if($("#next-''' + engine + "-" + str(i) + '''") != null) {
                    $("#next-''' + engine + "-" + str(i) + '''").removeAttr("disabled");
                } ''' if item_steps[int(engine) - 1][i] not in auto_steps else '''
                $("#modal-test-''' + engine + "-" + str(i) + '''").modal('hide');
                if($("#modal-test-''' + engine + "-" + str(i+1) + '''") != null) {
                    $("#modal-test-''' + engine + "-" + str(i+1) + '''").modal({backdrop: 'static', keyboard: false, show: true});

                }
            ''') + '''
            });
            Dynamic.console("''' + item_steps[int(engine) - 1][i] + '''");
        });
        '''
    return js.replace('\n', '')


def generate_dynamic_html(engine, dynamic):
    if engine == 0:
        return ""
    html = generate_row(engine, dynamic)
    modal = generate_modal(engine)
    js = generate_js(engine)
    return html, modal, js

