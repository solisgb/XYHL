# -*- coding: Latin-1 -*-
"""
Script para hacer graficos temporales con lineas horizontales

@solis
"""
import traceback
import logging

if __name__ == "__main__":

    try:
        from datetime import timedelta
        from time import time
        startTime = time()

        xtime = time.time()-startTime
        print('The script took {0}'.format(str(timedelta(seconds=xtime))))
    except Exception as e:
        logging.error(traceback.format_exc())
    finally:
        print('fin')
