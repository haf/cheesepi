""" Copyright (c) 2015, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
      * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
      * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
      * Neither the name of The Swedish Institute of Computer Science nor the
        names of its contributors may be used to endorse or promote products
        derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
"""
import sys
import logging
import hashlib

# Influx
try:
    from influxdb import InfluxDBClient
except:
    msg="Missing InfluxDB python module (and GridFS and bson), use 'pip install influxdb'"
    logging.error(msg)
    exit(1)

import cheesepi
import dao

host     = "localhost"
port     = 8083
username = "user"
password = "password"
database = "cheesepi"

class DAO_mongo(dao.DAO):
    def __init__(self):
        try: # Get a hold of a MongoDB connection
            self.conn =  = InfluxDBClient(host, port, username, password, database)
        except Exception as e:
            msg = "Error: Connection to Influx database failed! Ensure InfluxDB is running. "+str(e)
            logging.error(msg)
            print msg
            exit(1)


    # user level interactions
    def read_user(self):
        user = self.conn..query('select * from user limit 1;')
        return user


    def write_user(self, user_data):
        # check we dont already exist
        print "Saving: ",user_data
        json = self.to_json("user",user_data)
        return self.conn.write_points(json)


    # operator level interactions
    def write_op(self, op_type, dic, binary=None):
        if not self.validate_op(op_type):
            return
        #if binary!=None:
        #    # save binary, check its not too big
        #    dic['binary'] = bson.Binary(binary)
        config = cheesepi.config.get_config()
        dic['version'] = config['version']
        md5 = hashlib.md5(config['secret']+str(dic)).hexdigest()
        dic['sign']    = md5

        json = to_json(op_type, dic)
        print "Saving Op: %s" % json
        try:
            return self.conn.write_points(json)
        except:
            logging.error("Database Influx Op write failed!")
            exit(1)
        return id


    def read_op(self, op_type, timestamp=0, limit=100):
        op = self.conn..query('select * from '+op_type+' limit 1;')
        return op


    def to_json(self, table, dic):
        json = [{"name":table, "columns":dic.keys(), "points":dic.values()}]
        return json

