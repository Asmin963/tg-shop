def argment_from_callback(call):
    dc = dict()
    args = call.split("-")
    for arg in args:
        if "=" in arg:
            arg, value = arg.split("=")
            dc[arg] = value
        else:
            dc[arg] = True
    return dc



