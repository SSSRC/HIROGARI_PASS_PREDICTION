import ephem
import datetime
import requests
import numpy as np
import csv
import os

def get_tle(cat_id='47930'):
    url = "https://celestrak.com/satcat/tle.php?CATNR=" + cat_id
    r = requests.post(url)
    TLE = r.text.split("\r\n")[:3]
    return TLE


def judge_round(az_rise, az_set, az_max):
    flag_round = False

    parameter = az_rise
    distance = 0
    while(parameter != az_max):
        parameter += 1
        distance += 1
        if parameter >= 360:
            parameter -= 360
    if distance <= 180:
        flag_clockwise = True
    else:
        flag_clockwise = False
    parameter = az_rise
    while(parameter != az_set):
        if flag_clockwise:
            parameter += 1
        else:
            parameter -= 1
        if parameter >= 360:
            parameter -= 360
        elif parameter < 0:
            parameter += 360
        if parameter > 160 and parameter < 165:
            flag_round = True
            break

    return flag_round

def shimcham(start_time, end_time):
    sssrc = ephem.Observer()
    sssrc.lat = '34.545898'
    sssrc.lon = '135.503224'
    sssrc.date = start_time

    filename_default = 'hirogari_pass_prediction'
    filename = filename_default
    i = 1
    while os.path.isfile('./' + filename + '.csv'):
        filename = filename_default + '(' + str(i) + ')'
        i += 1

    f = open('./' + filename + '.csv', 'w')
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow( ['AOS', 'LOS', 'PASS', 'MEL[deg]', 'MEL_TIME', 'AZ_AOS[deg]', 'AZ_LOS[deg]', 'DAISENKAI'] )

    TLE = get_tle('47930')
    hirogari = ephem.readtle(TLE[0], TLE[1], TLE[2])
    current_time = start_time
    while (current_time - end_time).total_seconds() < 0:
        sssrc.date = current_time - datetime.timedelta(hours=9)
        rise_t, az_rise, max_t, alt_max, set_t, az_set = sssrc.next_pass(hirogari)
        #az_max = orbit.cal_orbit(TLE, max_t)[0]
        rise_t = ephem.localtime(rise_t)
        max_t = ephem.localtime(max_t)
        set_t = ephem.localtime(set_t)
        sssrc.date = max_t - datetime.timedelta(hours=9)
        hirogari.compute(sssrc)
        az_max = hirogari.az * (180/3.141592)
        current_time = set_t
        pass_len = set_t - rise_t
        pass_len = pass_len.seconds
        pass_min = int(pass_len/60)
        pass_sec = pass_len%60
        pass_len = str(pass_min)+':'+str(pass_sec)
        az_rise = '{0:.1f}'.format(np.rad2deg(az_rise))
        alt_max = '{0:.1f}'.format(np.rad2deg(alt_max))
        az_set = '{0:.1f}'.format(np.rad2deg(az_set))
        daisenkai = judge_round(int(float(az_rise)), int(float(az_set)), int(float(az_max)))
        pass_info = [rise_t.strftime("%Y-==%m-%d %H:%M:%S"), set_t.strftime("%Y-%m-%d %H:%M:%S"), pass_len, alt_max, max_t.strftime("%Y-%m-%d %H:%M:%S"), az_rise, az_set, daisenkai]
        writer.writerow(pass_info)

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(days = 30)
    #start_time = datetime.datetime(2021, 5, 16, 9, 30, 0)
    #end_time = datetime.datetime(2021, 6, 16, 9, 30, 0)
    shimcham(start_time, end_time)