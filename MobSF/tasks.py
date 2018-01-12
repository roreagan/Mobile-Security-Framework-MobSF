from cele import app
from StaticAnalyzer.views.android.static_analyzer import xday
from MobSF.models import Task


@app.task()
def static_analysis(id, md5, engines):
    try:
        task = Task.objects.get(id=id)
        if engines[0] == 0:
            xday(id, md5)
    except:
        print("task doesn't exist!")

