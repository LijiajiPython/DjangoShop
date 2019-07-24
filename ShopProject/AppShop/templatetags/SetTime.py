import re
from django import template
import time

register=template.Library()

@register.filter(name="setTime")
def cst_to_str(cstTime):
    cstTime=str(cstTime)
    timeList=cstTime.split("-")
    newTime="%s-%s-%s"%(timeList[0],timeList[1],timeList[2])
    return newTime
