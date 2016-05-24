__author__ = 'elisa'
from simon_app.management.commands.tweet import *
from simon_app.models import *
from django.core.management.base import BaseCommand
import simon_project.settings as settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        import random

        rs = Results.objects.inner(settings.PROTOCOLS['HTTP'], 12)
        top = []
        bottom = []
        i = 0
        order = sorted(rs, key=lambda tup: tup[1])
        #print len(order)
        for r in order:
            i=i+1
            if(i<6):
                if(int(r[1])%10 >= 5):
                    #print r[0], '|'*(int(r[1])/10),'+'
                    top.append((r[0], '|'*(int(r[1])/10)+'+'))
                else:
                    #print r[0], '|'*(int(r[1])/10)
                    top.append((r[0], '|'*(int(r[1])/10)))
            elif(i>17):
                if(int(r[1])%10 >= 5):
                    #print r[0], '|'*(int(r[1])/10),'+'
                    bottom.append((r[0], '|'*(int(r[1])/10)+'+'))
                else:
                    #print r[0], '|'*(int(r[1])/10)
                    bottom.append((r[0], '|'*(int(r[1])/10)))
            #suma = suma + int(r[1])/10

        #print top[0][1]

        textTop = "Top 5 inner latency via HTTP\n %s %s\n %s %s\n %s %s\n %s %s\n %s %s\n(| = 10ms)" % (top[0][0], top[0][1], top[1][0], top[1][1], top[2][0], top[2][1], top[3][0], top[3][1], top[4][0], top[4][1])
        textBottom = "Bottom 5 inner latency via HTTP\n %s %s\n %s %s\n %s %s\n %s %s\n %s %s\n(| = 10ms)" % (bottom[0][0], bottom[0][1], bottom[1][0], bottom[1][1], bottom[2][0], bottom[2][1], bottom[3][0], bottom[3][1], bottom[4][0], bottom[4][1])

        print len(textTop), len(textBottom)
        print textTop
        print textBottom
        #tweet(text)