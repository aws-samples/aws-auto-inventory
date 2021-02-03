# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
  
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
  
#       http://www.apache.org/licenses/LICENSE-2.0
  
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import collections

log = logging.getLogger('aws-auto-inventory.converter')


def flatten(d,sep="_"):
    import collections

    obj={}

    def recurse(t,parent_key=""):
        
        if 'Tags' in parent_key:
            if isinstance(t, list):
                for i in t:
                    if isinstance(i, dict):
                        obj['tag:{}'.format(i['Key'])]=i['Value']
        else:
            if isinstance(t,list):
                for i in range(len(t)):
                    recurse(t[i],parent_key + sep + str(i) if parent_key else str(i))
            elif isinstance(t,dict):
                for k,v in t.items():
                    recurse(v,parent_key + sep + k if parent_key else k)
            else:
                obj[parent_key] = t

    recurse(d)

    return obj

def flatten_list(response, sep):
    if isinstance(response, list):
        result = [ flatten(x,sep) for x in response ]
        return result
    else:
        return [flatten(response, sep)]