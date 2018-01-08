from cele import app
from StaticAnalyzer.views.android.static_analyzer import xday
from MobSF.models import Task

analysis_engiens = [
    xday
]


@app.task()
def static_analysis(id, md5, engines):
    task = Task.objects.get(id=id)
    for engine in engines:
        try:
            analysis_engiens[int(engine)](id, md5)
        except:
            print "Chosen Engines don't exist!"
        task.PROGRESS = task.PROGRESS + 1
        task.save()