from urllib.request import urlopen, Request
import sys


def disable_cert_check_context():
    try:
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode    = ssl.CERT_NONE
        return context
    except:
        return None
 
 
def allow_tls_only_context():
    try:
        import ssl
        encrption_protocol = ssl.PROTOCOL_TLSv1
        python_version = sys.version_info
        if python_version >= (3,6):
            encrption_protocol = ssl.PROTOCOL_TLS
        
        context = ssl.SSLContext(encrption_protocol)
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        return context
    except:
        return None


def http_request(url, headers={}, data=None):
    try:
        http_headers = {
            'Content-Type' : 'application/json',
            'Accept'       : '*/*'
        }
        http_headers.update(headers)
        req = Request(url, data, http_headers)
        python_version = sys.version_info
        if sys.version_info >= (3,4,3):
            return urlopen(req, context=allow_tls_only_context(), timeout=30).read()
            #return urlopen(req, context=disable_cert_check_context(), timeout=30).read()
        elif python_version >= (2,6):
            return urlopen(req, timeout=30).read()
        else:
            return urlopen(req).read()
    except Exception:
        raise

