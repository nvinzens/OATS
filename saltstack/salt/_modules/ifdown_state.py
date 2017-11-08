




def ping(destination='192.168.50.10'):
    '''
    Execution function to ping and determine if a state should be invoked.
    '''
    ping_result = __salt__['net.ping'](destination)
    # determine if should run the state
    print ping_result
    execute_the_state = false
    if execute_the_state:
        return __salt__['state.sls']('sls_name')
    return {
        'comment': 'No need to run the state',
        'result': None,
        'id': 'dummy',
        'changes': {}
    }
