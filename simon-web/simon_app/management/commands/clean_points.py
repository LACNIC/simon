from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint
from simon_app.decorators import chatty_command
import sys
from Queue import Queue
from threading import Thread
from collections import defaultdict

__author__ = 'agustin'


class Command(BaseCommand):
    @chatty_command(command="Clean Test Points")
    def handle(self, *args, **options):
        tps = SpeedtestTestPoint.objects.all()

        results = defaultdict(lambda: defaultdict(bool))
        concurrent = 100

        def do_work():
            while True:
                tp = q.get()
                before = tp.enabled
                enabled = tp.check_point()
                after = enabled

                results[tp.url]['before'] = before
                results[tp.url]['after'] = after

                q.task_done()

        q = Queue(concurrent)
        for i in range(concurrent):
            t = Thread(target=do_work)
            t.daemon = True
            t.start()

        try:
            for tp in tps[:]:
                q.put(tp)
            q.join()
        except KeyboardInterrupt:
            sys.exit(1)

        up = []
        down = []
        still_up = []
        for url, statuses in results.iteritems():
            _before = statuses['before']
            _after = statuses['after']
            if _before != _after and not _after:
                down.append(url)
            elif _before != _after and _after:
                up.append(url)
            elif _after:
                still_up.append(url)

        if up: print "UP ", up
        if down: print "DOWN ", down
        if still_up: print "STILL UP ", still_up
        return "The following points have been disabled"
