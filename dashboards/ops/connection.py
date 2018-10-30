#
# Script for Database connectivity
#
# Prerequisite : install mysql-connector-python
#
#@---------------------------------------------------
#@ History
#@---------------------------------------------------
#@ Date   : 01 June, 2018
#@ Author : Sarath G
#@ Reason : Initial release
#@---------------------------------------------------
#
'''
/*
 * This computer program is the confidential information and proprietary trade
 * secret  of  OpsRamp, Inc. Possessions and use of this program must conform
 * strictly to the license agreement between the user and OpsRamp, Inc., and
 * receipt or possession does not convey any rights to divulge, reproduce, or
 * allow others to use this program without specific written authorization of
 * OpsRamp, Inc.
 * 
 * Copyright (c) 2018 OpsRamp, Inc. All rights reserved. 
 */
'''
import _thread
from queue import Queue
from threading import Thread

_threadex = _thread.allocate_lock()
qthreads = 0
sqlqueue = Queue()

CONNECT = "connect"
SQL = "SQL"
STOP = "stop"
wrap = None

import mysql.connector
from mysql.connector import errorcode
from dashboards.ops import properties
import base64
config = properties.configs[properties.saas_key]["mysql"]
config['password'] = base64.b64decode(config['password']).decode()


class DBCmd:
    def __init__(self, cmd, query=None, params=()):
        self.cmd = cmd
        self.query = query
        self.params = params



class DBWrapper(Thread):

    def __init__(self):
        try:
            Thread.__init__(self)
            self.setDaemon(True)

            self.cnx = mysql.connector.connect(**config)
            self.cur = self.cnx.cursor()
        except mysql.connector.Error as err:
            print("DBWrapper: Exception - " + str(err))
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        except Exception as emsg:
            print("DBWrapper: Exception - " + str(emsg))
            raise


    def run(self):
        global qthreads
        while True:
            try:
                cmdObj = sqlqueue.get()
                #logger.debug("Cmd %s -> %s" % (cmdObj.cmd, cmdObj.params))
                if cmdObj.cmd == SQL:
                    res = []
                    # cmdObj.params is a list to bundle statements into a "transaction"
                    try:
                        # For (query, params) in cmdObj.params:
                        query  = cmdObj.query
                        params = cmdObj.params
                        self.cur.execute(query, params)
                        res.append(self.cur.rowcount)
                        res.append(self.cur.fetchall())
                        cmdObj.resultqueue.put(res)

                        if not query.upper().startswith("SELECT"):
                            self.cnx.commit()
                    except Exception as emsg:
                        cmdObj.resultqueue.put(emsg)
                elif cmdObj.cmd == STOP:
                    try:
                        if self.cur:
                            self.cur.close()
                        if self.cnx:
                            self.cnx.close()
                    except Exception as emsg:
                        print("DBWrapper: STOP > Exception while closing db connection - " + str(emsg))

                    _threadex.acquire()
                    qthreads = 0
                    _threadex.release()
                    # Allow other threads to stop
                    sqlqueue.put(cmdObj)
                    cmdObj.resultqueue.put(None)
                    break
            except Exception as emsg:
                try:
                    if self.cur:
                        self.cur.close()
                    if self.cnx:
                        self.cnx.close()
                except:
                    pass

                _threadex.acquire()
                qthreads = 0
                _threadex.release()
                print('DBWrapper: Exception in while - ' + str(emsg))



def executeQuery(cmdObj):
    try:
        global qthreads, wrap
        if cmdObj.cmd == CONNECT:
            # Do not allow multiple threads to start
            _threadex.acquire()
            if qthreads == 0:
                qthreads = 1
            else: 
                _threadex.release()
                return
            _threadex.release()
            
            try:
                wrap = DBWrapper()
                wrap.start()
            except Exception as emsg:
                print("executeQuery: Exception while initializing DB connection - " + str(emsg))
                if qthreads > 0:
                    _threadex.acquire()
                    qthreads = 0
                    _threadex.release()


        elif cmdObj.cmd == STOP:
            try:
                if wrap and not wrap.isAlive() and qthreads > 0:
                    _threadex.acquire()
                    qthreads = 0
                    _threadex.release()
            except Exception as emsg:
                print("executeQuery: STOP > Exception while resetting qthread when wrapper object is not alive  - " + str(emsg))

            if qthreads > 0:
                cmdObj.resultqueue = Queue()
                sqlqueue.put(cmdObj)

        elif cmdObj.cmd == SQL:
            try:
                if wrap and not wrap.isAlive() and qthreads > 0:
                    _threadex.acquire()
                    qthreads = 0
                    _threadex.release()
            except Exception as emsg:
                print("executeQuery: SQL > Exception while resetting qthread when wrapper object is not alive  - " + str(emsg))

            if qthreads == 0:
                executeQuery(DBCmd(CONNECT))
            cmdObj.resultqueue = Queue()
            sqlqueue.put(cmdObj)
            result = cmdObj.resultqueue.get()
            if isinstance(result, Exception):
                raise result
            return result
        else:
            if qthreads == 0:
                executeQuery(DBCmd(CONNECT))
    except:
        raise


''' Sample querying '''
'''
query = "select * from agent_patch_info;"
rows  = executeQuery( DBCmd(SQL, query) )[1]
'''
