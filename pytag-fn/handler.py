import sys, json, requests, os
import urllib3

# Surpress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### VAPI REST endpoints
VAPI_SESSION_PATH='/rest/com/vmware/cis/session'
VAPI_TAG_PATH='/rest/com/vmware/cis/tagging/tag-association/id:'

### Simple VAPI REST tagging implementation
class FaaSResponse:
    def __init__(self, status, message):
        self.status=status
        self.message=message

class Tagger:
    def __init__(self,conn):
        try:
            self.username=os.environ['VC_USERNAME']
            self.password=os.environ['VC_PASSWORD']
            self.vc=os.environ['VC']
            self.tagurn=os.environ['TAG_URN']
            self.action=os.environ['TAG_ACTION'].lower()
        except KeyError:
            print('VC, VC_USERNAME, VC_PASSWORD, TAG_URN and TAG_ACTION environment variables must be set')
            sys.exit(1)
        self.session=conn

    # vCenter connection handling    
    def connect(self):
        try:
            resp = self.session.post('https://'+self.vc+VAPI_SESSION_PATH,auth=(self.username,self.password))
            resp.raise_for_status()
            return FaaSResponse('200', 'successfully connected to vCenter')
        except (requests.HTTPError, requests.ConnectionError) as err:
            return FaaSResponse('500', 'could not connect to vCenter {0}'.format(err))

    # VAPI REST tagging implementation        
    def tag(self,obj):
        try:
            resp = self.session.post('https://'+self.vc+VAPI_TAG_PATH+self.tagurn+'?~action='+self.action,json=obj)
            resp.raise_for_status()
            print(resp.text)
            return FaaSResponse('200', 'successfully {0}ed tag on VM: {1}'.format(self.action, obj['object_id']['id']))
        except requests.HTTPError as err:
            return FaaSResponse('500', 'could not tag object {0}'.format(err))

def handle(req):
    # Validate input
    try:
        j = json.loads(req)
    except ValueError as err:
        res = FaaSResponse('400','invalid JSON {0}'.format(err))
        print(json.dumps(vars(res)))
        return
        
    # Assert managed object reference ('moref', e.g. to aVM) exists
    try:
        ref = (j['moref'])
    except KeyError as err:
        res = FaaSResponse('400','JSON does not contain ManagedObjectReference {0}'.format(err))
        print(json.dumps(vars(res)))
        return

    # Convert MoRef to an object VAPI REST tagging endpoint requires
    obj = {
        'object_id': {
            'id': ref['Value'],
            'type': ref['Type']
        }
    }

    # Open session to VAPI REST and obtain session token
    s=requests.Session()
    s.verify=False
    t = Tagger(s)
    res = t.connect()
    if res.status != '200':
        print(json.dumps(vars(res)))
        return

    # Perform tagging action on the object
    res = t.tag(obj)
    if res.status != '200':
        print(json.dumps(vars(res)))
        return

    # Close session to VC
    s.close()

    print(json.dumps(vars(res)))
    return

