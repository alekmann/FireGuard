from firebase_functions import https_fn

@https_fn.on_request()
def hello(req):
    return "Firebase Python deploy works!"
