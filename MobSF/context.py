# -*- coding: utf_8 -*-
"""
Generate UIs of dynamic engines
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# engines_name = ["???????", "?????????????", "?????????????§Ϋ?", "????????????", "???????????", "?????????????",
#            "???????????§Ϋ????", "?????????????????????", "???????????", "????????????", "??????????????",
#            "????DOS???", "?????????????", "?υτ??????????", "????????????????????", "??????υτ?????????????",
#            "?υτ?????????????????", "?????????????", "????›¥??????"]

engines_name = ["Static", "Sensitive Data"]

item_steps = [
    # can't locate package correctly before static analysis as reject to 'adb's
    ['download', 'zip', 'dex2jar', 'jdgui', 'openso'],
    ['adb-pull'],
    ['adb-pull']
]

auto_steps = ['download', 'zip', 'dex2jar']


dynamic_attr = [
    "HARDCODED",
    "DATABASE",
    "CONFIG_MANIPULATION",
    "SOURCE_MANIPULATION",
    "DATABASE_MANIPULATION",
    "COMMUNICATION_PLAIN",
    "CERT_LOCKED",
    "REPLAY",
    "TIMEOUT",
    "HIJACK",
    "MSG_DOS",
    "REGISTER",
    "LOGIN",
    "NETWORK",
    "CLOUD_AUTH",
    "DEVICE_AUTH",
    "DEVICE_CLOUD",
    "FIRMWARE_UPDATE",
    "FIRMWARE_STORAGE"]


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
                            ''' + (''''<button type="button" class="btn btn-primary" id="next-''' + engine + '-' + str(step) + '''" disabled="disabled">Next</button>''' if not end else '''<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>''') if type else "" + '''
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
    modal += choose_modal(engine, len(item_steps[int(engine)-1])-1, item_steps[int(engine) - 1][len(item_steps[int(engine)-1]) - 1], True)

    return modal.replace('\n', '')


def generate_js(engine):
    js = '''
    $("#dynamic-instruction-''' + engine + '''").click(function () {
        $("#modal-instruction-''' + engine + '''").modal('toggle');
    });
    
    $("#dynamic-start-''' + engine + '''").click(function () {
        $("#modal-test-''' + engine + '-0' + '''").modal({backdrop: 'static', keyboard: false});
    });
    '''

    for i in range(len(item_steps[int(engine) - 1]) - 1):
        js += '''
    $("#next-''' + engine + '-' + str(i) + '''").click(function () {
        $("#modal-test-''' + engine + '-' + str(i) + '''").modal('toggle');
        $("#modal-test-''' + engine + '-' + str(i+1) + '''").modal({backdrop: 'static', keyboard: false});
        Dynamic.''' + item_steps[int(engine) - 1][i+1] + '''(md5, function() {
            if($("#next-''' + engine + '-' + str(i) + '''") != null) {
                $("#next-''' + engine + '-' + str(i) + '''").removeAttr("disabled");
            } 
        });
    });
        '''

    for i in range(len(item_steps[int(engine) - 1])):
        js += '''
        $("#modal-test-''' + engine + '-' + str(i) + '''").on('shown.bs.modal', function () {
            Dynamic.''' + item_steps[int(engine) - 1][0] + '''(md5, function() {''' + ''' 
            if($("#next-''' + engine + '''-0") != null) {
                $("#next-''' + engine + '''-0").removeAttr("disabled");
            } ''' if item_steps[int(engine) - 1][0] not in auto_steps else '''
            $("#modal-test-''' + engine + '''-0").modal('toggle');
            if($("#modal-test-''' + engine + '''-1") != null) {
                $("#modal-test-''' + engine + '''-1").modal({backdrop: 'static', keyboard: false});
                
            }
            ''' + '''
        })
        '''


    return js.replace('\n', '')


def generate_dynamic_html(engine, dynamic):
    if engine == 0:
        return ""
    html = generate_row(engine, dynamic)
    modal = generate_modal(engine)
    js = generate_js(engine)
    return html, modal, js

