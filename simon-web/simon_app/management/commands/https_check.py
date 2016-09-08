#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from simon_app.models import *
from random import shuffle
import datetime, logging
from multiprocessing.dummy import Pool as ThreadPool
from simon_app.reportes import GMTUY
from simon_app.decorators import chatty_command


@chatty_command(command="HTTPS Check")
class Command(BaseCommand):
    threads = 10
    max_job_queue_size = 500  # 0 for limitless
    max_points = 100  # 0 for limitless

    def handle(self, *args, **options):
        def do_work(tp):
            try:
                online = tp.check_point(timeout=10, save=False, protocol="https")
                if tp.get_latest_https_check != online:
                    check = HttpsCheck(test_point=tp, status=online)
                    tp.httpscheck_set.add(check)

            except Exception as e:
                logging.error(e)
                pass

            finally:
                return

        tps = SpeedtestTestPoint.objects.all()

        thread_pool = ThreadPool(self.threads)

        then = datetime.datetime.now(tz=GMTUY())

        if self.max_points > 1:
            tps = tps[:self.max_points]
        elif self.max_points == 1:
            tps = [tps[0]]

        tps = list(tps)
        shuffle(tps)  # shuffle in case the script get aborted (do not run only the small alphanumeric tps only)

        logging.info("TPs: %s " % (len(tps)))
        logging.info("Launching %.0f worker threads on a %.0f jobs queue" % (self.threads, len(tps)))
        thread_pool.map(do_work, tps)

        thread_pool.close()
        thread_pool.join()

        logging.info("Command ended with %.0f worker threads on a %.0f jobs queue" % (self.threads, len(tps)))
        logging.info("Command took %s" % (datetime.datetime.now(tz=GMTUY()) - then))
