import sys, json, requests, os
import urllib3

# Surpress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### VAPI REST endpoints
VAPI_SESSION_PATH="/rest/com/vmware/cis/session"
VAPI_TAG_PATH="/rest/com/vmware/cis/tagging/tag-association/id:"

### Simple VAPI REST tagging implementation
class Tagger:
    def __init__(self,conn):
        try:
            self.username=os.environ['VCUSERNAME']
            self.password=os.environ['VCPASSWORD']
            self.vc=os.environ['VC']
            self.tagurn=os.environ['TAGURN']
        except KeyError:
            print('VC, VCUSERNAME, VCPASSWORD and TAGURN environment variables must be set')
            sys.exit(1)
        self.session=conn
    def connect(self):
        try:
            resp = self.session.post('https://'+self.vc+VAPI_SESSION_PATH,auth=(self.username,self.password))
            resp.raise_for_status()
        except requests.HTTPError as err:
            if err.response is not None and err.response.status_code == 401:
                resp = {
                    "statusCode": "500",
                    "message": str('could not connect to vCenter {0}'.format(err))
                }
                print(json.dumps(resp))
                return
    def tag(self,obj, action):
        try:
            resp = self.session.post('https://'+self.vc+VAPI_TAG_PATH+self.tagurn+'?~action='+action,json=obj)
            resp.raise_for_status()
        except requests.HTTPError as err:
            if err.response is not None:
                resp = {
                    "statusCode": "500",
                    "message": str('could not tag object {0}'.format(err))
                }
                print(json.dumps(resp))
                return
        else:
            resp = {
                "statusCode": "200",
                "message": str('successfully tagged VM: '+obj['object_id']['id'])
            }
            print(json.dumps(resp))

def handle(req):
    # Validate input
    try:
        j = json.loads(req)
    except ValueError as err:
        resp = {
            "statusCode": "400",
            "message": str('invalid JSON {0}'.format(err))
        }
        print(json.dumps(resp))
        return

    # Assert managed object reference ("moref", e.g. to aVM) exists
    try:
        ref = (j['moref'])
    except KeyError as err:
        resp = {
            "statusCode": "400",
            "message": str('JSON does not contain ManagedObjectReference {0}'.format(err))
        }
        print(json.dumps(resp))
        return

    # Convert MoRef to an object VAPI REST tagging endpoint requires
    obj = {
        "object_id": {
            "id": ref['Value'],
            "type": ref['Type']
        }
    }

    # Open session to VAPI REST and obtain session token
    s=requests.Session()
    s.verify=False
    t = Tagger(s)
    t.connect()

    # Attach tag to the object
    t.tag(obj, "attach")

    # Close session to VC
    s.close()

